import ast
import time
from collections import defaultdict
import torch
import itertools
import pandas as pd
from transformers import AutoTokenizer, AutoModelForCausalLM


MODEL_NAME = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"

MAPPING_CSV = "top3000_superset_token_mapping.csv"
TRACE_CSV = "output_side_channel_traces.csv"
RESULT_CSV = "output_recovery_results.csv"

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

START_N = 2


def parse_list(x):
    if isinstance(x, list):
        return x
    return ast.literal_eval(str(x))


def load_superset_to_tokens(path):
    df = pd.read_csv(path)

    assert "superset" in df.columns
    assert "tokens" in df.columns

    group_to_tokens = defaultdict(list)

    for _, row in df.iterrows():
        superset_id = int(row["superset"])
        tokens = parse_list(row["tokens"])
        group_to_tokens[superset_id] = [int(t) for t in tokens]

    return group_to_tokens





def recover_start(trace, group_to_tokens, tokenizer, model, device, n=2, batch_size=512):
    bos_token_id = tokenizer.bos_token_id or tokenizer.cls_token_id

    # candidate for first token
    token_candidate_0 = group_to_tokens.get(trace[0], [])
    token_candidate_1 = []

    for first_token in token_candidate_0:
        word = tokenizer.decode([first_token], skip_special_tokens=True)
        if len(word) > 0 and "A" <= word[0] <= "Z":
            token_candidate_1.append(first_token)

    token_candidates = [token_candidate_1]

    # next n tokens
    for i in range(n):
        token_candidates.append(group_to_tokens.get(trace[i + 1], []))

    if any(len(cands) == 0 for cands in token_candidates):
        return []

    # all start token combinations
    token_combinations = list(itertools.product(*token_candidates))

    next_idx = n + 1
    if next_idx >= len(trace):
        return list(token_combinations[0])

    token_candidates_next = group_to_tokens.get(trace[next_idx], [])
    if len(token_candidates_next) == 0:
        return list(token_combinations[0])

    token_candidates_next_tensor = torch.tensor(
        token_candidates_next,
        dtype=torch.long,
        device=device
    )

    best_score = -1.0
    best_tokens = None

    model.eval()

    with torch.no_grad():
        for start in range(0, len(token_combinations), batch_size):
            batch_combos = token_combinations[start:start + batch_size]

            # input shape: [B, seq_len]
            # each row: [BOS, token1, token2, ..., token_{n+1}]
            input_ids = torch.tensor(
                [[bos_token_id] + list(tokens) for tokens in batch_combos],
                dtype=torch.long,
                device=device
            )

            outputs = model(input_ids=input_ids)
            logits = outputs.logits
            probs = torch.softmax(logits, dim=-1)

            # Compute probability of each candidate sequence:
            # P(t1 | BOS) * P(t2 | BOS,t1) * ...
            seq_probs = torch.ones(
                input_ids.shape[0],
                dtype=torch.float32,
                device=device
            )

            # input_ids[:, 1:] are the true next tokens
            for pos in range(input_ids.shape[1] - 1):
                next_tokens = input_ids[:, pos + 1]
                token_probs = probs[:, pos, :].gather(
                    dim=1,
                    index=next_tokens.unsqueeze(1)
                ).squeeze(1)

                seq_probs *= token_probs.float()

            # Now predict the next token after this start sequence
            next_probs = probs[:, -1, :]  # [B, vocab_size]

            # restrict to candidates matching trace[next_idx]
            candidate_probs = next_probs[:, token_candidates_next_tensor]

            best_next_probs, best_next_indices = torch.max(candidate_probs, dim=1)

            total_scores = seq_probs * best_next_probs.float()

            batch_best_score, batch_best_row = torch.max(total_scores, dim=0)

            if batch_best_score.item() > best_score:
                best_score = batch_best_score.item()

                best_combo = list(batch_combos[batch_best_row.item()])
                best_next_token = token_candidates_next[
                    best_next_indices[batch_best_row].item()
                ]

                best_tokens = best_combo + [best_next_token]

    return best_tokens


def recover(trace, group_to_tokens, model, device, start_tokens):
    tokens = start_tokens.copy()

    for i in range(len(trace) - len(start_tokens)):
        trace_idx = len(start_tokens) + i
        token_candidates_next = group_to_tokens.get(trace[trace_idx], [])

        if len(token_candidates_next) == 0:
            break

        inputs = {
            "input_ids": torch.tensor(
                [tokens],
                dtype=torch.long,
                device=device
            )
        }

        with torch.no_grad():
            logits = model(**inputs).logits

        probs = torch.softmax(logits[0, -1, :], dim=-1)
        best_j = max(token_candidates_next, key=lambda j: probs[j].item())

        tokens.append(best_j)

    return tokens


