import csv
import json
import statistics
from pathlib import Path


ROOT = Path("results")
TASKS = ["medium", "hard"]
SEEDS = list(range(47, 55))
VARIANTS = {
    "metadata_027": {
        "prefix": "metadata",
        "comp": "027",
        "label": "metadata-driven comp=0.27/p4",
    },
    "activation_027": {
        "prefix": "confirm",
        "comp": "027",
        "label": "activation-derived comp=0.27/p4",
    },
    "no_comp_000": {
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
                if not path.exists():
                    raise FileNotFoundError(path)
                data = json.loads(path.read_text())
                rows.append(
                    {
                        "task": f"border_{task}",
                        "variant": variant,
                        "label": meta["label"],
                        "seed": seed,
                        "threshold": data["selected_threshold"],
                        "val_accuracy": data["validation"]["accuracy"],
                        "val_f1": data["validation"]["f1"],
                        "test_accuracy": data["test"]["accuracy"],
                        "test_f1": data["test"]["f1"],
                        "test_precision": data["test"]["precision"],
                        "test_recall": data["test"]["recall"],
                    }
                )
    return rows


def write_csv(path, rows):
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main():
    rows = load_rows()
    write_csv(ROOT / "metadata_vs_activation_mechanism.csv", rows)

    summary = []
    for task in [f"border_{name}" for name in TASKS]:
        for variant, meta in VARIANTS.items():
            group = [row for row in rows if row["task"] == task and row["variant"] == variant]
            acc = [row["test_accuracy"] for row in group]
            f1 = [row["test_f1"] for row in group]
            summary.append(
                {
                    "task": task,
                    "variant": variant,
                    "label": meta["label"],
                    "n_seeds": len(group),
                    "test_accuracy_mean": mean(acc),
                    "test_accuracy_std": std(acc),
                    "test_accuracy_min": min(acc),
                    "test_accuracy_max": max(acc),
                    "test_f1_mean": mean(f1),
                    "test_f1_std": std(f1),
                    "per_seed_accuracy": " / ".join(f"{value:.4f}" for value in acc),
                }
            )
    write_csv(ROOT / "metadata_vs_activation_mechanism_summary.csv", summary)

    combined = []
    for variant, meta in VARIANTS.items():
        group = [row for row in rows if row["variant"] == variant]
        acc = [row["test_accuracy"] for row in group]
        f1 = [row["test_f1"] for row in group]
        combined.append(
            {
                "variant": variant,
                "label": meta["label"],
                "n_runs": len(group),
                "test_accuracy_mean": mean(acc),
                "test_accuracy_std": std(acc),
                "test_accuracy_min": min(acc),
                "test_accuracy_max": max(acc),
                "test_f1_mean": mean(f1),
                "test_f1_std": std(f1),
            }
        )
    write_csv(ROOT / "metadata_vs_activation_mechanism_combined_summary.csv", combined)

    md = ROOT / "metadata_vs_activation_mechanism.md"
    with md.open("w") as handle:
        handle.write("# Metadata-Driven vs Activation-Derived Compensation\n\n")
        handle.write(
            "Protocol: held-out seeds `47-54`, real DNABERT-2 backbone, same target modules, "
            "`compensation_strength=0.27`, `early_stopping_patience=4`, validation-accuracy best checkpoint, "
            "and validation-threshold tuned test evaluation. All train/eval commands must use "
            "`CUDA_VISIBLE_DEVICES=3`.\n\n"
        )
        handle.write("## Per-Task Summary\n\n")
        handle.write("| Task | Variant | Test Acc Mean +/- Std | Test F1 Mean +/- Std | Min Acc | Max Acc |\n")
        handle.write("|---|---|---:|---:|---:|---:|\n")
        for item in summary:
            handle.write(
                f"| {item['task']} | {item['label']} | "
                f"{item['test_accuracy_mean']:.4f} +/- {item['test_accuracy_std']:.4f} | "
                f"{item['test_f1_mean']:.4f} +/- {item['test_f1_std']:.4f} | "
                f"{item['test_accuracy_min']:.4f} | {item['test_accuracy_max']:.4f} |\n"
            )
        handle.write("\n## Combined Medium+Hard\n\n")
        handle.write("| Variant | Runs | Test Acc Mean +/- Std | Test F1 Mean +/- Std | Min Acc | Max Acc |\n")
        handle.write("|---|---:|---:|---:|---:|---:|\n")
        for item in combined:
            handle.write(
                f"| {item['label']} | {item['n_runs']} | "
                f"{item['test_accuracy_mean']:.4f} +/- {item['test_accuracy_std']:.4f} | "
                f"{item['test_f1_mean']:.4f} +/- {item['test_f1_std']:.4f} | "
                f"{item['test_accuracy_min']:.4f} | {item['test_accuracy_max']:.4f} |\n"
            )
    print(md)
    print(ROOT / "metadata_vs_activation_mechanism.csv")
    print(ROOT / "metadata_vs_activation_mechanism_summary.csv")
    print(ROOT / "metadata_vs_activation_mechanism_combined_summary.csv")


if __name__ == "__main__":
    main()
