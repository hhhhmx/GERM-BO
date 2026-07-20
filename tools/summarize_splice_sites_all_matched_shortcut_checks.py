import csv
from pathlib import Path


ROOT = Path("results")

FILES = [
    ("original_larger", "Original larger split", ROOT / "splice_sites_all_larger_kmer_comparison_summary.csv"),
    ("gc_matched", "GC-matched split", ROOT / "splice_sites_all_gc_matched_kmer_comparison_summary.csv"),
    ("kmer_balanced", "3-mer-balanced split", ROOT / "splice_sites_all_kmer_balanced_kmer_comparison_summary.csv"),
]


def read_csv(path):
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def numeric(row, key):
    return float(row[key])


def write_csv(path, rows):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main():
    rows = []
    for split_id, split_label, path in FILES:
        for row in read_csv(path):
            rows.append(
                {
                    "split_id": split_id,
                    "split_label": split_label,
                    "method": row["method"],
                    "label": row["label"],
                    "n_seeds": int(row["n_seeds"]),
                    "test_accuracy_mean": numeric(row, "test_accuracy_mean"),
                    "test_accuracy_std": numeric(row, "test_accuracy_std"),
                    "test_macro_f1_mean": numeric(row, "test_macro_f1_mean"),
                    "test_macro_f1_std": numeric(row, "test_macro_f1_std"),
                }
            )
    if not rows:
        raise RuntimeError("No matched shortcut-check summaries found.")

    rows.sort(key=lambda item: (item["label"], item["split_id"]))
    write_csv(ROOT / "splice_sites_all_matched_shortcut_checks.csv", rows)

    by_method = {}
    for row in rows:
        by_method.setdefault(row["label"], []).append(row)

    with (ROOT / "splice_sites_all_matched_shortcut_checks.md").open("w", encoding="utf-8") as handle:
        handle.write("# Splice Sites All Matched Split Shortcut Checks\n\n")
        handle.write(
            "Protocol: compare traditional 3-mer baselines on the original larger split, "
            "a `GC-matched` split, and a stricter `3-mer-balanced` split. "
            "Lower 3-mer accuracy on matched splits would indicate that the original split contains stronger short-range composition shortcuts.\n\n"
        )
        handle.write("## Summary Table\n\n")
        handle.write("| Method | Original Larger Macro-F1 | GC-Matched Macro-F1 | 3-mer-Balanced Macro-F1 | Original Larger Acc | GC-Matched Acc | 3-mer-Balanced Acc |\n")
        handle.write("|---|---:|---:|---:|---:|---:|---:|\n")
        for label in sorted(by_method):
            group = {row["split_id"]: row for row in by_method[label]}
            handle.write(
                f"| {label} | "
                f"{group['original_larger']['test_macro_f1_mean']:.4f} +/- {group['original_larger']['test_macro_f1_std']:.4f} | "
                f"{group.get('gc_matched', {}).get('test_macro_f1_mean', float('nan')):.4f} +/- {group.get('gc_matched', {}).get('test_macro_f1_std', float('nan')):.4f} | "
                f"{group.get('kmer_balanced', {}).get('test_macro_f1_mean', float('nan')):.4f} +/- {group.get('kmer_balanced', {}).get('test_macro_f1_std', float('nan')):.4f} | "
                f"{group['original_larger']['test_accuracy_mean']:.4f} +/- {group['original_larger']['test_accuracy_std']:.4f} | "
                f"{group.get('gc_matched', {}).get('test_accuracy_mean', float('nan')):.4f} +/- {group.get('gc_matched', {}).get('test_accuracy_std', float('nan')):.4f} | "
                f"{group.get('kmer_balanced', {}).get('test_accuracy_mean', float('nan')):.4f} +/- {group.get('kmer_balanced', {}).get('test_accuracy_std', float('nan')):.4f} |\n"
            )
    print(ROOT / "splice_sites_all_matched_shortcut_checks.md")


if __name__ == "__main__":
    main()
