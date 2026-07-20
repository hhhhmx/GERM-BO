import argparse
import csv
import random
import urllib.request
from pathlib import Path


SOURCE_URL = (
    "https://archive.ics.uci.edu/ml/machine-learning-databases/"
    "molecular-biology/promoter-gene-sequences/promoters.data"
)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="data/benchmarks/uci_promoter")
    parser.add_argument("--seed", type=int, default=20260419)
    parser.add_argument("--source-url", default=SOURCE_URL)
    return parser.parse_args()


def transition_border_score(sequence: str) -> float:
    if len(sequence) <= 1:
        return 1.0
    transitions = sum(1 for left, right in zip(sequence, sequence[1:]) if left != right)
    # Keep the score centered near 1.0 so it is compatible with the existing
    # metadata-driven compensation scale.
    return 0.5 + transitions / (len(sequence) - 1)


def load_records(source_url: str):
    with urllib.request.urlopen(source_url, timeout=30) as response:
        text = response.read().decode("utf-8")
    records = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        parts = [part.strip() for part in stripped.split(",")]
        if len(parts) != 3:
            raise ValueError(f"Unexpected promoter row: {line}")
        raw_label, sample_id, sequence = parts
        sequence = sequence.upper().replace("\t", "").replace(" ", "")
        invalid = sorted({base for base in sequence if base not in {"A", "C", "G", "T"}})
        if invalid:
            raise ValueError(f"Unsupported bases in {sample_id}: {invalid}")
        label = 1 if raw_label == "+" else 0
        border_score = transition_border_score(sequence)
        records.append(
            {
                "id": sample_id,
                "sequence": sequence,
                "label": label,
                "metadata": (
                    f"benchmark=uci_promoter;source=uci_molecular_biology;"
                    f"border_score={border_score:.6f}"
                ),
            }
        )
    return records


def stratified_split(records, seed: int):
    rng = random.Random(seed)
    by_label = {}
    for record in records:
        by_label.setdefault(record["label"], []).append(record)
    splits = {"train": [], "val": [], "test": []}
    for label_records in by_label.values():
        label_records = list(label_records)
        rng.shuffle(label_records)
        total = len(label_records)
        train_end = int(round(total * 0.70))
        val_end = train_end + int(round(total * 0.15))
        splits["train"].extend(label_records[:train_end])
        splits["val"].extend(label_records[train_end:val_end])
        splits["test"].extend(label_records[val_end:])
    for split_records in splits.values():
        rng.shuffle(split_records)
    return splits


def write_split(path: Path, records):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["id", "sequence", "label", "metadata"])
        writer.writeheader()
        writer.writerows(records)


def main():
    args = parse_args()
    output_dir = Path(args.output_dir)
    records = load_records(args.source_url)
    splits = stratified_split(records, args.seed)
    for split_name, split_records in splits.items():
        write_split(output_dir / f"{split_name}.csv", split_records)
    readme = output_dir / "README.md"
    readme.write_text(
        "\n".join(
            [
                "# UCI Promoter Benchmark",
                "",
                f"Source: {args.source_url}",
                "Task: binary promoter classification from DNA sequences.",
                "Labels: `1` is promoter (`+`), `0` is non-promoter (`-`).",
                "Metadata border score: sequence-derived adjacent-base transition score, not label-derived.",
                "",
                "Split sizes:",
                f"- train: {len(splits['train'])}",
                f"- val: {len(splits['val'])}",
                f"- test: {len(splits['test'])}",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(
        {
            "output_dir": str(output_dir),
            "total": len(records),
            "train": len(splits["train"]),
            "val": len(splits["val"]),
            "test": len(splits["test"]),
        }
    )


if __name__ == "__main__":
    main()
