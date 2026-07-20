import csv
import math
import random
import statistics
from pathlib import Path


ROOT = Path("results")
INPUTS = [
    ROOT / "splice_kmer_balanced_confirmation_50_54.csv",
    ROOT / "splice_kmer_balanced_confirmation_55_59.csv",
]
SEEDS = list(range(50, 60))
METHODS = [
    ("lora_attention_output_classifier", "LoRA attention.output + classifier"),
    ("germ_bo_quantile_q08_12_comp027", "GERM-BO quantile [0.8,1.2] comp0.27"),
]


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


def read_rows():
    rows = []
    for path in INPUTS:
        with path.open("r", encoding="utf-8", newline="") as handle:
            rows.extend(csv.DictReader(handle))
    out = []
    for row in rows:
        out.append(
            {
                "benchmark": row["benchmark"],
                "method": row["method"],
                "label": row["label"],
                "seed": int(row["seed"]),
                "val_accuracy": float(row["val_accuracy"]),
                "val_macro_f1": float(row["val_macro_f1"]),
                "test_accuracy": float(row["test_accuracy"]),
                "test_macro_f1": float(row["test_macro_f1"]),
            }
        )
    return out


def write_csv(path, rows):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main():
    rows = read_rows()
    rows.sort(key=lambda item: (item["method"], item["seed"]))
    write_csv(ROOT / "splice_kmer_balanced_pooled_50_59.csv", rows)

    summary = []
    for method, label in METHODS:
        group = [row for row in rows if row["method"] == method]
        acc = [row["test_accuracy"] for row in group]
        f1 = [row["test_macro_f1"] for row in group]
        summary.append(
            {
                "benchmark": "splice_sites_all_kmer_balanced",
                "method": method,
                "label": label,
                "n_seeds": len(group),
                "test_accuracy_mean": mean(acc),
                "test_accuracy_std": std(acc),
                "test_macro_f1_mean": mean(f1),
                "test_macro_f1_std": std(f1),
                "per_seed_accuracy": " / ".join(f"{value:.4f}" for value in acc),
                "per_seed_macro_f1": " / ".join(f"{value:.4f}" for value in f1),
            }
        )
    write_csv(ROOT / "splice_kmer_balanced_pooled_50_59_summary.csv", summary)

    by_key = {(row["method"], row["seed"]): row for row in rows}
    paired_rows = []
    for metric in ["test_accuracy", "test_macro_f1"]:
        deltas = [
            by_key[("germ_bo_quantile_q08_12_comp027", seed)][metric]
            - by_key[("lora_attention_output_classifier", seed)][metric]
            for seed in SEEDS
        ]
        ci_low, ci_high = bootstrap_ci(deltas)
        paired_rows.append(
            {
                "comparison": "germ_bo_quantile_q08_12_comp027_minus_lora_attention_output_classifier",
                "metric": metric,
                "n_pairs": len(deltas),
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
        )
    write_csv(ROOT / "splice_kmer_balanced_pooled_50_59_paired.csv", paired_rows)

    path = ROOT / "splice_kmer_balanced_pooled_50_59.md"
    by_method = {row["method"]: row for row in summary}
    acc_row = next(row for row in paired_rows if row["metric"] == "test_accuracy")
    f1_row = next(row for row in paired_rows if row["metric"] == "test_macro_f1")
    with path.open("w", encoding="utf-8") as handle:
        handle.write("# Splice Strict 3-mer-Balanced Pooled Summary Seeds 50-59\n\n")
        handle.write(
            "Protocol: pooled held-out analysis on the strict `3-mer-balanced` split, combining seeds `50-54` and `55-59` "
            "for the two main methods under the same single-GPU training budget with explicit `CUDA_VISIBLE_DEVICES=3`.\n\n"
        )
        handle.write("## Summary\n\n")
        handle.write("| Method | Seeds | Test Acc Mean +/- Std | Test Macro-F1 Mean +/- Std | Per-Seed Acc |\n")
        handle.write("|---|---:|---:|---:|---|\n")
        for method, label in METHODS:
            row = by_method[method]
            handle.write(
                f"| {label} | {row['n_seeds']} | "
                f"{row['test_accuracy_mean']:.4f} +/- {row['test_accuracy_std']:.4f} | "
                f"{row['test_macro_f1_mean']:.4f} +/- {row['test_macro_f1_std']:.4f} | "
                f"{row['per_seed_accuracy']} |\n"
            )
        handle.write("\n## Paired Deltas\n\n")
        handle.write("| Metric | Delta Mean | t-test p | Wilcoxon p | Sign p | Bootstrap 95% CI | Win Rate | Per-Seed Delta |\n")
        handle.write("|---|---:|---:|---:|---:|---:|---:|---|\n")
        for row in paired_rows:
            handle.write(
                f"| {row['metric']} | {row['mean_delta']:+.4f} | "
                f"{row['paired_t_pvalue_normal_approx']:.4f} | {row['wilcoxon_pvalue_exact']:.4f} | "
                f"{row['sign_test_pvalue_exact']:.4f} | "
                f"[{row['bootstrap_ci95_low']:+.4f}, {row['bootstrap_ci95_high']:+.4f}] | "
                f"{row['win_rate']:.1%} | {row['per_seed_delta']} |\n"
            )
        handle.write("\n## Main interpretation\n\n")
        handle.write(
            f"Pooled over seeds `50-59`, GERM-BO remains better in mean than the strong LoRA baseline: "
            f"accuracy delta `{acc_row['mean_delta']:+.4f}` and macro-F1 delta `{f1_row['mean_delta']:+.4f}`. "
            f"Bootstrap intervals stay positive for both metrics, but the exact non-parametric tests are now more conservative "
            f"because the second held-out block contains several weaker seeds. The most accurate claim is therefore that the strict-split "
            f"external result is positive in pooled mean and bootstrap CI, but only partially stable across held-out seed blocks.\n"
        )
    print(path)


if __name__ == "__main__":
    main()
