import argparse
import csv
import math
import random
import urllib.request
from collections import Counter
from pathlib import Path


CLASSES = {"negative": 0, "positive": 1}
HF_PARQUET = {
    "human_nontata_promoters": {
        "train": "https://huggingface.co/datasets/simecek/human_nontata_promoters/resolve/main/data/train-00000-of-00001-9af6936029261ba1.parquet",
        "test": "https://huggingface.co/datasets/simecek/human_nontata_promoters/resolve/main/data/test-00000-of-00001-5ba65be5fd0fb68f.parquet",
    }
}


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", default="human_nontata_promoters")
    parser.add_argument("--version", type=int, default=0)
    parser.add_argument("--output-dir", default="data/benchmarks/human_nontata_promoters_border_estimated")
    parser.add_argument("--seed", type=int, default=20260420)
    parser.add_argument("--max-train", type=int, default=2000)
    parser.add_argument("--max-val", type=int, default=500)
    parser.add_argument("--max-test", type=int, default=1000)
    parser.add_argument("--window", type=int, default=32)
    parser.add_argument("--kmer", type=int, default=2)
    parser.add_argument("--top-ratio", type=float, default=0.10)
    parser.add_argument("--score-base", type=float, default=0.75)
    parser.add_argument("--score-scale", type=float, default=3.0)
    parser.add_argument("--score-min", type=float, default=0.60)
    parser.add_argument("--score-max", type=float, default=1.50)
    parser.add_argument("--source", choices=["hf_parquet", "genomic_benchmarks"], default="hf_parquet")
    return parser.parse_args()


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


def estimate_border_score(
    sequence: str,
    window: int,
    kmer: int,
    top_ratio: float,
    score_base: float,
    score_scale: float,
    score_min: float,
    score_max: float,
) -> float:
    sequence = sequence.upper()
    if len(sequence) < 2 * window + kmer:
        return 1.0
    scores = []
    for center in range(window, len(sequence) - window + 1):
        left = sequence[center - window : center]
        right = sequence[center : center + window]
        scores.append(js_divergence(kmer_distribution(left, kmer), kmer_distribution(right, kmer)))
    if not scores:
        return 1.0
    scores.sort(reverse=True)
    top_count = max(1, int(round(len(scores) * top_ratio)))
    top_mean = sum(scores[:top_count]) / top_count
    # JSD is label-free and usually small on fixed-length genomic sequences.
    # The affine mapping keeps scores near the scale expected by GERM-BO.
    return max(score_min, min(score_max, score_base + score_scale * top_mean))


def read_class_dir(path: Path, label: int, split_name: str, args):
    records = []
    for file_path in sorted(path.glob("*.txt")):
        sequence = file_path.read_text(encoding="utf-8").strip().upper()
        invalid = sorted({base for base in sequence if base not in {"A", "C", "G", "T"}})
        if invalid:
            continue
        border_score = estimate_border_score(
            sequence,
            window=args.window,
            kmer=args.kmer,
            top_ratio=args.top_ratio,
            score_base=args.score_base,
            score_scale=args.score_scale,
            score_min=args.score_min,
            score_max=args.score_max,
        )
        records.append(
            {
                "id": f"{split_name}_{path.name}_{file_path.stem}",
                "sequence": sequence,
                "label": label,
                "metadata": (
                    f"benchmark=genomic_benchmarks;dataset=human_nontata_promoters;"
                    f"border_estimator=label_free_kmer_jsd;window={args.window};kmer={args.kmer};"
                    f"top_ratio={args.top_ratio};score_base={args.score_base};"
                    f"score_scale={args.score_scale};"
                    f"border_score={border_score:.6f}"
                ),
            }
        )
    return records


