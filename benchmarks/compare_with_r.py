"""Compare R method results with ground truth.

Usage:
    python compare_with_r.py <r_labels_csv> <true_labels_csv> <method_name>

Loads labels from R output and computes ARI, NMI, rare F1.
"""
from __future__ import annotations
import sys
import json
import numpy as np
import pandas as pd
from pathlib import Path
from run_benchmark import compute_rare_f1
from sklearn.metrics import adjusted_rand_score, normalized_mutual_info_score


def main():
    if len(sys.argv) < 4:
        print("Usage: python compare_with_r.py <r_labels_csv> <true_labels_csv> <method_name>")
        sys.exit(1)

    r_labels_path = sys.argv[1]
    true_labels_path = sys.argv[2]
    method_name = sys.argv[3]

    labels_pred = pd.read_csv(r_labels_path)["label"].values
    labels_true = np.loadtxt(true_labels_path, skiprows=1, dtype=int)

    assert len(labels_pred) == len(labels_true), (
        f"Label count mismatch: pred={len(labels_pred)}, true={len(labels_true)}"
    )

    ari = adjusted_rand_score(labels_true, labels_pred)
    nmi = normalized_mutual_info_score(labels_true, labels_pred)
    rf1 = compute_rare_f1(labels_true, labels_pred)

    # Load timing if available
    timing_path = Path(r_labels_path).with_suffix("").with_suffix("_timing.json")
    runtime = None
    if timing_path.exists():
        with open(timing_path) as f:
            runtime = json.load(f).get("runtime_s")

    print(f"\n{'='*50}")
    print(f"Method: {method_name}")
    print(f"ARI:      {ari:.4f}")
    print(f"NMI:      {nmi:.4f}")
    print(f"Rare F1:  {rf1:.4f}")
    if runtime:
        print(f"Runtime:  {runtime:.1f}s")
    print(f"{'='*50}")

    # Save result
    result = {
        "method": method_name,
        "ari": ari,
        "nmi": nmi,
        "rare_f1": rf1,
        "runtime_s": runtime,
        "n_cells": len(labels_true),
    }
    out_path = Path("results") / f"{method_name.lower()}_metrics.json"
    out_path.parent.mkdir(exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"Saved: {out_path}")


if __name__ == "__main__":
    main()
