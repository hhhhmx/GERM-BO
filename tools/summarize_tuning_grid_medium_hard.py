import csv
import json
import math
import statistics
from pathlib import Path


ROOT = Path("results")
TASKS = ["medium", "hard"]
COMPS = ["015", "020", "025", "027"]
SEEDS = [42, 43, 44, 45, 46]
LABELS = {
    "015": "comp=0.15, clip=[0.85,1.30], patience=4",
    "020": "comp=0.20, clip=[0.80,1.35], patience=4",
    "025": "comp=0.25, clip=[0.75,1.40], patience=4",
    "027": "comp=0.27, clip=[0.73,1.42], patience=4",
}


def mean(values):
    return statistics.mean(values)


def std(values):
    return statistics.stdev(values) if len(values) > 1 else 0.0


def ci95(values):
    if len(values) < 2:
        return values[0], values[0]
    tcrit = 2.776 if len(values) == 5 else 1.96
    error = tcrit * std(values) / math.sqrt(len(values))
    center = mean(values)
    return center - error, center + error


def read_rows():
    rows = []
    for task in TASKS:
        for comp in COMPS:
            for seed in SEEDS:
                path = ROOT / f"tuning_{task}_comp{comp}_p4_seed{seed}_threshold.json"
                if not path.exists():
                    raise FileNotFoundError(path)
                data = json.loads(path.read_text())
                device = data.get("device_report", {})
                rows.append(
                    {
                        "task": f"border_{task}",
                        "comp": comp,
                        "label": LABELS[comp],
                        "seed": seed,
                        "threshold": data["selected_threshold"],
                        "val_accuracy": data["validation"]["accuracy"],
                        "val_f1": data["validation"]["f1"],
                        "test_accuracy": data["test"]["accuracy"],
                        "test_f1": data["test"]["f1"],
                        "test_precision": data["test"]["precision"],
                        "test_recall": data["test"]["recall"],
                        "pred_0": data["test"]["predicted_label_counts"].get("0", 0),
                        "pred_1": data["test"]["predicted_label_counts"].get("1", 0),
                        "cuda_visible_devices": device.get("cuda_visible_devices"),
                        "visible_gpu_count": device.get("visible_gpu_count"),
                        "selected_device": device.get("selected_device"),
                        "selected_gpu_name": device.get("selected_gpu_name"),
                    }
                )
    return rows


