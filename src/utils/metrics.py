from typing import Dict, Optional

import torch


def compute_classification_metrics(logits: torch.Tensor, labels: torch.Tensor) -> Dict[str, Optional[float]]:
    predictions = logits.argmax(dim=-1)
    accuracy = (predictions == labels).float().mean().item()
    true_positive = ((predictions == 1) & (labels == 1)).sum().item()
    false_positive = ((predictions == 1) & (labels == 0)).sum().item()
    false_negative = ((predictions == 0) & (labels == 1)).sum().item()
    precision = true_positive / max(true_positive + false_positive, 1)
    recall = true_positive / max(true_positive + false_negative, 1)
    f1 = 2 * precision * recall / max(precision + recall, 1e-8)
    return {"accuracy": accuracy, "f1": f1, "auroc": None}
