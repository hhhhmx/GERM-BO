import csv
import json
import statistics
from pathlib import Path


ROOT = Path("results")
TASKS = ["medium", "hard"]
SEEDS = list(range(47, 55))
COMPS = {
    "000": {
        "prefix": "mechanism",
        "label": "no compensation: comp=0.00, clip=[1.00,1.00], p4",
    },
    "015": {
        "prefix": "confirm",
        "label": "medium-stabilized: comp=0.15, clip=[0.85,1.30], p4",
    },
    "027": {
        "prefix": "confirm",
        "label": "combined main: comp=0.27, clip=[0.73,1.42], p4",
    },
}


def mean(values):
    return statistics.mean(values)


def std(values):
    return statistics.stdev(values) if len(values) > 1 else 0.0


def load_rows():
    rows = []
    for task in TASKS:
        for comp, meta in COMPS.items():
            for seed in SEEDS:
                path = ROOT / f"{meta['prefix']}_{task}_comp{comp}_p4_seed{seed}_threshold.json"
                if not path.exists():
                    raise FileNotFoundError(path)
                data = json.loads(path.read_text())
                device = data.get("device_report", {})
                rows.append(
                    {
                        "task": f"border_{task}",
                        "comp": comp,
                        "label": meta["label"],
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
                    }
                )
    return rows


def write_csv(path, rows):
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def summarize(rows):
    summary = []
    for task in [f"border_{name}" for name in TASKS]:
        for comp, meta in COMPS.items():
            group = [r for r in rows if r["task"] == task and r["comp"] == comp]
            acc = [r["test_accuracy"] for r in group]
            f1 = [r["test_f1"] for r in group]
            val = [r["val_accuracy"] for r in group]
            summary.append(
                {
                    "task": task,
                    "comp": comp,
                    "label": meta["label"],
                    "n_seeds": len(group),
                    "val_accuracy_mean": mean(val),
                    "val_accuracy_std": std(val),
                    "test_accuracy_mean": mean(acc),
                    "test_accuracy_std": std(acc),
                    "test_accuracy_min": min(acc),
                    "test_accuracy_max": max(acc),
                    "test_f1_mean": mean(f1),
                    "test_f1_std": std(f1),
                    "collapse_count_acc_lt_0_75": sum(1 for x in acc if x < 0.75),
                    "per_seed_test_accuracy": " / ".join(f"{x:.4f}" for x in acc),
                }
            )
    return summary


def summarize_combined(rows):
    combined = []
    for comp, meta in COMPS.items():
        group = [r for r in rows if r["comp"] == comp]
        acc = [r["test_accuracy"] for r in group]
        f1 = [r["test_f1"] for r in group]
        val = [r["val_accuracy"] for r in group]
        combined.append(
            {
                "comp": comp,
                "label": meta["label"],
                "n_runs": len(group),
                "val_accuracy_mean": mean(val),
                "val_accuracy_std": std(val),
                "test_accuracy_mean": mean(acc),
                "test_accuracy_std": std(acc),
                "test_accuracy_min": min(acc),
                "test_accuracy_max": max(acc),
                "test_f1_mean": mean(f1),
                "test_f1_std": std(f1),
                "collapse_count_acc_lt_0_75": sum(1 for x in acc if x < 0.75),
            }
        )
    return combined


