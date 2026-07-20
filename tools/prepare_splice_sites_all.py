import argparse
import csv
import math
import random
from collections import Counter
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--train-fna", default="data/cache/splice_sites_all_train.fna")
    parser.add_argument("--test-fna", default="data/cache/splice_sites_all_test.fna")
    parser.add_argument("--output-dir", default="data/benchmarks/splice_sites_all_center_jsd")
    parser.add_argument("--seed", type=int, default=20260420)
    parser.add_argument("--max-train", type=int, default=3000)
    parser.add_argument("--max-val", type=int, default=600)
    parser.add_argument("--max-test", type=int, default=1200)
    parser.add_argument("--window", type=int, default=48)
    parser.add_argument("--search-radius", type=int, default=24)
    parser.add_argument("--kmer", type=int, default=2)
    parser.add_argument("--top-ratio", type=float, default=0.25)
    parser.add_argument("--score-base", type=float, default=0.75)
    parser.add_argument("--score-scale", type=float, default=4.0)
    parser.add_argument("--score-min", type=float, default=0.60)
    parser.add_argument("--score-max", type=float, default=1.50)
    parser.add_argument("--score-normalization", choices=["raw", "train_quantile", "train_minmax"], default="raw")
    parser.add_argument("--quantile-score-min", type=float, default=0.80)
    parser.add_argument("--quantile-score-max", type=float, default=1.20)
    parser.add_argument(
        "--estimator",
        choices=["center_jsd", "center_jsd_motif"],
        default="center_jsd",
    )
    parser.add_argument("--motif-weight", type=float, default=0.0)
    parser.add_argument("--motif-radius", type=int, default=12)
    return parser.parse_args()


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
    raw_score = sum(scores[:top_count]) / top_count
    return raw_score


def center_boundary_score(sequence: str, args):
    sequence = sequence.upper()
    center = len(sequence) // 2
    raw_score = center_boundary_raw_score(sequence, args)
    motif_score = 0.0
    if args.estimator == "center_jsd_motif" and args.motif_weight > 0:
        motif_score = splice_motif_score(sequence, center, args.motif_radius)
    score = args.score_base + args.score_scale * raw_score + args.motif_weight * motif_score
    return max(args.score_min, min(args.score_max, score))


def splice_motif_score(sequence: str, center: int, radius: int):
    """Label-free biological prior: GT/AG motif concentration near the shared center."""
    start = max(0, center - radius)
    end = min(len(sequence), center + radius)
    if end - start < 2:
        return 0.0
    window = sequence[start:end]
    dinucs = max(len(window) - 1, 1)
    motif_hits = sum(1 for index in range(dinucs) if window[index : index + 2] in {"GT", "AG"})
    return motif_hits / dinucs


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
    labels = sorted(by_label)
    train_per_label = max_train // len(labels)
    val_per_label = max_val // len(labels)
    for label in labels:
        group = list(by_label[label])
        rng.shuffle(group)
        val.extend(group[:val_per_label])
        train.extend(group[val_per_label : val_per_label + train_per_label])
    rng.shuffle(train)
    rng.shuffle(val)
    return train, val


def empirical_quantile(value, reference_values):
    if not reference_values:
        return 0.5
    lower_or_equal = 0
    for reference in reference_values:
        if reference <= value:
            lower_or_equal += 1
    if len(reference_values) == 1:
        return 0.5
    return (lower_or_equal - 0.5) / len(reference_values)


def score_from_raw(raw_score, sequence, args, reference_raw_scores=None):
    center = len(sequence) // 2
    motif_score = 0.0
    if args.estimator == "center_jsd_motif" and args.motif_weight > 0:
        motif_score = splice_motif_score(sequence, center, args.motif_radius)
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
    return max(args.score_min, min(args.score_max, args.score_base + args.score_scale * raw_score + args.motif_weight * motif_score))


def add_metadata(rows, args, reference_raw_scores=None):
    out = []
    for row in rows:
        raw_score = center_boundary_raw_score(row["sequence"], args)
        score = score_from_raw(raw_score, row["sequence"], args, reference_raw_scores)
        out.append(
            {
                "id": row["id"],
                "sequence": row["sequence"],
                "label": row["label"],
                "metadata": (
                    "benchmark=nucleotide_transformer_downstream_tasks;"
                    "dataset=splice_sites_all;"
                    "border_estimator=center_window_kmer_jsd;"
                    f"estimator={args.estimator};"
                    f"window={args.window};search_radius={args.search_radius};"
                    f"kmer={args.kmer};top_ratio={args.top_ratio};"
                    f"score_scale={args.score_scale};motif_weight={args.motif_weight};"
                    f"motif_radius={args.motif_radius};score_normalization={args.score_normalization};"
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
    raw_train = read_fna(Path(args.train_fna), "train")
    raw_test = read_fna(Path(args.test_fna), "test")
    train, val = split_train_val(raw_train, args.max_train, args.max_val, args.seed)
    test = balanced_sample(raw_test, args.max_test, args.seed + 1)
    reference_raw_scores = sorted(center_boundary_raw_score(row["sequence"], args) for row in train)
    train = add_metadata(train, args, reference_raw_scores)
    val = add_metadata(val, args, reference_raw_scores)
    test = add_metadata(test, args, reference_raw_scores)
    output_dir = Path(args.output_dir)
    write_csv(output_dir / "train.csv", train)
    write_csv(output_dir / "val.csv", val)
    write_csv(output_dir / "test.csv", test)
    readme = output_dir / "README.md"
    readme.write_text(
        "\n".join(
            [
                "# Splice Sites All Center-JSD Benchmark",
                "",
                "Source: Hugging Face `InstaDeepAI/nucleotide_transformer_downstream_tasks/splice_sites_all`.",
                "Task: 3-class splice-site classification.",
                "Estimator: label-free center-window k-mer Jensen-Shannon divergence.",
                "Optional splice-specific variant adds a label-free GT/AG motif prior near the shared center.",
                "The estimator uses the benchmark's shared center-position prior for all samples, but never reads labels.",
                f"estimator={args.estimator}",
                f"window={args.window} search_radius={args.search_radius} kmer={args.kmer} top_ratio={args.top_ratio}",
                f"score_base={args.score_base} score_scale={args.score_scale} motif_weight={args.motif_weight}",
                f"score_normalization={args.score_normalization}",
                f"quantile_score_min={args.quantile_score_min} quantile_score_max={args.quantile_score_max}",
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
            "raw_train": len(raw_train),
            "raw_test": len(raw_test),
            "train": len(train),
            "val": len(val),
            "test": len(test),
            "train_counts": label_counts(train),
            "val_counts": label_counts(val),
            "test_counts": label_counts(test),
            "output_dir": str(output_dir),
        }
    )


if __name__ == "__main__":
    main()
