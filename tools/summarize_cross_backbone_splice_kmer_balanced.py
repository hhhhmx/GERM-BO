import csv
import json
import random
import statistics
from pathlib import Path


ROOT = Path("results")
SEEDS = [50, 51, 52, 53, 54]

BACKBONES = [
    (
        "dnabert2",
        "DNABERT-2",
        [
            ("lora", "LoRA", "splice_kmer_balanced_confirm_lora_attention_output_classifier_seed{seed}_argmax.json"),
            (
                "germ_bo_quantile",
                "GERM-BO quantile",
                "splice_kmer_balanced_confirm_germ_bo_quantile_q08_12_comp027_seed{seed}_argmax.json",
            ),
        ],
    ),
    (
        "nt_v2_50m",
        "NT v2 50M",
        [
            ("lora", "LoRA", "splice_kmer_balanced_crossbackbone_nt_v2_50m_lora_seed{seed}_argmax.json"),
            (
                "germ_bo_quantile",
                "GERM-BO quantile",
                "splice_kmer_balanced_crossbackbone_nt_v2_50m_germ_bo_quantile_seed{seed}_argmax.json",
            ),
        ],
    ),
    (
        "hyenadna_tiny",
        "HyenaDNA tiny",
        [
            ("lora", "LoRA", "splice_kmer_balanced_crossbackbone_hyenadna_tiny_lora_seed{seed}_argmax.json"),
            (
                "germ_bo_quantile",
                "GERM-BO quantile",
                "splice_kmer_balanced_crossbackbone_hyenadna_tiny_germ_bo_quantile_seed{seed}_argmax.json",
            ),
        ],
    ),
]


def mean(values):
    return statistics.mean(values)


def std(values):
    return statistics.stdev(values) if len(values) > 1 else 0.0


def bootstrap_ci(deltas, iterations=10000, seed=20260424):
    rng = random.Random(seed)
    samples = []
    for _ in range(iterations):
        samples.append(mean([rng.choice(deltas) for _ in deltas]))
    samples.sort()
    return samples[int(0.025 * iterations)], samples[int(0.975 * iterations)]


def load_rows():
    rows = []
    for backbone_id, backbone_label, specs in BACKBONES:
        for method_id, method_label, pattern in specs:
            for seed in SEEDS:
                path = ROOT / pattern.format(seed=seed)
                if not path.exists():
                    raise FileNotFoundError(path)
                data = json.loads(path.read_text(encoding="utf-8"))
                rows.append(
                    {
                        "backbone_id": backbone_id,
                        "backbone_label": backbone_label,
                        "method_id": method_id,
                        "method_label": method_label,
                        "seed": seed,
                        "test_accuracy": data["test"]["accuracy"],
                        "test_macro_f1": data["test"]["macro_f1"],
                    }
                )
    return rows


def summarize(rows):
    summary = []
    for backbone_id, backbone_label, specs in BACKBONES:
        for method_id, method_label, _ in specs:
            group = [
                row
                for row in rows
                if row["backbone_id"] == backbone_id and row["method_id"] == method_id
            ]
            acc = [row["test_accuracy"] for row in group]
            f1 = [row["test_macro_f1"] for row in group]
            summary.append(
                {
                    "backbone_id": backbone_id,
                    "backbone_label": backbone_label,
                    "method_id": method_id,
                    "method_label": method_label,
                    "n_seeds": len(group),
                    "test_accuracy_mean": mean(acc),
                    "test_accuracy_std": std(acc),
                    "test_macro_f1_mean": mean(f1),
                    "test_macro_f1_std": std(f1),
                    "per_seed_accuracy": " / ".join(f"{value:.4f}" for value in acc),
                }
            )
    return summary


def paired(rows):
    by_key = {(row["backbone_id"], row["method_id"], row["seed"]): row for row in rows}
    out = []
    for backbone_id, backbone_label, _ in BACKBONES:
        for metric in ["test_accuracy", "test_macro_f1"]:
            deltas = [
                by_key[(backbone_id, "germ_bo_quantile", seed)][metric]
                - by_key[(backbone_id, "lora", seed)][metric]
                for seed in SEEDS
            ]
            ci_low, ci_high = bootstrap_ci(deltas)
            out.append(
                {
                    "backbone_id": backbone_id,
                    "backbone_label": backbone_label,
                    "metric": metric,
                    "mean_delta": mean(deltas),
                    "bootstrap_ci95_low": ci_low,
                    "bootstrap_ci95_high": ci_high,
                    "win_rate": sum(1 for value in deltas if value > 0) / len(deltas),
                    "per_seed_delta": " / ".join(f"{value:+.4f}" for value in deltas),
                }
            )
    return out


def write_markdown(summary, paired_rows):
    path = ROOT / "cross_backbone_splice_kmer_balanced_50_54.md"
    with path.open("w", encoding="utf-8") as handle:
        handle.write("# Cross-Backbone Strict Splice (Label-Free Estimator, Seeds 50--54)\n\n")
        handle.write(
            "Protocol: strict `3-mer-balanced` splice split, train-quantile center-window k-mer JSD metadata, "
            "quantile clip `[0.8,1.2]`, compensation `0.27`, seeds `50-54`. "
            "Tests whether GERM-BO gains transfer beyond DNABERT-2 under label-free border estimation.\n\n"
        )
        for backbone_id, backbone_label, _ in BACKBONES:
            handle.write(f"## {backbone_label}\n\n")
            handle.write("| Method | Seeds | Test Acc Mean +/- Std | Test Macro-F1 Mean +/- Std | Per-Seed Acc |\n")
            handle.write("|---|---:|---:|---:|---|\n")
            for row in summary:
                if row["backbone_id"] != backbone_id:
                    continue
                handle.write(
                    f"| {row['method_label']} | {row['n_seeds']} | "
                    f"{row['test_accuracy_mean']:.4f} +/- {row['test_accuracy_std']:.4f} | "
                    f"{row['test_macro_f1_mean']:.4f} +/- {row['test_macro_f1_std']:.4f} | "
                    f"{row['per_seed_accuracy']} |\n"
                )
            handle.write("\n")
        handle.write("## Paired Deltas (GERM-BO minus LoRA)\n\n")
        handle.write("| Backbone | Metric | Delta Mean | Bootstrap 95% CI | Win Rate | Per-Seed Delta |\n")
        handle.write("|---|---|---:|---:|---:|---|\n")
        for row in paired_rows:
            handle.write(
                f"| {row['backbone_label']} | {row['metric']} | {row['mean_delta']:+.4f} | "
                f"[{row['bootstrap_ci95_low']:+.4f}, {row['bootstrap_ci95_high']:+.4f}] | "
                f"{row['win_rate']:.0%} | {row['per_seed_delta']} |\n"
            )
    return path


def main():
    rows = load_rows()
    summary = summarize(rows)
    paired_rows = paired(rows)
    with (ROOT / "cross_backbone_splice_kmer_balanced_50_54.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    with (ROOT / "cross_backbone_splice_kmer_balanced_50_54_summary.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(summary[0].keys()))
        writer.writeheader()
        writer.writerows(summary)
    with (ROOT / "cross_backbone_splice_kmer_balanced_50_54_paired.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(paired_rows[0].keys()))
        writer.writeheader()
        writer.writerows(paired_rows)
    print(write_markdown(summary, paired_rows))


if __name__ == "__main__":
    main()
