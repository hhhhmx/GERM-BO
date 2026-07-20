import torch
from torch import nn

from src.adapters.lora import LoRALinear, resolve_module_and_name


class GermBOLinear(LoRALinear):
    def __init__(
        self,
        base_layer: nn.Linear,
        rank: int,
        alpha: float,
        dropout: float,
        compensation_strength: float,
        clip_min: float,
        clip_max: float,
        score_type: str = "activation_abs_mean",
    ):
        super().__init__(base_layer=base_layer, rank=rank, alpha=alpha, dropout=dropout)
        self.compensation_strength = compensation_strength
        self.clip_min = clip_min
        self.clip_max = clip_max
        self.score_type = score_type
        self.current_border_scores = None
        self.current_token_border_scores = None

    def set_border_scores(self, border_scores, token_border_scores=None):
        self.current_border_scores = border_scores
        self.current_token_border_scores = token_border_scores

    def _activation_signal(self, x):
        return x.abs().mean(dim=-1, keepdim=True)

    def _metadata_signal(self, x):
        if self.current_border_scores is None:
            raise ValueError("metadata_border_score compensation requires batch border_scores.")
        border_scores = self.current_border_scores.to(device=x.device, dtype=x.dtype)
        if x.dim() == 3:
            return border_scores.view(-1, 1, 1)
        if x.dim() == 2 and x.shape[0] == border_scores.shape[0]:
            return border_scores.view(-1, 1)
        if self.current_token_border_scores is not None:
            token_scores = self.current_token_border_scores.to(device=x.device, dtype=x.dtype)
            if x.dim() == 2 and x.shape[0] == token_scores.shape[0]:
                return token_scores.view(-1, 1)
        return border_scores.view(-1, 1)

    def _compensation_signal(self, x):
        if self.score_type in {"activation_abs_mean", "normalized_border_length"}:
            return self._activation_signal(x)
        if self.score_type == "metadata_border_score":
            return self._metadata_signal(x)
        raise ValueError(f"Unsupported GERM-BO border_score_type: {self.score_type}")

    def forward(self, x):
        base = self.base_layer(x)
        projected = self.lora_a(self.dropout(x))
        border_signal = self._compensation_signal(x)
        normalized = border_signal / border_signal.detach().mean().clamp_min(1e-6)
        compensation = 1.0 + self.compensation_strength * (normalized - 1.0)
        compensation = compensation.clamp(self.clip_min, self.clip_max)
        update = self.lora_b(projected * compensation) * self.scaling
        return base + update


def attach_germ_bo(
    module: nn.Module,
    target_name: str,
    rank: int,
    alpha: float,
    dropout: float,
    compensation_strength: float,
    clip_min: float,
    clip_max: float,
    score_type: str = "activation_abs_mean",
) -> None:
    parent, leaf_name = resolve_module_and_name(module, target_name)
    target = getattr(parent, leaf_name)
    if not isinstance(target, nn.Linear):
        raise TypeError(f"Target module '{target_name}' must be nn.Linear for GERM-BO attachment.")
    setattr(
        parent,
        leaf_name,
        GermBOLinear(
            target,
            rank=rank,
            alpha=alpha,
            dropout=dropout,
            compensation_strength=compensation_strength,
            clip_min=clip_min,
            clip_max=clip_max,
            score_type=score_type,
        ),
    )


def set_germ_bo_border_scores(module: nn.Module, border_scores, token_border_scores=None) -> None:
    for child in module.modules():
        if isinstance(child, GermBOLinear):
            child.set_border_scores(border_scores, token_border_scores)
