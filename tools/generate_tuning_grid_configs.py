from pathlib import Path


BASE = """seed: 42
device: cuda
gpu_id: 3
output_dir: outputs
results_dir: results
task:
  name: genomic_sequence_classification
  num_labels: 2
data:
  dataset_type: genomic
  seq_length: 128
  num_workers: 0
  sequence_column: sequence
  label_column: label
  id_column: id
  metadata_column: metadata
  tokenizer_mode: raw
  splits:
    train: data/splits_border_{task}/train.csv
    val: data/splits_border_{task}/val.csv
    test: data/splits_border_{task}/test.csv
model:
  backbone_type: hf
  pretrained_model_name_or_path: local_assets/dnabert2_117m
  tokenizer_name_or_path: local_assets/dnabert2_117m
  cache_dir: null
  trust_remote_code: true
  attention_probs_dropout_prob: 0.1
  classifier_dropout: 0.1
adapter:
  name: germ_bo
  rank: 8
  alpha: 16
  dropout: 0.05
  target_modules:
    - encoder.encoder.layer.0.attention.output.dense
    - encoder.encoder.layer.1.attention.output.dense
    - classifier
  compensation_strength: {strength:.2f}
  border_score_type: normalized_border_length
  border_normalization: mean
  compensation_clip_min: {clip_min:.2f}
  compensation_clip_max: {clip_max:.2f}
optim:
  lr: 0.0003
  weight_decay: 0.01
scheduler:
  name: none
train:
  epochs: 12
  batch_size: 4
  checkpoint_every: 1
  log_every: 10
  checkpoint_monitor: accuracy
  checkpoint_mode: max
  early_stopping_patience: 4
  early_stopping_min_delta: 0.0
debug:
  train_size: 32
  val_size: 16
  test_size: 16
  batch_size: 2
  epochs: 1
  max_steps: 4
  output_subdir: debug_real_dnabert2_germ_bo_border_{task}_comp{tag}_p4
logging:
  save_predictions: true
"""


GRID = {
    "015": (0.15, 0.85, 1.30),
    "020": (0.20, 0.80, 1.35),
    "025": (0.25, 0.75, 1.40),
    "027": (0.27, 0.73, 1.42),
}


def main():
    out = Path("configs")
    for task in ("medium", "hard"):
        for tag, (strength, clip_min, clip_max) in GRID.items():
            path = out / f"real_dnabert2_germ_bo_border_{task}_comp{tag}_p4_tuning.yaml"
            path.write_text(
                BASE.format(
                    task=task,
                    tag=tag,
                    strength=strength,
                    clip_min=clip_min,
                    clip_max=clip_max,
                ),
                encoding="utf-8",
            )
            print(path)


if __name__ == "__main__":
    main()
