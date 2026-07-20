import csv
import math
import random
import statistics
from pathlib import Path


ROOT = Path("results")
INPUT = ROOT / "splice_kmer_balanced_full_comparison_table.csv"
SEEDS = [50, 51, 52, 53, 54]
COMPARISONS = [
    ("GERM-BO quantile [0.8,1.2] comp0.27", "LoRA attention.output + classifier"),
    ("GERM-BO quantile [0.8,1.2] comp0.27", "GERM-BO comp=0"),
    ("GERM-BO quantile [0.8,1.2] comp0.27", "Baseline LoRA full target set"),
]
METRICS = ["test_accuracy", "test_macro_f1"]


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


def exact_sign_test_pvalue(deltas):
    wins = sum(1 for delta in deltas if delta > 0)
    losses = sum(1 for delta in deltas if delta < 0)
    n = wins + losses
    if n == 0:
        return 1.0
    extreme = min(wins, losses)
    cumulative = 0.0
    for k in range(extreme + 1):
        cumulative += math.comb(n, k)
    return min(1.0, 2.0 * cumulative / (2 ** n))


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


def bootstrap_ci(deltas, iterations=20000, seed=20260425):
    rng = random.Random(seed)
    samples = []
    for _ in range(iterations):
        samples.append(mean([rng.choice(deltas) for _ in deltas]))
    samples.sort()
    return samples[int(0.025 * iterations)], samples[int(0.975 * iterations)]


def load_rows():
    rows = {}
    with INPUT.open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            if row["family"] == "traditional_kmer":
                continue
            rows[(row["label"], int(row["seed"]))] = {
                "test_accuracy": float(row["test_accuracy"]),
                "test_macro_f1": float(row["test_macro_f1"]),
            }
    return rows


def compute(rows, better, worse, metric):
    better_values = [rows[(better, seed)][metric] for seed in SEEDS]
    worse_values = [rows[(worse, seed)][metric] for seed in SEEDS]
    deltas = [left - right for left, right in zip(better_values, worse_values)]
    ci_low, ci_high = bootstrap_ci(deltas)
    return {
        "comparison": f"{better}_minus_{worse}",
        "better": better,
        "worse": worse,
        "metric": metric,
        "n_pairs": len(deltas),
        "better_mean": mean(better_values),
        "better_std": std(better_values),
        "worse_mean": mean(worse_values),
        "worse_std": std(worse_values),
        "mean_delta": mean(deltas),
        "delta_std": std(deltas),
        "paired_t_pvalue_normal_approx": paired_t_pvalue(deltas),
        "wilcoxon_pvalue_exact": wilcoxon_signed_rank_pvalue(deltas),
        "sign_test_pvalue_exact": exact_sign_test_pvalue(deltas),
        "bootstrap_ci95_low": ci_low,
        "bootstrap_ci95_high": ci_high,
        "win_rate": sum(1 for value in deltas if value > 0) / len(deltas),
        "tie_count": sum(1 for value in deltas if value == 0),
        "per_seed_delta": " / ".join(f"{value:+.4f}" for value in deltas),
    }


def write_csv(path, rows):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main():
    rows = load_rows()
    stats = []
    for better, worse in COMPARISONS:
        for metric in METRICS:
            stats.append(compute(rows, better, worse, metric))
    write_csv(ROOT / "splice_kmer_balanced_significance.csv", stats)

    md = ROOT / "splice_kmer_balanced_significance.md"
    with md.open("w", encoding="utf-8") as handle:
        handle.write("# Statistical Significance: strict 3-mer-balanced splice benchmark\n\n")
        handle.write(
            "Protocol: paired comparison over held-out seeds `50-54` on the strict `3-mer-balanced` split. "
            "Metrics use validation-accuracy best checkpoint and argmax test evaluation. "
            "P-values are paired t-test normal approximation, exact Wilcoxon signed-rank test, and exact sign test. "
            "Bootstrap CIs use 20,000 paired bootstrap samples over mean deltas.\n\n"
        )
        handle.write("| Metric | Comparison | Mean A +/- Std | Mean B +/- Std | Delta | t-test p | Wilcoxon p | Sign p | Bootstrap 95% CI | Win Rate |\n")
        handle.write("|---|---|---:|---:|---:|---:|---:|---:|---:|---:|\n")
        for item in stats:
            handle.write(
                f"| {item['metric']} | {item['comparison']} | "
                f"{item['better_mean']:.4f} +/- {item['better_std']:.4f} | "
                f"{item['worse_mean']:.4f} +/- {item['worse_std']:.4f} | "
                f"{item['mean_delta']:+.4f} | "
                f"{item['paired_t_pvalue_normal_approx']:.4f} | "
                f"{item['wilcoxon_pvalue_exact']:.4f} | "
                f"{item['sign_test_pvalue_exact']:.4f} | "
                f"[{item['bootstrap_ci95_low']:+.4f}, {item['bootstrap_ci95_high']:+.4f}] | "
                f"{item['win_rate']:.1%} |\n"
            )
    print(md)


if __name__ == "__main__":
    main()
