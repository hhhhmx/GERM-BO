import argparse
import csv
import random
from pathlib import Path


def deranged(values, rng):
    if len(values) < 2:
        return list(values)
    indices = list(range(len(values)))
    for _ in range(1000):
        shuffled = indices[:]
        rng.shuffle(shuffled)
        if all(source != target for source, target in zip(indices, shuffled)):
            return [values[index] for index in shuffled]
    # Fallback rotation is a deterministic derangement for len >= 2.
    return values[1:] + values[:1]


def shuffle_split(input_path, output_path, rng):
    with input_path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
        fieldnames = handle.seek(0) or None
    with input_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = reader.fieldnames
    if not rows:
        raise ValueError(f"Empty split: {input_path}")
    if "metadata" not in rows[0]:
        raise ValueError(f"Missing metadata column: {input_path}")
    metadata_values = [row["metadata"] for row in rows]
    shuffled_metadata = deranged(metadata_values, rng)
    unchanged = 0
    for row, metadata in zip(rows, shuffled_metadata):
        if row["metadata"] == metadata:
            unchanged += 1
        row["metadata"] = metadata
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return {"rows": len(rows), "unchanged_metadata_positions": unchanged}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tasks", nargs="+", default=["medium", "hard"])
    parser.add_argument("--seed", type=int, default=20260419)
    parser.add_argument("--data-root", default="data")
    args = parser.parse_args()

    rng = random.Random(args.seed)
    for task in args.tasks:
        input_dir = Path(args.data_root) / f"splits_border_{task}"
        output_dir = Path(args.data_root) / f"splits_border_{task}_metadata_shuffled"
        for split in ["train", "val", "test"]:
            stats = shuffle_split(input_dir / f"{split}.csv", output_dir / f"{split}.csv", rng)
            print(f"{task}/{split}: {stats}")


if __name__ == "__main__":
    main()
