import csv
import json
import math
import statistics
from pathlib import Path


ROOT = Path("results")
TASKS = ["medium", "hard"]
COMPS = ["027", "015"]
SEEDS = list(range(47, 55))
LABELS = {
    "027": "combined main candidate: comp=0.27, clip=[0.73,1.42], patience=4",
    "015": "medium-stabilized candidate: comp=0.15, clip=[0.85,1.30], patience=4",
}


def mean(values):
    return statistics.mean(values)


def std(values):
    return statistics.stdev(values) if len(values) > 1 else 0.0


def ci95(values):
    if len(values) < 2:
        return values[0], values[0]
    # t critical for df=7.
    error = 2.365 * std(values) / math.sqrt(len(values))
    center = mean(values)
    return center - error, center + error


def write_csv(path, rows):
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def load_rows():
    rows = []
    for task in TASKS:
        for comp in COMPS:
            for seed in SEEDS:
                path = ROOT / f"confirm_{task}_comp{comp}_p4_seed{seed}_threshold.json"
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


def paired_delta(rows, task, metric):
    by_seed = {}
    for row in rows:
        if row["task"] != task:
            continue
        by_seed.setdefault(row["seed"], {})[row["comp"]] = row[metric]
    deltas = []
    for seed in SEEDS:
        pair = by_seed[seed]
        deltas.append(pair["027"] - pair["015"])
    return deltas


def main():
    rows = load_rows()
    write_csv(ROOT / "confirmation_medium_hard_heldout.csv", rows)

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
    write_csv(ROOT / "confirmation_medium_hard_heldout_summary.csv", summary)

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
    write_csv(ROOT / "confirmation_medium_hard_heldout_combined_summary.csv", combined)

    paired = []
    for task in [f"border_{name}" for name in TASKS]:
        for metric in ["test_accuracy", "test_f1"]:
            deltas = paired_delta(rows, task, metric)
            low, high = ci95(deltas)
            paired.append(
                {
                    "task": task,
                    "metric": metric,
                    "delta_definition": "comp027_minus_comp015",
                    "mean_delta": mean(deltas),
                    "std_delta": std(deltas),
                    "ci95_low": low,
                    "ci95_high": high,
                    "win_rate_comp027": sum(1 for x in deltas if x > 0) / len(deltas),
                    "ties": sum(1 for x in deltas if x == 0),
                    "per_seed_delta": " / ".join(f"{x:+.4f}" for x in deltas),
                }
            )
    write_csv(ROOT / "confirmation_medium_hard_heldout_paired.csv", paired)

    md = ROOT / "confirmation_medium_hard_heldout.md"
    with md.open("w") as handle:
        handle.write("# Held-Out Confirmation: medium/hard Candidate Comparison\n\n")
        handle.write(
            "Protocol: held-out seeds `47-54`, real DNABERT-2 backbone, GERM-BO final "
            "`attention.output + classifier`, `early_stopping_patience=4`, validation-accuracy "
            "best checkpoint, validation-threshold tuned test evaluation. All train/eval commands "
            "used `CUDA_VISIBLE_DEVICES=3`.\n\n"
        )
        handle.write("## Summary\n\n")
        handle.write("| Task | Candidate | Test Acc Mean +/- Std | Test F1 Mean +/- Std | Min Acc | Max Acc |\n")
        handle.write("|---|---|---:|---:|---:|---:|\n")
        for item in summary:
            handle.write(
                f"| {item['task']} | {item['label']} | "
                f"{item['test_accuracy_mean']:.4f} +/- {item['test_accuracy_std']:.4f} | "
                f"{item['test_f1_mean']:.4f} +/- {item['test_f1_std']:.4f} | "
                f"{item['test_accuracy_min']:.4f} | {item['test_accuracy_max']:.4f} |\n"
            )
        handle.write("\n## Combined Across Medium+Hard\n\n")
        handle.write("| Candidate | Runs | Test Acc Mean +/- Std | Test F1 Mean +/- Std | Min Acc | Max Acc |\n")
        handle.write("|---|---:|---:|---:|---:|---:|\n")
        for item in combined:
            handle.write(
                f"| {item['label']} | {item['n_runs']} | "
                f"{item['test_accuracy_mean']:.4f} +/- {item['test_accuracy_std']:.4f} | "
                f"{item['test_f1_mean']:.4f} +/- {item['test_f1_std']:.4f} | "
                f"{item['test_accuracy_min']:.4f} | {item['test_accuracy_max']:.4f} |\n"
            )
        handle.write("\n## Paired Delta: comp027 - comp015\n\n")
        handle.write("| Task | Metric | Mean Delta | 95% CI | Win Rate comp027 | Per-Seed Delta |\n")
        handle.write("|---|---|---:|---:|---:|---:|\n")
        for item in paired:
            handle.write(
                f"| {item['task']} | {item['metric']} | {item['mean_delta']:+.4f} | "
                f"[{item['ci95_low']:+.4f}, {item['ci95_high']:+.4f}] | "
                f"{item['win_rate_comp027']:.1%} | {item['per_seed_delta']} |\n"
            )
        best = max(combined, key=lambda x: x["test_accuracy_mean"])
        handle.write("\n## Interpretation\n\n")
        handle.write(
            f"On held-out seeds, the higher combined mean test accuracy is from `{best['label']}` "
            f"with mean `{best['test_accuracy_mean']:.4f}`. Because these are held-out confirmation "
            "seeds, this comparison is stronger evidence than the tuning grid, but it should still be "
            "reported as a candidate confirmation rather than a fully independent benchmark result.\n"
        )

    print(md)
    print(ROOT / "confirmation_medium_hard_heldout.csv")
    print(ROOT / "confirmation_medium_hard_heldout_summary.csv")
    print(ROOT / "confirmation_medium_hard_heldout_combined_summary.csv")
    print(ROOT / "confirmation_medium_hard_heldout_paired.csv")


if __name__ == "__main__":
    main()
