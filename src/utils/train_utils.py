import json
import random
import re
from pathlib import Path
from typing import Dict

import numpy as np
import torch
import yaml
from torch.utils.data import DataLoader

from src.adapters.germ_bo import attach_germ_bo
from src.adapters.gated_lora import attach_gated_lora
from src.adapters.lora import attach_lora
from src.data.genomic_dataset import GenomicSequenceDataset
from src.data.mock_dataset import MockGenomicDataset
from src.models.backbone_loader import build_backbone
from src.utils.device import get_device_report, resolve_device, validate_single_gpu_setup
from src.utils.metrics import compute_classification_metrics


BORDER_SCORE_PATTERN = re.compile(r"(?:^|[;,\s])border_score=([-+]?(?:\d+(?:\.\d*)?|\.\d+))")


def parse_border_score(metadata) -> float:
    if metadata is None:
        return 1.0
    if isinstance(metadata, dict):
        for key in ("border_score", "motif_border_score"):
            if key in metadata:
                return float(metadata[key])
        return 1.0
    text = str(metadata)
    match = BORDER_SCORE_PATTERN.search(text)
    if match:
        return float(match.group(1))
    return 1.0


def load_config(config_path: str) -> Dict:
    with open(config_path, "r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def apply_debug_overrides(config: Dict) -> Dict:
    debug = config["debug"]
    config = json.loads(json.dumps(config))
    config["data"]["train_size"] = debug["train_size"]
    config["data"]["val_size"] = debug["val_size"]
    config["data"]["test_size"] = debug["test_size"]
    config["train"]["batch_size"] = debug["batch_size"]
    config["train"]["epochs"] = debug["epochs"]
    return config


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def ensure_output_dirs(base_output_dir: str, results_dir: str) -> None:
    Path(base_output_dir, "checkpoints").mkdir(parents=True, exist_ok=True)
    Path(base_output_dir, "logs").mkdir(parents=True, exist_ok=True)
    Path(results_dir).mkdir(parents=True, exist_ok=True)


def collate_batch(batch):
    max_length = max(item["input_ids"].shape[0] for item in batch)
    input_ids = []
    attention_masks = []
    labels = []
    sequences = []
    sample_ids = []
    metadata = []
    border_scores = []
    for item in batch:
        current_length = item["input_ids"].shape[0]
        pad_length = max_length - current_length
        if pad_length > 0:
            pad_ids = torch.full(
                (pad_length,),
                fill_value=item.get("pad_token_id", 0),
                dtype=item["input_ids"].dtype,
            )
            pad_mask = torch.zeros(pad_length, dtype=item["attention_mask"].dtype)
            input_ids.append(torch.cat([item["input_ids"], pad_ids], dim=0))
            attention_masks.append(torch.cat([item["attention_mask"], pad_mask], dim=0))
        else:
            input_ids.append(item["input_ids"])
            attention_masks.append(item["attention_mask"])
        labels.append(item["labels"])
        sequences.append(item["sequence"])
        sample_ids.append(item["id"])
        item_metadata = item.get("metadata")
        metadata.append(item_metadata)
        border_scores.append(parse_border_score(item_metadata))
    input_ids = torch.stack(input_ids)
    attention_mask = torch.stack(attention_masks)
    labels = torch.stack([item["labels"] for item in batch])
    return {
        "input_ids": input_ids,
        "attention_mask": attention_mask,
        "labels": labels,
        "sequence": sequences,
        "id": sample_ids,
        "metadata": metadata,
        "border_scores": torch.tensor(border_scores, dtype=torch.float32),
    }


def build_tokenizer(config: Dict):
    if config["model"]["backbone_type"] != "hf":
        return None
    from transformers import AutoTokenizer

    model_cfg = config["model"]
    tokenizer_name = model_cfg.get("tokenizer_name_or_path") or model_cfg["pretrained_model_name_or_path"]
    resolved_path = Path(tokenizer_name).expanduser()
    local_files_only = resolved_path.exists()
    tokenizer = AutoTokenizer.from_pretrained(
        tokenizer_name,
        cache_dir=model_cfg.get("cache_dir"),
        trust_remote_code=model_cfg.get("trust_remote_code", False),
        local_files_only=local_files_only,
    )
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token or tokenizer.unk_token
    if tokenizer.pad_token is None:
        raise ValueError("The selected tokenizer does not define a usable pad token.")
    return tokenizer


def build_datasets(config: Dict):
    dataset_type = config["data"]["dataset_type"]
    if dataset_type == "mock":
        train_dataset = MockGenomicDataset(config["data"]["train_size"], config["data"]["seq_length"], "train")
        val_dataset = MockGenomicDataset(config["data"]["val_size"], config["data"]["seq_length"], "val")
        test_dataset = MockGenomicDataset(config["data"]["test_size"], config["data"]["seq_length"], "test")
        return train_dataset, val_dataset, test_dataset
    if dataset_type != "genomic":
        raise ValueError("Unsupported dataset_type: {0}".format(dataset_type))
    tokenizer = build_tokenizer(config)
    split_cfg = config["data"]["splits"]
    common_kwargs = {
        "seq_length": config["data"]["seq_length"],
        "sequence_column": config["data"].get("sequence_column", "sequence"),
        "label_column": config["data"].get("label_column", "label"),
        "id_column": config["data"].get("id_column", "id"),
        "metadata_column": config["data"].get("metadata_column", "metadata"),
        "tokenizer": tokenizer,
        "tokenizer_mode": config["data"].get("tokenizer_mode", "raw"),
    }
    train_dataset = GenomicSequenceDataset(split_path=split_cfg["train"], split_name="train", **common_kwargs)
    label_to_id = train_dataset.label_to_id
    val_dataset = GenomicSequenceDataset(
        split_path=split_cfg["val"],
        split_name="val",
        label_to_id=label_to_id,
        **common_kwargs
    )
    test_dataset = GenomicSequenceDataset(
        split_path=split_cfg["test"],
        split_name="test",
        label_to_id=label_to_id,
        **common_kwargs
    )
    config["task"]["num_labels"] = len(label_to_id)
    return train_dataset, val_dataset, test_dataset


def build_dataloaders(config: Dict):
    train_dataset, val_dataset, test_dataset = build_datasets(config)
    batch_size = config["train"]["batch_size"]
    num_workers = config["data"]["num_workers"]
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=num_workers, collate_fn=collate_batch)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False, num_workers=num_workers, collate_fn=collate_batch)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False, num_workers=num_workers, collate_fn=collate_batch)
    return train_loader, val_loader, test_loader


