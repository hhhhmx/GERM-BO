import csv
import argparse
import math
import re
from collections import Counter, defaultdict
from itertools import product
from pathlib import Path


ROOT = Path("results")
SEEDS = [45, 46, 47, 48, 49]
BORDER_SCORE_PATTERN = re.compile(r"(?:^|[;,\s])border_score=([-+]?(?:\d+(?:\.\d*)?|\.\d+))")
KMERS = ["".join(item) for item in product("ACGT", repeat=3)]


def read_csv(path):
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def border_score(metadata):
    match = BORDER_SCORE_PATTERN.search(metadata or "")
    return float(match.group(1)) if match else 1.0


def pearson(xs, ys):
    if len(xs) < 2:
        return 0.0
    mean_x = sum(xs) / len(xs)
    mean_y = sum(ys) / len(ys)
    num = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
    den_x = sum((x - mean_x) ** 2 for x in xs) ** 0.5
    den_y = sum((y - mean_y) ** 2 for y in ys) ** 0.5
    return num / max(den_x * den_y, 1e-12)


def ranks(values):
    indexed = sorted(enumerate(values), key=lambda item: item[1])
    out = [0.0] * len(values)
    i = 0
    while i < len(indexed):
        j = i
        while j + 1 < len(indexed) and indexed[j + 1][1] == indexed[i][1]:
            j += 1
        rank = (i + j) / 2 + 1
        for k in range(i, j + 1):
            out[indexed[k][0]] = rank
        i = j + 1
    return out


def spearman(xs, ys):
    return pearson(ranks(xs), ranks(ys))


def mean(values):
    return sum(values) / max(len(values), 1)


def std(values):
    if len(values) <= 1:
        return 0.0
    m = mean(values)
    return (sum((value - m) ** 2 for value in values) / (len(values) - 1)) ** 0.5


def quantile(values, q):
    if not values:
        return 0.0
    ordered = sorted(values)
    index = min(len(ordered) - 1, max(0, int(round(q * (len(ordered) - 1)))))
    return ordered[index]


def kmer_features(sequence):
    sequence = sequence.upper()
    counts = Counter(sequence[index : index + 3] for index in range(max(len(sequence) - 2, 0)))
    total = sum(counts.values())
    if total == 0:
        return {"gc": 0.0, "entropy3": 0.0, "max3": 0.0, "cpg": 0.0, "gt_ag_center": 0.0}
    probs = [count / total for count in counts.values()]
    entropy = -sum(prob * math.log2(prob) for prob in probs)
    center = len(sequence) // 2
    center_window = sequence[max(0, center - 32) : min(len(sequence), center + 32)]
    dinucs = max(len(center_window) - 1, 1)
    gt_ag = sum(1 for idx in range(dinucs) if center_window[idx : idx + 2] in {"GT", "AG"}) / dinucs
    return {
        "gc": (sequence.count("G") + sequence.count("C")) / max(len(sequence), 1),
        "entropy3": entropy,
        "max3": max(probs),
        "cpg": sequence.count("CG") / max(len(sequence) - 1, 1),
        "gt_ag_center": gt_ag,
    }


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--split-dir", default="data/benchmarks/splice_sites_all_larger_center_w64_k3_t10_s3")
    parser.add_argument("--output-prefix", default="results/splice_sites_all_larger_estimator_quality")
    return parser.parse_args()


def load_split_rows(split_dir):
    rows = []
    for split in ["train", "val", "test"]:
        for row in read_csv(split_dir / f"{split}.csv"):
            features = kmer_features(row["sequence"])
            rows.append(
                {
                    "split": split,
                    "id": row["id"],
                    "raw_label": int(row["label"]),
                    "score": border_score(row["metadata"]),
                    **features,
                }
            )
    return rows


def summarize_score_by_label(rows):
    out = []
    for split in ["train", "val", "test"]:
        split_rows = [row for row in rows if row["split"] == split]
        for label in sorted({row["raw_label"] for row in split_rows}):
            values = [row["score"] for row in split_rows if row["raw_label"] == label]
            out.append(
                {
                    "split": split,
                    "label": label,
                    "n": len(values),
                    "score_mean": mean(values),
                    "score_std": std(values),
                    "score_min": min(values),
                    "score_q25": quantile(values, 0.25),
                    "score_median": quantile(values, 0.50),
                    "score_q75": quantile(values, 0.75),
                    "score_max": max(values),
                    "clip_max_rate": sum(1 for value in values if value >= 1.499999) / len(values),
                }
            )
    return out


