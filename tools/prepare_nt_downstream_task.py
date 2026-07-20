import argparse
import csv
import math
import random
from collections import Counter
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--task-name", required=True, help="NT downstream task folder name, e.g. H3K4me3")
    parser.add_argument("--train-fna", default=None)
    parser.add_argument("--test-fna", default=None)
    parser.add_argument("--download-from-hf", action="store_true")
    parser.add_argument("--hf-cache-dir", default="data/cache")
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--seed", type=int, default=20260420)
    parser.add_argument("--max-train", type=int, default=2000)
    parser.add_argument("--max-val", type=int, default=500)
    parser.add_argument("--max-test", type=int, default=1000)
    parser.add_argument("--window", type=int, default=48)
    parser.add_argument("--search-radius", type=int, default=24)
    parser.add_argument("--kmer", type=int, default=2)
    parser.add_argument("--top-ratio", type=float, default=0.25)
    parser.add_argument("--score-base", type=float, default=0.75)
    parser.add_argument("--score-scale", type=float, default=4.0)
    parser.add_argument("--score-min", type=float, default=0.60)
    parser.add_argument("--score-max", type=float, default=1.50)
    parser.add_argument(
        "--score-normalization",
        choices=["raw", "train_quantile", "train_minmax"],
        default="train_quantile",
    )
    parser.add_argument("--quantile-score-min", type=float, default=0.80)
    parser.add_argument("--quantile-score-max", type=float, default=1.20)
    return parser.parse_args()


def download_fna(task_name: str, cache_dir: Path):
    from huggingface_hub import hf_hub_download

    repo = "InstaDeepAI/nucleotide_transformer_downstream_tasks"
    local_dir = cache_dir / f"nt_{task_name}"
    train_path = hf_hub_download(
        repo,
        f"{task_name}/train.fna",
        repo_type="dataset",
        local_dir=str(local_dir),
    )
    test_path = hf_hub_download(
        repo,
        f"{task_name}/test.fna",
        repo_type="dataset",
        local_dir=str(local_dir),
    )
    return Path(train_path), Path(test_path)


def read_fna(path: Path, split_name: str):
    rows = []
    current_id = None
    current_label = None
    pieces = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            stripped = line.strip()
            if not stripped:
                continue
            if stripped.startswith(">"):
                if current_id is not None:
                    rows.append(
                        {
                            "id": f"{split_name}_{current_id}",
                            "sequence": "".join(pieces).upper(),
                            "label": current_label,
                        }
                    )
                header = stripped[1:]
                sample_id, label = header.split("|", 1)
                current_id = sample_id
                current_label = int(label)
                pieces = []
            else:
                pieces.append(stripped)
    if current_id is not None:
        rows.append(
            {
                "id": f"{split_name}_{current_id}",
                "sequence": "".join(pieces).upper(),
                "label": current_label,
            }
        )
    return rows


def kmer_distribution(sequence: str, kmer: int):
    total = max(len(sequence) - kmer + 1, 0)
    if total == 0:
        return {}
    counts = Counter(sequence[index : index + kmer] for index in range(total))
    return {key: value / total for key, value in counts.items()}


def kl_divergence(left, right):
    value = 0.0
    for key, left_prob in left.items():
        right_prob = right.get(key, 0.0)
        if left_prob > 0 and right_prob > 0:
            value += left_prob * math.log2(left_prob / right_prob)
    return value


def js_divergence(left, right):
    keys = set(left) | set(right)
    midpoint = {key: 0.5 * (left.get(key, 0.0) + right.get(key, 0.0)) for key in keys}
    return 0.5 * kl_divergence(left, midpoint) + 0.5 * kl_divergence(right, midpoint)


def center_boundary_raw_score(sequence: str, args):
    sequence = sequence.upper()
    center = len(sequence) // 2
    scores = []
    for offset in range(-args.search_radius, args.search_radius + 1):
        boundary = center + offset
        left_start = boundary - args.window
        right_end = boundary + args.window
        if left_start < 0 or right_end > len(sequence):
            continue
        left = sequence[left_start:boundary]
        right = sequence[boundary:right_end]
        scores.append(js_divergence(kmer_distribution(left, args.kmer), kmer_distribution(right, args.kmer)))
    if not scores:
        return 0.0
    scores.sort(reverse=True)
    top_count = max(1, int(round(len(scores) * args.top_ratio)))
    return sum(scores[:top_count]) / top_count


def balanced_sample(rows, max_size, seed):
    if max_size <= 0 or len(rows) <= max_size:
        return list(rows)
    rng = random.Random(seed)
    by_label = {}
    for row in rows:
        by_label.setdefault(row["label"], []).append(row)
    sampled = []
    labels = sorted(by_label)
    per_label = max_size // len(labels)
    remainder = max_size - per_label * len(labels)
    for label in labels:
        group = list(by_label[label])
        rng.shuffle(group)
        take = per_label + (1 if remainder > 0 else 0)
        remainder -= 1 if remainder > 0 else 0
        sampled.extend(group[:take])
    rng.shuffle(sampled)
    return sampled


