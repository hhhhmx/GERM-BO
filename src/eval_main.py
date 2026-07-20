import argparse
import json
from pathlib import Path

import torch

from src.utils.train_utils import (
    apply_debug_overrides,
    build_dataloaders,
    build_model_and_device,
    evaluate_model,
    load_config,
    save_json,
)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--checkpoint", required=True)
    parser.add_argument("--split", default="test", choices=["val", "test"])
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--output", default=None)
    parser.add_argument("--device", choices=["cpu", "cuda"], default=None)
    return parser.parse_args()


def main():
    args = parse_args()
    config = load_config(args.config)
    if args.debug:
        config = apply_debug_overrides(config)
    if args.device is not None:
        config["device"] = args.device
    _, val_loader, test_loader = build_dataloaders(config)
    model, device, device_report = build_model_and_device(config)
    checkpoint = torch.load(args.checkpoint, map_location=device, weights_only=False)
    model.load_state_dict(checkpoint["model_state_dict"])
    data_loader = val_loader if args.split == "val" else test_loader
    metrics = evaluate_model(model, data_loader, device)
    metrics["split"] = args.split
    metrics["device_report"] = device_report
    output_path = Path(args.output) if args.output else Path(config["results_dir"]) / f"{args.split}_metrics.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    save_json(metrics, output_path)
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
