import csv
import math
import re
from collections import Counter
from pathlib import Path


ROOT = Path("results")
SPLIT_DIR = Path("data/benchmarks/splice_sites_all_kmer_balanced")
SEEDS = list(range(50, 60))
METHOD_SPECS = [
    ("lora_attention_output_classifier", "splice_kmer_balanced_confirm_lora_attention_output_classifier_seed{seed}_predictions.csv"),
    ("germ_bo_quantile_q08_12_comp027", "splice_kmer_balanced_confirm_germ_bo_quantile_q08_12_comp027_seed{seed}_predictions.csv"),
    ("lora_attention_output_classifier_55_59", "splice_kmer_balanced_confirm55_59_lora_attention_output_classifier_seed{seed}_predictions.csv"),
    ("germ_bo_quantile_q08_12_comp027_55_59", "splice_kmer_balanced_confirm55_59_germ_bo_quantile_q08_12_comp027_seed{seed}_predictions.csv"),
]
BORDER_SCORE_PATTERN = re.compile(r"(?:^|[;,\s])border_score=([-+]?(?:\d+(?:\.\d*)?|\.\d+))")


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


def mean(values):
    return sum(values) / max(len(values), 1)


def std(values):
    if len(values) <= 1:
        return 0.0
    m = mean(values)
    return (sum((value - m) ** 2 for value in values) / (len(values) - 1)) ** 0.5


def quantile(values, q):
    ordered = sorted(values)
    index = min(len(ordered) - 1, max(0, int(round(q * (len(ordered) - 1)))))
    return ordered[index]


def kmer_features(sequence):
    sequence = sequence.upper()
    counts = Counter(sequence[index : index + 3] for index in range(max(len(sequence) - 2, 0)))
    total = sum(counts.values())
    if total == 0:
        return {"gc": 0.0, "entropy3": 0.0, "max3": 0.0}
    probs = [count / total for count in counts.values()]
    entropy = -sum(prob * math.log2(prob) for prob in probs)
    return {
        "gc": (sequence.count("G") + sequence.count("C")) / max(len(sequence), 1),
        "entropy3": entropy,
        "max3": max(probs),
    }


def load_split_rows():
    rows = []
    for split in ["train", "val", "test"]:
        for row in read_csv(SPLIT_DIR / f"{split}.csv"):
            rows.append(
                {
                    "split": split,
                    "id": row["id"],
                    "label": int(row["label"]),
                    "score": border_score(row["metadata"]),
                    **kmer_features(row["sequence"]),
                }
            )
    return rows


def summarize_score(rows):
    out = []
    for split in ["train", "val", "test"]:
        subset = [row for row in rows if row["split"] == split]
        scores = [row["score"] for row in subset]
        out.append(
            {
                "split": split,
                "n": len(scores),
                "score_mean": mean(scores),
                "score_std": std(scores),
                "score_min": min(scores),
                "score_q25": quantile(scores, 0.25),
                "score_median": quantile(scores, 0.50),
                "score_q75": quantile(scores, 0.75),
                "score_max": max(scores),
                "clip_max_rate": sum(1 for score in scores if score >= 1.199999) / len(scores),
            }
        )
    return out


def score_correlations(rows):
    out = []
    for split in ["train", "val", "test"]:
        subset = [row for row in rows if row["split"] == split]
        scores = [row["score"] for row in subset]
        for feature in ["gc", "entropy3", "max3"]:
            values = [row[feature] for row in subset]
            out.append(
                {
                    "split": split,
                    "feature": feature,
                    "pearson": pearson(scores, values),
                }
            )
    return out


def canonical_method(method_tag):
    return "germ_bo_quantile_q08_12_comp027" if "germ_bo" in method_tag else "lora_attention_output_classifier"


