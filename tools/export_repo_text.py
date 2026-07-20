import json
from pathlib import Path


FILES = [
    "README.md",
    "requirements.txt",
    "train.py",
    "eval.py",
    "RUN_LOG.md",
    "configs/default.yaml",
    "configs/baseline_lora.yaml",
    "configs/germ_bo.yaml",
    "configs/real_baseline_lora.yaml",
    "configs/real_germ_bo.yaml",
    "configs/real_hf_smoke_baseline.yaml",
    "data/README.md",
    "data/splits/train.csv",
    "data/splits/val.csv",
    "data/splits/test.csv",
    "outputs/.gitkeep",
    "outputs/checkpoints/.gitkeep",
    "outputs/logs/.gitkeep",
    "results/.gitkeep",
    "src/__init__.py",
    "src/train_main.py",
    "src/eval_main.py",
    "src/data/__init__.py",
    "src/data/mock_dataset.py",
    "src/data/genomic_dataset.py",
    "src/models/__init__.py",
    "src/models/backbone_loader.py",
    "src/adapters/__init__.py",
    "src/adapters/lora.py",
    "src/adapters/germ_bo.py",
    "src/utils/__init__.py",
    "src/utils/border_features.py",
    "src/utils/device.py",
    "src/utils/metrics.py",
    "src/utils/train_utils.py",
    "tools/create_hf_smoke_backbone.py",
]


def main() -> None:
    payload = {}
    for relative_path in FILES:
        payload[relative_path] = Path(relative_path).read_text(encoding="utf-8")
    print(json.dumps(payload))


if __name__ == "__main__":
    main()
