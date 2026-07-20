import csv
import json
import random
import statistics
from pathlib import Path


ROOT = Path("results")
SEEDS = [50, 51, 52, 53, 54]

METHOD_SPECS = [
    ("LoRA attention.output + classifier", "dnabert2_lora_baseline", "splice_kmer_balanced_confirm_lora_attention_output_classifier_seed{seed}_argmax.json"),
    ("GERM-BO quantile [0.8,1.2] comp0.27", "dnabert2_germ_bo", "splice_kmer_balanced_confirm_germ_bo_quantile_q08_12_comp027_seed{seed}_argmax.json"),
    ("Gated LoRA attention.output + classifier", "direction_aware_peft", "splice_kmer_balanced_direction_gated_lora_seed{seed}_argmax.json"),
    ("GERM-BO activation-derived comp0.27", "direction_aware_peft", "splice_kmer_balanced_direction_germ_bo_activation_seed{seed}_argmax.json"),
    ("Baseline LoRA full target set", "dnabert2_lora", "splice_kmer_balanced_ablation_baseline_lora_full_seed{seed}_argmax.json"),
    ("GERM-BO comp=0", "mechanism_ablation", "splice_kmer_balanced_ablation_germ_bo_comp0_seed{seed}_argmax.json"),
    ("GERM-BO shuffled metadata", "mechanism_ablation", "splice_kmer_balanced_ablation_germ_bo_shuffled_seed{seed}_argmax.json"),
    ("DNABERT-2 frozen linear probe", "dnabert2_probe", "splice_kmer_balanced_ablation_linear_probe_seed{seed}_argmax.json"),
]


def mean(values):
    return statistics.mean(values)


def std(values):
    return statistics.stdev(values) if len(values) > 1 else 0.0


def bootstrap_ci(deltas, iterations=10000, seed=20260425):
    rng = random.Random(seed)
    samples = []
    for _ in range(iterations):
        samples.append(mean([rng.choice(deltas) for _ in deltas]))
    samples.sort()
    return samples[int(0.025 * iterations)], samples[int(0.975 * iterations)]


def load_argmax_rows():
    rows = []
    missing = []
    for label, family, pattern in METHOD_SPECS:
        for seed in SEEDS:
            path = ROOT / pattern.format(seed=seed)
            if not path.exists():
                missing.append(str(path))
                continue
            data = json.loads(path.read_text(encoding="utf-8"))
            method = pattern.split("_seed{seed}")[0]
            rows.append(
                {
                    "benchmark": "splice_sites_all_kmer_balanced",
                    "method": method,
                    "label": label,
                    "family": family,
                    "seed": seed,
                    "val_accuracy": data["validation"]["accuracy"],
                    "val_macro_f1": data["validation"]["macro_f1"],
                    "test_accuracy": data["test"]["accuracy"],
                    "test_macro_f1": data["test"]["macro_f1"],
                }
            )
    return rows, missing


