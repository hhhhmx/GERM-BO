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
    parser.add_argument("--split", choices=["val", "test"], default="test")
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--output-csv", required=True)
    return parser.parse_args()


def main():
    args = parse_args()
    config = load_config(args.config)
    _, val_loader, test_loader = build_dataloaders(config)
    data_loader = val_loader if args.split == "val" else test_loader
    model, device, device_report = build_model_and_device(config)

    checkpoint = torch.load(args.checkpoint, map_location=device, weights_only=False)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()

    prediction_rows = []
    predicted_label_counts = {}
    true_label_counts = {}

    with torch.no_grad():
        for batch in data_loader:
            inputs = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            border_scores = batch.get("border_scores")
            if border_scores is not None:
                border_scores = border_scores.to(device)
            outputs = model(input_ids=inputs, attention_mask=attention_mask, border_scores=border_scores)
            logits = outputs["logits"]
            probabilities = torch.softmax(logits, dim=-1).cpu()
            predictions = torch.argmax(probabilities, dim=-1)
            labels = batch["labels"].cpu()

            for index in range(labels.shape[0]):
                predicted_label = int(predictions[index].item())
                true_label = int(labels[index].item())
                predicted_label_counts[str(predicted_label)] = predicted_label_counts.get(str(predicted_label), 0) + 1
                true_label_counts[str(true_label)] = true_label_counts.get(str(true_label), 0) + 1
                prediction_rows.append(
                    {
                        "id": batch["id"][index],
                        "true_label": true_label,
                        "pred_label": predicted_label,
                        "prob_0": float(probabilities[index, 0].item()),
                        "prob_1": float(probabilities[index, 1].item()),
                        "sequence": batch["sequence"][index],
                        "metadata": batch["metadata"][index],
                    }
                )

    summary = {
        "split": args.split,
        "num_examples": len(prediction_rows),
        "predicted_label_counts": predicted_label_counts,
        "true_label_counts": true_label_counts,
        "device_report": device_report,
        "checkpoint": args.checkpoint,
        "config": args.config,
    }

    output_json = Path(args.output_json)
    output_csv = Path(args.output_csv)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_csv.parent.mkdir(parents=True, exist_ok=True)

    with open(output_json, "w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2)

    with open(output_csv, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["id", "true_label", "pred_label", "prob_0", "prob_1", "sequence", "metadata"],
        )
        writer.writeheader()
        writer.writerows(prediction_rows)

    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
