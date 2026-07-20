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


def collect_probabilities(model, data_loader, device):
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
            for index in range(labels.shape[0]):
                rows.append(
                    {
                        "id": batch["id"][index],
                        "true_label": int(labels[index].item()),
                        "prob_1": float(probabilities[index, 1].item()),
                        "metadata": batch["metadata"][index],
                    }
                )
    return rows


def compute_metrics(rows, threshold):
    true_positive = false_positive = true_negative = false_negative = 0
    for row in rows:
        predicted = 1 if row["prob_1"] >= threshold else 0
        label = row["true_label"]
        if predicted == 1 and label == 1:
            true_positive += 1
        elif predicted == 1 and label == 0:
            false_positive += 1
        elif predicted == 0 and label == 0:
            true_negative += 1
        else:
            false_negative += 1
    total = max(len(rows), 1)
    accuracy = (true_positive + true_negative) / total
    precision = true_positive / max(true_positive + false_positive, 1)
    recall = true_positive / max(true_positive + false_negative, 1)
    f1 = 2 * precision * recall / max(precision + recall, 1e-8)
    return {
        "threshold": threshold,
        "accuracy": accuracy,
        "f1": f1,
        "precision": precision,
        "recall": recall,
        "predicted_label_counts": {
            "0": true_negative + false_negative,
            "1": true_positive + false_positive,
        },
        "confusion": {
            "true_positive": true_positive,
            "false_positive": false_positive,
            "true_negative": true_negative,
            "false_negative": false_negative,
        },
    }


def choose_threshold(rows):
    candidates = {0.0, 0.5, 1.0}
    candidates.update(row["prob_1"] for row in rows)
    scored = [compute_metrics(rows, threshold) for threshold in sorted(candidates)]
    return max(
        scored,
        key=lambda item: (
            item["accuracy"],
            item["f1"],
            -abs(item["threshold"] - 0.5),
        ),
    )


def write_predictions(rows, threshold, output_csv):
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    with open(output_csv, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["id", "true_label", "pred_label", "prob_1", "threshold", "metadata"],
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    **row,
                    "pred_label": 1 if row["prob_1"] >= threshold else 0,
                    "threshold": threshold,
                }
            )


def main():
    args = parse_args()
    config = load_config(args.config)
    _, val_loader, test_loader = build_dataloaders(config)
    model, device, device_report = build_model_and_device(config)
    checkpoint = torch.load(args.checkpoint, map_location=device, weights_only=False)
    model.load_state_dict(checkpoint["model_state_dict"])

    val_rows = collect_probabilities(model, val_loader, device)
    test_rows = collect_probabilities(model, test_loader, device)
    val_metrics = choose_threshold(val_rows)
    threshold = val_metrics["threshold"]
    test_metrics = compute_metrics(test_rows, threshold)

    summary = {
        "config": args.config,
        "checkpoint": args.checkpoint,
        "selected_threshold": threshold,
        "validation": val_metrics,
        "test": test_metrics,
        "device_report": device_report,
    }

    output_json = Path(args.output_json)
    output_csv = Path(args.output_csv)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    with open(output_json, "w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2)
    write_predictions(test_rows, threshold, output_csv)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
