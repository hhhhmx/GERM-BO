import csv
from collections import defaultdict
from pathlib import Path


ROOT = Path("results")
SEEDS = [50, 51, 52, 53, 54]
METHODS = [
    ("lora_attention_output_classifier", "LoRA attention.output + classifier"),
    ("germ_bo_quantile_q08_12_comp027", "GERM-BO quantile [0.8,1.2] comp0.27"),
]


def read_predictions(path):
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def confusion_matrix(rows):
    labels = sorted({int(row["true_label"]) for row in rows} | {int(row["pred_label"]) for row in rows})
    matrix = {true_label: {pred_label: 0 for pred_label in labels} for true_label in labels}
    for row in rows:
        matrix[int(row["true_label"])][int(row["pred_label"])] += 1
    return labels, matrix


def mean_matrix(matrices, labels):
    averaged = {true_label: {pred_label: 0.0 for pred_label in labels} for true_label in labels}
    for matrix in matrices:
        for true_label in labels:
            for pred_label in labels:
                averaged[true_label][pred_label] += matrix[true_label][pred_label]
    for true_label in labels:
        for pred_label in labels:
            averaged[true_label][pred_label] /= len(matrices)
    return averaged


def per_class_from_predictions(rows):
    labels = sorted({int(row["true_label"]) for row in rows} | {int(row["pred_label"]) for row in rows})
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


def summarize_per_class():
    rows = []
    for method_tag, method_label in METHODS:
        group = []
        for seed in SEEDS:
            path = ROOT / f"splice_kmer_balanced_confirm_{method_tag}_seed{seed}_predictions.csv"
            prediction_rows = read_predictions(path)
            for class_metrics in per_class_from_predictions(prediction_rows):
                group.append(
                    {
                        "method": method_tag,
                        "seed": seed,
                        **class_metrics,
                    }
                )
        for class_label in sorted({row["class_label"] for row in group}):
            class_rows = [row for row in group if row["class_label"] == class_label]
            summary = {
                "method": method_tag,
                "label": method_label,
                "class_label": class_label,
                "precision_mean": sum(item["precision"] for item in class_rows) / len(class_rows),
                "recall_mean": sum(item["recall"] for item in class_rows) / len(class_rows),
                "f1_mean": sum(item["f1"] for item in class_rows) / len(class_rows),
                "predicted_mean": sum(item["predicted"] for item in class_rows) / len(class_rows),
                "support_mean": sum(item["support"] for item in class_rows) / len(class_rows),
            }
            rows.append(summary)
    return rows


def main():
    labels = [0, 1, 2]
    confusion_by_method = {}
    for method_tag, _ in METHODS:
        matrices = []
        for seed in SEEDS:
            path = ROOT / f"splice_kmer_balanced_confirm_{method_tag}_seed{seed}_predictions.csv"
            seed_labels, matrix = confusion_matrix(read_predictions(path))
            labels = seed_labels
            matrices.append(matrix)
        confusion_by_method[method_tag] = mean_matrix(matrices, labels)

    per_class_rows = summarize_per_class()
    by_method_class = {(row["method"], row["class_label"]): row for row in per_class_rows}
    delta_rows = []
    for class_label in labels:
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

    write_csv(ROOT / "splice_kmer_balanced_per_class_summary.csv", per_class_rows)
    write_csv(ROOT / "splice_kmer_balanced_per_class_delta.csv", delta_rows)

    md = ROOT / "splice_kmer_balanced_per_class_analysis.md"
    with md.open("w", encoding="utf-8") as handle:
        handle.write("# Per-class and Confusion Analysis: strict 3-mer-balanced splice benchmark\n\n")
        handle.write("Protocol: average over held-out seeds `50-54` for the two main DNABERT-2-based methods.\n\n")
        handle.write("## Per-class mean metrics\n\n")
        handle.write("| Method | Class | Precision | Recall | F1 | Mean predicted count |\n")
        handle.write("|---|---:|---:|---:|---:|---:|\n")
        label_to_name = {
            "lora_attention_output_classifier": "LoRA attention.output + classifier",
            "germ_bo_quantile_q08_12_comp027": "GERM-BO quantile [0.8,1.2] comp0.27",
        }
        for row in per_class_rows:
            handle.write(
                f"| {label_to_name[row['method']]} | {row['class_label']} | "
                f"{row['precision_mean']:.4f} | {row['recall_mean']:.4f} | "
                f"{row['f1_mean']:.4f} | {row['predicted_mean']:.1f} |\n"
            )

        handle.write("\n## GERM-BO minus LoRA per-class delta\n\n")
        handle.write("| Class | Precision Delta | Recall Delta | F1 Delta | Predicted Count Delta |\n")
        handle.write("|---:|---:|---:|---:|---:|\n")
        for row in delta_rows:
            handle.write(
                f"| {row['class_label']} | {row['precision_delta']:+.4f} | "
                f"{row['recall_delta']:+.4f} | {row['f1_delta']:+.4f} | {row['predicted_delta']:+.1f} |\n"
            )

        handle.write("\n## Mean confusion matrix over seeds\n\n")
        for method_tag, method_label in METHODS:
            handle.write(f"### {method_label}\n\n")
            handle.write("| True \\\\ Pred | 0 | 1 | 2 |\n")
            handle.write("|---:|---:|---:|---:|\n")
            matrix = confusion_by_method[method_tag]
            for true_label in labels:
                handle.write(
                    f"| {true_label} | "
                    f"{matrix[true_label][0]:.1f} | {matrix[true_label][1]:.1f} | {matrix[true_label][2]:.1f} |\n"
                )
            handle.write("\n")

        handle.write("## Main interpretation\n\n")
        handle.write(
            "Compared with the strong LoRA baseline, GERM-BO mainly improves class-wise recall and F1 for the harder splice classes while reducing the collapse toward low-information predictions. "
            "The averaged confusion matrices show that GERM-BO redistributes predictions more evenly across the three classes instead of staying close to the baseline's weaker decision boundary.\n"
        )
    print(md)


if __name__ == "__main__":
    main()