def write_csv(path, rows):
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main():
    rows = read_rows()
    write_csv(ROOT / "tuning_border_medium_hard_grid.csv", rows)

    summary = []
    for task in TASKS:
        for comp in COMPS:
            group = [r for r in rows if r["task"] == f"border_{task}" and r["comp"] == comp]
            val_acc = [r["val_accuracy"] for r in group]
            test_acc = [r["test_accuracy"] for r in group]
            test_f1 = [r["test_f1"] for r in group]
            low, high = ci95(test_acc)
            summary.append(
                {
                    "task": f"border_{task}",
                    "comp": comp,
                    "label": LABELS[comp],
                    "n_seeds": len(group),
                    "selection_score": mean(val_acc) - 0.5 * std(val_acc),
                    "val_accuracy_mean": mean(val_acc),
                    "val_accuracy_std": std(val_acc),
                    "test_accuracy_mean": mean(test_acc),
                    "test_accuracy_std": std(test_acc),
                    "test_accuracy_min": min(test_acc),
                    "test_accuracy_max": max(test_acc),
                    "test_accuracy_ci95_low": low,
                    "test_accuracy_ci95_high": high,
                    "test_f1_mean": mean(test_f1),
                    "test_f1_std": std(test_f1),
                    "per_seed_test_accuracy": " / ".join(f"{x:.4f}" for x in test_acc),
                }
            )
    write_csv(ROOT / "tuning_border_medium_hard_grid_summary.csv", summary)

    combined = []
    for comp in COMPS:
        group = [r for r in rows if r["comp"] == comp]
        val_acc = [r["val_accuracy"] for r in group]
        test_acc = [r["test_accuracy"] for r in group]
        test_f1 = [r["test_f1"] for r in group]
        combined.append(
            {
                "comp": comp,
                "label": LABELS[comp],
                "n_runs": len(group),
                "selection_score": mean(val_acc) - 0.5 * std(val_acc),
                "val_accuracy_mean": mean(val_acc),
                "val_accuracy_std": std(val_acc),
                "test_accuracy_mean": mean(test_acc),
                "test_accuracy_std": std(test_acc),
                "test_accuracy_min": min(test_acc),
                "test_accuracy_max": max(test_acc),
                "test_f1_mean": mean(test_f1),
                "test_f1_std": std(test_f1),
            }
        )
    write_csv(ROOT / "tuning_border_medium_hard_grid_combined_summary.csv", combined)

    md = ROOT / "tuning_border_medium_hard_grid.md"
    with md.open("w") as handle:
        handle.write("# Failure-Driven Tuning Grid: border_medium and border_hard\n\n")
        handle.write(
            "Protocol: real DNABERT-2 backbone, GERM-BO final `attention.output + classifier`, "
            "`early_stopping_patience=4`, seeds `42-46`, validation-accuracy best checkpoint, "
            "validation-threshold tuned test evaluation. All train/eval commands used "
            "`CUDA_VISIBLE_DEVICES=3`.\n\n"
        )
        handle.write("## Per-Task Summary\n\n")
        handle.write("| Task | Config | Selection Score | Val Acc Mean +/- Std | Test Acc Mean +/- Std | Test F1 Mean +/- Std | Min Acc | Max Acc |\n")
        handle.write("|---|---|---:|---:|---:|---:|---:|---:|\n")
        for item in summary:
            handle.write(
                f"| {item['task']} | {item['label']} | {item['selection_score']:.4f} | "
                f"{item['val_accuracy_mean']:.4f} +/- {item['val_accuracy_std']:.4f} | "
                f"{item['test_accuracy_mean']:.4f} +/- {item['test_accuracy_std']:.4f} | "
                f"{item['test_f1_mean']:.4f} +/- {item['test_f1_std']:.4f} | "
                f"{item['test_accuracy_min']:.4f} | {item['test_accuracy_max']:.4f} |\n"
            )
        handle.write("\n## Combined Medium+Hard Summary\n\n")
        handle.write("| Config | Runs | Selection Score | Val Acc Mean +/- Std | Test Acc Mean +/- Std | Test F1 Mean +/- Std | Min Acc | Max Acc |\n")
        handle.write("|---|---:|---:|---:|---:|---:|---:|---:|\n")
        for item in combined:
            handle.write(
                f"| {item['label']} | {item['n_runs']} | {item['selection_score']:.4f} | "
                f"{item['val_accuracy_mean']:.4f} +/- {item['val_accuracy_std']:.4f} | "
                f"{item['test_accuracy_mean']:.4f} +/- {item['test_accuracy_std']:.4f} | "
                f"{item['test_f1_mean']:.4f} +/- {item['test_f1_std']:.4f} | "
                f"{item['test_accuracy_min']:.4f} | {item['test_accuracy_max']:.4f} |\n"
            )
        best = max(combined, key=lambda x: (x["selection_score"], -x["test_accuracy_std"]))
        handle.write("\n## Provisional Selection\n\n")
        handle.write(
            f"Using the pre-specified validation score `val_accuracy_mean - 0.5 * val_accuracy_std`, "
            f"the provisional best combined configuration is `{best['label']}` with score "
            f"`{best['selection_score']:.4f}`. This should be treated as tuning-stage evidence only; "
            "a final claim should use held-out seeds.\n"
        )

    print(md)
    print(ROOT / "tuning_border_medium_hard_grid.csv")
    print(ROOT / "tuning_border_medium_hard_grid_summary.csv")
    print(ROOT / "tuning_border_medium_hard_grid_combined_summary.csv")


if __name__ == "__main__":
    main()
