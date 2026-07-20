import argparse
import json
import statistics
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--label", required=True)
    parser.add_argument("--files", nargs="+", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = []
    for file_path in args.files:
        path = Path(file_path)
        with open(path, "r", encoding="utf-8") as handle:
            metrics = json.load(handle)
        rows.append(
            {
                "file": path.name,
                "accuracy": float(metrics["accuracy"]),
                "f1": float(metrics["f1"]),
                "loss": float(metrics["loss"]),
            }
        )
    summary = {"label": args.label, "count": len(rows), "rows": rows}
    for metric_name in ("accuracy", "f1", "loss"):
        values = [row[metric_name] for row in rows]
        summary[f"{metric_name}_mean"] = statistics.mean(values)
        summary[f"{metric_name}_stdev"] = statistics.stdev(values) if len(values) > 1 else 0.0
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