def score_kmer_correlations(rows):
    out = []
    for split in ["train", "val", "test"]:
        split_rows = [row for row in rows if row["split"] == split]
        scores = [row["score"] for row in split_rows]
        for feature in ["gc", "entropy3", "max3", "cpg", "gt_ag_center"]:
            values = [row[feature] for row in split_rows]
            out.append(
                {
                    "split": split,
                    "feature": feature,
                    "pearson": pearson(scores, values),
                    "spearman": spearman(scores, values),
                }
            )
    return out


def prediction_quality(split_by_id):
    rows = []
    per_sample = defaultdict(list)
    for method, prefix in [
        ("baseline_lora", "splice_sites_all_larger_w64k3_heldout_baseline_lora_seed{seed}_predictions.csv"),
        ("germ_bo_w64k3", "splice_sites_all_larger_w64k3_heldout_germ_bo_center_w64_k3_t10_s3_seed{seed}_predictions.csv"),
    ]:
        for seed in SEEDS:
            for pred in read_csv(ROOT / prefix.format(seed=seed)):
                item = split_by_id[pred["id"]]
                correct = int(pred["true_label"]) == int(pred["pred_label"])
                confidence = max(float(pred[f"prob_{idx}"]) for idx in range(3))
                margin_values = sorted([float(pred[f"prob_{idx}"]) for idx in range(3)], reverse=True)
                margin = margin_values[0] - margin_values[1]
                row = {
                    "method": method,
                    "seed": seed,
                    "id": pred["id"],
                    "true_label": int(pred["true_label"]),
                    "pred_label": int(pred["pred_label"]),
                    "correct": int(correct),
                    "confidence": confidence,
                    "margin": margin,
                    "score": item["score"],
                    "gc": item["gc"],
                    "entropy3": item["entropy3"],
                    "max3": item["max3"],
                    "cpg": item["cpg"],
                    "gt_ag_center": item["gt_ag_center"],
                }
                rows.append(row)
                per_sample[(seed, pred["id"])].append(row)
    return rows


def summarize_prediction_rows(rows):
    out = []
    for method in sorted({row["method"] for row in rows}):
        group = [row for row in rows if row["method"] == method]
        scores = [row["score"] for row in group]
        errors = [1 - row["correct"] for row in group]
        margins = [row["margin"] for row in group]
        confs = [row["confidence"] for row in group]
        out.append(
            {
                "method": method,
                "n_predictions": len(group),
                "accuracy": mean([row["correct"] for row in group]),
                "score_error_pearson": pearson(scores, errors),
                "score_error_spearman": spearman(scores, errors),
                "score_confidence_pearson": pearson(scores, confs),
                "score_margin_pearson": pearson(scores, margins),
                "score_mean_correct": mean([row["score"] for row in group if row["correct"]]),
                "score_mean_wrong": mean([row["score"] for row in group if not row["correct"]]),
            }
        )
    return out


def score_bins(rows):
    out = []
    for method in sorted({row["method"] for row in rows}):
        group = [row for row in rows if row["method"] == method]
        score_values = sorted({row["score"] for row in group})
        q1 = quantile(score_values, 0.25)
        q2 = quantile(score_values, 0.50)
        q3 = quantile(score_values, 0.75)
        bins = [
            ("low", lambda value: value <= q1),
            ("mid_low", lambda value: q1 < value <= q2),
            ("mid_high", lambda value: q2 < value <= q3),
            ("high", lambda value: value > q3),
        ]
        for name, predicate in bins:
            subset = [row for row in group if predicate(row["score"])]
            out.append(
                {
                    "method": method,
                    "score_bin": name,
                    "n_predictions": len(subset),
                    "score_min": min([row["score"] for row in subset]) if subset else 0.0,
                    "score_max": max([row["score"] for row in subset]) if subset else 0.0,
                    "accuracy": mean([row["correct"] for row in subset]),
                    "confidence": mean([row["confidence"] for row in subset]),
                    "margin": mean([row["margin"] for row in subset]),
                }
            )
    return out