def load_kmer_rows():
    path = ROOT / "splice_sites_all_kmer_balanced_kmer_comparison.csv"
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    out = []
    for row in rows:
        out.append(
            {
                "benchmark": "splice_sites_all_kmer_balanced",
                "method": row["method"],
                "label": row["label"],
                "family": row["family"],
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


def summarize(rows):
    summary = []
    keys = []
    for row in rows:
        key = (row["method"], row["label"], row["family"])
        if key not in keys:
            keys.append(key)
    for method, label, family in keys:
        group = [row for row in rows if row["method"] == method]
        acc = [row["test_accuracy"] for row in group]
        f1 = [row["test_macro_f1"] for row in group]
        summary.append(
            {
                "benchmark": "splice_sites_all_kmer_balanced",
                "method": method,
                "label": label,
                "family": family,
                "n_seeds": len(group),
                "test_accuracy_mean": mean(acc),
                "test_accuracy_std": std(acc),
                "test_macro_f1_mean": mean(f1),
                "test_macro_f1_std": std(f1),
                "per_seed_accuracy": " / ".join(f"{value:.4f}" for value in acc),
                "per_seed_macro_f1": " / ".join(f"{value:.4f}" for value in f1),
            }
        )
    summary.sort(key=lambda row: row["test_macro_f1_mean"], reverse=True)
    return summary


def paired_vs(rows, reference_label):
    references = [row for row in rows if row["label"] == reference_label]
    if len(references) != len(SEEDS):
        return []
    ref_by_seed = {row["seed"]: row for row in references}
    out = []
    labels = sorted({row["label"] for row in rows})
    for label in labels:
        if label == reference_label:
            continue
        group = [row for row in rows if row["label"] == label]
        if len(group) != len(SEEDS):
            continue
        by_seed = {row["seed"]: row for row in group}
        for metric in ["test_accuracy", "test_macro_f1"]:
            deltas = [by_seed[seed][metric] - ref_by_seed[seed][metric] for seed in SEEDS]
            ci_low, ci_high = bootstrap_ci(deltas)
            out.append(
                {
                    "reference": reference_label,
                    "method": label,
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


def write_markdown(summary, paired_rows, missing):
    path = ROOT / "splice_kmer_balanced_full_comparison_table.md"
    with path.open("w", encoding="utf-8") as handle:
        handle.write("# Splice Strict 3-mer-Balanced Full Comparison Table\n\n")
        handle.write(
            "Protocol: strict `3-mer-balanced` split. DNABERT-2 runs use held-out seeds `50-54` on a single GPU with explicit `CUDA_VISIBLE_DEVICES=3`. "
            "Traditional 3-mer baselines come from the same split and are sequence-only comparison models.\n\n"
        )
        handle.write("## Main Table\n\n")
        handle.write("| Rank | Method | Family | Seeds | Test Acc Mean +/- Std | Test Macro-F1 Mean +/- Std | Per-Seed Acc |\n")
        handle.write("|---:|---|---|---:|---:|---:|---|\n")
        for index, row in enumerate(summary, start=1):
            handle.write(
                f"| {index} | {row['label']} | {row['family']} | {row['n_seeds']} | "
                f"{row['test_accuracy_mean']:.4f} +/- {row['test_accuracy_std']:.4f} | "
                f"{row['test_macro_f1_mean']:.4f} +/- {row['test_macro_f1_std']:.4f} | "
                f"{row['per_seed_accuracy']} |\n"
            )
        handle.write("\n## Paired Deltas vs GERM-BO quantile [0.8,1.2] comp0.27\n\n")
        handle.write("| Method - Reference | Metric | Delta Mean | Bootstrap 95% CI | Win Rate | Per-Seed Delta |\n")
        handle.write("|---|---|---:|---:|---:|---|\n")
        for row in paired_rows:
            handle.write(
                f"| {row['method']} - {row['reference']} | {row['metric']} | "
                f"{row['mean_delta']:+.4f} | [{row['bootstrap_ci95_low']:+.4f}, {row['bootstrap_ci95_high']:+.4f}] | "
                f"{row['win_rate']:.1%} | {row['per_seed_delta']} |\n"
            )
        if missing:
            handle.write("\n## Missing Optional Inputs\n\n")
            for item in missing:
                handle.write(f"- `{item}`\n")
    return path


def main():
    argmax_rows, missing = load_argmax_rows()
    rows = argmax_rows + load_kmer_rows()
    if not rows:
        raise RuntimeError("No rows found for strict 3-mer-balanced comparison table.")
    summary = summarize(rows)
    paired_rows = paired_vs(argmax_rows, "GERM-BO quantile [0.8,1.2] comp0.27")
    write_csv(ROOT / "splice_kmer_balanced_full_comparison_table.csv", rows)
    write_csv(ROOT / "splice_kmer_balanced_full_comparison_table_summary.csv", summary)
    write_csv(ROOT / "splice_kmer_balanced_full_comparison_table_paired.csv", paired_rows)
    print(write_markdown(summary, paired_rows, missing))


if __name__ == "__main__":
    main()
