import argparse
import csv
import random
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--seed", type=int, default=20260421)
    return parser.parse_args()


def read_rows(path):
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_rows(path, rows, fieldnames):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def shuffle_metadata(rows, seed):
    rng = random.Random(seed)
    metadata = [row["metadata"] for row in rows]
    rng.shuffle(metadata)
    out = []
    for row, shuffled in zip(rows, metadata):
        copied = dict(row)
        copied["metadata"] = shuffled
        out.append(copied)
    return out


def main():
    args = parse_args()
    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    summaries = []
    for offset, split in enumerate(["train", "val", "test"]):
        rows = read_rows(input_dir / f"{split}.csv")
        shuffled = shuffle_metadata(rows, args.seed + offset)
        write_rows(output_dir / f"{split}.csv", shuffled, rows[0].keys())
        changed = sum(1 for before, after in zip(rows, shuffled) if before["metadata"] != after["metadata"])
        summaries.append(f"{split}: rows={len(rows)} metadata_changed={changed}")
    (output_dir / "README.md").write_text(
        "\n".join(
            [
                "# Shuffled Metadata Split",
                "",
                f"Source: `{input_dir}`",
                "Sequences and labels are unchanged; metadata strings are shuffled within each split.",
                "Purpose: test whether metadata-estimated GERM-BO depends on correct sample-to-score alignment.",
                "",
                *summaries,
                "",
            ]
        ),
        encoding="utf-8",
    )
    print({"input_dir": str(input_dir), "output_dir": str(output_dir), "summary": summaries})


if __name__ == "__main__":
    main()
