import csv
import json
import random
import statistics
from pathlib import Path


ROOT = Path("results")
SEEDS = [42, 43, 44]
ALL_TASKS = [
    ("H3", "histone"),
    ("H3K14ac", "histone"),
    ("H3K36me3", "histone"),
    ("H3K4me1", "histone"),
    ("H3K4me2", "histone"),
    ("H3K4me3", "histone"),
    ("H3K79me3", "histone"),
    ("H3K9ac", "histone"),
    ("H4", "histone"),
    ("H4ac", "histone"),
    ("enhancers", "regulatory"),
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
    for task, category in ALL_TASKS:
        for method, method_label in METHODS:
            for seed in SEEDS:
                path = ROOT / f"{task}_{method}_seed{seed}_argmax.json"
                if not path.exists():
                    raise FileNotFoundError(path)
                data = json.loads(path.read_text(encoding="utf-8"))
                rows.append(
                    {
                        "task": task,
                        "category": category,
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
    for task, category in ALL_TASKS:
        for method, method_label in METHODS:
            group = [row for row in rows if row["task"] == task and row["method"] == method]
            acc = [row["test_accuracy"] for row in group]
            f1 = [row["test_f1"] for row in group]
            summary.append(
                {
                    "task": task,
                    "category": category,
                    "method": method,
                    "method_label": method_label,
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
    for task, _ in ALL_TASKS:
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
    path = ROOT / "nt_downstream_all.md"
    with path.open("w", encoding="utf-8") as handle:
        handle.write("# NT Downstream: All Histone Marks + Enhancers\n\n")
        handle.write("| Task | Category | LoRA Acc | GERM-BO Acc | ? Acc [95% CI] | Win Rate |\n")
        handle.write("|---|---|---:|---:|---:|---:|\n")
        by_task = {task: {} for task, _ in ALL_TASKS}
        for row in summary:
            by_task[row["task"]][row["method"]] = row
        for task, category in ALL_TASKS:
            lora = by_task[task]["baseline_lora"]
            germ = by_task[task]["germ_bo_center_jsd"]
            acc = next(row for row in paired_rows if row["task"] == task and row["metric"] == "test_accuracy")
            handle.write(
                f"| {task} | {category} | {lora['test_accuracy_mean']:.4f} | "
                f"{germ['test_accuracy_mean']:.4f} | {acc['mean_delta']:+.4f} "
                f"[{acc['bootstrap_ci95_low']:+.4f}, {acc['bootstrap_ci95_high']:+.4f}] | "
                f"{acc['win_rate']:.0%} |\n"
            )
        histone_acc = [row for row in paired_rows if row["metric"] == "test_accuracy" and row["task"] != "enhancers"]
        wins = sum(1 for row in histone_acc if row["mean_delta"] > 0)
        handle.write(f"\nHistone marks with positive mean accuracy delta: {wins}/{len(histone_acc)}.\n")
    return path


def main():
    rows = load_rows()
    summary = summarize(rows)
    paired_rows = paired(rows)
    with (ROOT / "nt_downstream_all_summary.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(summary[0].keys()))
        writer.writeheader()
        writer.writerows(summary)
    with (ROOT / "nt_downstream_all_paired.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(paired_rows[0].keys()))
        writer.writeheader()
        writer.writerows(paired_rows)
    print(write_markdown(summary, paired_rows))


if __name__ == "__main__":
    main()
