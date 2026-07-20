import argparse
import json
from pathlib import Path


ROOT = Path("results")


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--pattern",
        default="retention_tau_calibration*.json",
        help="Glob pattern under results/ (e.g. retention_tau_calibration_trained_*.json)",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output markdown path (default depends on pattern)",
    )
    return parser.parse_args()


def lookup_group(data, which):
    groups = data[which]["R_empirical_by_group"]
    sorted_items = sorted(
        groups.items(),
        key=lambda item: data[which]["border_score_mean_by_group"][item[0]],
    )
    return sorted_items[0], sorted_items[-1]


def main():
    args = parse_args()
    paths = sorted(ROOT.glob(args.pattern))
    if not paths:
        raise SystemExit(f"No files matched {args.pattern}")

    trained = "trained" in args.pattern
    token_level = "token" in args.pattern
    if token_level:
        title = "Trained-checkpoint, token-level"
    elif trained:
        title = "Trained-checkpoint, sample-pooled"
    else:
        title = "Random-init, sample-pooled"
    md_name = (
        "retention_tau_calibration_trained_token.md"
        if token_level
        else "retention_tau_calibration_trained.md"
        if trained
        else "retention_tau_calibration.md"
    )
    md_path = Path(args.output) if args.output else ROOT / md_name

    lines = [
        f"# Retention Ratio R_w(tau) Calibration ({title})",
        "",
        "Empirical estimate: R_emp = E[phi_tau(a)^2 g^2]/E[g^2] at layer-0 attention output.",
        "",
        "## Summary",
        "",
    ]
    if trained:
        lines.append(
            "| Split | Model | tau* | R at tau* (low / high) | tau_med | R at tau_med (low / high) | Spearman_med |"
        )
        lines.append("|---|---|---:|---:|---:|---:|---:|")
    else:
        lines.append(
            "| Split | tau* (1% clip) | R at tau* (low / high border) | tau_med | R at tau_med (low / high border) | Spearman_med |"
        )
        lines.append("|---|---:|---:|---:|---:|---:|")

    for path in paths:
        data = json.loads(path.read_text(encoding="utf-8"))
        stem = path.stem.replace("retention_tau_calibration_trained_token_", "").replace(
            "retention_tau_calibration_trained_", ""
        ).replace(
            "retention_tau_calibration_", ""
        )
        if trained:
            parts = stem.rsplit("_seed", 1)[0]
            if parts.endswith("_lora"):
                split_tag = parts[: -len("_lora")]
                model_tag = "LoRA"
            elif parts.endswith("_germ_bo"):
                split_tag = parts[: -len("_germ_bo")]
                model_tag = "GERM-BO"
            else:
                split_tag = stem
                model_tag = data.get("model_label", "unknown")
        else:
            split_tag = stem
            model_tag = None

        tau = data["calibrated_tau"]["tau"]
        low_star, high_star = lookup_group(data, "monotonicity_at_calibrated_tau")
        med = data["monotonicity_at_median_tau"]
        low_med, high_med = lookup_group(data, "monotonicity_at_median_tau")

        if trained:
            lines.append(
                f"| {split_tag} | {model_tag} | {tau:.4f} | {low_star[1]:.3f} / {high_star[1]:.3f} | "
                f"{med['tau']:.4f} | {low_med[1]:.3f} / {high_med[1]:.3f} | "
                f"{med['spearman_border_vs_R_empirical']:.3f} |"
            )
        else:
            lines.append(
                f"| {split_tag} | {tau:.4f} | {low_star[1]:.3f} / {high_star[1]:.3f} | "
                f"{med['tau']:.4f} | {low_med[1]:.3f} / {high_med[1]:.3f} | "
                f"{med['spearman_border_vs_R_empirical']:.3f} |"
            )

    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(md_path)


if __name__ == "__main__":
    main()
