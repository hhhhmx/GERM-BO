import csv
import json
import random
import statistics
from pathlib import Path


ROOT = Path("results")
SEEDS = [42, 43, 44]
METHODS = [
    ("baseline_lora", "Baseline LoRA"),
    ("germ_bo_activation", "GERM-BO activation-derived"),
    ("germ_bo_metadata_estimated", "GERM-BO metadata-estimated"),
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
    for method, label in METHODS:
        for seed in SEEDS:
            path = ROOT / f"human_nontata_{method}_seed{seed}_threshold.json"
            data = json.loads(path.read_text(encoding="utf-8"))
            rows.append(
                {
                    "benchmark": "human_nontata_promoters",
                    "method": method,
                    "label": label,
                    "seed": seed,
                    "selected_threshold": data["selected_threshold"],
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
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def summarize(rows):
    out = []
    for method, label in METHODS:
        group = [row for row in rows if row["method"] == method]
        acc = [row["test_accuracy"] for row in group]
        f1 = [row["test_f1"] for row in group]
        out.append(
            {
                "benchmark": "human_nontata_promoters",
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
    return out


def paired(rows, left, right):
    by_key = {(row["method"], row["seed"]): row for row in rows}
    out = []
    for metric in ["test_accuracy", "test_f1"]:
        deltas = [by_key[(left, seed)][metric] - by_key[(right, seed)][metric] for seed in SEEDS]
        ci_low, ci_high = bootstrap_ci(deltas)
        out.append(
            {
                "comparison": f"{left}_minus_{right}",
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


def write_markdown(summary, paired_rows):
    path = ROOT / "human_nontata_promoters_pilot.md"
    with path.open("w", encoding="utf-8") as handle:
        handle.write("# Real Benchmark Pilot: Human Non-TATA Promoters\n\n")
        handle.write(
            "Protocol: Genomic Benchmarks `human_nontata_promoters`, real DNABERT-2 backbone, "
            "single GPU, train/val/test pilot subset `2000/500/1000`, seeds `42-44`, "
            "validation-accuracy best checkpoint, and validation-threshold tuned test evaluation. "
            "Metadata-estimated GERM-BO uses a label-free sequence-only k-mer JSD border-score estimator.\n\n"
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
    paired_rows = []
    paired_rows.extend(paired(rows, "germ_bo_metadata_estimated", "baseline_lora"))
    paired_rows.extend(paired(rows, "germ_bo_metadata_estimated", "germ_bo_activation"))
    paired_rows.extend(paired(rows, "germ_bo_activation", "baseline_lora"))
    write_csv(ROOT / "human_nontata_promoters_pilot.csv", rows)
    write_csv(ROOT / "human_nontata_promoters_pilot_summary.csv", summary)
    write_csv(ROOT / "human_nontata_promoters_pilot_paired.csv", paired_rows)
    print(write_markdown(summary, paired_rows))


if __name__ == "__main__":
    main()
