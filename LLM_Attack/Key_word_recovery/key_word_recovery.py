import pandas as pd
import ast
import random


QUESTION_CSV = "question_side_channel_traces.csv"
FOCUS_CSV = "focus_area_side_channel_traces.csv"
OUTPUT_CSV = "keyword_recovery_results.csv"



def parse_trace(trace_str):
    """
    Convert trace string like "[0, 1, 0, ..., 1]" to list[int].
    """
    if isinstance(trace_str, list):
        return trace_str

    trace = ast.literal_eval(trace_str)
    return [int(x) for x in trace]


def is_fully_contained(keyword_trace, question_trace):
    """
    Check whether all active supersets in keyword_trace
    are also active in question_trace.

    Equivalent to:
        keyword_trace[j] <= question_trace[j] for all j
    """
    return all(k <= q for k, q in zip(keyword_trace, question_trace))


def main():

    print("Reading files...")
    question_df = pd.read_csv(QUESTION_CSV)
    focus_df = pd.read_csv(FOCUS_CSV)

    assert "label" in question_df.columns, "QUESTION_CSV must contain column: label"
    assert "trace" in question_df.columns, "QUESTION_CSV must contain column: trace"
    assert "label" in focus_df.columns, "FOCUS_CSV must contain column: label"
    assert "trace" in focus_df.columns, "FOCUS_CSV must contain column: trace"

    print("Question file size:", question_df.shape)
    print("Focus area file size:", focus_df.shape)

    print("Parsing focus_area traces...")
    focus_profiles = []
    for _, row in focus_df.iterrows():
        label = str(row["label"])
        trace = parse_trace(row["trace"])
        active_set = frozenset(i for i, v in enumerate(trace) if v == 1)
        focus_profiles.append((label, active_set))

    print("Number of focus_area profiles:", len(focus_profiles))

    results = []
    correct = 0
    no_match = 0

    print("Running keyword recovery attack...")
    for idx, row in question_df.iterrows():
        if idx % 1000 == 0:
            print(f"Processing {idx}/{len(question_df)}")

        true_label = str(row["label"])
        q_trace = parse_trace(row["trace"])
        q_active_set = set(i for i, v in enumerate(q_trace) if v == 1)

        matched_labels = []

        for focus_label, focus_active_set in focus_profiles:
            if focus_active_set.issubset(q_active_set):
                matched_labels.append(focus_label)

        if len(matched_labels) == 0:
            pred_label = None
            no_match += 1
            is_correct = False
        else:
            pred_label = random.choice(matched_labels)
            is_correct = pred_label == true_label

        if is_correct:
            correct += 1

        results.append({
            "true_label": true_label,
            "pred_label": pred_label,
            "num_matches": len(matched_labels),
            "correct": is_correct,
        })

    total = len(question_df)
    accuracy = correct / total if total > 0 else 0.0
    no_match_ratio = no_match / total if total > 0 else 0.0

    result_df = pd.DataFrame(results)
    result_df.to_csv(OUTPUT_CSV, index=False)

    print("\n========== Results ==========")
    print("Total questions:", total)
    print("Correct:", correct)
    print("Accuracy:", accuracy)
    print("No match:", no_match)
    print("No match ratio:", no_match_ratio)
    print("Average number of matches:", result_df["num_matches"].mean())
    print("Median number of matches:", result_df["num_matches"].median())
    print("Saved results to:", OUTPUT_CSV)

    print("\nFirst result row:")
    print(result_df.iloc[0].to_string())


if __name__ == "__main__":
    main()