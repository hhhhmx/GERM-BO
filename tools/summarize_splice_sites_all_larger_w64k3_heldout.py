import csv
import json
import random
import statistics
from pathlib import Path


ROOT = Path("results")
SEEDS = [45, 46, 47, 48, 49]
METHODS = [
    ("baseline_lora", "Baseline LoRA"),
    ("germ_bo_center_w64_k3_t10_s3", "GERM-BO center-JSD w64 k3 top10 scale3"),
]


def mean(values):
    return statistics.mean(values)


def std(values):
    return statistics.stdev(values) if len(values) > 1 else 0.0


def bootstrap_ci(deltas, iterations=10000, seed=20260421):
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
            path = ROOT / f"splice_sites_all_larger_w64k3_heldout_{method}_seed{seed}_argmax.json"
            data = json.loads(path.read_text(encoding="utf-8"))
            rows.append(
                {
                    "benchmark": "splice_sites_all_larger",
                    "method": method,
                    "label": label,
                    "seed": seed,
                    "val_accuracy": data["validation"]["accuracy"],
                    "val_macro_f1": data["validation"]["macro_f1"],
                    "test_accuracy": data["test"]["accuracy"],
                    "test_macro_f1": data["test"]["macro_f1"],
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
    for method, label in METHODS:
        group = [row for row in rows if row["method"] == method]
        acc = [row["test_accuracy"] for row in group]
        f1 = [row["test_macro_f1"] for row in group]
        summary.append(
            {
                "benchmark": "splice_sites_all_larger",
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
    return summary


def paired(rows):
    by_key = {(row["method"], row["seed"]): row for row in rows}
    out = []
    for metric in ["test_accuracy", "test_macro_f1"]:
        deltas = [
            by_key[("germ_bo_center_w64_k3_t10_s3", seed)][metric]
            - by_key[("baseline_lora", seed)][metric]
            for seed in SEEDS
        ]
        ci_low, ci_high = bootstrap_ci(deltas)
        out.append(
            {
                "comparison": "germ_bo_center_w64_k3_t10_s3_minus_baseline_lora",
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
    path = ROOT / "splice_sites_all_larger_w64k3_heldout.md"
    with path.open("w", encoding="utf-8") as handle:
        handle.write("# Splice Sites All Larger Split W64K3 Held-Out Confirmation\n\n")
        handle.write(
            "Protocol: `splice_sites_all`, larger balanced split `9000/1800/3000`, held-out seeds `45-49`, "
            "real DNABERT-2 backbone, validation-accuracy best checkpoint, argmax test evaluation, "
            "single GPU `CUDA_VISIBLE_DEVICES=3`. This run stops the full 4-estimator grid and confirms only "
            "the best first-stage estimator: center-JSD `w64/k3/top10/scale3`.\n\n"
        )
        handle.write("## Summary\n\n")
        handle.write("| Method | Seeds | Test Acc Mean +/- Std | Test Macro-F1 Mean +/- Std | Per-Seed Acc |\n")
        handle.write("|---|---:|---:|---:|---|\n")
        for row in summary:
            handle.write(
                f"| {row['label']} | {row['n_seeds']} | "
                f"{row['test_accuracy_mean']:.4f} +/- {row['test_accuracy_std']:.4f} | "
                f"{row['test_macro_f1_mean']:.4f} +/- {row['test_macro_f1_std']:.4f} | "
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
    write_csv(ROOT / "splice_sites_all_larger_w64k3_heldout.csv", rows)
    write_csv(ROOT / "splice_sites_all_larger_w64k3_heldout_summary.csv", summary)
    write_csv(ROOT / "splice_sites_all_larger_w64k3_heldout_paired.csv", paired_rows)
    print(write_markdown(summary, paired_rows))


if __name__ == "__main__":
    main()
