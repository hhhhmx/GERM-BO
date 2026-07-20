import csv
import json
import statistics
from pathlib import Path


ROOT = Path("results")
TASKS = ["medium", "hard"]
SEEDS = list(range(47, 55))
VARIANTS = {
    "metadata_real": {
        "prefix": "metadata",
        "comp": "027",
        "label": "metadata real comp=0.27/p4",
    },
    "metadata_shuffled": {
        "prefix": "metadata_shuffled",
        "comp": "027",
        "label": "metadata shuffled comp=0.27/p4",
    },
    "activation": {
        "prefix": "confirm",
        "comp": "027",
        "label": "activation-derived comp=0.27/p4",
    },
    "no_comp": {
        "prefix": "mechanism",
        "comp": "000",
        "label": "no compensation comp=0.00/p4",
    },
}


def mean(values):
    return statistics.mean(values)


def std(values):
    return statistics.stdev(values) if len(values) > 1 else 0.0


def load_rows():
    rows = []
    for task in TASKS:
        for variant, meta in VARIANTS.items():
            for seed in SEEDS:
                path = ROOT / f"{meta['prefix']}_{task}_comp{meta['comp']}_p4_seed{seed}_threshold.json"
                data = json.loads(path.read_text())
                rows.append(
                    {
                        "task": f"border_{task}",
                        "variant": variant,
                        "label": meta["label"],
                        "seed": seed,
                        "test_accuracy": data["test"]["accuracy"],
                        "test_f1": data["test"]["f1"],
                        "test_precision": data["test"]["precision"],
                        "test_recall": data["test"]["recall"],
                        "val_accuracy": data["validation"]["accuracy"],
                    }
                )
    return rows


def write_csv(path, rows):
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def summarize(rows):
    out = []
    for task in [f"border_{task}" for task in TASKS] + ["combined"]:
        for variant, meta in VARIANTS.items():
            group = [row for row in rows if row["variant"] == variant and (task == "combined" or row["task"] == task)]
            acc = [row["test_accuracy"] for row in group]
            f1 = [row["test_f1"] for row in group]
            out.append(
                {
                    "group": task,
                    "variant": variant,
                    "label": meta["label"],
                    "n": len(group),
                    "test_accuracy_mean": mean(acc),
                    "test_accuracy_std": std(acc),
                    "test_accuracy_min": min(acc),
                    "test_accuracy_max": max(acc),
                    "test_f1_mean": mean(f1),
                    "test_f1_std": std(f1),
                    "per_seed_accuracy": " / ".join(f"{value:.4f}" for value in acc),
                }
            )
    return out


def paired(rows, group, left, right):
    pairs = []
    tasks = [f"border_{task}" for task in TASKS] if group == "combined" else [group]
    for task in tasks:
        for seed in SEEDS:
            left_row = next(row for row in rows if row["task"] == task and row["seed"] == seed and row["variant"] == left)
            right_row = next(row for row in rows if row["task"] == task and row["seed"] == seed and row["variant"] == right)
            pairs.append(left_row["test_accuracy"] - right_row["test_accuracy"])
    return {
        "group": group,
        "comparison": f"{left}_minus_{right}",
        "n": len(pairs),
        "accuracy_delta_mean": mean(pairs),
        "accuracy_delta_std": std(pairs),
        "win_rate": sum(1 for value in pairs if value > 0) / len(pairs),
        "per_seed_delta": " / ".join(f"{value:+.4f}" for value in pairs),
    }


def main():
    rows = load_rows()
    write_csv(ROOT / "metadata_shuffled_ablation.csv", rows)
    summary = summarize(rows)
    write_csv(ROOT / "metadata_shuffled_ablation_summary.csv", summary)
    paired_rows = []
    for group in ["border_medium", "border_hard", "combined"]:
        for left, right in [
            ("metadata_real", "metadata_shuffled"),
            ("metadata_real", "activation"),
            ("metadata_shuffled", "activation"),
            ("metadata_shuffled", "no_comp"),
        ]:
            paired_rows.append(paired(rows, group, left, right))
    write_csv(ROOT / "metadata_shuffled_ablation_paired.csv", paired_rows)

    md = ROOT / "metadata_shuffled_ablation.md"
    with md.open("w") as handle:
        handle.write("# Metadata Shuffled Ablation\n\n")
        handle.write(
            "Protocol: sequence and label are unchanged; only metadata strings are shuffled within each split. "
            "Runs use metadata-driven `comp=0.27/p4`, held-out seeds `47-54`, real DNABERT-2 backbone, "
            "validation-accuracy best checkpoint, and validation-threshold tuned test evaluation.\n\n"
        )
        handle.write("## Summary\n\n")
        handle.write("| Group | Variant | Test Acc Mean +/- Std | Test F1 Mean +/- Std | Min Acc | Max Acc |\n")
        handle.write("|---|---|---:|---:|---:|---:|\n")
        for item in summary:
            handle.write(
                f"| {item['group']} | {item['label']} | "
                f"{item['test_accuracy_mean']:.4f} +/- {item['test_accuracy_std']:.4f} | "
                f"{item['test_f1_mean']:.4f} +/- {item['test_f1_std']:.4f} | "
                f"{item['test_accuracy_min']:.4f} | {item['test_accuracy_max']:.4f} |\n"
            )
        handle.write("\n## Paired Accuracy Deltas\n\n")
        handle.write("| Group | Comparison | Delta Mean | Delta Std | Win Rate | Per-Seed Delta |\n")
        handle.write("|---|---|---:|---:|---:|---:|\n")
        for item in paired_rows:
            handle.write(
                f"| {item['group']} | {item['comparison']} | "
                f"{item['accuracy_delta_mean']:+.4f} | {item['accuracy_delta_std']:.4f} | "
                f"{item['win_rate']:.1%} | {item['per_seed_delta']} |\n"
            )
    print(md)
    print(ROOT / "metadata_shuffled_ablation.csv")
    print(ROOT / "metadata_shuffled_ablation_summary.csv")
    print(ROOT / "metadata_shuffled_ablation_paired.csv")


if __name__ == "__main__":
    main()
