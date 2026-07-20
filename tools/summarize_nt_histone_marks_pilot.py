import csv
import json
import random
import statistics
from pathlib import Path


ROOT = Path("results")
SEEDS = [42, 43, 44]
HISTONE_TASKS = [
    "H3",
    "H3K14ac",
    "H3K36me3",
    "H3K4me1",
    "H3K4me2",
    "H3K79me3",
    "H3K9ac",
    "H4",
    "H4ac",
]
METHODS = [
    ("baseline_lora", "Baseline LoRA"),
    ("germ_bo_center_jsd", "Metadata-estimated GERM-BO center-JSD"),
]


def mean(values):
    return statistics.mean(values)


def std(values):
    return statistics.stdev(values) if len(values) > 1 else 0.0


def bootstrap_ci(deltas, iterations=10000, seed=20260420):
    rng = random.Random(seed)
    samples = []
    for _ in range(iterations):
        samples.append(mean([rng.choice(deltas) for _ in deltas]))
    samples.sort()
    return samples[int(0.025 * iterations)], samples[int(0.975 * iterations)]


def load_rows():
    rows = []
    for task in HISTONE_TASKS:
        for method, method_label in METHODS:
            for seed in SEEDS:
                path = ROOT / f"{task}_{method}_seed{seed}_argmax.json"
                data = json.loads(path.read_text(encoding="utf-8"))
                rows.append(
                    {
                        "task": task,
                        "method": method,
                        "method_label": method_label,
                        "seed": seed,
                        "test_accuracy": data["test"]["accuracy"],
                        "test_f1": data["test"].get("macro_f1", data["test"].get("f1")),
                    }
                )
    return rows


def summarize(rows):
    summary = []
    for task in HISTONE_TASKS:
        for method, method_label in METHODS:
            group = [row for row in rows if row["task"] == task and row["method"] == method]
            acc = [row["test_accuracy"] for row in group]
            f1 = [row["test_f1"] for row in group]
            summary.append(
                {
                    "task": task,
                    "method": method,
                    "method_label": method_label,
                    "n_seeds": len(group),
                    "test_accuracy_mean": mean(acc),
                    "test_accuracy_std": std(acc),
                    "test_f1_mean": mean(f1),
                    "test_f1_std": std(f1),
                }
            )
    return summary


def paired(rows):
    by_key = {(row["task"], row["method"], row["seed"]): row for row in rows}
    out = []
    for task in HISTONE_TASKS:
        for metric in ["test_accuracy", "test_f1"]:
            deltas = [
                by_key[(task, "germ_bo_center_jsd", seed)][metric]
                - by_key[(task, "baseline_lora", seed)][metric]
                for seed in SEEDS
            ]
            ci_low, ci_high = bootstrap_ci(deltas)
            out.append(
                {
                    "task": task,
                    "metric": metric,
                    "mean_delta": mean(deltas),
                    "bootstrap_ci95_low": ci_low,
                    "bootstrap_ci95_high": ci_high,
                    "win_rate": sum(1 for value in deltas if value > 0) / len(deltas),
                }
            )
    return out


def write_markdown(summary, paired_rows):
    path = ROOT / "nt_histone_marks_pilot.md"
    with path.open("w", encoding="utf-8") as handle:
        handle.write("# NT Histone-Mark Pilot (excluding H3K4me3)\n\n")
        handle.write(
            "Protocol: nine histone ChIP-seq peak tasks from "
            "`InstaDeepAI/nucleotide_transformer_downstream_tasks`, pilot subset "
            "`2000/500/1000`, seeds `42-44`, DNABERT-2 LoRA vs metadata-estimated GERM-BO.\n\n"
        )
        handle.write("## Summary Table\n\n")
        handle.write("| Task | LoRA Acc | GERM-BO Acc | ? Acc | LoRA F1 | GERM-BO F1 | ? F1 | Win Rate (Acc) |\n")
        handle.write("|---|---:|---:|---:|---:|---:|---:|---:|\n")
        by_task = {task: {} for task in HISTONE_TASKS}
        for row in summary:
            by_task[row["task"]][row["method"]] = row
        for task in HISTONE_TASKS:
            lora = by_task[task]["baseline_lora"]
            germ = by_task[task]["germ_bo_center_jsd"]
            acc_delta = next(row for row in paired_rows if row["task"] == task and row["metric"] == "test_accuracy")
            f1_delta = next(row for row in paired_rows if row["task"] == task and row["metric"] == "test_f1")
            handle.write(
                f"| {task} | {lora['test_accuracy_mean']:.4f} | {germ['test_accuracy_mean']:.4f} | "
                f"{acc_delta['mean_delta']:+.4f} | {lora['test_f1_mean']:.4f} | {germ['test_f1_mean']:.4f} | "
                f"{f1_delta['mean_delta']:+.4f} | {acc_delta['win_rate']:.0%} |\n"
            )
        wins = sum(1 for row in paired_rows if row["metric"] == "test_accuracy" and row["mean_delta"] > 0)
        handle.write(f"\nGERM-BO wins on accuracy (mean delta > 0): {wins}/{len(HISTONE_TASKS)} tasks.\n")
    return path


def main():
    rows = load_rows()
    summary = summarize(rows)
    paired_rows = paired(rows)
    with (ROOT / "nt_histone_marks_pilot.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    with (ROOT / "nt_histone_marks_pilot_summary.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(summary[0].keys()))
        writer.writeheader()
        writer.writerows(summary)
    print(write_markdown(summary, paired_rows))


if __name__ == "__main__":
    main()
