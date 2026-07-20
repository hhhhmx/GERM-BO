import argparse
import csv
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.utils.border_features import normalized_border_length


BACKGROUND_PATTERNS = ("ACGT", "TGCA", "CATG", "GTAC", "AGCT", "TCGA")
HIGH_BORDER_MOTIFS = ("ATATAT", "TATATA", "AATAAT")
LOW_BORDER_MOTIFS = ("ACGTGA", "CGTACC", "GACTTC")
DISTRACTORS = ("GCGT", "CGCG", "TATA", "AGGA")


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--task", choices=["primary", "hard_border", "border_easy", "border_medium", "border_hard"], required=True)
    parser.add_argument("--train-size", type=int, default=512)
    parser.add_argument("--val-size", type=int, default=128)
    parser.add_argument("--test-size", type=int, default=128)
    parser.add_argument("--seq-length", type=int, default=128)
    parser.add_argument("--seed", type=int, default=1101)
    return parser.parse_args()


def fill_background(seq_length: int, rng: random.Random) -> list[str]:
    chars: list[str] = []
    while len(chars) < seq_length:
        chars.extend(list(rng.choice(BACKGROUND_PATTERNS)))
    return chars[:seq_length]


def insert_token(chars: list[str], token: str, start: int) -> None:
    for offset, char in enumerate(token):
        position = start + offset
        if 0 <= position < len(chars):
            chars[position] = char


def bounded_start(base_start: int, token_length: int, seq_length: int, rng: random.Random, jitter: int) -> int:
    limit = max(seq_length - token_length, 0)
    return max(0, min(limit, base_start + rng.randint(-jitter, jitter)))


def build_primary_sample(label: int, seq_length: int, rng: random.Random) -> tuple[str, str]:
    chars = fill_background(seq_length, rng)
    motif_pool = HIGH_BORDER_MOTIFS if label == 1 else LOW_BORDER_MOTIFS
    motif = rng.choice(motif_pool)
    repeat_count = rng.randint(2, 4) if label == 1 else 1
    anchor = rng.randint(seq_length // 4, seq_length // 2)
    for repeat_index in range(repeat_count):
        start = bounded_start(anchor + repeat_index * 3, len(motif), seq_length, rng, jitter=2)
        insert_token(chars, motif, start)
    distractor_count = 1 if label == 1 else rng.randint(2, 3)
    for distractor_index in range(distractor_count):
        distractor = DISTRACTORS[(distractor_index + label) % len(DISTRACTORS)]
        base_start = (distractor_index * 11 + label * 7) % max(seq_length - len(distractor), 1)
        start = bounded_start(base_start, len(distractor), seq_length, rng, jitter=3)
        insert_token(chars, distractor, start)
    metadata = "task=primary;border_score={0:.3f};motif={1};repeats={2}".format(
        normalized_border_length(motif),
        motif,
        repeat_count,
    )
    return "".join(chars), metadata


def build_hard_border_sample(label: int, seq_length: int, rng: random.Random) -> tuple[str, str]:
    chars = fill_background(seq_length, rng)
    motif_pool = HIGH_BORDER_MOTIFS if label == 1 else LOW_BORDER_MOTIFS
    motif = rng.choice(motif_pool)
    repeat_count = rng.randint(2, 4)
    anchor = rng.randint(seq_length // 5, seq_length // 2)
    for repeat_index in range(repeat_count):
        step = rng.randint(2, 4)
        start = bounded_start(anchor + repeat_index * step, len(motif), seq_length, rng, jitter=2)
        insert_token(chars, motif, start)
    distractor_count = rng.randint(2, 3)
    for distractor_index in range(distractor_count):
        distractor = DISTRACTORS[(distractor_index + repeat_count) % len(DISTRACTORS)]
        base_start = (distractor_index * 13 + repeat_count * 5) % max(seq_length - len(distractor), 1)
        start = bounded_start(base_start, len(distractor), seq_length, rng, jitter=4)
        insert_token(chars, distractor, start)
    metadata = "task=hard_border;border_score={0:.3f};motif={1};repeats={2}".format(
        normalized_border_length(motif),
        motif,
        repeat_count,
    )
    return "".join(chars), metadata


def build_border_difficulty_sample(task: str, label: int, seq_length: int, rng: random.Random) -> tuple[str, str]:
    chars = fill_background(seq_length, rng)
    motif_pool = HIGH_BORDER_MOTIFS if label == 1 else LOW_BORDER_MOTIFS
    motif = rng.choice(motif_pool)
    if task == "border_easy":
        repeat_count = 1 if label == 0 else rng.randint(3, 4)
        step_range = (5, 7)
        jitter = 1
        distractor_count = 1 if label == 1 else 2
    elif task == "border_medium":
        repeat_count = rng.randint(2, 4) if label == 1 else rng.randint(1, 3)
        step_range = (3, 5)
        jitter = 2
        distractor_count = 2
    elif task == "border_hard":
        repeat_count = rng.randint(2, 4)
        step_range = (2, 4)
        jitter = 3
        distractor_count = rng.randint(2, 3)
    else:
        raise ValueError(f"Unsupported border difficulty task: {task}")

    anchor = rng.randint(seq_length // 5, seq_length // 2)
    for repeat_index in range(repeat_count):
        step = rng.randint(*step_range)
        start = bounded_start(anchor + repeat_index * step, len(motif), seq_length, rng, jitter=jitter)
        insert_token(chars, motif, start)

    for distractor_index in range(distractor_count):
        if task == "border_easy":
            distractor = DISTRACTORS[(distractor_index + label) % len(DISTRACTORS)]
        else:
            distractor = rng.choice(DISTRACTORS)
        base_start = (distractor_index * 13 + repeat_count * 5 + label * 7) % max(seq_length - len(distractor), 1)
        start = bounded_start(base_start, len(distractor), seq_length, rng, jitter=jitter + 1)
        insert_token(chars, distractor, start)

    metadata = "task={0};border_score={1:.3f};motif={2};repeats={3}".format(
        task,
        normalized_border_length(motif),
        motif,
        repeat_count,
    )
    return "".join(chars), metadata


def build_sample(task: str, label: int, seq_length: int, rng: random.Random) -> tuple[str, str]:
    if task == "primary":
        return build_primary_sample(label, seq_length, rng)
    if task == "hard_border":
        return build_hard_border_sample(label, seq_length, rng)
    if task in {"border_easy", "border_medium", "border_hard"}:
        return build_border_difficulty_sample(task=task, label=label, seq_length=seq_length, rng=rng)
    raise ValueError(f"Unsupported task: {task}")


def write_split(path: Path, task: str, split_name: str, size: int, seq_length: int, seed: int) -> None:
    rng = random.Random(seed)
    with open(path, "w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["id", "sequence", "label", "metadata"])
        for index in range(size):
            label = index % 2
            sequence, metadata = build_sample(task=task, label=label, seq_length=seq_length, rng=rng)
            writer.writerow([f"{split_name}-{index}", sequence, label, metadata])


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    settings = {
        "train.csv": ("train", args.train_size, args.seq_length, args.seed),
        "val.csv": ("val", args.val_size, args.seq_length, args.seed + 100),
        "test.csv": ("test", args.test_size, args.seq_length, args.seed + 200),
    }
    for filename, (split_name, size, seq_length, seed) in settings.items():
        write_split(output_dir / filename, task=args.task, split_name=split_name, size=size, seq_length=seq_length, seed=seed)
    print(f"Generated {args.task} train/val/test CSV splits under {output_dir.as_posix()}")


if __name__ == "__main__":
    main()
