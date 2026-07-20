"""Snapshot trainable parameters and GPU memory for a config (no full training)."""
import argparse
import json
from pathlib import Path

import torch

from src.utils.train_utils import build_model_and_device, load_config, set_seed


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output-json", required=True)
    args = parser.parse_args()

    config = load_config(args.config)
    config["seed"] = args.seed
    set_seed(args.seed)
    model, device, device_report = build_model_and_device(config)
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    total = sum(p.numel() for p in model.parameters())
    snapshot = {
        "config": args.config,
        "seed": args.seed,
        "trainable_params": trainable,
        "total_params": total,
        "trainable_fraction": round(trainable / max(total, 1), 6),
        "device_report": device_report,
    }
    if device.type == "cuda":
        torch.cuda.reset_peak_memory_stats(device)
        batch_size = 2
        dummy = torch.randint(0, 4, (batch_size, config["data"]["seq_length"]), device=device)
        mask = torch.ones_like(dummy)
        border_scores = torch.ones(batch_size, device=device)
        with torch.no_grad():
            model(input_ids=dummy, attention_mask=mask, border_scores=border_scores)
        snapshot["peak_memory_mb"] = round(torch.cuda.max_memory_allocated(device) / 1024 ** 2, 2)
    out = Path(args.output_json)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(snapshot, indent=2))
    print(json.dumps(snapshot, indent=2))


if __name__ == "__main__":
    main()
