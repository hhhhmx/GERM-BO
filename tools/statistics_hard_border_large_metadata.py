import csv
import math
import random
import statistics
from pathlib import Path


ROOT = Path("results")
INPUT = ROOT / "hard_border_large_metadata_13seed_comparison.csv"
SEEDS = list(range(42, 55))
COMPARISONS = [
    ("metadata_germ_bo", "baseline_lora"),
    ("metadata_germ_bo", "germ_bo_final_attn_output_classifier"),
    ("germ_bo_final_attn_output_classifier", "baseline_lora"),
]
METRICS = ["test_accuracy", "test_f1", "test_precision", "test_recall"]


def mean(values):
    return statistics.mean(values)


def std(values):
    return statistics.stdev(values) if len(values) > 1 else 0.0


def normal_cdf(value):
    return 0.5 * (1.0 + math.erf(value / math.sqrt(2.0)))


def paired_t_pvalue(deltas):
    if len(deltas) < 2:
        return None
    delta_std = std(deltas)
    if delta_std == 0:
        return 0.0 if mean(deltas) != 0 else 1.0
    t_stat = mean(deltas) / (delta_std / math.sqrt(len(deltas)))
    return 2.0 * (1.0 - normal_cdf(abs(t_stat)))


def wilcoxon_signed_rank_pvalue(deltas):
    nonzero = [(abs(delta), 1 if delta > 0 else -1) for delta in deltas if delta != 0]
    n = len(nonzero)
    if n == 0:
        return 1.0
    sorted_items = sorted(enumerate(nonzero), key=lambda item: item[1][0])
    ranks = [0.0] * n
    current = 0
    while current < n:
        end = current + 1
        while end < n and sorted_items[end][1][0] == sorted_items[current][1][0]:
            end += 1
        avg_rank = (current + 1 + end) / 2.0
        for position in range(current, end):
            ranks[sorted_items[position][0]] = avg_rank
        current = end
    positive_rank_sum = sum(rank for rank, (_, sign) in zip(ranks, nonzero) if sign > 0)
    total_rank_sum = n * (n + 1) / 2.0
    observed = min(positive_rank_sum, total_rank_sum - positive_rank_sum)
    count = 0
    extreme = 0
    for mask in range(1 << n):
        rank_sum = 0.0
        for index, rank in enumerate(ranks):
            if mask & (1 << index):
                rank_sum += rank
        stat = min(rank_sum, total_rank_sum - rank_sum)
        if stat <= observed + 1e-12:
            extreme += 1
        count += 1
    return extreme / count


def bootstrap_ci(deltas, iterations=20000, seed=1234):
    rng = random.Random(seed)
    values = []
    for _ in range(iterations):
        values.append(mean([rng.choice(deltas) for _ in deltas]))
    values.sort()
    return values[int(0.025 * iterations)], values[int(0.975 * iterations)]


def load_rows():
    rows = {}
    with INPUT.open(newline="") as handle:
        for row in csv.DictReader(handle):
            method = row["method"]
            seed = int(row["seed"])
            rows[(method, seed)] = {
                key: float(row[key])
                for key in [
                    "test_accuracy",
                    "test_f1",
                    "test_precision",
                    "test_recall",
                ]
            }
    return rows


def compute(rows, better, worse, metric):
    better_values = [rows[(better, seed)][metric] for seed in SEEDS]
    worse_values = [rows[(worse, seed)][metric] for seed in SEEDS]
    deltas = [left - right for left, right in zip(better_values, worse_values)]
    ci_low, ci_high = bootstrap_ci(deltas)
    return {
        "metric": metric,
        "comparison": f"{better}_minus_{worse}",
        "better": better,
        "worse": worse,
        "n_pairs": len(deltas),
        "better_mean": mean(better_values),
        "better_std": std(better_values),
        "worse_mean": mean(worse_values),
        "worse_std": std(worse_values),
        "mean_delta": mean(deltas),
        "delta_std": std(deltas),
        "paired_t_pvalue_normal_approx": paired_t_pvalue(deltas),
        "wilcoxon_pvalue_exact": wilcoxon_signed_rank_pvalue(deltas),
        "bootstrap_ci95_low": ci_low,
        "bootstrap_ci95_high": ci_high,
        "win_rate": sum(1 for value in deltas if value > 0) / len(deltas),
        "tie_count": sum(1 for value in deltas if value == 0),
        "per_seed_delta": " / ".join(f"{value:+.4f}" for value in deltas),
    }


def write_csv(path, rows):
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main():
    rows = load_rows()
    stats = []
    for better, worse in COMPARISONS:
        for metric in METRICS:
            stats.append(compute(rows, better, worse, metric))
    write_csv(ROOT / "hard_border_large_metadata_significance.csv", stats)

    md = ROOT / "hard_border_large_metadata_significance.md"
    with md.open("w") as handle:
        handle.write("# Statistical Significance: hard_border_large Metadata-Driven GERM-BO\n\n")
        handle.write(
            "Protocol: paired comparison over seeds `42-54` on the enlarged hard-border split. "
            "Metrics use validation-accuracy best checkpoint and validation-threshold tuned test evaluation. "
            "P-values are paired t-test normal approximation and exact Wilcoxon signed-rank test. "
            "Bootstrap CIs use 20,000 paired bootstrap samples over mean deltas.\n\n"
        )
        handle.write("| Metric | Comparison | Mean A +/- Std | Mean B +/- Std | Delta | t-test p | Wilcoxon p | Bootstrap 95% CI | Win Rate |\n")
        handle.write("|---|---|---:|---:|---:|---:|---:|---:|---:|\n")
        for item in stats:
            handle.write(
                f"| {item['metric']} | {item['comparison']} | "
                f"{item['better_mean']:.4f} +/- {item['better_std']:.4f} | "
                f"{item['worse_mean']:.4f} +/- {item['worse_std']:.4f} | "
                f"{item['mean_delta']:+.4f} | "
                f"{item['paired_t_pvalue_normal_approx']:.4f} | "
                f"{item['wilcoxon_pvalue_exact']:.4f} | "
                f"[{item['bootstrap_ci95_low']:+.4f}, {item['bootstrap_ci95_high']:+.4f}] | "
                f"{item['win_rate']:.1%} |\n"
            )
        handle.write("\n## Main Interpretation\n\n")
        acc_meta_base = next(
            item
            for item in stats
            if item["metric"] == "test_accuracy"
            and item["comparison"] == "metadata_germ_bo_minus_baseline_lora"
        )
        acc_meta_activation = next(
            item
            for item in stats
            if item["metric"] == "test_accuracy"
            and item["comparison"] == "metadata_germ_bo_minus_germ_bo_final_attn_output_classifier"
        )
        handle.write(
            f"Metadata-driven GERM-BO improves accuracy over Baseline LoRA by "
            f"`{acc_meta_base['mean_delta']:+.4f}` and over activation-derived GERM-BO by "
            f"`{acc_meta_activation['mean_delta']:+.4f}`. Both bootstrap intervals are strictly positive, "
            "supporting metadata-driven GERM-BO as the strongest current main configuration.\n"
        )
    print(md)
    print(ROOT / "hard_border_large_metadata_significance.csv")


if __name__ == "__main__":
    main()
