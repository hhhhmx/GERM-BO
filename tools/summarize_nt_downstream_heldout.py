import csv
import json
import random
import statistics
from pathlib import Path


ROOT = Path("results")
PILOT_SEEDS = [42, 43, 44]
HELDOUT_SEEDS = [45, 46, 47, 48, 49]
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


def load_rows(seeds, split_label):
    rows = []
    for task, category in ALL_TASKS:
        for method, method_label in METHODS:
            for seed in seeds:
                path = ROOT / f"{task}_{method}_seed{seed}_argmax.json"
                if not path.exists():
                    raise FileNotFoundError(path)
                data = json.loads(path.read_text(encoding="utf-8"))
                rows.append(
                    {
                        "split": split_label,
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


def summarize(rows, split_label):
    summary = []
    for task, category in ALL_TASKS:
        for method, method_label in METHODS:
            group = [
                row
                for row in rows
                if row["split"] == split_label and row["task"] == task and row["method"] == method
            ]
            acc = [row["test_accuracy"] for row in group]
            f1 = [row["test_f1"] for row in group]
            summary.append(
                {
                    "split": split_label,
                    "task": task,
                    "category": category,
                    "method": method,
                    "method_label": method_label,
                    "n_seeds": len(group),
                    "test_accuracy_mean": mean(acc),
                    "test_accuracy_std": std(acc),
                    "test_f1_mean": mean(f1),
                    "test_f1_std": std(f1),
                    "per_seed_accuracy": " / ".join(f"{value:.4f}" for value in acc),
                }
            )
    return summary


def paired(rows, split_label, seeds):
    by_key = {(row["task"], row["method"], row["seed"]): row for row in rows if row["split"] == split_label}
    out = []
    for task, category in ALL_TASKS:
        for metric in ["test_accuracy", "test_f1"]:
            deltas = [
                by_key[(task, "germ_bo_center_jsd", seed)][metric]
                - by_key[(task, "baseline_lora", seed)][metric]
                for seed in seeds
            ]
            ci_low, ci_high = bootstrap_ci(deltas)
            out.append(
                {
                    "split": split_label,
                    "task": task,
                    "category": category,
                    "metric": metric,
                    "mean_delta": mean(deltas),
                    "delta_std": std(deltas),
                    "bootstrap_ci95_low": ci_low,
                    "bootstrap_ci95_high": ci_high,
                    "win_rate": sum(1 for value in deltas if value > 0) / len(deltas),
                    "per_seed_delta": " / ".join(f"{value:+.4f}" for value in deltas),
                }
            )
    return out


def write_split_markdown(path, split_label, seeds, summary, paired_rows):
    with path.open("w", encoding="utf-8") as handle:
        handle.write(f"# NT Downstream Held-Out Confirmation ({split_label})\n\n")
        handle.write(
            f"Protocol: ten histone ChIP-seq peak tasks plus `enhancers` from "
            f"`InstaDeepAI/nucleotide_transformer_downstream_tasks`, pilot subset `2000/500/1000`, "
            f"seeds `{seeds[0]}-{seeds[-1]}`, DNABERT-2 LoRA vs metadata-estimated GERM-BO "
            f"(train-quantile center-window k-mer JSD).\n\n"
        )
        handle.write("| Task | Category | LoRA Acc | GERM-BO Acc | ? Acc [95% CI] | Win Rate |\n")
        handle.write("|---|---|---:|---:|---:|---:|\n")
        by_task = {task: {} for task, _ in ALL_TASKS}
        for row in summary:
            by_task[row["task"]][row["method"]] = row
        for task, category in ALL_TASKS:
            lora = by_task[task]["baseline_lora"]
            germ = by_task[task]["germ_bo_center_jsd"]
            acc = next(
                row for row in paired_rows if row["task"] == task and row["metric"] == "test_accuracy"
            )
            handle.write(
                f"| {task} | {category} | {lora['test_accuracy_mean']:.4f} | "
                f"{germ['test_accuracy_mean']:.4f} | {acc['mean_delta']:+.4f} "
                f"[{acc['bootstrap_ci95_low']:+.4f}, {acc['bootstrap_ci95_high']:+.4f}] | "
                f"{acc['win_rate']:.0%} |\n"
            )
        histone_acc = [
            row for row in paired_rows if row["metric"] == "test_accuracy" and row["task"] != "enhancers"
        ]
        wins = sum(1 for row in histone_acc if row["mean_delta"] > 0)
        sig = sum(
            1
            for row in histone_acc
            if row["bootstrap_ci95_low"] > 0 or row["bootstrap_ci95_high"] < 0
        )
        handle.write(
            f"\nHistone marks with positive mean accuracy delta: {wins}/{len(histone_acc)}. "
            f"Tasks with bootstrap 95% CI excluding zero: {sig}/{len(histone_acc)}.\n"
        )
    return path


def write_combined_markdown(pilot_paired, heldout_paired):
    path = ROOT / "nt_downstream_combined.md"
    with path.open("w", encoding="utf-8") as handle:
        handle.write("# NT Downstream: Pilot vs Held-Out Confirmation\n\n")
        handle.write("| Task | Pilot ? Acc [95% CI] | Held-out ? Acc [95% CI] | Consistent sign? |\n")
        handle.write("|---|---:|---:|---|\n")
        pilot_by_task = {
            row["task"]: row for row in pilot_paired if row["metric"] == "test_accuracy"
        }
        heldout_by_task = {
            row["task"]: row for row in heldout_paired if row["metric"] == "test_accuracy"
        }
        for task, _ in ALL_TASKS:
            pilot = pilot_by_task[task]
            heldout = heldout_by_task[task]
            same_sign = (pilot["mean_delta"] >= 0) == (heldout["mean_delta"] >= 0)
            handle.write(
                f"| {task} | {pilot['mean_delta']:+.4f} "
                f"[{pilot['bootstrap_ci95_low']:+.4f}, {pilot['bootstrap_ci95_high']:+.4f}] | "
                f"{heldout['mean_delta']:+.4f} "
                f"[{heldout['bootstrap_ci95_low']:+.4f}, {heldout['bootstrap_ci95_high']:+.4f}] | "
                f"{'yes' if same_sign else 'no'} |\n"
            )
    return path


def write_csv(path, rows):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main():
    pilot_rows = load_rows(PILOT_SEEDS, "pilot")
    heldout_rows = load_rows(HELDOUT_SEEDS, "heldout")
    all_rows = pilot_rows + heldout_rows
    pilot_summary = summarize(all_rows, "pilot")
    heldout_summary = summarize(all_rows, "heldout")
    pilot_paired = paired(all_rows, "pilot", PILOT_SEEDS)
    heldout_paired = paired(all_rows, "heldout", HELDOUT_SEEDS)

    write_csv(ROOT / "nt_downstream_heldout.csv", [row for row in all_rows if row["split"] == "heldout"])
    write_csv(ROOT / "nt_downstream_heldout_summary.csv", heldout_summary)
    write_csv(ROOT / "nt_downstream_heldout_paired.csv", heldout_paired)
    print(write_split_markdown(ROOT / "nt_downstream_heldout.md", "heldout", HELDOUT_SEEDS, heldout_summary, heldout_paired))
    print(write_combined_markdown(pilot_paired, heldout_paired))


if __name__ == "__main__":
    main()
