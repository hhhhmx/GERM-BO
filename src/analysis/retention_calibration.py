"""Empirical retention-ratio and tau calibration utilities."""

from __future__ import annotations

import math
from typing import Dict, Iterable, List, Sequence, Tuple

import torch


def phi_hard(abs_activation: torch.Tensor, tau: float) -> torch.Tensor:
    return (abs_activation <= tau).to(abs_activation.dtype)


def phi_smooth(abs_activation: torch.Tensor, tau: float) -> torch.Tensor:
    if tau <= 0:
        return torch.zeros_like(abs_activation)
    ratio = abs_activation / tau
    return torch.clamp(1.0 - ratio, min=0.0)


def pool_sample_magnitude(tensor: torch.Tensor, attention_mask: torch.Tensor) -> torch.Tensor:
    """Mean absolute magnitude per sample over valid tokens and hidden dims."""
    if tensor.dim() == 3:
        mask = attention_mask.unsqueeze(-1).to(tensor.dtype)
        summed = (tensor.abs() * mask).sum(dim=(1, 2))
        counts = mask.sum(dim=(1, 2)).clamp_min(1.0)
        return summed / counts
    if tensor.dim() == 2:
        return tensor.abs().mean(dim=1)
    raise ValueError(f"Unsupported activation rank: {tensor.dim()}")


def pool_token_magnitude(tensor: torch.Tensor, attention_mask: torch.Tensor) -> torch.Tensor:
    """Mean absolute magnitude per valid token (flattened over batch)."""
    if tensor.dim() == 3:
        per_token = tensor.abs().mean(dim=-1)
        return per_token[attention_mask.bool()]
    if tensor.dim() == 2:
        return tensor.abs().mean(dim=-1)
    raise ValueError(f"Unsupported activation rank: {tensor.dim()}")


def expand_border_scores_to_tokens(
    border_scores: torch.Tensor,
    attention_mask: torch.Tensor,
) -> torch.Tensor:
    """Broadcast sample-level border scores to each valid token."""
    if border_scores.dim() != 1:
        raise ValueError("border_scores must be a 1D batch tensor.")
    expanded = border_scores.unsqueeze(1).expand(-1, attention_mask.shape[1])
    return expanded[attention_mask.bool()]


def retention_ratio(
    activations: torch.Tensor,
    gradients: torch.Tensor,
    tau: float,
    phi: str = "hard",
) -> Dict[str, float]:
    phi_fn = phi_hard if phi == "hard" else phi_smooth
    phi_values = phi_fn(activations, tau)
    grad_sq = gradients.pow(2)
    numerator = (phi_values.pow(2) * grad_sq).sum()
    denominator = grad_sq.sum().clamp_min(1e-12)
    scale_numerator = phi_values.pow(2).sum()
    count = float(activations.numel())
    return {
        "R_empirical": float((numerator / denominator).item()),
        "R_scale": float((scale_numerator / max(count, 1.0)).item()),
        "clip_fraction": float((activations > tau).float().mean().item()),
        "n": count,
    }


def summarize_group(
    activations: Sequence[float],
    gradients: Sequence[float],
    border_scores: Sequence[float],
    tau_grid: Sequence[float],
    phi: str = "hard",
) -> Dict:
    act = torch.tensor(activations, dtype=torch.float32)
    grad = torch.tensor(gradients, dtype=torch.float32)
    border = torch.tensor(border_scores, dtype=torch.float32)
    per_tau = {}
    for tau in tau_grid:
        per_tau[str(tau)] = retention_ratio(act, grad, float(tau), phi=phi)
    return {
        "n_units": len(activations),
        "border_score_mean": float(border.mean().item()),
        "border_score_std": float(border.std(unbiased=False).item()) if len(border_scores) > 1 else 0.0,
        "activation_mean": float(act.mean().item()),
        "activation_std": float(act.std(unbiased=False).item()) if len(activations) > 1 else 0.0,
        "gradient_mean": float(grad.mean().item()),
        "retention_by_tau": per_tau,
    }


def spearman_rho(x: Sequence[float], y: Sequence[float]) -> float:
    if len(x) < 2:
        return float("nan")
    rank_x = _rankdata(x)
    rank_y = _rankdata(y)
    mean_x = sum(rank_x) / len(rank_x)
    mean_y = sum(rank_y) / len(rank_y)
    num = sum((a - mean_x) * (b - mean_y) for a, b in zip(rank_x, rank_y))
    den_x = math.sqrt(sum((a - mean_x) ** 2 for a in rank_x))
    den_y = math.sqrt(sum((b - mean_y) ** 2 for b in rank_y))
    if den_x == 0 or den_y == 0:
        return float("nan")
    return num / (den_x * den_y)


def _rankdata(values: Sequence[float]) -> List[float]:
    indexed = sorted(enumerate(values), key=lambda item: item[1])
    ranks = [0.0] * len(values)
    pos = 0
    while pos < len(indexed):
        end = pos + 1
        while end < len(indexed) and indexed[end][1] == indexed[pos][1]:
            end += 1
        avg_rank = (pos + 1 + end) / 2.0
        for j in range(pos, end):
            ranks[indexed[j][0]] = avg_rank
        pos = end
    return ranks


def choose_calibrated_tau(
    activations: Sequence[float],
    target_clip_fraction: float = 0.01,
) -> Dict[str, float]:
    if not activations:
        raise ValueError("Cannot calibrate tau without activation samples.")
    sorted_vals = sorted(activations)
    index = min(len(sorted_vals) - 1, max(0, int(round((1.0 - target_clip_fraction) * (len(sorted_vals) - 1)))))
    tau = sorted_vals[index]
    empirical_clip = sum(1 for value in activations if value > tau) / len(activations)
    return {
        "tau": float(tau),
        "target_clip_fraction": float(target_clip_fraction),
        "empirical_clip_fraction": float(empirical_clip),
        "activation_p95": float(sorted_vals[int(0.95 * (len(sorted_vals) - 1))]),
        "activation_p99": float(sorted_vals[int(0.99 * (len(sorted_vals) - 1))]),
    }
