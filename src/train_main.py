import argparse
import json
import math
from pathlib import Path

import torch

from src.utils.train_utils import (
    apply_debug_overrides,
    build_dataloaders,
    build_model_and_device,
    ensure_output_dirs,
    evaluate_model,
    load_config,
    save_json,
    set_seed,
)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--gpu-id", type=int, default=None)
    parser.add_argument("--device", choices=["cpu", "cuda"], default=None)
    return parser.parse_args()


def main():
    args = parse_args()
    config = load_config(args.config)
    if args.debug:
        config = apply_debug_overrides(config)
    if args.output_dir is not None:
        config["output_dir"] = args.output_dir
    if args.seed is not None:
        config["seed"] = args.seed
    if args.gpu_id is not None:
        config["gpu_id"] = args.gpu_id
    if args.device is not None:
        config["device"] = args.device
    if torch.cuda.device_count() > 1:
        print("Multiple GPUs may be visible, but this code uses only one selected device.")
    set_seed(config["seed"])
    output_dir = config["output_dir"]
    if args.debug:
        output_dir = str(Path(output_dir) / config["debug"]["output_subdir"])
    ensure_output_dirs(output_dir, config["results_dir"])
    train_loader, val_loader, _ = build_dataloaders(config)
    model, device, device_report = build_model_and_device(config)
    optimizer = torch.optim.AdamW(
        [parameter for parameter in model.parameters() if parameter.requires_grad],
        lr=config["optim"]["lr"],
        weight_decay=config["optim"]["weight_decay"],
    )
    criterion = torch.nn.CrossEntropyLoss()
    log_path = Path(output_dir) / "logs" / "train_metrics.json"
    checkpoint_path = Path(output_dir) / "checkpoints" / "debug_last.pt"
    best_checkpoint_path = Path(output_dir) / "checkpoints" / "best.pt"
    checkpoint_monitor = config["train"].get("checkpoint_monitor", "loss")
    checkpoint_mode = config["train"].get("checkpoint_mode", "min")
    if checkpoint_mode not in {"min", "max"}:
        raise ValueError("train.checkpoint_mode must be either 'min' or 'max'.")
    early_stopping_patience = config["train"].get("early_stopping_patience")
    early_stopping_min_delta = config["train"].get("early_stopping_min_delta", 0.0)
    if early_stopping_patience is not None and early_stopping_patience < 0:
        raise ValueError("train.early_stopping_patience must be null or non-negative.")
    max_steps = config["debug"]["max_steps"] if args.debug else None
    best_score = math.inf if checkpoint_mode == "min" else -math.inf
    best_summary = None
    epochs_without_improvement = 0
    stopped_early = False
    stop_reason = None
    history = {
        "device_report": device_report,
        "train": [],
        "val": [],
        "checkpointing": {
            "last_checkpoint": str(checkpoint_path),
            "best_checkpoint": str(best_checkpoint_path),
            "monitor": checkpoint_monitor,
            "mode": checkpoint_mode,
            "best": None,
        },
        "early_stopping": {
            "enabled": early_stopping_patience is not None,
            "patience": early_stopping_patience,
            "min_delta": early_stopping_min_delta,
            "stopped": False,
            "stop_epoch": None,
            "reason": None,
        },
    }

    global_step = 0
    for epoch in range(config["train"]["epochs"]):
        model.train()
        for batch in train_loader:
            global_step += 1
            inputs = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            border_scores = batch.get("border_scores")
            if border_scores is not None:
                border_scores = border_scores.to(device)
            labels = batch["labels"].to(device)
            optimizer.zero_grad()
            outputs = model(input_ids=inputs, attention_mask=attention_mask, border_scores=border_scores)
            logits = outputs["logits"]
            loss = criterion(logits, labels)
            loss.backward()
            optimizer.step()
            history["train"].append({"epoch": epoch, "step": global_step, "loss": loss.item()})
            if max_steps is not None and global_step >= max_steps:
                break
        val_metrics = evaluate_model(model, val_loader, device)
        val_metrics["epoch"] = epoch
        history["val"].append(val_metrics)
        if checkpoint_monitor not in val_metrics:
            raise ValueError(f"Monitored validation metric is missing: {checkpoint_monitor}")
        current_score = val_metrics[checkpoint_monitor]
        if current_score is None:
            raise ValueError(f"Monitored validation metric is null: {checkpoint_monitor}")
        if checkpoint_mode == "min":
            is_best = current_score < best_score - early_stopping_min_delta
        else:
            is_best = current_score > best_score + early_stopping_min_delta
        if is_best:
            best_score = current_score
            epochs_without_improvement = 0
            best_summary = {
                "epoch": epoch,
                "metric": checkpoint_monitor,
                "mode": checkpoint_mode,
                "score": current_score,
                "val_metrics": val_metrics,
            }
            history["checkpointing"]["best"] = best_summary
        else:
            epochs_without_improvement += 1
        should_stop_early = (
            early_stopping_patience is not None
            and epochs_without_improvement >= early_stopping_patience
        )
        if should_stop_early:
            stopped_early = True
            stop_reason = (
                f"No improvement in validation {checkpoint_monitor} for "
                f"{epochs_without_improvement} epoch(s)."
            )
            history["early_stopping"]["stopped"] = True
            history["early_stopping"]["stop_epoch"] = epoch
            history["early_stopping"]["reason"] = stop_reason
        checkpoint_payload = {
            "model_state_dict": model.state_dict(),
            "config": config,
            "device_report": device_report,
            "history": history,
            "epoch": epoch,
            "val_metrics": val_metrics,
        }
        torch.save(checkpoint_payload, checkpoint_path)
        if is_best:
            torch.save(checkpoint_payload, best_checkpoint_path)
        if should_stop_early:
            break
        if max_steps is not None and global_step >= max_steps:
            break

    history["early_stopping"]["stopped"] = stopped_early
    history["early_stopping"]["reason"] = stop_reason
    save_json(history, log_path)
    print(
        json.dumps(
            {
                "output_dir": output_dir,
                "checkpoint": str(checkpoint_path),
                "best_checkpoint": str(best_checkpoint_path),
                "best": best_summary,
                "early_stopping": history["early_stopping"],
                "last_val": history["val"][-1],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
