from pathlib import Path
from typing import Dict, Optional

import torch
from torch import nn

from src.adapters.germ_bo import set_germ_bo_border_scores


def expand_border_scores_to_tokens(border_scores, attention_mask):
    if border_scores is None or attention_mask is None:
        return None
    token_counts = attention_mask.to(dtype=torch.long).sum(dim=1).cpu().tolist()
    pieces = []
    for index, count in enumerate(token_counts):
        if count > 0:
            pieces.append(border_scores[index].repeat(int(count)))
    if not pieces:
        return None
    return torch.cat(pieces, dim=0)


class MockSequenceBackbone(nn.Module):
    def __init__(self, vocab_size: int, hidden_dim: int, num_labels: int):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, hidden_dim)
        self.local_encoder = nn.Sequential(
            nn.Conv1d(hidden_dim, hidden_dim, kernel_size=5, padding=2),
            nn.ReLU(),
            nn.Conv1d(hidden_dim, hidden_dim, kernel_size=3, padding=1),
            nn.ReLU(),
        )
        self.projection = nn.Sequential(
            nn.Linear(hidden_dim * 2, hidden_dim),
            nn.ReLU(),
        )
        self.classifier = nn.Linear(hidden_dim, num_labels)

    def forward(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        border_scores: Optional[torch.Tensor] = None,
    ) -> Dict[str, torch.Tensor]:
        token_border_scores = expand_border_scores_to_tokens(border_scores, attention_mask)
        set_germ_bo_border_scores(self, border_scores, token_border_scores)
        embeddings = self.embedding(input_ids)
        encoded = self.local_encoder(embeddings.transpose(1, 2)).transpose(1, 2)
        if attention_mask is None:
            mean_pooled = encoded.mean(dim=1)
            max_pooled = encoded.max(dim=1).values
        else:
            mask = attention_mask.unsqueeze(-1).to(encoded.dtype)
            mean_pooled = (encoded * mask).sum(dim=1) / mask.sum(dim=1).clamp_min(1.0)
            masked_encoded = encoded.masked_fill(mask == 0, float("-inf"))
            max_pooled = masked_encoded.max(dim=1).values
            max_pooled = torch.where(torch.isfinite(max_pooled), max_pooled, torch.zeros_like(max_pooled))
        pooled = torch.cat([mean_pooled, max_pooled], dim=-1)
        hidden = self.projection(pooled)
        logits = self.classifier(hidden)
        return {"logits": logits, "hidden_states": hidden}


def _resolve_hidden_size(model_config) -> int:
    for key in ("hidden_size", "d_model", "n_embd"):
        value = getattr(model_config, key, None)
        if value is not None:
            return int(value)
    raise ValueError("Loaded Hugging Face backbone does not expose hidden_size, d_model, or n_embd.")


def _extract_encoder_module(wrapper: nn.Module) -> nn.Module:
    for attr in ("esm", "bert", "model", "base_model", "backbone"):
        if hasattr(wrapper, attr):
            candidate = getattr(wrapper, attr)
            if isinstance(candidate, nn.Module):
                return candidate
    return wrapper


def _load_hf_encoder(model_cfg: Dict, hf_config):
    from transformers import AutoModel, AutoModelForMaskedLM

    pretrained_name = model_cfg["pretrained_model_name_or_path"]
    resolved_path = Path(pretrained_name).expanduser()
    local_files_only = resolved_path.exists()
    cache_dir = model_cfg.get("cache_dir")
    trust_remote_code = model_cfg.get("trust_remote_code", False)
    load_as = model_cfg.get("load_as", "auto")
    common_kwargs = {
        "cache_dir": cache_dir,
        "trust_remote_code": trust_remote_code,
        "config": hf_config,
        "local_files_only": local_files_only,
    }

    if load_as == "masked_lm":
        return _extract_encoder_module(AutoModelForMaskedLM.from_pretrained(pretrained_name, **common_kwargs))

    if load_as == "base_model":
        return AutoModel.from_pretrained(pretrained_name, **common_kwargs)

    try:
        return AutoModel.from_pretrained(pretrained_name, **common_kwargs)
    except (RuntimeError, ValueError, OSError):
        return _extract_encoder_module(AutoModelForMaskedLM.from_pretrained(pretrained_name, **common_kwargs))


class HFSequenceClassifier(nn.Module):
    def __init__(self, config: Dict):
        super().__init__()
        from transformers import AutoConfig

        model_cfg = config["model"]
        pretrained_name = model_cfg["pretrained_model_name_or_path"]
        resolved_path = Path(pretrained_name).expanduser()
        local_files_only = resolved_path.exists()
        cache_dir = model_cfg.get("cache_dir")
        trust_remote_code = model_cfg.get("trust_remote_code", False)
        hf_config = AutoConfig.from_pretrained(
            pretrained_name,
            cache_dir=cache_dir,
            trust_remote_code=trust_remote_code,
            local_files_only=local_files_only,
        )
        attention_dropout = model_cfg.get("attention_probs_dropout_prob")
        if attention_dropout is not None and hasattr(hf_config, "attention_probs_dropout_prob"):
            hf_config.attention_probs_dropout_prob = attention_dropout
        self.encoder = _load_hf_encoder(model_cfg, hf_config)
        hidden_size = _resolve_hidden_size(self.encoder.config)
        dropout_prob = model_cfg.get("classifier_dropout", 0.1)
        self.dropout = nn.Dropout(dropout_prob)
        self.classifier = nn.Linear(hidden_size, config["task"]["num_labels"])

    def forward(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        border_scores: Optional[torch.Tensor] = None,
    ) -> Dict[str, torch.Tensor]:
        token_border_scores = expand_border_scores_to_tokens(border_scores, attention_mask)
        set_germ_bo_border_scores(self, border_scores, token_border_scores)
        encoder_kwargs = {"input_ids": input_ids}
        forward_params = self.encoder.forward.__code__.co_varnames
        if attention_mask is not None and "attention_mask" in forward_params:
            encoder_kwargs["attention_mask"] = attention_mask
        outputs = self.encoder(**encoder_kwargs)
        pooled = getattr(outputs, "pooler_output", None)
        if pooled is None:
            if isinstance(outputs, tuple):
                last_hidden_state = outputs[0]
            else:
                last_hidden_state = outputs.last_hidden_state
            if attention_mask is None:
                pooled = last_hidden_state[:, 0]
            else:
                mask = attention_mask.unsqueeze(-1).to(last_hidden_state.dtype)
                summed = (last_hidden_state * mask).sum(dim=1)
                pooled = summed / mask.sum(dim=1).clamp_min(1.0)
        hidden = self.dropout(pooled)
        logits = self.classifier(hidden)
        return {"logits": logits, "hidden_states": pooled}


def build_backbone(config: Dict) -> nn.Module:
    backbone_type = config["model"]["backbone_type"]
    if backbone_type == "mock":
        return MockSequenceBackbone(
            vocab_size=config["model"]["vocab_size"],
            hidden_dim=config["model"]["hidden_dim"],
            num_labels=config["task"]["num_labels"],
        )
    if backbone_type == "hf":
        return HFSequenceClassifier(config)
    raise NotImplementedError("Unsupported backbone_type: {0}".format(backbone_type))
