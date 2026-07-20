import json
import random
import statistics
from pathlib import Path


ROOT = Path("results")
SEEDS = [50, 51, 52, 53, 54]

METHOD_SPECS = [
    (
        "Gated LoRA attention.output + classifier",
        "direction_aware_peft",
        "splice_kmer_balanced_direction_gated_lora_seed{seed}_argmax.json",
    ),
    (
        "GERM-BO activation-derived comp0.27",
        "direction_aware_peft",
        "splice_kmer_balanced_direction_germ_bo_activation_seed{seed}_argmax.json",
    ),
]


def mean(values):
    return statistics.mean(values)


def std(values):
    return statistics.pstdev(values) if len(values) > 1 else 0.0


def bootstrap_ci(deltas, iterations=10000, seed=20260425):
    rng = random.Random(seed)
    samples = sorted(mean([rng.choice(deltas) for _ in deltas]) for _ in range(iterations))
    return samples[int(0.025 * iterations)], samples[int(0.975 * iterations)]


def load_rows():
    rows = []
    missing = []
    for label, family, pattern in METHOD_SPECS:
        for seed in SEEDS:
            path = ROOT / pattern.format(seed=seed)
            if not path.exists():
                missing.append(str(path))
                continue
            data = json.loads(path.read_text(encoding="utf-8"))
            method = pattern.split("_seed{seed}")[0]
            rows.append(
                {
                    "label": label,
                    "family": family,
                    "method": method,
                    "seed": seed,
                    "test_accuracy": data["test"]["accuracy"],
                    "test_macro_f1": data["test"]["macro_f1"],
                }
            )
    return rows, missing


def summarize(rows):
    summary = []
    by_label = {}
    for row in rows:
        by_label.setdefault(row["label"], []).append(row)
    for label, group in by_label.items():
        acc = [row["test_accuracy"] for row in group]
        f1 = [row["test_macro_f1"] for row in group]
        summary.append(
            {
                "label": label,
                "family": group[0]["family"],
                "seeds": len(group),
                "test_accuracy_mean": mean(acc),
                "test_accuracy_std": std(acc),
                "test_macro_f1_mean": mean(f1),
                "test_macro_f1_std": std(f1),
                "per_seed_acc": " / ".join(f"{value:.4f}" for value in acc),
            }
        )
    return summary


def main():
    rows, missing = load_rows()
    summary = summarize(rows)
    md_path = ROOT / "direction_aware_baselines_splice.md"
    lines = [
        "# Direction-Aware PEFT Baselines on Strict 3-mer-Balanced Splice Split",
        "",
        "Protocol: held-out seeds 50--54, same target modules as LoRA-ATT (`attention.output + classifier`), rank 8, lr 3e-4.",
        "",
        "## Summary",
        "",
        "| Method | Seeds | Test Acc Mean +/- Std | Test Macro-F1 Mean +/- Std | Per-Seed Acc |",
        "|---|---:|---:|---:|---|",
    ]
    for row in summary:
        lines.append(
            f"| {row['label']} | {row['seeds']} | "
            f"{row['test_accuracy_mean']:.4f} +/- {row['test_accuracy_std']:.4f} | "
            f"{row['test_macro_f1_mean']:.4f} +/- {row['test_macro_f1_std']:.4f} | "
            f"{row['per_seed_acc']} |"
        )
    if missing:
        lines.extend(["", "## Missing runs", ""])
        lines.extend(f"- `{path}`" for path in missing)
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(md_path)


if __name__ == "__main__":
    main()
