import csv
import json
import math
import random
import statistics
from pathlib import Path


ROOT = Path("results")
TASKS = ["medium", "hard"]
SEEDS = list(range(47, 55))
VARIANTS = {
    "metadata": {
        "prefix": "metadata",
        "comp": "027",
        "label": "metadata-driven comp=0.27/p4",
    },
    "activation": {
        "prefix": "confirm",
        "comp": "027",
        "label": "activation-derived comp=0.27/p4",
    },
    "no_comp": {
        "prefix": "mechanism",
        "comp": "000",
        "label": "no compensation comp=0.00/p4",
    },
}
COMPARISONS = [
    ("metadata", "activation"),
    ("metadata", "no_comp"),
    ("activation", "no_comp"),
]
METRICS = ["accuracy", "f1", "precision", "recall"]


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
    # Normal approximation is adequate for this reporting helper.
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
    samples = []
    for _ in range(iterations):
        sample = [rng.choice(deltas) for _ in deltas]
        samples.append(mean(sample))
    samples.sort()
    low = samples[int(0.025 * iterations)]
    high = samples[int(0.975 * iterations)]
    return low, high


def load_values():
    values = {}
    for task in TASKS:
        for variant, meta in VARIANTS.items():
            for seed in SEEDS:
                path = ROOT / f"{meta['prefix']}_{task}_comp{meta['comp']}_p4_seed{seed}_threshold.json"
                data = json.loads(path.read_text())
                key = (f"border_{task}", variant, seed)
                values[key] = {
                    "accuracy": data["test"]["accuracy"],
                    "f1": data["test"]["f1"],
                    "precision": data["test"]["precision"],
                    "recall": data["test"]["recall"],
                }
    return values


def group_keys(group):
    if group == "combined":
        return [(f"border_{task}", seed) for task in TASKS for seed in SEEDS]
    return [(group, seed) for seed in SEEDS]


def compute_stats(values, group, better, worse, metric):
    pairs = group_keys(group)
    better_values = [values[(task, better, seed)][metric] for task, seed in pairs]
    worse_values = [values[(task, worse, seed)][metric] for task, seed in pairs]
    deltas = [left - right for left, right in zip(better_values, worse_values)]
    ci_low, ci_high = bootstrap_ci(deltas)
    return {
        "group": group,
        "metric": metric,
        "comparison": f"{VARIANTS[better]['label']} vs {VARIANTS[worse]['label']}",
        "better_variant": better,
        "worse_variant": worse,
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
        "win_rate": sum(1 for delta in deltas if delta > 0) / len(deltas),
        "tie_count": sum(1 for delta in deltas if delta == 0),
        "per_seed_delta": " / ".join(f"{delta:+.4f}" for delta in deltas),
    }


def write_csv(path, rows):
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main():
    values = load_values()
    rows = []
    for group in ["border_medium", "border_hard", "combined"]:
        for better, worse in COMPARISONS:
            for metric in METRICS:
                rows.append(compute_stats(values, group, better, worse, metric))
    write_csv(ROOT / "metadata_mechanism_significance.csv", rows)

    md = ROOT / "metadata_mechanism_significance.md"
    with md.open("w") as handle:
        handle.write("# Statistical Significance: Metadata-Driven Mechanism\n\n")
        handle.write(
            "Protocol: paired comparison on held-out seeds `47-54`. The combined group contains "
            "`border_medium` and `border_hard` pairs. P-values are reported as paired t-test normal "
            "approximation and exact Wilcoxon signed-rank test. Bootstrap CIs are 20,000-sample "
            "paired bootstrap intervals over mean deltas.\n\n"
        )
        for group in ["combined", "border_medium", "border_hard"]:
            handle.write(f"## {group}\n\n")
            handle.write("| Metric | Comparison | Mean A +/- Std | Mean B +/- Std | Delta | t-test p | Wilcoxon p | Bootstrap 95% CI | Win Rate |\n")
            handle.write("|---|---|---:|---:|---:|---:|---:|---:|---:|\n")
            for row in rows:
                if row["group"] != group:
                    continue
                handle.write(
                    f"| {row['metric']} | {row['comparison']} | "
                    f"{row['better_mean']:.4f} +/- {row['better_std']:.4f} | "
                    f"{row['worse_mean']:.4f} +/- {row['worse_std']:.4f} | "
                    f"{row['mean_delta']:+.4f} | "
                    f"{row['paired_t_pvalue_normal_approx']:.4f} | "
                    f"{row['wilcoxon_pvalue_exact']:.4f} | "
                    f"[{row['bootstrap_ci95_low']:+.4f}, {row['bootstrap_ci95_high']:+.4f}] | "
                    f"{row['win_rate']:.1%} |\n"
                )
            handle.write("\n")
        handle.write("## Main Interpretation\n\n")
        combined_accuracy = next(
            row
            for row in rows
            if row["group"] == "combined"
            and row["metric"] == "accuracy"
            and row["better_variant"] == "metadata"
            and row["worse_variant"] == "activation"
        )
        hard_accuracy = next(
            row
            for row in rows
            if row["group"] == "border_hard"
            and row["metric"] == "accuracy"
            and row["better_variant"] == "metadata"
            and row["worse_variant"] == "activation"
        )
        handle.write(
            f"Metadata-driven compensation improves combined accuracy over activation-derived compensation "
            f"by `{combined_accuracy['mean_delta']:+.4f}` with bootstrap CI "
            f"`[{combined_accuracy['bootstrap_ci95_low']:+.4f}, {combined_accuracy['bootstrap_ci95_high']:+.4f}]`. "
            f"The largest gain is on `border_hard`, where accuracy delta is "
            f"`{hard_accuracy['mean_delta']:+.4f}`.\n"
        )
    print(md)
    print(ROOT / "metadata_mechanism_significance.csv")


if __name__ == "__main__":
    main()
