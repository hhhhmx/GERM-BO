import argparse
import csv
import math
import random
from collections import Counter, defaultdict
from itertools import product
from pathlib import Path


ALPHABET = "ACGT"
THREE_MERS = ["".join(item) for item in product(ALPHABET, repeat=3)]


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--train-fna", default="data/cache/splice_sites_all_train.fna")
    parser.add_argument("--test-fna", default="data/cache/splice_sites_all_test.fna")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--seed", type=int, default=20260424)
    parser.add_argument("--max-train", type=int, default=9000)
    parser.add_argument("--max-val", type=int, default=1800)
    parser.add_argument("--max-test", type=int, default=3000)
    parser.add_argument("--match-mode", choices=["gc_matched", "kmer_balanced"], required=True)
    parser.add_argument("--gc-bins", type=int, default=20)
    parser.add_argument("--match-kmer", type=int, default=3)
    parser.add_argument("--window", type=int, default=48)
    parser.add_argument("--search-radius", type=int, default=24)
    parser.add_argument("--kmer", type=int, default=2)
    parser.add_argument("--top-ratio", type=float, default=0.25)
    parser.add_argument("--score-base", type=float, default=0.75)
    parser.add_argument("--score-scale", type=float, default=4.0)
    parser.add_argument("--score-min", type=float, default=0.60)
    parser.add_argument("--score-max", type=float, default=1.50)
    parser.add_argument("--score-normalization", choices=["raw", "train_quantile", "train_minmax"], default="train_quantile")
    parser.add_argument("--quantile-score-min", type=float, default=0.80)
    parser.add_argument("--quantile-score-max", type=float, default=1.20)
    parser.add_argument("--estimator", choices=["center_jsd", "center_jsd_motif"], default="center_jsd")
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
    return sum(scores[:top_count]) / top_count


def splice_motif_score(sequence: str, center: int, radius: int):
    start = max(0, center - radius)
    end = min(len(sequence), center + radius)
    if end - start < 2:
        return 0.0
    window = sequence[start:end]
    dinucs = max(len(window) - 1, 1)
    motif_hits = sum(1 for index in range(dinucs) if window[index : index + 2] in {"GT", "AG"})
    return motif_hits / dinucs


def empirical_quantile(value, reference_values):
    if not reference_values:
        return 0.5
    lower_or_equal = 0
    for reference in reference_values:
        if reference <= value:
            lower_or_equal += 1
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


def gc_fraction(sequence: str):
    if not sequence:
        return 0.0
    return sum(1 for char in sequence if char in {"G", "C"}) / len(sequence)


def gc_bucket(sequence: str, bins: int):
    return min(bins - 1, int(gc_fraction(sequence) * bins))


def dominant_kmer(sequence: str, kmer: int):
    total = max(len(sequence) - kmer + 1, 0)
    if total <= 0:
        return "NA"
    counts = Counter(sequence[index : index + kmer] for index in range(total))
    return max(counts.items(), key=lambda item: (item[1], item[0]))[0]


def match_key(row, args):
    gc_bin = gc_bucket(row["sequence"], args.gc_bins)
    if args.match_mode == "gc_matched":
        return (gc_bin,)
    return (gc_bin, dominant_kmer(row["sequence"], args.match_kmer))


def choose_shared_quotas(rows, per_label_target, args, seed):
    rng = random.Random(seed)
    labels = sorted({row["label"] for row in rows})
    by_label_key = {label: defaultdict(list) for label in labels}
    for row in rows:
        by_label_key[row["label"]][match_key(row, args)].append(row)
    quotas = {}
    for key in set().union(*[set(key_map.keys()) for key_map in by_label_key.values()]):
        shared = min(len(by_label_key[label].get(key, [])) for label in labels)
        if shared > 0:
            quotas[key] = shared
    shared_total = sum(quotas.values())
    if shared_total < per_label_target:
        raise RuntimeError(
            f"{args.match_mode} shared overlap only supports {shared_total} examples per label, "
            f"but target is {per_label_target}."
        )
    expanded_keys = []
    for key, count in quotas.items():
        expanded_keys.extend([key] * count)
    rng.shuffle(expanded_keys)
    selected_keys = expanded_keys[:per_label_target]
    selected_quota = Counter(selected_keys)
    selected_rows = []
    for label in labels:
        key_to_rows = by_label_key[label]
        for key in key_to_rows:
            rng.shuffle(key_to_rows[key])
        for key, take in selected_quota.items():
            selected_rows.extend(key_to_rows[key][:take])
    rng.shuffle(selected_rows)
    return selected_rows, quotas, selected_quota, shared_total