def split_train_val(rows, max_train, max_val, seed):
    rng = random.Random(seed)
    by_label = {}
    for row in rows:
        by_label.setdefault(row["label"], []).append(row)
    train = []
    val = []
    for label in sorted(by_label):
        group = list(by_label[label])
        rng.shuffle(group)
        val_per_label = max_val // len(by_label)
        train_per_label = max_train // len(by_label)
        val.extend(group[:val_per_label])
        train.extend(group[val_per_label : val_per_label + train_per_label])
    rng.shuffle(train)
    rng.shuffle(val)
    return train, val


def empirical_quantile(value, reference_values):
    if not reference_values:
        return 0.5
    lower_or_equal = sum(1 for reference in reference_values if reference <= value)
    if len(reference_values) == 1:
        return 0.5
    return (lower_or_equal - 0.5) / len(reference_values)


def score_from_raw(raw_score, args, reference_raw_scores=None):
    if args.score_normalization == "train_quantile":
        quantile = empirical_quantile(raw_score, reference_raw_scores or [])
        return args.quantile_score_min + (args.quantile_score_max - args.quantile_score_min) * quantile
    if args.score_normalization == "train_minmax":
        reference = reference_raw_scores or []
        if not reference:
            normalized = 0.5
        else:
            min_value = min(reference)
            max_value = max(reference)
            normalized = (raw_score - min_value) / max(max_value - min_value, 1e-12)
            normalized = max(0.0, min(1.0, normalized))
        return args.quantile_score_min + (args.quantile_score_max - args.quantile_score_min) * normalized
    return max(args.score_min, min(args.score_max, args.score_base + args.score_scale * raw_score))


def add_metadata(rows, task_name, args, reference_raw_scores=None):
    out = []
    for row in rows:
        raw_score = center_boundary_raw_score(row["sequence"], args)
        score = score_from_raw(raw_score, args, reference_raw_scores)
        out.append(
            {
                "id": row["id"],
                "sequence": row["sequence"],
                "label": row["label"],
                "metadata": (
                    "benchmark=nucleotide_transformer_downstream_tasks;"
                    f"dataset={task_name};"
                    "border_estimator=center_window_kmer_jsd;"
                    f"window={args.window};search_radius={args.search_radius};"
                    f"kmer={args.kmer};top_ratio={args.top_ratio};"
                    f"score_scale={args.score_scale};score_normalization={args.score_normalization};"
                    f"raw_border_score={raw_score:.6f};border_score={score:.6f}"
                ),
            }
        )
    return out


def write_csv(path: Path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["id", "sequence", "label", "metadata"])
        writer.writeheader()
        writer.writerows(rows)


def label_counts(rows):
    counts = Counter(row["label"] for row in rows)
    return {str(key): counts[key] for key in sorted(counts)}


def main():
    args = parse_args()
    task_name = args.task_name
    output_dir = Path(args.output_dir or f"data/benchmarks/{task_name}_center_jsd")
    if args.download_from_hf:
        train_fna, test_fna = download_fna(task_name, Path(args.hf_cache_dir))
    else:
        train_fna = Path(args.train_fna or f"data/cache/nt_{task_name}/train.fna")
        test_fna = Path(args.test_fna or f"data/cache/nt_{task_name}/test.fna")

    raw_train = read_fna(train_fna, "train")
    raw_test = read_fna(test_fna, "test")
    train, val = split_train_val(raw_train, args.max_train, args.max_val, args.seed)
    test = balanced_sample(raw_test, args.max_test, args.seed + 1)
    reference_raw_scores = sorted(center_boundary_raw_score(row["sequence"], args) for row in train)
    train = add_metadata(train, task_name, args, reference_raw_scores)
    val = add_metadata(val, task_name, args, reference_raw_scores)
    test = add_metadata(test, task_name, args, reference_raw_scores)
    write_csv(output_dir / "train.csv", train)
    write_csv(output_dir / "val.csv", val)
    write_csv(output_dir / "test.csv", test)
    readme = output_dir / "README.md"
    readme.write_text(
        "\n".join(
            [
                f"# NT Downstream Task: {task_name}",
                "",
                "Source: Hugging Face `InstaDeepAI/nucleotide_transformer_downstream_tasks`.",
                "Task: binary ChIP-seq peak / regulatory-element classification.",
                "Estimator: label-free center-window k-mer Jensen-Shannon divergence with train-quantile normalization.",
                "",
                f"train={len(train)} counts={label_counts(train)}",
                f"val={len(val)} counts={label_counts(val)}",
                f"test={len(test)} counts={label_counts(test)}",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(
        {
            "task": task_name,
            "raw_train": len(raw_train),
            "raw_test": len(raw_test),
            "train": len(train),
            "val": len(val),
            "test": len(test),
            "output_dir": str(output_dir),
        }
    )


if __name__ == "__main__":
    main()