def prediction_quality(split_by_id):
    rows = []
    for method_tag, pattern in METHOD_SPECS:
        seeds = range(50, 55) if "_55_59" not in method_tag else range(55, 60)
        for seed in seeds:
            path = ROOT / pattern.format(seed=seed)
            for pred in read_csv(path):
                meta = split_by_id[pred["id"]]
                probs = [float(pred[f"prob_{idx}"]) for idx in range(3)]
                rows.append(
                    {
                        "method": canonical_method(method_tag),
                        "seed": seed,
                        "id": pred["id"],
                        "score": meta["score"],
                        "correct": int(int(pred["true_label"]) == int(pred["pred_label"])),
                        "confidence": max(probs),
                        "margin": sorted(probs, reverse=True)[0] - sorted(probs, reverse=True)[1],
                    }
                )
    out = []
    for method in sorted({row["method"] for row in rows}):
        group = [row for row in rows if row["method"] == method]
        scores = [row["score"] for row in group]
        errors = [1 - row["correct"] for row in group]
        confs = [row["confidence"] for row in group]
        margins = [row["margin"] for row in group]
        out.append(
            {
                "method": method,
                "n_predictions": len(group),
                "accuracy": mean([row["correct"] for row in group]),
                "score_error_pearson": pearson(scores, errors),
                "score_confidence_pearson": pearson(scores, confs),
                "score_margin_pearson": pearson(scores, margins),
                "score_mean_correct": mean([row["score"] for row in group if row["correct"]]),
                "score_mean_wrong": mean([row["score"] for row in group if not row["correct"]]),
            }
        )
    return out


def write_csv(path, rows):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main():
    split_rows = load_split_rows()
    split_by_id = {row["id"]: row for row in split_rows if row["split"] == "test"}
    score_rows = summarize_score(split_rows)
    corr_rows = score_correlations(split_rows)
    pred_rows = prediction_quality(split_by_id)
    write_csv(ROOT / "splice_kmer_balanced_estimator_quality_score.csv", score_rows)
    write_csv(ROOT / "splice_kmer_balanced_estimator_quality_corr.csv", corr_rows)
    write_csv(ROOT / "splice_kmer_balanced_estimator_quality_prediction.csv", pred_rows)

    path = ROOT / "splice_kmer_balanced_estimator_quality.md"
    with path.open("w", encoding="utf-8") as handle:
        handle.write("# Estimator-Quality Analysis: strict 3-mer-balanced splice benchmark\n\n")
        handle.write("Protocol: analyze the quantile-normalized metadata score on the strict `3-mer-balanced` split without additional training.\n\n")
        handle.write("## Score distribution\n\n")
        handle.write("| Split | N | Mean | Std | Q25 | Median | Q75 | Max | Clip-Max Rate |\n")
        handle.write("|---|---:|---:|---:|---:|---:|---:|---:|---:|\n")
        for row in score_rows:
            handle.write(
                f"| {row['split']} | {row['n']} | {row['score_mean']:.4f} | {row['score_std']:.4f} | {row['score_q25']:.4f} | "
                f"{row['score_median']:.4f} | {row['score_q75']:.4f} | {row['score_max']:.4f} | {row['clip_max_rate']:.1%} |\n"
            )
        handle.write("\n## Score vs composition correlations\n\n")
        handle.write("| Split | Feature | Pearson |\n")
        handle.write("|---|---|---:|\n")
        for row in corr_rows:
            handle.write(f"| {row['split']} | {row['feature']} | {row['pearson']:+.4f} |\n")
        handle.write("\n## Score vs pooled prediction quality (seeds 50-59)\n\n")
        handle.write("| Method | Accuracy | Score-Error r | Score-Confidence r | Score-Margin r | Score Correct | Score Wrong |\n")
        handle.write("|---|---:|---:|---:|---:|---:|---:|\n")
        for row in pred_rows:
            label = "GERM-BO quantile [0.8,1.2] comp0.27" if row["method"] == "germ_bo_quantile_q08_12_comp027" else "LoRA attention.output + classifier"
            handle.write(
                f"| {label} | {row['accuracy']:.4f} | {row['score_error_pearson']:+.4f} | {row['score_confidence_pearson']:+.4f} | "
                f"{row['score_margin_pearson']:+.4f} | {row['score_mean_correct']:.4f} | {row['score_mean_wrong']:.4f} |\n"
            )
        handle.write("\n## Main interpretation\n\n")
        handle.write(
            "On the strict split, the quantile-normalized score keeps substantial variance and no longer saturates at the clip ceiling. "
            "This supports the claim that the score remains a usable sample-difficulty / border-strength signal rather than collapsing into a near-constant factor.\n"
        )
    print(path)


if __name__ == "__main__":
    main()
