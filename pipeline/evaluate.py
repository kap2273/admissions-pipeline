from itertools import combinations
from pathlib import Path

import pandas as pd
from sqlalchemy import text

from db import get_engine

ROOT = Path(__file__).resolve().parent.parent
TRUTH_FILE = ROOT / "data" / "truth.csv"
BENCHMARK_FILE = ROOT / "docs" / "benchmark.md"


def pairs_from_groups(df, group_col):
    # every two records in the same group form a pair
    pairs = set()
    for _, group in df.groupby(group_col):
        records = sorted(zip(group["source"], group["source_id"]))
        for a, b in combinations(records, 2):
            pairs.add((a, b))
    return pairs


def evaluate(engine):
    truth = pd.read_csv(TRUTH_FILE, dtype=str)
    links = pd.read_sql(text("SELECT source, source_id, person_key FROM core.source_link"), engine)

    true_pairs = pairs_from_groups(truth, "person_id")
    predicted_pairs = pairs_from_groups(links, "person_key")
    correct = true_pairs & predicted_pairs

    return {
        "records": len(links),
        "true_people": truth["person_id"].nunique(),
        "predicted_people": links["person_key"].nunique(),
        "true_pairs": len(true_pairs),
        "predicted_pairs": len(predicted_pairs),
        "correct_pairs": len(correct),
        "precision": len(correct) / len(predicted_pairs),
        "recall": len(correct) / len(true_pairs),
    }


def write_benchmark(r):
    BENCHMARK_FILE.parent.mkdir(exist_ok=True)
    lines = [
        "# Matching benchmark",
        "",
        "| Metric | Value |",
        "|---|---|",
        f"| Source records | {r['records']} |",
        f"| True people | {r['true_people']} |",
        f"| Predicted people | {r['predicted_people']} |",
        f"| True pairs | {r['true_pairs']} |",
        f"| Predicted pairs | {r['predicted_pairs']} |",
        f"| Correct pairs | {r['correct_pairs']} |",
        f"| Precision | {r['precision']:.1%} |",
        f"| Recall | {r['recall']:.1%} |",
    ]
    BENCHMARK_FILE.write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    results = evaluate(get_engine())
    write_benchmark(results)
    for key, value in results.items():
        print(f"{key}: {value}")
