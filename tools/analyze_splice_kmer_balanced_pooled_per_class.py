import csv
from pathlib import Path


ROOT = Path("results")
SEEDS = list(range(50, 60))
METHODS = [
    ("lora_attention_output_classifier", "LoRA attention.output + classifier", [
        "splice_kmer_balanced_confirm_lora_attention_output_classifier_seed{seed}_predictions.csv",
        "splice_kmer_balanced_confirm55_59_lora_attention_output_classifier_seed{seed}_predictions.csv",
    ]),
    ("germ_bo_quantile_q08_12_comp027", "GERM-BO quantile [0.8,1.2] comp0.27", [
        "splice_kmer_balanced_confirm_germ_bo_quantile_q08_12_comp027_seed{seed}_predictions.csv",
        "splice_kmer_balanced_confirm55_59_germ_bo_quantile_q08_12_comp027_seed{seed}_predictions.csv",
    ]),
]


def read_csv(path):
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def get_prediction_path(patterns, seed):
    for pattern in patterns:
        path = ROOT / pattern.format(seed=seed)
        if path.exists():
            return path
    raise FileNotFoundError(seed)


def per_class_metrics(rows):
    labels = [0, 1, 2]
    out = []
    for class_label in labels:
        tp = sum(1 for row in rows if int(row["true_label"]) == class_label and int(row["pred_label"]) == class_label)
        fp = sum(1 for row in rows if int(row["true_label"]) != class_label and int(row["pred_label"]) == class_label)
        fn = sum(1 for row in rows if int(row["true_label"]) == class_label and int(row["pred_label"]) != class_label)
        support = sum(1 for row in rows if int(row["true_label"]) == class_label)
        predicted = sum(1 for row in rows if int(row["pred_label"]) == class_label)
        precision = tp / max(tp + fp, 1)
        recall = tp / max(tp + fn, 1)
        f1 = 2 * precision * recall / max(precision + recall, 1e-12)
        out.append(
            {
                "class_label": class_label,
                "precision": precision,
                "recall": recall,
                "f1": f1,
                "support": support,
                "predicted": predicted,
            }
        )
    return out


def confusion(rows):
    labels = [0, 1, 2]
    matrix = {true_label: {pred_label: 0 for pred_label in labels} for true_label in labels}
    for row in rows:
        matrix[int(row["true_label"])][int(row["pred_label"])] += 1
    return matrix


def main():
    per_class_rows = []
    confusions = {}
    for method_tag, method_label, patterns in METHODS:
        matrices = []
        pooled_metrics = []
        for seed in SEEDS:
            rows = read_csv(get_prediction_path(patterns, seed))
            matrices.append(confusion(rows))
            for item in per_class_metrics(rows):
                pooled_metrics.append({"method": method_tag, "seed": seed, **item})
        confusions[method_tag] = matrices
        for class_label in [0, 1, 2]:
            group = [row for row in pooled_metrics if row["class_label"] == class_label]
            per_class_rows.append(
                {
                    "method": method_tag,
                    "label": method_label,
                    "class_label": class_label,
                    "precision_mean": sum(item["precision"] for item in group) / len(group),
                    "recall_mean": sum(item["recall"] for item in group) / len(group),
                    "f1_mean": sum(item["f1"] for item in group) / len(group),
                    "predicted_mean": sum(item["predicted"] for item in group) / len(group),
                    "support_mean": sum(item["support"] for item in group) / len(group),
                }
            )

    by_method_class = {(row["method"], row["class_label"]): row for row in per_class_rows}
    delta_rows = []
    for class_label in [0, 1, 2]:
        germ = by_method_class[("germ_bo_quantile_q08_12_comp027", class_label)]
        lora = by_method_class[("lora_attention_output_classifier", class_label)]
        delta_rows.append(
            {
                "class_label": class_label,
                "precision_delta": germ["precision_mean"] - lora["precision_mean"],
                "recall_delta": germ["recall_mean"] - lora["recall_mean"],
                "f1_delta": germ["f1_mean"] - lora["f1_mean"],
                "predicted_delta": germ["predicted_mean"] - lora["predicted_mean"],
            }
        )

    def write_csv(path, rows):
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)

    write_csv(ROOT / "splice_kmer_balanced_pooled_per_class_summary.csv", per_class_rows)
    write_csv(ROOT / "splice_kmer_balanced_pooled_per_class_delta.csv", delta_rows)

    path = ROOT / "splice_kmer_balanced_pooled_per_class_analysis.md"
    with path.open("w", encoding="utf-8") as handle:
        handle.write("# Pooled Per-class and Confusion Analysis: strict 3-mer-balanced splice benchmark\n\n")
        handle.write("Protocol: average over pooled held-out seeds `50-59` for the two main DNABERT-2-based methods.\n\n")
        handle.write("## Per-class mean metrics\n\n")
        handle.write("| Method | Class | Precision | Recall | F1 | Mean predicted count |\n")
        handle.write("|---|---:|---:|---:|---:|---:|\n")
        for row in per_class_rows:
            handle.write(
                f"| {row['label']} | {row['class_label']} | {row['precision_mean']:.4f} | {row['recall_mean']:.4f} | "
                f"{row['f1_mean']:.4f} | {row['predicted_mean']:.1f} |\n"
            )
        handle.write("\n## GERM-BO minus LoRA per-class delta\n\n")
        handle.write("| Class | Precision Delta | Recall Delta | F1 Delta | Predicted Count Delta |\n")
        handle.write("|---:|---:|---:|---:|---:|\n")
        for row in delta_rows:
            handle.write(
                f"| {row['class_label']} | {row['precision_delta']:+.4f} | {row['recall_delta']:+.4f} | "
                f"{row['f1_delta']:+.4f} | {row['predicted_delta']:+.1f} |\n"
            )
        handle.write("\n## Mean confusion matrix over pooled seeds\n\n")
        for method_tag, method_label, _ in METHODS:
            handle.write(f"### {method_label}\n\n")
            handle.write("| True \\\\ Pred | 0 | 1 | 2 |\n")
            handle.write("|---:|---:|---:|---:|\n")
            matrix = {i: {j: 0.0 for j in [0, 1, 2]} for i in [0, 1, 2]}
            for seed_matrix in confusions[method_tag]:
                for i in [0, 1, 2]:
                    for j in [0, 1, 2]:
                        matrix[i][j] += seed_matrix[i][j]
            for i in [0, 1, 2]:
                for j in [0, 1, 2]:
                    matrix[i][j] /= len(confusions[method_tag])
                handle.write(f"| {i} | {matrix[i][0]:.1f} | {matrix[i][1]:.1f} | {matrix[i][2]:.1f} |\n")
            handle.write("\n")
        handle.write("## Main interpretation\n\n")
        handle.write(
            "Pooled over seeds `50-59`, GERM-BO still improves class balance relative to the strong LoRA baseline, but the additional seed block weakens the stability of class-0/class-1 gains. "
            "The pooled confusion matrices should therefore be read as support for a positive but not perfectly stable external effect.\n"
        )
    print(path)


if __name__ == "__main__":
    main()
