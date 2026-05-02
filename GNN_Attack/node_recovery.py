import os
import json
import math
import pickle
from itertools import combinations

import numpy as np
import torch
from torch_geometric.datasets import Planetoid, Amazon


SLC_NUM_SETS = 4096
MAX_ENUM_COMBINATIONS = 10_000_000

datasets= {
    "cora": {
        "f": 46.78,
        "T": {"cprime": 60, "gprime": 95},
        "loader": lambda: Planetoid(root="data/Cora", name="Cora"),
    },
    "amazon_photo": {
        "f": 25.29,
        "T": {"cprime": 36, "gprime": 58},
        "loader": lambda: Amazon(root="data/Amazon", name="Photo"),
    },
}


def build_undirected_neighbors(edge_index, num_nodes):
    neighbors = [set() for _ in range(num_nodes)]

    src = edge_index[0].cpu().numpy()
    dst = edge_index[1].cpu().numpy()

    for u, v in zip(src, dst):
        u = int(u)
        v = int(v)

        if u == v:
            continue

        neighbors[u].add(v)
        neighbors[v].add(u)

    return neighbors


def compute_trace_with_adjacent_overlap_correction(
    selected_nodes,
    node_sets,
    device="mps",
):
    selected_nodes_tensor = torch.tensor(
        selected_nodes,
        dtype=torch.long,
        device=device,
    )

    selected_cache = torch.index_select(
        node_sets,
        dim=0,
        index=selected_nodes_tensor,
    )

    # Sum all selected nodes first.
    trace = selected_cache.sum(dim=0)

    # Subtract overlap only between adjacent memory-layout node ids.
    for i in range(len(selected_nodes)):
        u = selected_nodes[i]
        for j in range(i + 1, len(selected_nodes)):
            v = selected_nodes[j]

            if abs(u - v) == 1:
                overlap = torch.minimum(node_sets[u], node_sets[v])

                # Keep your exact rule.
                if torch.sum(overlap).item() == 1:
                    trace -= overlap

    return trace


def recover_one_node(
    target_node,
    observed_trace,
    node_sets,
    f_avg,
    threshold_T,
    device="mps",
):
    """
    Appendix-D-like single-node recovery.

    observed_trace:
        v, shape [4096]

    node_sets:
        M_G, shape [N, 4096]

    Return:
        recovered node ids as a Python set.
    """

    # Step 1: filtering, M[i, j] <= v[j] for all j.
    dominated = (node_sets <= observed_trace.unsqueeze(0)).all(dim=1)
    candidates = torch.nonzero(dominated).flatten().cpu().tolist()

    # Step 2: estimate m_hat using Table 2 f.
    m_hat = int(round(float(observed_trace.sum().item()) / f_avg))
    m_hat = max(0, m_hat)

    # If not trustworthy, or no pruning needed, return candidates.
    if m_hat >= threshold_T:
        return set(candidates), {
            "m_hat": m_hat,
            "num_candidates": len(candidates),
            "status": "return_candidates_m_hat_ge_T",
        }
    
    if len(candidates) <= m_hat:
        return set(candidates), {
            "m_hat": m_hat,
            "num_candidates": len(candidates),
            "status": "return_candidates_already_small",
        }

    if m_hat == 0:
        return set(), {
            "m_hat": m_hat,
            "num_candidates": len(candidates),
            "status": "m_hat_zero",
        }

    num_comb = math.comb(len(candidates), m_hat)
    if num_comb > MAX_ENUM_COMBINATIONS:
        return set(candidates), {
            "m_hat": m_hat,
            "num_candidates": len(candidates),
            "status": f"return_candidates_too_many_combinations_{num_comb}",
        }

    # Step 3: pruning.
    # Enumerate size-m_hat subsets whose combined footprint is contained in v.
    valid_union = set()
    num_valid = 0


    if(len(list(combinations(candidates, m_hat))))>10000:
        return set(candidates), {
            "m_hat": m_hat,
            "num_candidates": len(candidates),
            "status": f"return_candidates_too_many_combinations_{num_comb}",
        }
    for subset in combinations(candidates, m_hat):
        fake_trace = compute_trace_with_adjacent_overlap_correction(
            selected_nodes=list(subset),
            node_sets=node_sets,
            device=device,
        )

        if torch.all(fake_trace <= observed_trace):
            valid_union.update(subset)
            num_valid += 1

    if num_valid == 0:
        return set(candidates), {
            "m_hat": m_hat,
            "num_candidates": len(candidates),
            "status": "return_candidates_no_valid_subset",
        }

    return valid_union, {
        "m_hat": m_hat,
        "num_candidates": len(candidates),
        "num_valid_subsets": num_valid,
        "status": "pruned",
    }


def evaluate_single_node(recovered_sets, true_neighbors):
    tp = fp = fn = 0

    for node_id, recovered in enumerate(recovered_sets):
        pred = set(recovered)
        true = set(true_neighbors[node_id])

        # The generated trace includes target node itself.
        # For edge recovery metrics, remove self.
        pred.discard(node_id)

        tp += len(pred & true)
        fp += len(pred - true)
        fn += len(true - pred)

    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0

    return {
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "precision": precision,
        "recall": recall,
    }


