from torch import nn


class LoRALinear(nn.Module):
    def __init__(self, base_layer: nn.Linear, rank: int, alpha: float, dropout: float):
        super().__init__()
        self.base_layer = base_layer
        self.rank = rank
        self.scaling = alpha / max(rank, 1)
        self.dropout = nn.Dropout(dropout)
        self.lora_a = nn.Linear(base_layer.in_features, rank, bias=False)
        self.lora_b = nn.Linear(rank, base_layer.out_features, bias=False)
        nn.init.kaiming_uniform_(self.lora_a.weight, a=5**0.5)
        nn.init.zeros_(self.lora_b.weight)
        self.base_layer.weight.requires_grad = False
        if self.base_layer.bias is not None:
            self.base_layer.bias.requires_grad = False

    def forward(self, x):
        base = self.base_layer(x)
        update = self.lora_b(self.lora_a(self.dropout(x))) * self.scaling
        return base + update


def resolve_module_and_name(module: nn.Module, target_name: str):
    parts = target_name.split(".")
    parent = module
    for part in parts[:-1]:
        if not hasattr(parent, part):
            raise AttributeError(f"Target path '{target_name}' is invalid at '{part}'.")
        parent = getattr(parent, part)
    leaf_name = parts[-1]
    if not hasattr(parent, leaf_name):
        raise AttributeError(f"Target path '{target_name}' is missing leaf '{leaf_name}'.")
    return parent, leaf_name


def attach_lora(module: nn.Module, target_name: str, rank: int, alpha: float, dropout: float) -> None:
    parent, leaf_name = resolve_module_and_name(module, target_name)
    target = getattr(parent, leaf_name)
    if not isinstance(target, nn.Linear):
        raise TypeError(f"Target module '{target_name}' must be nn.Linear for LoRA attachment.")
    setattr(parent, leaf_name, LoRALinear(target, rank=rank, alpha=alpha, dropout=dropout))