def split_train_val_from_matched(rows, train_per_label, val_per_label, args, seed):
    rng = random.Random(seed)
    labels = sorted({row["label"] for row in rows})
    by_label_key = {label: defaultdict(list) for label in labels}
    for row in rows:
        by_label_key[row["label"]][match_key(row, args)].append(row)
    reference_label = labels[0]
    expanded_keys = []
    for key, items in by_label_key[reference_label].items():
        expanded_keys.extend([key] * len(items))
    rng.shuffle(expanded_keys)
    val_keys = Counter(expanded_keys[:val_per_label])
    train_keys = Counter(expanded_keys[val_per_label : val_per_label + train_per_label])
    train_rows = []
    val_rows = []
    for label in labels:
        for key in by_label_key[label]:
            rng.shuffle(by_label_key[label][key])
        for key, take in val_keys.items():
            val_rows.extend(by_label_key[label][key][:take])
        for key, take in train_keys.items():
            start = val_keys.get(key, 0)
            train_rows.extend(by_label_key[label][key][start : start + take])
    rng.shuffle(train_rows)
    rng.shuffle(val_rows)
    return train_rows, val_rows


def add_metadata(rows, args, reference_raw_scores=None):
    out = []
    for row in rows:
        raw_score = center_boundary_raw_score(row["sequence"], args)
        score = score_from_raw(raw_score, row["sequence"], args, reference_raw_scores)
        matching_signature = match_key(row, args)
        out.append(
            {
                "id": row["id"],
                "sequence": row["sequence"],
                "label": row["label"],
                "metadata": (
                    "benchmark=nucleotide_transformer_downstream_tasks;"
                    "dataset=splice_sites_all;"
                    f"matching={args.match_mode};"
                    f"matching_signature={matching_signature};"
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
    return {str(label): counts[label] for label in sorted(counts)}


def signature_preview(rows, args, limit=10):
    counts = Counter(match_key(row, args) for row in rows)
    top = counts.most_common(limit)
    return ", ".join(f"{key}:{value}" for key, value in top)


def gc_summary(rows):
    by_label = defaultdict(list)
    for row in rows:
        by_label[row["label"]].append(gc_fraction(row["sequence"]))
    parts = []
    for label in sorted(by_label):
        values = by_label[label]
        mean_value = sum(values) / max(len(values), 1)
        parts.append(f"label{label}={mean_value:.4f}")
    return ", ".join(parts)


def main():
    args = parse_args()
    train_per_label = args.max_train // 3
    val_per_label = args.max_val // 3
    test_per_label = args.max_test // 3

    raw_train = read_fna(Path(args.train_fna), "train")
    raw_test = read_fna(Path(args.test_fna), "test")

    matched_train_pool, train_quotas, train_selected_quota, train_shared_total = choose_shared_quotas(
        raw_train,
        train_per_label + val_per_label,
        args,
        args.seed,
    )
    matched_test, test_quotas, test_selected_quota, test_shared_total = choose_shared_quotas(
        raw_test,
        test_per_label,
        args,
        args.seed + 1,
    )
    train_rows, val_rows = split_train_val_from_matched(
        matched_train_pool,
        train_per_label,
        val_per_label,
        args,
        args.seed + 2,
    )
    reference_raw_scores = sorted(center_boundary_raw_score(row["sequence"], args) for row in train_rows)
    train_rows = add_metadata(train_rows, args, reference_raw_scores)
    val_rows = add_metadata(val_rows, args, reference_raw_scores)
    test_rows = add_metadata(matched_test, args, reference_raw_scores)

    output_dir = Path(args.output_dir)
    write_csv(output_dir / "train.csv", train_rows)
    write_csv(output_dir / "val.csv", val_rows)
    write_csv(output_dir / "test.csv", test_rows)

    readme = output_dir / "README.md"
    readme.write_text(
        "\n".join(
            [
                f"# Splice Sites All {args.match_mode}",
                "",
                "Source: Hugging Face `InstaDeepAI/nucleotide_transformer_downstream_tasks/splice_sites_all`.",
                "Task: 3-class splice-site classification.",
                f"match_mode={args.match_mode}",
                f"gc_bins={args.gc_bins}",
                f"match_kmer={args.match_kmer}",
                f"train_shared_overlap_per_label={train_shared_total}",
                f"test_shared_overlap_per_label={test_shared_total}",
                f"train_selected_signature_total={sum(train_selected_quota.values())}",
                f"test_selected_signature_total={sum(test_selected_quota.values())}",
                f"train_gc_mean={gc_summary(train_rows)}",
                f"val_gc_mean={gc_summary(val_rows)}",
                f"test_gc_mean={gc_summary(test_rows)}",
                f"train_signature_preview={signature_preview(train_rows, args)}",
                f"test_signature_preview={signature_preview(test_rows, args)}",
                "",
                f"train={len(train_rows)} counts={label_counts(train_rows)}",
                f"val={len(val_rows)} counts={label_counts(val_rows)}",
                f"test={len(test_rows)} counts={label_counts(test_rows)}",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(
        {
            "match_mode": args.match_mode,
            "train_shared_overlap_per_label": train_shared_total,
            "test_shared_overlap_per_label": test_shared_total,
            "train": len(train_rows),
            "val": len(val_rows),
            "test": len(test_rows),
            "train_counts": label_counts(train_rows),
            "val_counts": label_counts(val_rows),
            "test_counts": label_counts(test_rows),
            "output_dir": str(output_dir),
        }
    )


if __name__ == "__main__":
    main()