def build_full_graph_edges(recovered_sets):
    directed = set()

    for u, recovered in enumerate(recovered_sets):
        for v in recovered:
            v = int(v)

            if u == v:
                continue

            directed.add((u, v))

    # Keep only bidirectionally confirmed edges.
    undirected = set()

    for u, v in directed:
        if (v, u) in directed:
            undirected.add((min(u, v), max(u, v)))

    return undirected


def true_undirected_edges(edge_index):
    edges = set()

    src = edge_index[0].cpu().numpy()
    dst = edge_index[1].cpu().numpy()

    for u, v in zip(src, dst):
        u = int(u)
        v = int(v)

        if u == v:
            continue

        edges.add((min(u, v), max(u, v)))

    return edges


def evaluate_full_graph(pred_edges, true_edges):
    tp = len(pred_edges & true_edges)
    fp = len(pred_edges - true_edges)
    fn = len(true_edges - pred_edges)

    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0

    return {
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "precision": precision,
        "recall": recall,
        "num_pred_edges": len(pred_edges),
        "num_true_edges": len(true_edges),
    }


def run_one_dataset(
    dataset_name,
    method="cprime",
    node_matrix_dir="nodes_matrix",
    trace_dir="index_select_traces",
    output_dir="recovery_results",
    device="mps",
):
    if dataset_name not in datasets:
        raise ValueError(f"No Table 2 f/T values for dataset: {dataset_name}")

    os.makedirs(output_dir, exist_ok=True)

    node_matrix_path = os.path.join(node_matrix_dir, f"{dataset_name}.npy")
    trace_path = os.path.join(trace_dir, f"{dataset_name}_index_select_trace.npy")

    if not os.path.exists(node_matrix_path):
        print(f"[!] Skip {dataset_name}: missing {node_matrix_path}")
        return None

    if not os.path.exists(trace_path):
        print(f"[!] Skip {dataset_name}: missing {trace_path}")
        return None

    print(f"[+] Running recovery for {dataset_name}, method={method}")

    cfg = datasets[dataset_name]
    f_avg = cfg["f"]
    threshold_T = cfg["T"][method]

    dataset = cfg["loader"]()
    data = dataset[0]

    node_sets = torch.from_numpy(np.load(node_matrix_path)).to(device)
    observed_traces = torch.from_numpy(np.load(trace_path)).to(device)

    assert node_sets.shape[1] == SLC_NUM_SETS
    assert observed_traces.shape[1] == SLC_NUM_SETS
    assert node_sets.shape[0] == data.num_nodes
    assert observed_traces.shape[0] == data.num_nodes

    true_neighbors = build_undirected_neighbors(data.edge_index, data.num_nodes)

    recovered_sets = []
    debug_info = []

    for node_id in range(data.num_nodes):
        if node_id % 100 == 0:
            print(f"    node {node_id}/{data.num_nodes}")

        recovered, info = recover_one_node(
            target_node=node_id,
            observed_trace=observed_traces[node_id],
            node_sets=node_sets,
            f_avg=f_avg,
            threshold_T=threshold_T,
            device=device,
        )

        recovered_sets.append(sorted(recovered))
        debug_info.append(info)

    single_metrics = evaluate_single_node(recovered_sets, true_neighbors)

    pred_edges = build_full_graph_edges(recovered_sets)
    gt_edges = true_undirected_edges(data.edge_index)
    full_metrics = evaluate_full_graph(pred_edges, gt_edges)

    result = {
        "dataset": dataset_name,
        "method": method,
        "f_avg": f_avg,
        "threshold_T": threshold_T,
        "single_node": single_metrics,
        "full_graph": full_metrics,
    }

    base = f"{dataset_name}_{method}"

    with open(os.path.join(output_dir, f"{base}_recovered_sets.pkl"), "wb") as f:
        pickle.dump(recovered_sets, f)

    with open(os.path.join(output_dir, f"{base}_debug.pkl"), "wb") as f:
        pickle.dump(debug_info, f)

    with open(os.path.join(output_dir, f"{base}_pred_edges.txt"), "w") as f:
        for u, v in sorted(pred_edges):
            f.write(f"{u} {v}\n")

    with open(os.path.join(output_dir, f"{base}_metrics.json"), "w") as f:
        json.dump(result, f, indent=2)

    print(f"[+] {dataset_name} single-node P/R: "
          f"{single_metrics['precision']:.4f} / {single_metrics['recall']:.4f}")

    print(f"[+] {dataset_name} full-graph  P/R: "
          f"{full_metrics['precision']:.4f} / {full_metrics['recall']:.4f}")

    return result


def main():
    method = "gprime" 

    dataset_names = [
        "cora",
        "amazon_photo"
    ]

    all_results = {}

    for dataset_name in dataset_names:
        result = run_one_dataset(
            dataset_name=dataset_name,
            method=method,
            node_matrix_dir="nodes_matrix",
            trace_dir="index_select_traces_noise",
            output_dir="recovery_results",
            device="mps",
        )

        if result is not None:
            all_results[dataset_name] = result

    os.makedirs("recovery_results", exist_ok=True)
    with open("recovery_results/all_metrics.json", "w") as f:
        json.dump(all_results, f, indent=2)


if __name__ == "__main__":
    main()