def download_file(url: str, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.stat().st_size > 0:
        return path
    urllib.request.urlretrieve(url, path)
    return path


def read_hf_parquet(dataset: str, cache_dir: Path, split_name: str, args):
    if dataset not in HF_PARQUET:
        raise ValueError(f"No Hugging Face parquet source configured for dataset: {dataset}")
    try:
        import pandas as pd
    except ImportError as error:
        raise SystemExit("Missing dependency `pandas` for Hugging Face parquet loading.") from error
    url = HF_PARQUET[dataset][split_name]
    parquet_path = download_file(url, cache_dir / f"{dataset}_{split_name}.parquet")
    frame = pd.read_parquet(parquet_path)
    records = []
    for index, row in frame.iterrows():
        sequence = str(row["seq"]).upper()
        invalid = sorted({base for base in sequence if base not in {"A", "C", "G", "T"}})
        if invalid:
            continue
        label = int(row["labels"])
        border_score = estimate_border_score(
            sequence,
            window=args.window,
            kmer=args.kmer,
            top_ratio=args.top_ratio,
            score_base=args.score_base,
            score_scale=args.score_scale,
            score_min=args.score_min,
            score_max=args.score_max,
        )
        records.append(
            {
                "id": f"{split_name}_{index}",
                "sequence": sequence,
                "label": label,
                "metadata": (
                    f"benchmark=genomic_benchmarks;dataset={dataset};source=hf_parquet;"
                    f"border_estimator=label_free_kmer_jsd;window={args.window};kmer={args.kmer};"
                    f"top_ratio={args.top_ratio};score_base={args.score_base};"
                    f"score_scale={args.score_scale};"
                    f"border_score={border_score:.6f}"
                ),
            }
        )
    return records


def sample_balanced(records, max_size, seed):
    if max_size is None or max_size <= 0 or len(records) <= max_size:
        return list(records)
    rng = random.Random(seed)
    by_label = {}
    for record in records:
        by_label.setdefault(record["label"], []).append(record)
    sampled = []
    per_label = max_size // len(by_label)
    remainder = max_size - per_label * len(by_label)
    for label in sorted(by_label):
        group = list(by_label[label])
        rng.shuffle(group)
        take = per_label + (1 if remainder > 0 else 0)
        remainder -= 1 if remainder > 0 else 0
        sampled.extend(group[:take])
    rng.shuffle(sampled)
    return sampled


def split_train_val(train_records, max_train, max_val, seed):
    rng = random.Random(seed)
    by_label = {}
    for record in train_records:
        by_label.setdefault(record["label"], []).append(record)
    train = []
    val = []
    for label in sorted(by_label):
        group = list(by_label[label])
        rng.shuffle(group)
        val_take = max_val // len(by_label)
        train_take = max_train // len(by_label)
        val.extend(group[:val_take])
        train.extend(group[val_take : val_take + train_take])
    rng.shuffle(train)
    rng.shuffle(val)
    return train, val


def write_csv(path: Path, records):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["id", "sequence", "label", "metadata"])
        writer.writeheader()
        writer.writerows(records)


def main():
    args = parse_args()
    dataset_path = None
    if args.source == "hf_parquet":
        cache_dir = Path("data/cache")
        raw_train = read_hf_parquet(args.dataset, cache_dir, "train", args)
        raw_test = read_hf_parquet(args.dataset, cache_dir, "test", args)
        dataset_path = cache_dir
    else:
        try:
            from genomic_benchmarks.loc2seq import download_dataset
        except ImportError as error:
            raise SystemExit(
                "Missing dependency `genomic-benchmarks`. Install it in the experiment "
                "environment before preparing this benchmark."
            ) from error

        dataset_path = Path(download_dataset(args.dataset, version=args.version))
        raw_train = []
        raw_test = []
        for class_name, label in CLASSES.items():
            raw_train.extend(
                read_class_dir(dataset_path / "train" / class_name, label, "train", args)
            )
            raw_test.extend(
                read_class_dir(dataset_path / "test" / class_name, label, "test", args)
            )

    train, val = split_train_val(raw_train, args.max_train, args.max_val, args.seed)
    test = sample_balanced(raw_test, args.max_test, args.seed + 1)
    output_dir = Path(args.output_dir)
    write_csv(output_dir / "train.csv", train)
    write_csv(output_dir / "val.csv", val)
    write_csv(output_dir / "test.csv", test)
    readme = output_dir / "README.md"
    readme.write_text(
        "\n".join(
            [
                "# Human Non-TATA Promoters Benchmark",
                "",
                "Source: Genomic Benchmarks `human_nontata_promoters`, version 0.",
                f"Download source used by this preparation script: `{args.source}`.",
                "Original size: 36,131 sequences, 27,097 train and 9,034 test.",
                "Task: binary human non-TATA promoter classification.",
                "",
                "This prepared split is a pilot subset for single-GPU comparison.",
                f"Prepared sizes: train={len(train)}, val={len(val)}, test={len(test)}.",
                "",
                "Border score estimator:",
                "- label-free sequence-only estimator",
                "- computes Jensen-Shannon divergence between left/right k-mer distributions",
                f"- window={args.window}, kmer={args.kmer}, top_ratio={args.top_ratio}",
                f"- score mapping: clamp({args.score_min}, {args.score_max}, {args.score_base} + {args.score_scale} * top_jsd)",
                "- stores only the resulting `border_score` in metadata",
                "- does not read or use labels",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(
        {
            "dataset_path": str(dataset_path),
            "output_dir": str(output_dir),
            "raw_train": len(raw_train),
            "raw_test": len(raw_test),
            "train": len(train),
            "val": len(val),
            "test": len(test),
        }
    )


if __name__ == "__main__":
    main()