def freeze_backbone_except_adapters(model: torch.nn.Module) -> None:
    for name, parameter in model.named_parameters():
        parameter.requires_grad = ("lora_" in name) or (".gate." in name)


def freeze_backbone_except_classifier(model: torch.nn.Module) -> None:
    for name, parameter in model.named_parameters():
        parameter.requires_grad = name.startswith("classifier.")


def attach_adapter(model: torch.nn.Module, config: Dict) -> None:
    adapter_cfg = config["adapter"]
    adapter_name = adapter_cfg["name"]
    if adapter_name == "none":
        return
    if adapter_name == "linear_probe":
        freeze_backbone_except_classifier(model)
        return
    if adapter_name == "baseline_lora":
        for target_name in adapter_cfg["target_modules"]:
            attach_lora(model, target_name, adapter_cfg["rank"], adapter_cfg["alpha"], adapter_cfg["dropout"])
        freeze_backbone_except_adapters(model)
        return
    if adapter_name == "gated_lora":
        for target_name in adapter_cfg["target_modules"]:
            attach_gated_lora(model, target_name, adapter_cfg["rank"], adapter_cfg["alpha"], adapter_cfg["dropout"])
        freeze_backbone_except_adapters(model)
        return
    if adapter_name == "germ_bo":
        for target_name in adapter_cfg["target_modules"]:
            attach_germ_bo(
                model,
                target_name,
                adapter_cfg["rank"],
                adapter_cfg["alpha"],
                adapter_cfg["dropout"],
                adapter_cfg["compensation_strength"],
                adapter_cfg["compensation_clip_min"],
                adapter_cfg["compensation_clip_max"],
                adapter_cfg.get("border_score_type", "activation_abs_mean"),
            )
        freeze_backbone_except_adapters(model)
        return
    raise ValueError(f"Unsupported adapter: {adapter_name}")


def build_model_and_device(config: Dict):
    validate_single_gpu_setup(config)
    model = build_backbone(config)
    attach_adapter(model, config)
    device = resolve_device(config)
    model.to(device)
    return model, device, get_device_report(device)


def save_json(data: Dict, path: Path) -> None:
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2)


def evaluate_model(model, data_loader, device):
    model.eval()
    all_logits = []
    all_labels = []
    total_loss = 0.0
    criterion = torch.nn.CrossEntropyLoss()
    with torch.no_grad():
        for batch in data_loader:
            inputs = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            border_scores = batch.get("border_scores")
            if border_scores is not None:
                border_scores = border_scores.to(device)
            labels = batch["labels"].to(device)
            outputs = model(input_ids=inputs, attention_mask=attention_mask, border_scores=border_scores)
            logits = outputs["logits"]
            loss = criterion(logits, labels)
            total_loss += loss.item()
            all_logits.append(logits.cpu())
            all_labels.append(labels.cpu())
    logits = torch.cat(all_logits, dim=0)
    labels = torch.cat(all_labels, dim=0)
    metrics = compute_classification_metrics(logits, labels)
    metrics["loss"] = total_loss / max(len(data_loader), 1)
    return metrics
