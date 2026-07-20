import csv
import json
import random
import statistics
from pathlib import Path


ROOT = Path("results")
SEEDS = [42, 43, 44]
TAGS = [
    "w16_k2_t10_s3",
    "w32_k2_t10_s3",
    "w64_k2_t10_s3",
    "w32_k3_t10_s3",
    "w32_k2_t20_s3",
    "w32_k2_t10_s6",
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
    for seed in SEEDS:
        metrics = load_metric(ROOT / f"human_nontata_baseline_lora_seed{seed}_threshold.json")
        rows.append({"method": "baseline_lora", "tag": "baseline_lora", "seed": seed, **metrics})
    for tag in TAGS:
        for seed in SEEDS:
            metrics = load_metric(ROOT / f"human_nontata_estimator_{tag}_seed{seed}_threshold.json")
            rows.append({"method": "metadata_estimated", "tag": tag, "seed": seed, **metrics})
    return rows


def write_csv(path, rows):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def summarize(rows):
    summary = []
    for tag in ["baseline_lora"] + TAGS:
        group = [row for row in rows if row["tag"] == tag]
        acc = [row["test_accuracy"] for row in group]
        f1 = [row["test_f1"] for row in group]
        summary.append(
            {
                "tag": tag,
                "method": group[0]["method"],
                "n_seeds": len(group),
                "test_accuracy_mean": mean(acc),
                "test_accuracy_std": std(acc),
                "test_f1_mean": mean(f1),
                "test_f1_std": std(f1),
                "per_seed_accuracy": " / ".join(f"{value:.4f}" for value in acc),
            }
        )
    return summary


def paired_vs_baseline(rows, tag):
    by_key = {(row["tag"], row["seed"]): row for row in rows}
    out = []
    for metric in ["test_accuracy", "test_f1"]:
        deltas = [by_key[(tag, seed)][metric] - by_key[("baseline_lora", seed)][metric] for seed in SEEDS]
        ci_low, ci_high = bootstrap_ci(deltas)
        out.append(
            {
                "tag": tag,
                "metric": metric,
                "mean_delta_vs_baseline": mean(deltas),
                "delta_std": std(deltas),
                "bootstrap_ci95_low": ci_low,
                "bootstrap_ci95_high": ci_high,
                "win_rate": sum(1 for value in deltas if value > 0) / len(deltas),
                "per_seed_delta": " / ".join(f"{value:+.4f}" for value in deltas),
            }
        )
    return out


def write_markdown(summary, paired_rows):
    path = ROOT / "human_nontata_estimator_grid.md"
    with path.open("w", encoding="utf-8") as handle:
        handle.write("# Human Non-TATA Promoters Estimator Grid\n\n")
        handle.write(
            "Protocol: metadata-estimated GERM-BO estimator grid on Genomic Benchmarks "
            "`human_nontata_promoters`, pilot subset `2000/500/1000`, seeds `42-44`. "
            "All estimators are label-free and sequence-only k-mer JSD variants.\n\n"
        )
        handle.write("## Summary\n\n")
        handle.write("| Tag | Method | Acc Mean +/- Std | F1 Mean +/- Std | Per-Seed Acc |\n")
        handle.write("|---|---|---:|---:|---|\n")
        for row in sorted(summary, key=lambda item: item["test_accuracy_mean"], reverse=True):
            handle.write(
                f"| {row['tag']} | {row['method']} | "
                f"{row['test_accuracy_mean']:.4f} +/- {row['test_accuracy_std']:.4f} | "
                f"{row['test_f1_mean']:.4f} +/- {row['test_f1_std']:.4f} | "
                f"{row['per_seed_accuracy']} |\n"
            )
        handle.write("\n## Paired Deltas vs Baseline\n\n")
        handle.write("| Tag | Metric | Delta Mean | Bootstrap 95% CI | Win Rate | Per-Seed Delta |\n")
        handle.write("|---|---|---:|---:|---:|---|\n")
        for row in paired_rows:
            handle.write(
                f"| {row['tag']} | {row['metric']} | {row['mean_delta_vs_baseline']:+.4f} | "
                f"[{row['bootstrap_ci95_low']:+.4f}, {row['bootstrap_ci95_high']:+.4f}] | "
                f"{row['win_rate']:.1%} | {row['per_seed_delta']} |\n"
            )
    return path


def main():
    rows = load_rows()
    summary = summarize(rows)
    paired_rows = []
    for tag in TAGS:
        paired_rows.extend(paired_vs_baseline(rows, tag))
    write_csv(ROOT / "human_nontata_estimator_grid.csv", rows)
    write_csv(ROOT / "human_nontata_estimator_grid_summary.csv", summary)
    write_csv(ROOT / "human_nontata_estimator_grid_paired.csv", paired_rows)
    print(write_markdown(summary, paired_rows))


if __name__ == "__main__":
    main()
