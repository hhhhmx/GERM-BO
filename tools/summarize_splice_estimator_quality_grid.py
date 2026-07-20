import csv
import re
from pathlib import Path


ROOT = Path("results")
TAG_PATTERN = re.compile(
    r"splice_estimator_quality_grid_(w(?P<window>\d+)_k(?P<kmer>\d+)_t(?P<top>\d+)_"
    r"(?P<normalization>train_minmax|train_quantile)_r(?P<min>\d+)_(?P<max>\d+))_score_by_label\.csv"
)


def read_csv(path):
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path, rows):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def parse_decimal(tag_value):
    if len(tag_value) == 2:
        return float(f"{tag_value[0]}.{tag_value[1]}")
    if len(tag_value) == 3:
        return float(f"{tag_value[0]}.{tag_value[1:]}")
    return float(tag_value)


def collect():
    rows = []
    for label_path in sorted(ROOT.glob("splice_estimator_quality_grid_*_score_by_label.csv")):
        match = TAG_PATTERN.match(label_path.name)
        if not match:
            continue
        tag = match.group(1)
        pred_path = ROOT / f"splice_estimator_quality_grid_{tag}_prediction_summary.csv"
        corr_path = ROOT / f"splice_estimator_quality_grid_{tag}_score_kmer_corr.csv"
        if not pred_path.exists() or not corr_path.exists():
            continue

        label_rows = [row for row in read_csv(label_path) if row["split"] == "test"]
        pred_rows = read_csv(pred_path)
        corr_rows = [row for row in read_csv(corr_path) if row["split"] == "test"]
        baseline = next(row for row in pred_rows if row["method"] == "baseline_lora")
        germ_bo = next(row for row in pred_rows if row["method"] == "germ_bo_w64k3")
        entropy = next(row for row in corr_rows if row["feature"] == "entropy3")
        gc = next(row for row in corr_rows if row["feature"] == "gc")
        max3 = next(row for row in corr_rows if row["feature"] == "max3")

        score_std_avg = sum(float(row["score_std"]) for row in label_rows) / len(label_rows)
        clip_rate_avg = sum(float(row["clip_max_rate"]) for row in label_rows) / len(label_rows)
        label_means = [float(row["score_mean"]) for row in label_rows]
        class_spread = max(label_means) - min(label_means)
        entropy_abs = abs(float(entropy["pearson"]))
        gc_abs = abs(float(gc["pearson"]))
        max3_abs = abs(float(max3["pearson"]))
        error_signal = max(abs(float(baseline["score_error_pearson"])), abs(float(germ_bo["score_error_pearson"])))
        margin_signal = max(abs(float(baseline["score_margin_pearson"])), abs(float(germ_bo["score_margin_pearson"])))
        composition_penalty = max(entropy_abs, gc_abs, max3_abs)
        # Ranking heuristic: prefer variation and prediction-quality association, penalize clipping and pure composition proxy.
        quality_score = score_std_avg + 0.5 * error_signal + 0.5 * margin_signal - 0.5 * clip_rate_avg - 0.25 * composition_penalty

        rows.append(
            {
                "tag": tag,
                "window": int(match.group("window")),
                "kmer": int(match.group("kmer")),
                "top_ratio": parse_decimal(match.group("top")),
                "normalization": match.group("normalization"),
                "score_min": parse_decimal(match.group("min")),
                "score_max": parse_decimal(match.group("max")),
                "test_score_std_avg": score_std_avg,
                "test_clip_max_rate_avg": clip_rate_avg,
                "test_class_score_spread": class_spread,
                "baseline_score_error_pearson": float(baseline["score_error_pearson"]),
                "germ_bo_score_error_pearson": float(germ_bo["score_error_pearson"]),
                "baseline_score_margin_pearson": float(baseline["score_margin_pearson"]),
                "germ_bo_score_margin_pearson": float(germ_bo["score_margin_pearson"]),
                "test_entropy3_pearson": float(entropy["pearson"]),
                "test_gc_pearson": float(gc["pearson"]),
                "test_max3_pearson": float(max3["pearson"]),
                "quality_score": quality_score,
            }
        )
    rows.sort(key=lambda row: row["quality_score"], reverse=True)
    return rows


def write_markdown(rows):
    path = ROOT / "splice_estimator_quality_grid_summary.md"
    with path.open("w", encoding="utf-8") as handle:
        handle.write("# Splice Estimator-Quality Grid Summary\n\n")
        handle.write(
            "Estimator-only grid. No model training was run. Ranking heuristic favors score variation and "
            "prediction-quality association, while penalizing score clipping and strong composition-proxy behavior.\n\n"
        )
        handle.write("## Top 20 Estimators\n\n")
        handle.write("| Rank | Tag | Score Std | Clip Rate | Error r Base | Error r GERM | Margin r Base | Entropy r | GC r | Quality |\n")
        handle.write("|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|\n")
        for index, row in enumerate(rows[:20], start=1):
            handle.write(
                f"| {index} | {row['tag']} | {row['test_score_std_avg']:.4f} | "
                f"{row['test_clip_max_rate_avg']:.1%} | {row['baseline_score_error_pearson']:+.4f} | "
                f"{row['germ_bo_score_error_pearson']:+.4f} | {row['baseline_score_margin_pearson']:+.4f} | "
                f"{row['test_entropy3_pearson']:+.4f} | {row['test_gc_pearson']:+.4f} | "
                f"{row['quality_score']:+.4f} |\n"
            )
        handle.write("\n## Recommended Candidates\n\n")
        for row in rows[:5]:
            handle.write(
                f"- `{row['tag']}`: std={row['test_score_std_avg']:.4f}, clip={row['test_clip_max_rate_avg']:.1%}, "
                f"baseline error r={row['baseline_score_error_pearson']:+.4f}, entropy r={row['test_entropy3_pearson']:+.4f}.\n"
            )
    return path


def main():
    rows = collect()
    if not rows:
        raise RuntimeError("No estimator-quality grid rows found.")
    write_csv(ROOT / "splice_estimator_quality_grid_summary.csv", rows)
    print(write_markdown(rows))


if __name__ == "__main__":
    main()
