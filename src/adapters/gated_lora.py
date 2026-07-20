import torch
from torch import nn

from src.adapters.lora import LoRALinear, resolve_module_and_name


class GatedLoRALinear(LoRALinear):
    """Input-dependent gate on the LoRA branch (direction-aware PEFT baseline)."""

    def __init__(self, base_layer: nn.Linear, rank: int, alpha: float, dropout: float):
        super().__init__(base_layer=base_layer, rank=rank, alpha=alpha, dropout=dropout)
        self.gate = nn.Linear(base_layer.in_features, 1, bias=True)
        nn.init.zeros_(self.gate.weight)
        nn.init.constant_(self.gate.bias, 2.0)

    def _sample_gate(self, x: torch.Tensor) -> torch.Tensor:
        if x.dim() == 3:
            pooled = x.mean(dim=1)
            gate = torch.sigmoid(self.gate(pooled))
            return gate.view(-1, 1, 1)
        if x.dim() == 2:
            gate = torch.sigmoid(self.gate(x))
            return gate.view(-1, 1)
        raise ValueError(f"Unsupported hidden-state rank for gated LoRA: {x.dim()}")

    def forward(self, x):
        base = self.base_layer(x)
        update = self.lora_b(self.lora_a(self.dropout(x))) * self.scaling
        return base + self._sample_gate(x) * update


def attach_gated_lora(
    module: nn.Module,
    target_name: str,
    rank: int,
    alpha: float,
    dropout: float,
) -> None:
    parent, leaf_name = resolve_module_and_name(module, target_name)
    target = getattr(parent, leaf_name)
    if not isinstance(target, nn.Linear):
        raise TypeError(f"Target module '{target_name}' must be nn.Linear for gated LoRA attachment.")
    setattr(parent, leaf_name, GatedLoRALinear(target, rank=rank, alpha=alpha, dropout=dropout))
