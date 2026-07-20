import csv
from pathlib import Path


ROOT = Path("results")
TAGS = [
    ("raw_clipped", "splice_sites_all_larger_estimator_quality"),
    ("quantile_q08_12", "splice_sites_all_larger_estimator_quality_quantile_q08_12"),
    ("quantile_q075_125", "splice_sites_all_larger_estimator_quality_quantile_q075_125"),
    ("quantile_q09_11", "splice_sites_all_larger_estimator_quality_quantile_q09_11"),
]


def read_csv(path):
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path, rows):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def collect_rows():
    rows = []
    for tag, prefix in TAGS:
        label_path = ROOT / f"{prefix}_score_by_label.csv"
        pred_path = ROOT / f"{prefix}_prediction_summary.csv"
        corr_path = ROOT / f"{prefix}_score_kmer_corr.csv"
        if not label_path.exists() or not pred_path.exists() or not corr_path.exists():
            continue
        test_labels = [row for row in read_csv(label_path) if row["split"] == "test"]
        pred_rows = read_csv(pred_path)
        corr_rows = [row for row in read_csv(corr_path) if row["split"] == "test"]
        rows.append(
            {
                "tag": tag,
                "test_score_mean_avg": sum(float(row["score_mean"]) for row in test_labels) / len(test_labels),
                "test_score_std_avg": sum(float(row["score_std"]) for row in test_labels) / len(test_labels),
                "test_clip_max_rate_avg": sum(float(row["clip_max_rate"]) for row in test_labels) / len(test_labels),
                "baseline_score_error_pearson": next(float(row["score_error_pearson"]) for row in pred_rows if row["method"] == "baseline_lora"),
                "germ_bo_score_error_pearson": next(float(row["score_error_pearson"]) for row in pred_rows if row["method"] == "germ_bo_w64k3"),
                "baseline_score_margin_pearson": next(float(row["score_margin_pearson"]) for row in pred_rows if row["method"] == "baseline_lora"),
                "germ_bo_score_margin_pearson": next(float(row["score_margin_pearson"]) for row in pred_rows if row["method"] == "germ_bo_w64k3"),
                "test_entropy3_pearson": next(float(row["pearson"]) for row in corr_rows if row["feature"] == "entropy3"),
                "test_gc_pearson": next(float(row["pearson"]) for row in corr_rows if row["feature"] == "gc"),
            }
        )
    return rows


def write_markdown(rows):
    path = ROOT / "splice_sites_all_quantile_estimator_quality_summary.md"
    with path.open("w", encoding="utf-8") as handle:
        handle.write("# Quantile-Normalized Estimator Quality Summary\n\n")
        handle.write(
            "Goal: compare raw clipped score with train-quantile normalized score ranges before running new training.\n\n"
        )
        handle.write("| Tag | Test Score Std Avg | Test Clip-Max Rate Avg | Baseline Score-Error r | GERM-BO Score-Error r | Entropy3 r | GC r |\n")
        handle.write("|---|---:|---:|---:|---:|---:|---:|\n")
        for row in rows:
            handle.write(
                f"| {row['tag']} | {row['test_score_std_avg']:.4f} | {row['test_clip_max_rate_avg']:.1%} | "
                f"{row['baseline_score_error_pearson']:+.4f} | {row['germ_bo_score_error_pearson']:+.4f} | "
                f"{row['test_entropy3_pearson']:+.4f} | {row['test_gc_pearson']:+.4f} |\n"
            )
        handle.write("\nInterpretation: a usable estimator should avoid saturation and produce non-trivial sample-level variation. "
                     "Score-error correlation is diagnostic only because predictions were produced by already-trained raw-score models.\n")
    return path


def main():
    rows = collect_rows()
    if not rows:
        raise RuntimeError("No estimator quality rows found.")
    write_csv(ROOT / "splice_sites_all_quantile_estimator_quality_summary.csv", rows)
    print(write_markdown(rows))


if __name__ == "__main__":
    main()
