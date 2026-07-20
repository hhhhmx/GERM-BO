import argparse
import csv
import json
from pathlib import Path

import torch

from src.utils.train_utils import build_dataloaders, build_model_and_device, load_config


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--checkpoint", required=True)
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--output-csv", required=True)
    return parser.parse_args()


def collect_predictions(model, data_loader, device):
    rows = []
    model.eval()
    with torch.no_grad():
        for batch in data_loader:
            inputs = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            border_scores = batch.get("border_scores")
            if border_scores is not None:
                border_scores = border_scores.to(device)
            labels = batch["labels"].cpu()
            outputs = model(input_ids=inputs, attention_mask=attention_mask, border_scores=border_scores)
            probabilities = torch.softmax(outputs["logits"], dim=-1).cpu()
            predictions = probabilities.argmax(dim=-1)
            for index in range(labels.shape[0]):
                row = {
                    "id": batch["id"][index],
                    "true_label": int(labels[index].item()),
                    "pred_label": int(predictions[index].item()),
                    "metadata": batch["metadata"][index],
                }
                for class_index in range(probabilities.shape[1]):
                    row[f"prob_{class_index}"] = float(probabilities[index, class_index].item())
                rows.append(row)
    return rows


def compute_metrics(rows, num_labels):
    total = max(len(rows), 1)
    accuracy = sum(1 for row in rows if row["true_label"] == row["pred_label"]) / total
    per_class = {}
    f1_values = []
    for label in range(num_labels):
        true_positive = sum(1 for row in rows if row["true_label"] == label and row["pred_label"] == label)
        false_positive = sum(1 for row in rows if row["true_label"] != label and row["pred_label"] == label)
        false_negative = sum(1 for row in rows if row["true_label"] == label and row["pred_label"] != label)
        precision = true_positive / max(true_positive + false_positive, 1)
        recall = true_positive / max(true_positive + false_negative, 1)
        f1 = 2 * precision * recall / max(precision + recall, 1e-8)
        per_class[str(label)] = {
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "support": sum(1 for row in rows if row["true_label"] == label),
            "predicted": sum(1 for row in rows if row["pred_label"] == label),
        }
        f1_values.append(f1)
    return {
        "accuracy": accuracy,
        "macro_f1": sum(f1_values) / max(len(f1_values), 1),
        "per_class": per_class,
        "true_label_counts": {str(label): sum(1 for row in rows if row["true_label"] == label) for label in range(num_labels)},
        "predicted_label_counts": {str(label): sum(1 for row in rows if row["pred_label"] == label) for label in range(num_labels)},
    }


def write_predictions(rows, output_csv):
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    with output_csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main():
    args = parse_args()
    config = load_config(args.config)
    _, val_loader, test_loader = build_dataloaders(config)
    model, device, device_report = build_model_and_device(config)
    checkpoint = torch.load(args.checkpoint, map_location=device, weights_only=False)
    model.load_state_dict(checkpoint["model_state_dict"])
    val_rows = collect_predictions(model, val_loader, device)
    test_rows = collect_predictions(model, test_loader, device)
    num_labels = int(config["task"]["num_labels"])
    summary = {
        "config": args.config,
        "checkpoint": args.checkpoint,
        "evaluation": "argmax",
        "validation": compute_metrics(val_rows, num_labels),
        "test": compute_metrics(test_rows, num_labels),
        "device_report": device_report,
    }
    output_json = Path(args.output_json)
    output_csv = Path(args.output_csv)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    write_predictions(test_rows, output_csv)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
