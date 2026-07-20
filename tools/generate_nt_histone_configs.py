import copy
from pathlib import Path

import yaml

HISTONE_MARKS = [
    "H3",
    "H3K14ac",
    "H3K36me3",
    "H3K4me1",
    "H3K4me2",
    "H3K4me3",
    "H3K79me3",
    "H3K9ac",
    "H4",
    "H4ac",
]

BASELINE_TEMPLATE = {
    "seed": 42,
    "device": "cuda",
    "gpu_id": 3,
    "output_dir": "outputs",
    "results_dir": "results",
    "task": {"name": "TASK", "num_labels": 2},
    "data": {
        "dataset_type": "genomic",
        "seq_length": 512,
        "num_workers": 0,
        "sequence_column": "sequence",
        "label_column": "label",
        "id_column": "id",
        "metadata_column": "metadata",
        "tokenizer_mode": "raw",
        "splits": {
            "train": "data/benchmarks/TASK_center_jsd/train.csv",
            "val": "data/benchmarks/TASK_center_jsd/val.csv",
            "test": "data/benchmarks/TASK_center_jsd/test.csv",
        },
    },
    "model": {
        "backbone_type": "hf",
        "pretrained_model_name_or_path": "local_assets/dnabert2_117m",
        "tokenizer_name_or_path": "local_assets/dnabert2_117m",
        "cache_dir": None,
        "trust_remote_code": True,
        "attention_probs_dropout_prob": 0.1,
        "classifier_dropout": 0.1,
    },
    "adapter": {
        "name": "baseline_lora",
        "rank": 8,
        "alpha": 16,
        "dropout": 0.05,
        "target_modules": [
            "encoder.encoder.layer.0.attention.self.Wqkv",
            "encoder.encoder.layer.0.attention.output.dense",
            "encoder.encoder.layer.1.attention.self.Wqkv",
            "encoder.encoder.layer.1.attention.output.dense",
            "classifier",
        ],
    },
    "optim": {"lr": 0.0003, "weight_decay": 0.01},
    "scheduler": {"name": "none"},
    "train": {
        "epochs": 4,
        "batch_size": 4,
        "checkpoint_every": 1,
        "log_every": 50,
        "checkpoint_monitor": "accuracy",
        "checkpoint_mode": "max",
        "early_stopping_patience": 2,
        "early_stopping_min_delta": 0.0,
    },
    "debug": {
        "train_size": 32,
        "val_size": 16,
        "test_size": 16,
        "batch_size": 2,
        "epochs": 1,
        "max_steps": 4,
        "output_subdir": "debug_real_dnabert2_baseline_TASK_pilot",
    },
    "logging": {"save_predictions": True},
}

GERM_BO_TEMPLATE = copy.deepcopy(BASELINE_TEMPLATE)
GERM_BO_TEMPLATE["adapter"] = {
    "name": "germ_bo",
    "rank": 8,
    "alpha": 16,
    "dropout": 0.05,
    "target_modules": [
        "encoder.encoder.layer.0.attention.output.dense",
        "encoder.encoder.layer.1.attention.output.dense",
        "classifier",
    ],
    "compensation_strength": 0.27,
    "border_score_type": "metadata_border_score",
    "border_normalization": "mean",
    "compensation_clip_min": 0.73,
    "compensation_clip_max": 1.42,
}
GERM_BO_TEMPLATE["debug"]["output_subdir"] = "debug_real_dnabert2_germ_bo_TASK_center_jsd_pilot"


def substitute(config, task):
    text = yaml.safe_dump(config, sort_keys=False)
    return yaml.safe_load(text.replace("TASK", task))


def main():
    config_dir = Path("configs")
    config_dir.mkdir(parents=True, exist_ok=True)
    for task in HISTONE_MARKS:
        baseline_path = config_dir / f"real_dnabert2_baseline_{task}_pilot.yaml"
        germ_bo_path = config_dir / f"real_dnabert2_germ_bo_{task}_center_jsd_pilot.yaml"
        baseline_path.write_text(yaml.safe_dump(substitute(BASELINE_TEMPLATE, task), sort_keys=False), encoding="utf-8")
        germ_bo_path.write_text(yaml.safe_dump(substitute(GERM_BO_TEMPLATE, task), sort_keys=False), encoding="utf-8")
        print(baseline_path)
        print(germ_bo_path)


if __name__ == "__main__":
    main()
