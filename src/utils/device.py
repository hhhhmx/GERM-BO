import os
from typing import Dict, Union

import torch


def validate_single_gpu_setup(config: Dict) -> None:
    requested = config.get("device", "cuda")
    if requested != "cuda":
        return
    requested_gpu_id = str(config.get("gpu_id", 3))
    visible_devices = os.environ.get("CUDA_VISIBLE_DEVICES")
    if visible_devices != requested_gpu_id:
        raise EnvironmentError(
            "This project requires explicit single-GPU execution with CUDA_VISIBLE_DEVICES={0} "
            "for training and evaluation commands.".format(requested_gpu_id)
        )
    if torch.cuda.is_available() and torch.cuda.device_count() > 1:
        raise EnvironmentError(
            "More than one GPU is visible after CUDA_VISIBLE_DEVICES filtering. "
            "This repository only supports one visible GPU."
        )


def resolve_device(config: Dict) -> torch.device:
    requested = config.get("device", "cuda")
    if requested == "cuda" and torch.cuda.is_available():
        return torch.device("cuda:0")
    return torch.device("cpu")


def get_device_report(device: torch.device) -> Dict[str, Union[str, int, float, bool, None]]:
    report = {
        "torch_version": torch.__version__,
        "cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES"),
        "cuda_available": torch.cuda.is_available(),
        "visible_gpu_count": torch.cuda.device_count(),
        "selected_device": str(device),
        "selected_gpu_name": None,
        "memory_allocated_mb": None,
        "memory_reserved_mb": None,
    }
    if device.type == "cuda":
        report["selected_gpu_name"] = torch.cuda.get_device_name(device)
        report["memory_allocated_mb"] = round(torch.cuda.memory_allocated(device) / 1024 ** 2, 2)
        report["memory_reserved_mb"] = round(torch.cuda.memory_reserved(device) / 1024 ** 2, 2)
    return report
