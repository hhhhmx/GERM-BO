"""Estimate empirical R_w(tau) and calibrate suppression threshold tau from activations."""

import argparse
import json
from pathlib import Path

import torch

from src.analysis.retention_calibration import (
    choose_calibrated_tau,
    expand_border_scores_to_tokens,
    pool_sample_magnitude,
    pool_token_magnitude,
    spearman_rho,
    summarize_group,
)
from src.utils.train_utils import build_dataloaders, build_model_and_device, load_config, parse_border_score, set_seed


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--checkpoint", default=None)
    parser.add_argument("--model-label", default="random_init")
    parser.add_argument("--hook-module", default="encoder.encoder.layer.0.attention.output.dense")
    parser.add_argument("--max-batches", type=int, default=None)
    parser.add_argument("--target-clip-fraction", type=float, default=0.01)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--pooling",
        choices=("sample", "token"),
        default="sample",
        help="Aggregate activations per sample (pooled) or per valid token.",
    )
    return parser.parse_args()


def resolve_module(model, target_name: str):
    parent = model
    for part in target_name.split("."):
        parent = getattr(parent, part)
    return parent


def collect_activation_gradients(model, data_loader, device, hook_module_name, max_batches, pooling):
    module = resolve_module(model, hook_module_name)
    captured = {"activation": None, "grad": None}

    def forward_hook(_, __, output):
        if isinstance(output, tuple):
            output = output[0]
        if torch.is_tensor(output):
            output.retain_grad()
        captured["activation"] = output

    def backward_hook(_, grad_input, grad_output):
        if grad_output[0] is not None:
            captured["grad"] = grad_output[0]
            return
        activation = captured.get("activation")
        if activation is not None and activation.grad is not None:
            captured["grad"] = activation.grad

    forward_handle = module.register_forward_hook(forward_hook)
    backward_handle = module.register_full_backward_hook(backward_hook)

    rows = []
    criterion = torch.nn.CrossEntropyLoss()
    model.eval()
    for batch_index, batch in enumerate(data_loader):
        if max_batches is not None and batch_index >= max_batches:
            break
        captured["activation"] = None
        captured["grad"] = None
        model.zero_grad(set_to_none=True)
        input_ids = batch["input_ids"].to(device)
        attention_mask = batch["attention_mask"].to(device)
        labels = batch["labels"].to(device)
        border_scores = batch.get("border_scores")
        if border_scores is not None:
            border_scores = border_scores.to(device)

        outputs = model(
            input_ids=input_ids,
            attention_mask=attention_mask,
            border_scores=border_scores,
        )
        loss = criterion(outputs["logits"], labels)
        loss.backward()

        activation = captured["activation"]
        grad = captured.get("grad")
        if activation is None:
            raise RuntimeError("Failed to capture activation from hook module.")
        if grad is None and activation.grad is not None:
            grad = activation.grad
        if grad is None:
            raise RuntimeError("Failed to capture gradient from hook module.")
        activation = activation.detach()
        grad = grad.detach()
        if pooling == "token":
            act = pool_token_magnitude(activation, attention_mask)
            grad_mag = pool_token_magnitude(grad, attention_mask)
            if border_scores is None:
                raise RuntimeError("Token-level calibration requires batch border_scores.")
            token_borders = expand_border_scores_to_tokens(border_scores, attention_mask)
            for index in range(act.shape[0]):
                rows.append(
                    {
                        "activation": float(act[index].item()),
                        "gradient": float(grad_mag[index].item()),
                        "border_score": float(token_borders[index].item()),
                    }
                )
            continue
        act = pool_sample_magnitude(activation, attention_mask)
        grad_mag = pool_sample_magnitude(grad, attention_mask)
        for index in range(labels.shape[0]):
            metadata = batch["metadata"][index]
            rows.append(
                {
                    "activation": float(act[index].item()),
                    "gradient": float(grad_mag[index].item()),
                    "border_score": float(parse_border_score(metadata)),
                    "label": int(labels[index].item()),
                }
            )

    forward_handle.remove()
    backward_handle.remove()
    return rows


