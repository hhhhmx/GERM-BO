from pathlib import Path
import sys
import argparse

import yaml

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.models.backbone_loader import HFSequenceClassifier


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/real_baseline_lora.yaml")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config_path = Path(args.config)
    with open(config_path, "r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)
    model = HFSequenceClassifier(config)
    for name, module in model.named_modules():
        if module.__class__.__name__ == "Linear":
            print(name)


if __name__ == "__main__":
    main()