def main():
    print("Device:", DEVICE)

    print("Loading tokenizer and model...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        device_map="auto" if DEVICE == "cuda" else None,
        torch_dtype=torch.bfloat16 if DEVICE == "cuda" else torch.float32,
        trust_remote_code=True
    )

    model.generation_config.pad_token_id = model.generation_config.eos_token_id
    model.to(DEVICE)
    model.eval()

    print("Loading superset-token mapping...")
    group_to_tokens = load_superset_to_tokens(MAPPING_CSV)

    non_empty_groups = sum(1 for _, tokens in group_to_tokens.items() if len(tokens) > 0)
    print("Non-empty supersets:", non_empty_groups)

    print("Loading side-channel traces...")
    df = pd.read_csv(TRACE_CSV)

    assert "text" in df.columns
    assert "token_ids" in df.columns
    assert "side_channel_trace" in df.columns

    print("Input size:", df.shape)

    results = []

    true_count = 0
    total_count = 0
    exact_match_count = 0
    recovered_rows = 0
    failed_rows = 0

    start_time = time.time()

    for idx, row in df.iterrows():
        # if idx % 10 == 0:
        print(f"Processing {idx}/{len(df)}")

        true_token_ids = [int(x) for x in str(row["token_ids"]).split()]
        trace = parse_list(row["side_channel_trace"])
        trace = [int(x) for x in trace if x is not None]

        if len(trace) == 0:
            failed_rows += 1
            continue

        try:
            start_tokens = recover_start(
                trace=trace,
                group_to_tokens=group_to_tokens,
                tokenizer=tokenizer,
                model=model,
                device=DEVICE,
                n=START_N
            )

            if len(start_tokens) == 0:
                failed_rows += 1
                continue

            recovered_tokens = recover(
                trace=trace,
                group_to_tokens=group_to_tokens,
                model=model,
                device=DEVICE,
                start_tokens=start_tokens
            )

        except Exception as e:
            failed_rows += 1
            print(f"Failed row {idx}: {e}")
            continue

        compare_len = min(len(true_token_ids), len(recovered_tokens))

        row_correct = sum(
            1 for j in range(compare_len)
            if true_token_ids[j] == recovered_tokens[j]
        )

        true_count += row_correct
        total_count += len(true_token_ids)

        exact_match = (
            len(recovered_tokens) == len(true_token_ids)
            and recovered_tokens == true_token_ids
        )

        if exact_match:
            exact_match_count += 1

        recovered_rows += 1

        recovered_text = tokenizer.decode(
            recovered_tokens,
            skip_special_tokens=True
        )

        results.append({
            "row_id": idx,
            "true_text": row["text"],
            "recovered_text": recovered_text,
            "true_token_ids": true_token_ids,
            "recovered_token_ids": recovered_tokens,
            "side_channel_trace": trace,
            "token_correct": row_correct,
            "token_total": len(true_token_ids),
            "token_accuracy": row_correct / len(true_token_ids) if len(true_token_ids) > 0 else 0.0,
            "exact_match": exact_match,
        })

        print([
            idx,
            "token_acc_so_far",
            true_count / total_count if total_count > 0 else 0.0,
            "recovered_rows",
            recovered_rows
        ])

    end_time = time.time()

    result_df = pd.DataFrame(results)
    result_df.to_csv(RESULT_CSV, index=False)

    token_accuracy = true_count / total_count if total_count > 0 else 0.0
    exact_match_accuracy = exact_match_count / recovered_rows if recovered_rows > 0 else 0.0

    print("\n========== Results ==========")
    print("Total rows:", len(df))
    print("Recovered rows:", recovered_rows)
    print("Failed rows:", failed_rows)
    print("Token correct:", true_count)
    print("Token total:", total_count)
    print("Token-level accuracy:", token_accuracy)
    print("Exact-match rows:", exact_match_count)
    print("Exact-match accuracy over recovered rows:", exact_match_accuracy)
    print("Elapsed time:", end_time - start_time)
    print("Saved results to:", RESULT_CSV)

    if len(result_df) > 0:
        print("\nFirst result row:")
        print(result_df.iloc[0].to_string())


if __name__ == "__main__":
    main()