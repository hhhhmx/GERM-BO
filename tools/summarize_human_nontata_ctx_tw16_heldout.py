import csv
import json
import random
import statistics
from pathlib import Path


ROOT = Path("results")
SEEDS = [45, 46, 47, 48, 49]
METHODS = [
    ("baseline_lora", "human_nontata_heldout_baseline_lora_seed{seed}_threshold.json", "Baseline LoRA"),
    ("ctx_tw16_t10_s015", "human_nontata_heldout_ctx_tw16_t10_s015_seed{seed}_threshold.json", "Contextual DNABERT-2 shift ctx_tw16_t10_s015"),
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


def load_metric(path):
    data = json.loads(path.read_text(encoding="utf-8"))
    return {
        "selected_threshold": data["selected_threshold"],
        "val_accuracy": data["validation"]["accuracy"],
        "val_f1": data["validation"]["f1"],
        "test_accuracy": data["test"]["accuracy"],
        "test_f1": data["test"]["f1"],
        "test_precision": data["test"]["precision"],
        "test_recall": data["test"]["recall"],
    }


def load_rows():
    rows = []
    for method, pattern, label in METHODS:
        for seed in SEEDS:
            rows.append(
                {
                    "method": method,
                    "label": label,
                    "seed": seed,
                    **load_metric(ROOT / pattern.format(seed=seed)),
                }
            )
    return rows


def write_csv(path, rows):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def summarize(rows):
    summary = []
    for method, _, label in METHODS:
        group = [row for row in rows if row["method"] == method]
        acc = [row["test_accuracy"] for row in group]
        f1 = [row["test_f1"] for row in group]
        summary.append(
            {
                "method": method,
                "label": label,
                "n_seeds": len(group),
                "test_accuracy_mean": mean(acc),
                "test_accuracy_std": std(acc),
                "test_f1_mean": mean(f1),
                "test_f1_std": std(f1),
                "per_seed_accuracy": " / ".join(f"{value:.4f}" for value in acc),
            }
        )
    return summary


def paired(rows):
    by_key = {(row["method"], row["seed"]): row for row in rows}
    out = []
    for metric in ["test_accuracy", "test_f1"]:
        deltas = [
            by_key[("ctx_tw16_t10_s015", seed)][metric] - by_key[("baseline_lora", seed)][metric]
            for seed in SEEDS
        ]
        ci_low, ci_high = bootstrap_ci(deltas)
        out.append(
            {
                "comparison": "ctx_tw16_t10_s015_minus_baseline_lora",
                "metric": metric,
                "mean_delta": mean(deltas),
                "delta_std": std(deltas),
                "bootstrap_ci95_low": ci_low,
                "bootstrap_ci95_high": ci_high,
                "win_rate": sum(1 for value in deltas if value > 0) / len(deltas),
                "tie_count": sum(1 for value in deltas if value == 0),
                "per_seed_delta": " / ".join(f"{value:+.4f}" for value in deltas),
            }
        )
    return out


def write_markdown(summary, paired_rows):
    path = ROOT / "human_nontata_ctx_tw16_heldout.md"
    with path.open("w", encoding="utf-8") as handle:
        handle.write("# Human Non-TATA Promoters Contextual TW16 Held-Out Confirmation\n\n")
        handle.write(
            "Protocol: held-out seeds `45-49` on Genomic Benchmarks `human_nontata_promoters`, "
            "pilot subset `2000/500/1000`, real DNABERT-2 backbone, validation-accuracy best checkpoint, "
            "and validation-threshold tuned test evaluation. The candidate estimator is frozen contextual "
            "DNABERT-2 representation shift with `token_window=16`, `top_ratio=0.10`, `score_scale=0.15`.\n\n"
        )
        handle.write("## Summary\n\n")
        handle.write("| Method | Seeds | Test Acc Mean +/- Std | Test F1 Mean +/- Std | Per-Seed Acc |\n")
        handle.write("|---|---:|---:|---:|---|\n")
        for row in summary:
            handle.write(
                f"| {row['label']} | {row['n_seeds']} | "
                f"{row['test_accuracy_mean']:.4f} +/- {row['test_accuracy_std']:.4f} | "
                f"{row['test_f1_mean']:.4f} +/- {row['test_f1_std']:.4f} | "
                f"{row['per_seed_accuracy']} |\n"
            )
        handle.write("\n## Paired Deltas\n\n")
        handle.write("| Comparison | Metric | Delta Mean | Bootstrap 95% CI | Win Rate | Per-Seed Delta |\n")
        handle.write("|---|---|---:|---:|---:|---|\n")
        for row in paired_rows:
            handle.write(
                f"| {row['comparison']} | {row['metric']} | {row['mean_delta']:+.4f} | "
                f"[{row['bootstrap_ci95_low']:+.4f}, {row['bootstrap_ci95_high']:+.4f}] | "
                f"{row['win_rate']:.1%} | {row['per_seed_delta']} |\n"
            )
    return path


def main():
    rows = load_rows()
    summary = summarize(rows)
    paired_rows = paired(rows)
    write_csv(ROOT / "human_nontata_ctx_tw16_heldout.csv", rows)
    write_csv(ROOT / "human_nontata_ctx_tw16_heldout_summary.csv", summary)
    write_csv(ROOT / "human_nontata_ctx_tw16_heldout_paired.csv", paired_rows)
    print(write_markdown(summary, paired_rows))


if __name__ == "__main__":
    main()
