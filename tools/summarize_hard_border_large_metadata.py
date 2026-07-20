import csv
import json
import random
import statistics
from pathlib import Path


ROOT = Path("results")
SEEDS = list(range(42, 55))


def mean(values):
    return statistics.mean(values)


def std(values):
    return statistics.stdev(values) if len(values) > 1 else 0.0


def bootstrap_ci(deltas, iterations=20000, seed=1234):
    rng = random.Random(seed)
    samples = []
    for _ in range(iterations):
        samples.append(mean([rng.choice(deltas) for _ in deltas]))
    samples.sort()
    return samples[int(0.025 * iterations)], samples[int(0.975 * iterations)]


def load_existing():
    rows = []
    with (ROOT / "hard_border_large_final_13seed_comparison.csv").open(newline="") as handle:
        for row in csv.DictReader(handle):
            row = dict(row)
            row["seed"] = int(row["seed"])
            for key in ["selected_threshold", "val_accuracy", "val_f1", "test_accuracy", "test_f1", "test_precision", "test_recall"]:
                row[key] = float(row[key])
            rows.append(row)
    return rows


def load_metadata():
    rows = []
    for seed in SEEDS:
        path = ROOT / f"hard_border_large_metadata_comp027_p4_seed{seed}_threshold.json"
        data = json.loads(path.read_text())
        rows.append(
            {
                "method": "metadata_germ_bo",
                "label": "Metadata-driven GERM-BO comp=0.27/p4",
                "seed": seed,
                "selected_threshold": data["selected_threshold"],
                "val_accuracy": data["validation"]["accuracy"],
                "val_f1": data["validation"]["f1"],
                "test_accuracy": data["test"]["accuracy"],
                "test_f1": data["test"]["f1"],
                "test_precision": data["test"]["precision"],
                "test_recall": data["test"]["recall"],
            }
        )
    return rows


def write_csv(path, rows):
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def summarize(rows):
    out = []
    for method in ["baseline_lora", "germ_bo_final_attn_output_classifier", "metadata_germ_bo"]:
        group = [row for row in rows if row["method"] == method]
        acc = [row["test_accuracy"] for row in group]
        f1 = [row["test_f1"] for row in group]
        out.append(
            {
                "method": method,
                "label": group[0]["label"],
                "n_seeds": len(group),
                "test_accuracy_mean": mean(acc),
                "test_accuracy_std": std(acc),
                "test_accuracy_min": min(acc),
                "test_accuracy_max": max(acc),
                "test_f1_mean": mean(f1),
                "test_f1_std": std(f1),
                "per_seed_accuracy": " / ".join(f"{value:.4f}" for value in acc),
            }
        )
    return out


def paired(rows, left, right):
    by_key = {(row["method"], row["seed"]): row for row in rows}
    out = []
    for metric in ["test_accuracy", "test_f1", "test_precision", "test_recall"]:
        deltas = [by_key[(left, seed)][metric] - by_key[(right, seed)][metric] for seed in SEEDS]
        ci_low, ci_high = bootstrap_ci(deltas)
        out.append(
            {
                "metric": metric,
                "comparison": f"{left}_minus_{right}",
                "mean_delta": mean(deltas),
                "delta_std": std(deltas),
                "bootstrap_ci95_low": ci_low,
                "bootstrap_ci95_high": ci_high,
                "win_rate": sum(1 for value in deltas if value > 0) / len(deltas),
                "tie_count": sum(1 for value in deltas if value == 0),
                "per_seed_delta": " / ".join(f"{value:+.4f}" for value in deltas),
            }
        )
    return out


def main():
    rows = load_existing() + load_metadata()
    write_csv(ROOT / "hard_border_large_metadata_13seed_comparison.csv", rows)
    summary = summarize(rows)
    write_csv(ROOT / "hard_border_large_metadata_13seed_summary.csv", summary)
    paired_rows = []
    paired_rows.extend(paired(rows, "metadata_germ_bo", "baseline_lora"))
    paired_rows.extend(paired(rows, "metadata_germ_bo", "germ_bo_final_attn_output_classifier"))
    paired_rows.extend(paired(rows, "germ_bo_final_attn_output_classifier", "baseline_lora"))
    write_csv(ROOT / "hard_border_large_metadata_13seed_paired.csv", paired_rows)

    md = ROOT / "hard_border_large_metadata_13seed_comparison.md"
    with md.open("w") as handle:
        handle.write("# Hard-Border-Large 13-Seed Metadata-Driven Confirmation\n\n")
        handle.write(
            "Protocol: enlarged hard-border split, real DNABERT-2 backbone, seeds `42-54`, "
            "validation-accuracy best checkpoint, validation-threshold tuned test evaluation. "
            "Metadata-driven GERM-BO uses `border_score_type=metadata_border_score`, "
            "`compensation_strength=0.27`, and `early_stopping_patience=4`.\n\n"
        )
        handle.write("## Summary\n\n")
        handle.write("| Method | Test Acc Mean +/- Std | Test F1 Mean +/- Std | Min Acc | Max Acc |\n")
        handle.write("|---|---:|---:|---:|---:|\n")
        for item in summary:
            handle.write(
                f"| {item['label']} | {item['test_accuracy_mean']:.4f} +/- {item['test_accuracy_std']:.4f} | "
                f"{item['test_f1_mean']:.4f} +/- {item['test_f1_std']:.4f} | "
                f"{item['test_accuracy_min']:.4f} | {item['test_accuracy_max']:.4f} |\n"
            )
        handle.write("\n## Paired Deltas\n\n")
        handle.write("| Metric | Comparison | Delta Mean | Bootstrap 95% CI | Win Rate | Per-Seed Delta |\n")
        handle.write("|---|---|---:|---:|---:|---:|\n")
        for item in paired_rows:
            handle.write(
                f"| {item['metric']} | {item['comparison']} | {item['mean_delta']:+.4f} | "
                f"[{item['bootstrap_ci95_low']:+.4f}, {item['bootstrap_ci95_high']:+.4f}] | "
                f"{item['win_rate']:.1%} | {item['per_seed_delta']} |\n"
            )
    print(md)
    print(ROOT / "hard_border_large_metadata_13seed_comparison.csv")
    print(ROOT / "hard_border_large_metadata_13seed_summary.csv")
    print(ROOT / "hard_border_large_metadata_13seed_paired.csv")


if __name__ == "__main__":
    main()
