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
    "H3K4me3",
    "H3K79me3",
    "H3K9ac",
    "H4",
    "H4ac",
]
BACKBONES = [
    ("dnabert2", "baseline_lora", "germ_bo_center_jsd"),
    ("nt_v2_50m", "nt_v2_50m_baseline_lora", "nt_v2_50m_germ_bo_center_jsd"),
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


def result_path(task, backbone, method, seed):
    if backbone == "dnabert2":
        return ROOT / f"{task}_{method}_seed{seed}_argmax.json"
    return ROOT / f"{task}_nt_v2_50m_{method}_seed{seed}_argmax.json"


def load_backbone_rows(backbone, lora_method, germ_method):
    rows = []
    for task in HISTONE_TASKS:
        for method in [lora_method, germ_method]:
            for seed in SEEDS:
                path = result_path(task, backbone, method, seed)
                if not path.exists():
                    raise FileNotFoundError(path)
                data = json.loads(path.read_text(encoding="utf-8"))
                rows.append(
                    {
                        "task": task,
                        "backbone": backbone,
                        "method": method,
                        "seed": seed,
                        "test_accuracy": data["test"]["accuracy"],
                        "test_f1": data["test"].get("macro_f1", data["test"].get("f1")),
                    }
                )
    return rows


def summarize(rows, backbone, lora_method, germ_method):
    summary = []
    for task in HISTONE_TASKS:
        for method in [lora_method, germ_method]:
            group = [row for row in rows if row["task"] == task and row["method"] == method]
            acc = [row["test_accuracy"] for row in group]
            f1 = [row["test_f1"] for row in group]
            summary.append(
                {
                    "task": task,
                    "backbone": backbone,
                    "method": method,
                    "test_accuracy_mean": mean(acc),
                    "test_accuracy_std": std(acc),
                    "test_f1_mean": mean(f1),
                    "test_f1_std": std(f1),
                }
            )
    return summary


def paired(rows, backbone, lora_method, germ_method):
    by_key = {(row["task"], row["method"], row["seed"]): row for row in rows}
    out = []
    for task in HISTONE_TASKS:
        deltas = [
            by_key[(task, germ_method, seed)]["test_accuracy"]
            - by_key[(task, lora_method, seed)]["test_accuracy"]
            for seed in SEEDS
        ]
        ci_low, ci_high = bootstrap_ci(deltas)
        out.append(
            {
                "task": task,
                "backbone": backbone,
                "mean_delta": mean(deltas),
                "bootstrap_ci95_low": ci_low,
                "bootstrap_ci95_high": ci_high,
                "win_rate": sum(1 for value in deltas if value > 0) / len(deltas),
            }
        )
    return out


def write_markdown(nt_summary, nt_paired, dnabert_paired):
    path = ROOT / "nt_backbone_histone_pilot.md"
    dnabert_by_task = {row["task"]: row for row in dnabert_paired}
    with path.open("w", encoding="utf-8") as handle:
        handle.write("# NT v2 50M Histone-Mark Pilot (seeds 42--44)\n\n")
        handle.write(
            "Protocol: ten histone ChIP-seq peak tasks, pilot subset `2000/500/1000`, "
            "Nucleotide Transformer v2 50M backbone, LoRA vs metadata-estimated GERM-BO.\n\n"
        )
        handle.write("| Task | NT LoRA Acc | NT GERM-BO Acc | ? Acc [95% CI] | DNABERT-2 ? Acc | Same sign? |\n")
        handle.write("|---|---:|---:|---:|---:|---|\n")
        by_task = {}
        for row in nt_summary:
            by_task.setdefault(row["task"], {})[row["method"]] = row
        for row in nt_paired:
            task = row["task"]
            lora = by_task[task]["baseline_lora"]
            germ = by_task[task]["germ_bo_center_jsd"]
            dnabert = dnabert_by_task[task]
            same_sign = (row["mean_delta"] >= 0) == (dnabert["mean_delta"] >= 0)
            handle.write(
                f"| {task} | {lora['test_accuracy_mean']:.4f} | {germ['test_accuracy_mean']:.4f} | "
                f"{row['mean_delta']:+.4f} [{row['bootstrap_ci95_low']:+.4f}, {row['bootstrap_ci95_high']:+.4f}] | "
                f"{dnabert['mean_delta']:+.4f} | {'yes' if same_sign else 'no'} |\n"
            )
        wins = sum(1 for row in nt_paired if row["mean_delta"] > 0)
        handle.write(f"\nNT v2 50M tasks with positive mean GERM-BO delta: {wins}/{len(nt_paired)}.\n")
    return path


def main():
    nt_rows = load_backbone_rows("nt_v2_50m", "baseline_lora", "germ_bo_center_jsd")
    dnabert_rows = load_backbone_rows("dnabert2", "baseline_lora", "germ_bo_center_jsd")
    nt_summary = summarize(nt_rows, "nt_v2_50m", "baseline_lora", "germ_bo_center_jsd")
    nt_paired = paired(nt_rows, "nt_v2_50m", "baseline_lora", "germ_bo_center_jsd")
    dnabert_paired = paired(dnabert_rows, "dnabert2", "baseline_lora", "germ_bo_center_jsd")
    with (ROOT / "nt_backbone_histone_pilot_summary.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(nt_summary[0].keys()))
        writer.writeheader()
        writer.writerows(nt_summary)
    with (ROOT / "nt_backbone_histone_pilot_paired.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(nt_paired[0].keys()))
        writer.writeheader()
        writer.writerows(nt_paired)
    print(write_markdown(nt_summary, nt_paired, dnabert_paired))


if __name__ == "__main__":
    main()