def main():
    rows = load_rows()
    write_csv(ROOT / "mechanism_compensation_heldout.csv", rows)
    summary = summarize(rows)
    combined = summarize_combined(rows)
    write_csv(ROOT / "mechanism_compensation_heldout_summary.csv", summary)
    write_csv(ROOT / "mechanism_compensation_heldout_combined_summary.csv", combined)

    by_key = {(item["task"], item["comp"]): item for item in summary}
    by_comp = {item["comp"]: item for item in combined}
    md = ROOT / "mechanism_and_failure_analysis.md"
    with md.open("w") as handle:
        handle.write("# Mechanism Ablation and Failure Analysis\n\n")
        handle.write(
            "This report separates mechanism evidence from tuning evidence. The no-compensation "
            "control uses the same GERM-BO wrapper, target modules, rank, dropout, patience, and "
            "held-out seeds, but sets `compensation_strength=0` and clamps compensation to 1.0.\n\n"
        )
        handle.write("## Compensation Mechanism: Held-Out Seeds 47-54\n\n")
        handle.write("| Task | Variant | Test Acc Mean +/- Std | Test F1 Mean +/- Std | Min Acc | Collapse Count Acc<0.75 |\n")
        handle.write("|---|---|---:|---:|---:|---:|\n")
        for item in summary:
            handle.write(
                f"| {item['task']} | {item['label']} | "
                f"{item['test_accuracy_mean']:.4f} +/- {item['test_accuracy_std']:.4f} | "
                f"{item['test_f1_mean']:.4f} +/- {item['test_f1_std']:.4f} | "
                f"{item['test_accuracy_min']:.4f} | {item['collapse_count_acc_lt_0_75']} |\n"
            )
        handle.write("\n## Combined Medium+Hard\n\n")
        handle.write("| Variant | Runs | Test Acc Mean +/- Std | Test F1 Mean +/- Std | Min Acc | Collapse Count Acc<0.75 |\n")
        handle.write("|---|---:|---:|---:|---:|---:|\n")
        for item in combined:
            handle.write(
                f"| {item['label']} | {item['n_runs']} | "
                f"{item['test_accuracy_mean']:.4f} +/- {item['test_accuracy_std']:.4f} | "
                f"{item['test_f1_mean']:.4f} +/- {item['test_f1_std']:.4f} | "
                f"{item['test_accuracy_min']:.4f} | {item['collapse_count_acc_lt_0_75']} |\n"
            )
        handle.write("\n## Failure-Analysis Conclusion\n\n")
        medium_000 = by_key[("border_medium", "000")]
        medium_027 = by_key[("border_medium", "027")]
        hard_000 = by_key[("border_hard", "000")]
        hard_027 = by_key[("border_hard", "027")]
        handle.write(
            f"On `border_medium`, compensation improves held-out mean accuracy from "
            f"{medium_000['test_accuracy_mean']:.4f} without compensation to "
            f"{medium_027['test_accuracy_mean']:.4f} with the main `comp=0.27/p4` setting. "
            f"On `border_hard`, the no-compensation control reaches {hard_000['test_accuracy_mean']:.4f}, "
            f"while `comp=0.27/p4` reaches {hard_027['test_accuracy_mean']:.4f}. "
            "This indicates that the compensation mechanism is most useful for the medium setting, "
            "while hard-task robustness is more sensitive and does not monotonically benefit from stronger compensation.\n\n"
        )
        handle.write("## Practical Failure Solution\n\n")
        handle.write(
            "The observed collapse is best handled by a conservative training protocol: monitor validation "
            "accuracy, save `best.pt`, use `early_stopping_patience=4`, and flag runs with weak validation "
            "accuracy or test-time probability collapse for rerun/diagnosis. The main config remains "
            "`comp=0.27/p4`; `comp=0.15/p4` is retained as a stability ablation.\n"
        )
        handle.write("\n## Current Main Recommendation\n\n")
        handle.write(
            f"Keep `comp=0.27/p4` as the combined main configuration because it has the best tuning-stage "
            f"validation score and the highest held-out combined accuracy among the compensation candidates "
            f"({by_comp['027']['test_accuracy_mean']:.4f}). Report `comp=0.15/p4` as a medium-stabilized "
            "robustness ablation rather than replacing the main configuration.\n"
        )
    print(md)
    print(ROOT / "mechanism_compensation_heldout.csv")
    print(ROOT / "mechanism_compensation_heldout_summary.csv")
    print(ROOT / "mechanism_compensation_heldout_combined_summary.csv")


if __name__ == "__main__":
    main()
