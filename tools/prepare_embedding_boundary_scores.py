import argparse
import csv
import json
from pathlib import Path

import torch
import torch.nn.functional as F


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-dir", default="data/benchmarks/human_nontata_promoters_border_estimated_w64_k2_t10_s3")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--model-path", default="local_assets/dnabert2_117m")
    parser.add_argument("--seq-length", type=int, default=256)
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--token-window", type=int, default=8)
    parser.add_argument("--top-ratio", type=float, default=0.10)
    parser.add_argument("--score-scale", type=float, default=0.15)
    parser.add_argument("--score-min", type=float, default=0.60)
    parser.add_argument("--score-max", type=float, default=1.50)
    parser.add_argument("--device", choices=["auto", "cpu", "cuda"], default="auto")
    parser.add_argument("--embedding-source", choices=["token_embedding", "contextual"], default="token_embedding")
    parser.add_argument("--contextual-attention-dropout", type=float, default=0.1)
    return parser.parse_args()


def read_split(path: Path):
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_split(path: Path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["id", "sequence", "label", "metadata"])
        writer.writeheader()
        writer.writerows(rows)


def batch_iter(items, batch_size):
    for start in range(0, len(items), batch_size):
        yield items[start : start + batch_size]


def hidden_boundary_score(hidden, attention_mask, token_window, top_ratio):
    valid_length = int(attention_mask.sum().item())
    hidden = hidden[:valid_length]
    if valid_length < 2 * token_window + 1:
        return 0.0
    scores = []
    for center in range(token_window, valid_length - token_window + 1):
        left = hidden[center - token_window : center].mean(dim=0)
        right = hidden[center : center + token_window].mean(dim=0)
        score = 1.0 - F.cosine_similarity(left, right, dim=0).item()
        scores.append(score)
    if not scores:
        return 0.0
    scores.sort(reverse=True)
    top_count = max(1, int(round(len(scores) * top_ratio)))
    return sum(scores[:top_count]) / top_count


def resolve_word_embeddings(model):
    candidates = [
        ("embeddings", "word_embeddings"),
        ("encoder", "embeddings", "word_embeddings"),
    ]
    for candidate in candidates:
        module = model
        found = True
        for name in candidate:
            if not hasattr(module, name):
                found = False
                break
            module = getattr(module, name)
        if found:
            return module
    raise AttributeError("Could not locate word_embeddings in the pretrained backbone.")


def compute_raw_scores(rows, tokenizer, model, device, args):
    raw_scores = {}
    model.eval()
    word_embeddings = resolve_word_embeddings(model) if args.embedding_source == "token_embedding" else None
    with torch.no_grad():
        for batch in batch_iter(rows, args.batch_size):
            sequences = [row["sequence"] for row in batch]
            encoded = tokenizer(
                sequences,
                truncation=True,
                max_length=args.seq_length,
                padding=True,
                return_tensors="pt",
            )
            input_ids = encoded["input_ids"].to(device)
            attention_mask = encoded["attention_mask"].to(device)
            if args.embedding_source == "token_embedding":
                hidden_states = word_embeddings(input_ids)
            else:
                outputs = model(input_ids=input_ids, attention_mask=attention_mask)
                hidden_states = outputs[0] if isinstance(outputs, tuple) else outputs.last_hidden_state
            for index, row in enumerate(batch):
                raw_scores[row["id"]] = hidden_boundary_score(
                    hidden_states[index].detach().cpu(),
                    attention_mask[index].detach().cpu(),
                    token_window=args.token_window,
                    top_ratio=args.top_ratio,
                )
    return raw_scores


def normalize_score(raw_score, train_mean, train_std, args):
    if train_std <= 1e-8:
        return 1.0
    score = 1.0 + args.score_scale * ((raw_score - train_mean) / train_std)
    return max(args.score_min, min(args.score_max, score))


def add_metadata(rows, raw_scores, train_mean, train_std, args):
    output = []
    for row in rows:
        raw_score = raw_scores[row["id"]]
        border_score = normalize_score(raw_score, train_mean, train_std, args)
        metadata = (
            "benchmark=genomic_benchmarks;dataset=human_nontata_promoters;"
            "border_estimator=frozen_dnabert2_embedding_shift;"
            f"token_window={args.token_window};top_ratio={args.top_ratio};"
            f"score_scale={args.score_scale};raw_score={raw_score:.6f};"
            f"border_score={border_score:.6f}"
        )
        output.append(
            {
                "id": row["id"],
                "sequence": row["sequence"],
                "label": row["label"],
                "metadata": metadata,
            }
        )
    return output


def main():
    args = parse_args()
    from transformers import AutoConfig, AutoModel, AutoTokenizer

    source_dir = Path(args.source_dir)
    output_dir = Path(args.output_dir)
    splits = {name: read_split(source_dir / f"{name}.csv") for name in ["train", "val", "test"]}
    resolved_model_path = Path(args.model_path).expanduser()
    local_files_only = resolved_model_path.exists()
    tokenizer = AutoTokenizer.from_pretrained(
        args.model_path,
        trust_remote_code=True,
        local_files_only=local_files_only,
    )
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token or tokenizer.unk_token
    config = AutoConfig.from_pretrained(
        args.model_path,
        trust_remote_code=True,
        local_files_only=local_files_only,
    )
    if args.embedding_source == "contextual" and hasattr(config, "attention_probs_dropout_prob"):
        # DNABERT-2 uses flash attention only when this value is zero. Setting a
        # non-zero value forces the ordinary PyTorch attention path while the
        # model remains frozen and in eval mode.
        config.attention_probs_dropout_prob = args.contextual_attention_dropout
    model = AutoModel.from_pretrained(
        args.model_path,
        config=config,
        trust_remote_code=True,
        local_files_only=local_files_only,
    )
    if args.device == "auto":
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    else:
        device = torch.device(args.device)
    model.to(device)
    raw_scores = {}
    for split_name in ["train", "val", "test"]:
        raw_scores[split_name] = compute_raw_scores(splits[split_name], tokenizer, model, device, args)
    train_values = list(raw_scores["train"].values())
    train_mean = sum(train_values) / max(len(train_values), 1)
    train_var = sum((value - train_mean) ** 2 for value in train_values) / max(len(train_values), 1)
    train_std = train_var ** 0.5
    for split_name in ["train", "val", "test"]:
        write_split(
            output_dir / f"{split_name}.csv",
            add_metadata(splits[split_name], raw_scores[split_name], train_mean, train_std, args),
        )
    summary = {
        "source_dir": str(source_dir),
        "output_dir": str(output_dir),
        "model_path": args.model_path,
        "seq_length": args.seq_length,
        "token_window": args.token_window,
        "top_ratio": args.top_ratio,
        "score_scale": args.score_scale,
        "embedding_source": args.embedding_source,
        "contextual_attention_dropout": args.contextual_attention_dropout,
        "train_raw_mean": train_mean,
        "train_raw_std": train_std,
        "sizes": {name: len(rows) for name, rows in splits.items()},
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "score_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    (output_dir / "README.md").write_text(
        "\n".join(
            [
                "# Frozen DNABERT-2 Embedding Boundary Scores",
                "",
                "This split reuses the same sequences/labels as the human non-TATA promoter pilot.",
                "Only metadata `border_score` is replaced.",
                "",
                "Estimator:",
                "- frozen pretrained DNABERT-2",
                "- no label input",
                f"- embedding source: {args.embedding_source}",
                "- token-level left/right window mean embedding cosine distance",
                "- top-window aggregation per sequence",
                "- train-split z-score normalization applied to all splits",
                "",
                json.dumps(summary, indent=2),
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