def write_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(label_rows, corr_rows, pred_summary, bin_rows, output_prefix, split_dir):
    path = output_prefix.with_suffix(".md")
    with path.open("w", encoding="utf-8") as handle:
        handle.write("# Splice Sites All Larger Estimator-Quality Analysis\n\n")
        handle.write(
            "Goal: diagnose why the non-oracle metadata estimator `center-JSD w64/k3/top10/scale3` "
            "does not produce stable GERM-BO gains on the external splice-site benchmark. "
            "This analysis uses no additional training.\n\n"
        )
        handle.write(f"Split directory: `{split_dir}`\n\n")
        handle.write("## Score Distribution by Raw Class\n\n")
        handle.write("| Split | Label | N | Mean | Std | Q25 | Median | Q75 | Max-Clip Rate |\n")
        handle.write("|---|---:|---:|---:|---:|---:|---:|---:|---:|\n")
        for row in label_rows:
            handle.write(
                f"| {row['split']} | {row['label']} | {row['n']} | {row['score_mean']:.4f} | "
                f"{row['score_std']:.4f} | {row['score_q25']:.4f} | {row['score_median']:.4f} | "
                f"{row['score_q75']:.4f} | {row['clip_max_rate']:.1%} |\n"
            )
        handle.write("\n## Score vs Sequence-Composition Correlations\n\n")
        handle.write("| Split | Feature | Pearson | Spearman |\n")
        handle.write("|---|---|---:|---:|\n")
        for row in corr_rows:
            handle.write(f"| {row['split']} | {row['feature']} | {row['pearson']:+.4f} | {row['spearman']:+.4f} |\n")
        handle.write("\n## Score vs Prediction Quality\n\n")
        handle.write("| Method | Accuracy | Score-Error r | Score-Error rho | Score-Confidence r | Score-Margin r | Score Correct | Score Wrong |\n")
        handle.write("|---|---:|---:|---:|---:|---:|---:|---:|\n")
        for row in pred_summary:
            handle.write(
                f"| {row['method']} | {row['accuracy']:.4f} | {row['score_error_pearson']:+.4f} | "
                f"{row['score_error_spearman']:+.4f} | {row['score_confidence_pearson']:+.4f} | "
                f"{row['score_margin_pearson']:+.4f} | {row['score_mean_correct']:.4f} | "
                f"{row['score_mean_wrong']:.4f} |\n"
            )
        handle.write("\n## Accuracy by Score Quantile Bin\n\n")
        handle.write("| Method | Score Bin | N Predictions | Score Range | Accuracy | Confidence | Margin |\n")
        handle.write("|---|---|---:|---|---:|---:|---:|\n")
        for row in bin_rows:
            handle.write(
                f"| {row['method']} | {row['score_bin']} | {row['n_predictions']} | "
                f"{row['score_min']:.4f}-{row['score_max']:.4f} | {row['accuracy']:.4f} | "
                f"{row['confidence']:.4f} | {row['margin']:.4f} |\n"
            )
        handle.write("\n## Interpretation\n\n")
        handle.write(
            "- If score is useful as a border-difficulty estimator, it should show a meaningful relationship "
            "with error rate, confidence/margin, or class-specific difficulty.\n"
        )
        handle.write(
            "- If score is mostly saturated at the clip maximum or highly correlated with simple k-mer composition, "
            "it is likely acting as a weak composition proxy rather than a precise boundary-quality signal.\n"
        )
        handle.write(
            "- This analysis should be read together with the full comparison table, where simple 3-mer Logistic "
            "Regression and Linear SVM outperform DNABERT-2 LoRA/GERM-BO on this split.\n"
        )
    return path


def main():
    args = parse_args()
    split_dir = Path(args.split_dir)
    output_prefix = Path(args.output_prefix)
    split_rows = load_split_rows(split_dir)
    split_by_id = {row["id"]: row for row in split_rows if row["split"] == "test"}
    label_rows = summarize_score_by_label(split_rows)
    corr_rows = score_kmer_correlations(split_rows)
    pred_rows = prediction_quality(split_by_id)
    pred_summary = summarize_prediction_rows(pred_rows)
    bin_rows = score_bins(pred_rows)
    write_csv(Path(str(output_prefix) + "_score_by_label.csv"), label_rows)
    write_csv(Path(str(output_prefix) + "_score_kmer_corr.csv"), corr_rows)
    write_csv(Path(str(output_prefix) + "_prediction_summary.csv"), pred_summary)
    write_csv(Path(str(output_prefix) + "_score_bins.csv"), bin_rows)
    print(write_markdown(label_rows, corr_rows, pred_summary, bin_rows, output_prefix, split_dir))


if __name__ == "__main__":
    main()