def build_tau_grid(activations):
    if not activations:
        return [0.0]
    sorted_vals = sorted(activations)
    quantiles = [0.50, 0.75, 0.90, 0.95, 0.975, 0.99, 0.995]
    grid = {0.0}
    for quantile in quantiles:
        index = int(round(quantile * (len(sorted_vals) - 1)))
        grid.add(float(sorted_vals[index]))
    return sorted(grid)


def main():
    args = parse_args()
    config = load_config(args.config)
    if args.checkpoint is None:
        config["adapter"] = {"name": "none"}
    set_seed(args.seed)
    train_loader, _, _ = build_dataloaders(config)
    model, device, device_report = build_model_and_device(config)

    if args.checkpoint is not None:
        checkpoint = torch.load(args.checkpoint, map_location=device, weights_only=False)
        model.load_state_dict(checkpoint["model_state_dict"])

    for parameter in model.parameters():
        parameter.requires_grad = True

    rows = collect_activation_gradients(
        model,
        train_loader,
        device,
        args.hook_module,
        args.max_batches,
        args.pooling,
    )
    activations = [row["activation"] for row in rows]
    gradients = [row["gradient"] for row in rows]
    border_scores = [row["border_score"] for row in rows]
    tau_grid = build_tau_grid(activations)
    calibration = choose_calibrated_tau(activations, target_clip_fraction=args.target_clip_fraction)
    median_tau = sorted(activations)[len(activations) // 2]

    unique_borders = sorted(set(border_scores))
    border_groups = {}
    if len(unique_borders) <= 6:
        for value in unique_borders:
            group_rows = [row for row in rows if row["border_score"] == value]
            border_groups[f"border={value:.3f}"] = summarize_group(
                [row["activation"] for row in group_rows],
                [row["gradient"] for row in group_rows],
                [row["border_score"] for row in group_rows],
                tau_grid,
            )
    else:
        sorted_rows = sorted(rows, key=lambda row: row["border_score"])
        bin_size = max(1, len(sorted_rows) // 5)
        for bin_index in range(5):
            start = bin_index * bin_size
            end = len(sorted_rows) if bin_index == 4 else (bin_index + 1) * bin_size
            group_rows = sorted_rows[start:end]
            label = f"quintile_{bin_index + 1}"
            border_groups[label] = summarize_group(
                [row["activation"] for row in group_rows],
                [row["gradient"] for row in group_rows],
                [row["border_score"] for row in group_rows],
                tau_grid,
            )

    tau_star = calibration["tau"]
    group_names = list(border_groups.keys())
    r_values = []
    border_means = []
    r_values_median = []

    def lookup_r_empirical(group, tau_value):
        best_key = min(
            group["retention_by_tau"].keys(),
            key=lambda key: abs(float(key) - tau_value),
        )
        return group["retention_by_tau"][best_key]["R_empirical"]

    for name in group_names:
        group = border_groups[name]
        border_means.append(group["border_score_mean"])
        r_values.append(lookup_r_empirical(group, tau_star))
        r_values_median.append(lookup_r_empirical(group, median_tau))

    summary = {
        "config": args.config,
        "checkpoint": args.checkpoint,
        "model_label": args.model_label,
        "pooling_level": args.pooling,
        "hook_module": args.hook_module,
        "seed": args.seed,
        "n_train_samples": len(train_loader.dataset),
        "n_units": len(rows),
        "device_report": device_report,
        "calibrated_tau": calibration,
        "tau_grid": tau_grid,
        "overall": summarize_group(activations, gradients, border_scores, tau_grid),
        "border_groups": border_groups,
        "monotonicity_at_calibrated_tau": {
            "tau": tau_star,
            "spearman_border_vs_R_empirical": spearman_rho(border_means, r_values),
            "R_empirical_by_group": {name: value for name, value in zip(group_names, r_values)},
            "border_score_mean_by_group": {name: value for name, value in zip(group_names, border_means)},
        },
        "monotonicity_at_median_tau": {
            "tau": median_tau,
            "spearman_border_vs_R_empirical": spearman_rho(border_means, r_values_median),
            "R_empirical_by_group": {name: value for name, value in zip(group_names, r_values_median)},
            "border_score_mean_by_group": {name: value for name, value in zip(group_names, border_means)},
        },
    }

    output_path = Path(args.output_json)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
