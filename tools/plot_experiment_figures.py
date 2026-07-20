from __future__ import annotations

from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
FIGURES = ROOT / "figures"
FIGURES.mkdir(exist_ok=True)

mpl.rcParams["pdf.fonttype"] = 42
mpl.rcParams["ps.fonttype"] = 42
mpl.rcParams["font.family"] = "DejaVu Sans"
mpl.rcParams["axes.unicode_minus"] = False
mpl.rcParams["axes.titleweight"] = "bold"
mpl.rcParams["axes.labelweight"] = "regular"
mpl.rcParams["figure.facecolor"] = "white"
mpl.rcParams["axes.facecolor"] = "white"
mpl.rcParams["savefig.facecolor"] = "white"
mpl.rcParams["axes.linewidth"] = 0.9
mpl.rcParams["xtick.major.width"] = 0.8
mpl.rcParams["ytick.major.width"] = 0.8
mpl.rcParams["xtick.major.size"] = 3
mpl.rcParams["ytick.major.size"] = 3
mpl.rcParams["legend.frameon"] = False

sns.set_theme(style="ticks", context="paper")

FIGURE_SIZES = {
    "01_controlled_main_results": (7, 2.3),
    "02_mechanism_comparison": (7, 3),
    "03_border_difficulty_profile": (6, 2.5),
    "04_target_module_ablation": (6, 2.2),
    "05_external_benchmark_overview": (8, 7),
    "06_splice_shortcut_split_check": (7, 3),
    "07_splice_strict_full_comparison": (8, 3),
    "08_splice_pooled_confirmation": (6, 2.6),
    "09_splice_class_balance": (7, 3),
    "10_splice_estimator_quality": (7, 3),
}

STYLE = {
    "figure_label_size": 20,
    "subpanel_label_size": 17,
    "title_size": 14,
    "label_size": 12,
    "tick_size": 12,
    "annot_size": 12,
    "heat_annot_size": 12,
    "grid_color": "#E9EDF3",
    "grid_width": 0.7,
    "spine_color": "#3A3A3A",
    "band_color": "#DDDDDD",
}

PALETTE = {
    "baseline": "#4C78A8",
    "activation": "#F58518",
    "metadata": "#2F9E8F",
    "shuffled": "#D95F5F",
    "no_comp": "#8E6BBE",
    "traditional_1": "#5C6F82",
    "traditional_2": "#7AA457",
    "traditional_3": "#C49A3A",
    "traditional_4": "#8C78B8",
    "probe": "#9A7B68",
    "neutral": "#70757F",
    "metric_acc": "#4C78A8",
    "metric_f1": "#E45756",
    "class0": "#4C78A8",
    "class1": "#F58518",
    "class2": "#54A24B",
}

SPLICE_CLASS_NAMES = ["Acceptor", "Donor", "Non-splice"]


def save(fig: plt.Figure, name: str) -> None:
    fig.tight_layout(pad=0.9, w_pad=1.2, h_pad=1.2, rect=(0.02, 0.02, 0.995, 0.97))
    fig.savefig(FIGURES / name, bbox_inches="tight")
    plt.close(fig)


def add_figure_letter(fig: plt.Figure, label: str) -> None:
    fig.text(
        0.01,
        0.995,
        label,
        fontsize=STYLE["figure_label_size"],
        fontweight="bold",
        ha="left",
        va="top",
    )


def add_subpanel(ax: plt.Axes, label: str) -> None:
    ax.text(
        -0.06,
        1.02,
        label,
        transform=ax.transAxes,
        fontsize=STYLE["subpanel_label_size"],
        fontweight="bold",
        ha="left",
        va="bottom",
    )


def style_axis(ax: plt.Axes, grid_axis: str | None = "x") -> None:
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(STYLE["spine_color"])
    ax.spines["bottom"].set_color(STYLE["spine_color"])
    ax.spines["left"].set_linewidth(0.9)
    ax.spines["bottom"].set_linewidth(0.9)
    ax.spines["left"].set_zorder(10)
    ax.spines["bottom"].set_zorder(10)
    ax.set_axisbelow(True)
    ax.tick_params(
        axis="both",
        labelsize=STYLE["tick_size"],
        length=3,
        width=0.8,
        colors=STYLE["spine_color"],
    )
    if grid_axis is not None:
        ax.grid(
            axis=grid_axis,
            color=STYLE["grid_color"],
            linewidth=STYLE["grid_width"],
            alpha=0.9,
        )
    else:
        ax.grid(False)


def annotate_barh(
    ax: plt.Axes,
    values: np.ndarray,
    ypos: np.ndarray,
    errs: np.ndarray | None = None,
    fmt: str = "{:.3f}",
) -> None:
    x0, x1 = ax.get_xlim()
    pad = (x1 - x0) * 0.012
    errs = np.zeros_like(values) if errs is None else errs
    for y, v, e in zip(ypos, values, errs):
        ax.text(
            v + e + pad,
            y,
            fmt.format(v),
            va="center",
            ha="left",
            fontsize=STYLE["annot_size"],
        )


def annotate_bar(
    ax: plt.Axes, xs: np.ndarray, values: np.ndarray, fmt: str = "{:.3f}"
) -> None:
    y0, y1 = ax.get_ylim()
    pad = (y1 - y0) * 0.02
    for x, v in zip(xs, values):
        ax.text(
            x,
            v + pad,
            fmt.format(v),
            va="bottom",
            ha="center",
            fontsize=STYLE["annot_size"],
        )


def short_method_label(text: str) -> str:
    mapping = {
        "Baseline LoRA": "Base",
        "Activation-derived GERM-BO": "Act-GB",
        "Metadata-driven GERM-BO": "Meta-GB",
        "Metadata-estimated GERM-BO": "MetaEst-GB",
        "Metadata-estimated GERM-BO center-JSD": "JSD-GB",
        "Metadata-estimated GERM-BO w64_k2_t10_s3": "w64k2-GB",
        "3-mer Logistic Regression": "3-mer LR",
        "3-mer Linear SVM": "3-mer SVM",
        "3-mer Multinomial NB": "3-mer NB",
        "3-mer Nearest Centroid": "3-mer NC",
        "GERM-BO quantile [0.8,1.2] comp0.27": "GERM-BO q[0.8,1.2]",
        "GERM-BO shuffled metadata": "GERM-BO shuffled",
        "LoRA attention.output + classifier": "LoRA attn.out+clf",
        "GERM-BO comp=0": "GERM-BO comp=0",
        "Baseline LoRA full target set": "LoRA full",
        "DNABERT-2 frozen linear probe": "Linear probe",
    }
    return mapping.get(text, text)


def family_color(label: str) -> str:
    if "Metadata-driven" in label or "Meta-GB" in label or "GERM-BO q" in label:
        return PALETTE["metadata"]
    if "Activation-derived" in label or "Act-GB" in label:
        return PALETTE["activation"]
    if "shuffled" in label.lower():
        return PALETTE["shuffled"]
    if "comp=0" in label or "No compensation" in label:
        return PALETTE["no_comp"]
    if "Linear SVM" in label:
        return PALETTE["traditional_1"]
    if "Logistic" in label:
        return PALETTE["traditional_2"]
    if "Multinomial" in label:
        return PALETTE["traditional_3"]
    if "Nearest" in label:
        return PALETTE["traditional_4"]
    if "probe" in label.lower():
        return PALETTE["probe"]
    return PALETTE["baseline"]


def section_band(ax: plt.Axes, y0: float, y1: float, shaded: bool) -> None:
    w = 0.37
    if shaded:
        ax.axhspan(y0 - w, y1 + w, color=STYLE["band_color"], zorder=0)


def plot_controlled_main() -> str:
    df = pd.read_csv(RESULTS / "hard_border_large_metadata_13seed_summary.csv")
    df["plot_label"] = [
        "LoRA",
        "GERM-BO\n(Act)",
        "GERM-BO\n(Meta)",
    ]
    df["color"] = [PALETTE["baseline"], PALETTE["activation"], PALETTE["metadata"]]

    fig, axes = plt.subplots(1, 2, figsize=FIGURE_SIZES["01_controlled_main_results"])
    specs = [
        ("test_accuracy_mean", "test_accuracy_std", "Accuracy"),
        ("test_f1_mean", "test_f1_std", "F1"),
    ]
    for ax, (mean_col, std_col, title) in zip(axes, specs):
        order = df.sort_values(mean_col, ascending=True)
        y = np.arange(len(order))
        ax.barh(
            y,
            order[mean_col],
            xerr=order[std_col],
            color=order["color"],
            edgecolor="none",
            error_kw={"elinewidth": 1.4, "capsize": 3, "capthick": 1.2},
            zorder=3,
        )
        ax.set_yticks(y)
        ax.set_yticklabels(order["plot_label"])
        # ax.set_title(title, fontsize=STYLE["title_size"])
        ax.set_xlabel(title, fontsize=STYLE["label_size"])
        x_min = float((order[mean_col] - order[std_col]).min()) - 0.03
        x_max = float((order[mean_col] + order[std_col]).max()) + 0.04
        ax.set_xlim(max(0.70, x_min), min(1.02, x_max))
        style_axis(ax, "x")
        annotate_barh(ax, order[mean_col].to_numpy(), y, order[std_col].to_numpy())
    add_figure_letter(fig, "A")
    add_subpanel(axes[0], "(a)")
    add_subpanel(axes[1], "(b)")
    save(fig, "01_controlled_main_results.pdf")
    return "01_controlled_main_results.pdf"


def plot_mechanism() -> str:
    df = pd.read_csv(RESULTS / "metadata_shuffled_ablation_summary.csv")
    groups = ["border_medium", "border_hard", "combined"]
    variants = ["no_comp", "activation", "metadata_real", "metadata_shuffled"]
    group_names = ["Medium", "Hard", "Combined"]
    variant_names = ["No comp", "Activation", "Metadata", "Shuffled"]
    cmap = sns.color_palette(["#FFF4E6", "#FFD08A", "#5CC8A1", "#007A64"], as_cmap=True)

    fig, axes = plt.subplots(1, 2, figsize=FIGURE_SIZES["02_mechanism_comparison"])
    specs = [
        ("test_accuracy_mean", "Held-out Accuracy"),
        ("test_f1_mean", "Held-out F1"),
    ]
    for ax, (value_col, title) in zip(axes, specs):
        heat = (
            df[df["group"].isin(groups)]
            .assign(
                group=lambda x: pd.Categorical(
                    x["group"], categories=groups, ordered=True
                ),
                variant=lambda x: pd.Categorical(
                    x["variant"], categories=variants, ordered=True
                ),
            )
            .pivot(index="group", columns="variant", values=value_col)
            .loc[groups, variants]
        )
        sns.heatmap(
            heat,
            ax=ax,
            cmap=cmap,
            cbar=False,
            linewidths=1.4,
            linecolor="white",
            annot=True,
            fmt=".3f",
            annot_kws={"fontsize": STYLE["heat_annot_size"]},
            square=True,
        )
        ax.set_xticklabels(
            variant_names, rotation=25, ha="right", fontsize=STYLE["tick_size"]
        )
        ax.set_yticklabels(group_names, rotation=0, fontsize=STYLE["tick_size"])
        ax.set_title(title, fontsize=STYLE["title_size"])
        ax.set_xlabel("")
        ax.set_ylabel("")
    add_figure_letter(fig, "B")
    add_subpanel(axes[0], "(a)")
    add_subpanel(axes[1], "(b)")
    save(fig, "02_mechanism_comparison.pdf")
    return "02_mechanism_comparison.pdf"


def plot_border_difficulty() -> str:
    df = pd.read_csv(RESULTS / "border_difficulty_5seed_comparison_summary.csv")
    task_order = ["border_easy", "border_medium", "border_hard"]
    task_label = ["Easy", "Medium", "Hard"]
    method_specs = [
        ("baseline", "Baseline LoRA", PALETTE["baseline"]),
        ("germ_bo", "GERM-BO final", PALETTE["metadata"]),
    ]
    fig, axes = plt.subplots(1, 2, figsize=FIGURE_SIZES["03_border_difficulty_profile"])
    x = np.arange(len(task_order))
    for ax, mean_col, std_col, title in [
        (axes[0], "accuracy_mean", "accuracy_std", "Accuracy"),
        (axes[1], "f1_mean", "f1_std", "F1"),
    ]:
        for method, label, color in method_specs:
            sub = df[df["method"] == method].set_index("task").loc[task_order]
            y = sub[mean_col].to_numpy()
            s = sub[std_col].to_numpy()
            ax.plot(
                x,
                y,
                marker="o",
                markersize=7,
                linewidth=2.6,
                color=color,
                label=label,
                zorder=3,
            )
            ax.fill_between(x, y - s, y + s, color=color, alpha=0.14, zorder=1)
        ax.set_xticks(x)
        ax.set_xticklabels(task_label)
        ax.set_ylabel(title, fontsize=STYLE["label_size"])
        ax.set_title(title, fontsize=STYLE["title_size"])
        ax.set_ylim(0.72 if title == "Accuracy" else 0.72, 1.01)
        style_axis(ax, "y")
    axes[0].legend(frameon=False, fontsize=10, loc="lower left")
    add_figure_letter(fig, "C")
    add_subpanel(axes[0], "(a)")
    add_subpanel(axes[1], "(b)")
    save(fig, "03_border_difficulty_profile.pdf")
    return "03_border_difficulty_profile.pdf"


def plot_target_module_ablation() -> str:
    df = pd.read_csv(RESULTS / "hard_border_large_target_module_ablation_summary.csv")
    labels = {
        "attention.output + classifier": "attn.out + clf",
        "Wqkv + classifier": "Wqkv + clf",
        "Classifier only": "clf only",
        "Wqkv + attention.output + classifier": "Wqkv + attn.out + clf",
    }
    df["label_short"] = df["label"].map(labels)
    df = df.sort_values("accuracy_mean", ascending=True).copy()

    fig, ax = plt.subplots(1, 1, figsize=FIGURE_SIZES["04_target_module_ablation"])
    y = np.array([0.42, 1.22, 2.02, 2.82])
    acc = df["accuracy_mean"].to_numpy()
    f1 = df["f1_mean"].to_numpy()

    for yi, a, f in zip(y, acc, f1):
        ax.plot([a, f], [yi, yi], color="#C7CED9", linewidth=3.0, zorder=1)
    ax.scatter(acc, y, s=50, color=PALETTE["metric_acc"], label="Accuracy", zorder=3)
    ax.scatter(
        f1, y, s=50, color=PALETTE["metric_f1"], marker="D", label="F1", zorder=3
    )
    for yi, a, f in zip(y, acc, f1):
        ax.text(
            a,
            yi + 0.17,
            f"{a:.3f}",
            color=PALETTE["metric_acc"],
            fontsize=STYLE["annot_size"],
            ha="center",
            va="bottom",
        )
        ax.text(
            f,
            yi - 0.17,
            f"{f:.3f}",
            color=PALETTE["metric_f1"],
            fontsize=STYLE["annot_size"],
            ha="center",
            va="top",
        )

    ax.set_yticks(y)
    ax.set_yticklabels(df["label_short"])
    ax.set_xlabel("Score", fontsize=STYLE["label_size"])
    # ax.set_title("Target-module ablation", fontsize=STYLE["title_size"])
    ax.set_xlim(0.855, 0.905)
    ax.set_ylim(-0.05, 3.25)
    style_axis(ax, "x")
    ax.legend(frameon=False, ncol=2, loc="lower right", fontsize=10)
    add_figure_letter(fig, "A")
    save(fig, "04_target_module_ablation.pdf")
    return "04_target_module_ablation.pdf"


def plot_external_overview() -> str:
    df = pd.read_csv(RESULTS / "paper_final_results_table.csv")
    keep = [
        "external_pilot",
        "larger_external_pilot",
        "external_heldout",
        "splice_external_pilot",
        "splice_external_heldout",
    ]
    section_names = {
        "external_pilot": "UCI promoter",
        "larger_external_pilot": "Human non-TATA",
        "external_heldout": "Human non-TATA held-out",
        "splice_external_pilot": "Splice sites pilot",
        "splice_external_heldout": "Splice sites held-out",
    }
    section_short = {
        "external_pilot": "UCI-P",
        "larger_external_pilot": "HN-P",
        "external_heldout": "HN-H",
        "splice_external_pilot": "SP-P",
        "splice_external_heldout": "SP-H",
    }
    section_order = keep
    model_order = {
        "Baseline LoRA": 0,
        "Activation-derived GERM-BO": 1,
        "Metadata-driven GERM-BO": 2,
        "Metadata-estimated GERM-BO": 2,
        "Metadata-estimated GERM-BO center-JSD": 2,
        "Metadata-estimated GERM-BO w64_k2_t10_s3": 2,
    }
    sub = df[df["section"].isin(keep)].copy()
    sub["section_rank"] = sub["section"].map(
        {s: i for i, s in enumerate(section_order)}
    )
    sub["model_rank"] = sub["model"].map(model_order).fillna(9)
    sub = sub.sort_values(["section_rank", "model_rank", "model"]).copy()
    sub["label_short"] = [
        f"{section_short[s]} | {short_method_label(m)}"
        for s, m in zip(sub["section"], sub["model"])
    ]
    sub["color"] = [family_color(m) for m in sub["model"]]

    y_positions = []
    current = 0.0
    section_ranges: list[tuple[str, float, float]] = []
    for idx, sec in enumerate(section_order):
        sec_rows = sub[sub["section"] == sec]
        start = current
        for _ in range(len(sec_rows)):
            y_positions.append(current)
            current += 1.0
        end = current - 1.0
        section_ranges.append((sec, start - 0.45, end + 0.45))
        current += 0.65
    sub["y"] = y_positions

    fig, axes = plt.subplots(
        2, 1, figsize=FIGURE_SIZES["05_external_benchmark_overview"], sharey=True
    )
    specs = [
        ("accuracy_mean", "accuracy_std", "Accuracy", (0.30, 0.86)),
        ("f1_mean", "f1_std", "F1 / Macro-F1", (0.15, 0.86)),
    ]

    for ax_idx, (ax, (mean_col, std_col, title, xlim)) in enumerate(zip(axes, specs)):
        for idx, (_, y0, y1) in enumerate(section_ranges):
            section_band(ax, y0, y1, idx % 2 == 0)

        ax.barh(
            sub["y"],
            sub[mean_col],
            xerr=sub[std_col],
            color=sub["color"],
            edgecolor="none",
            error_kw={"elinewidth": 1.2, "capsize": 2.5, "capthick": 1.1},
            zorder=3,
        )

        # ax.set_title(title, fontsize=STYLE["title_size"])
        ax.set_xlabel(title, fontsize=STYLE["label_size"], loc="left")
        ax.xaxis.set_label_coords(1.05, 0)
        ax.set_xlim(*xlim)
        ax.set_yticks(sub["y"])
        ax.set_yticklabels(sub["label_short"], fontsize=9)
        style_axis(ax, "x")
        annotate_barh(
            ax, sub[mean_col].to_numpy(), sub["y"].to_numpy(), sub[std_col].to_numpy()
        )

        # Optional left-side section labels.
        # for sec, y0, y1 in section_ranges:
        #     ax.text(
        #         xlim[0] - (xlim[1] - xlim[0]) * 0.01,
        #         (y0 + y1) / 2,
        #         section_names[sec],
        #         fontsize=8.2,
        #         ha="right",
        #         va="center",
        #         color=PALETTE["neutral"],
        #     )

        # Add right-side braces and section labels.
        # Compute the x position of the right-side brace.
        x_brace = xlim[1] + (xlim[1] - xlim[0]) * 0.02

        for sec, y0, y1 in section_ranges:
            # Draw the brace shape.
            # Vertical line.
            ax.plot(
                [x_brace + 0.15, x_brace + 0.15],
                [y0, y1],
                color="black",
                linewidth=1.0,
                clip_on=False,
                zorder=5,
            )
            # Top horizontal segment.
            ax.plot(
                [x_brace + 0.14, x_brace + 0.15],
                [y1, y1],
                color="black",
                linewidth=1.0,
                clip_on=False,
                zorder=5,
            )
            # Bottom horizontal segment.
            ax.plot(
                [x_brace + 0.14, x_brace + 0.15],
                [y0, y0],
                color="black",
                linewidth=1.0,
                clip_on=False,
                zorder=5,
            )

            # Add the section label to the right of the brace.
            label_x = x_brace + 0.16
            label_y = (y0 + y1) / 2

            ax.text(
                label_x,
                label_y,
                section_names[sec],
                fontsize=12,
                ha="left",
                va="center",
                color="black",
                weight="normal",
                clip_on=False,
                zorder=5,
            )

        ax.invert_yaxis()

    # axes[1].tick_params(labelleft=False)
    add_figure_letter(fig, "A")
    add_subpanel(axes[0], "(a)")
    add_subpanel(axes[1], "(b)")
    save(fig, "05_external_benchmark_overview.pdf")
    return "05_external_benchmark_overview.pdf"


def plot_shortcut_check() -> str:
    df = pd.read_csv(RESULTS / "splice_sites_all_matched_shortcut_checks.csv")
    methods = [
        ("kmer_logreg", "3-mer LR", PALETTE["traditional_2"]),
        ("kmer_linear_svm", "3-mer SVM", PALETTE["traditional_1"]),
        ("kmer_multinomial_nb", "3-mer NB", PALETTE["traditional_3"]),
        ("kmer_nearest_centroid", "3-mer NC", PALETTE["traditional_4"]),
    ]
    split_order = ["original_larger", "gc_matched", "kmer_balanced"]
    split_names = ["Orig", "GC-match", "3-mer-bal"]
    x = np.arange(len(split_order))

    fig, axes = plt.subplots(
        1, 2, figsize=FIGURE_SIZES["06_splice_shortcut_split_check"]
    )
    specs = [
        ("test_accuracy_mean", "test_accuracy_std", "Accuracy"),
        ("test_macro_f1_mean", "test_macro_f1_std", "Macro-F1"),
    ]
    y_limits = [(0.010, 0.020), (0.010, 0.010)]
    for ax, (mean_col, std_col, title), (y_min, y_max) in zip(axes, specs, y_limits):
        for method, label, color in methods:
            sub = df[df["method"] == method].set_index("split_id").loc[split_order]
            y = sub[mean_col].to_numpy()
            s = sub[std_col].to_numpy()
            ax.plot(
                x, y, marker="o", markersize=6, linewidth=2.2, color=color, label=label
            )
            ax.fill_between(x, y - s, y + s, color=color, alpha=0.08)
        ax.set_xticks(x)
        ax.set_xticklabels(split_names)
        # ax.set_title(title, fontsize=STYLE["title_size"])
        ax.set_ylabel(title, fontsize=STYLE["label_size"])
        y_all = df[mean_col].to_numpy()
        ax.set_ylim(float(y_all.min()) - y_min, float(y_all.max()) + y_max)
        style_axis(ax, "y")
    axes[0].legend(frameon=False, fontsize=9.5, ncol=2, loc="upper left")
    add_figure_letter(fig, "A")
    add_subpanel(axes[0], "(a)")
    add_subpanel(axes[1], "(b)")
    save(fig, "06_splice_shortcut_split_check.pdf")
    return "06_splice_shortcut_split_check.pdf"


def plot_strict_full_comparison() -> str:
    df = pd.read_csv(RESULTS / "splice_kmer_balanced_full_comparison_table_summary.csv")
    df["short"] = [short_method_label(v) for v in df["label"]]
    df["color"] = [family_color(v) for v in df["label"]]

    fig, axes = plt.subplots(
        1, 2, figsize=FIGURE_SIZES["07_splice_strict_full_comparison"]
    )

    left = df.sort_values("test_macro_f1_mean", ascending=True).copy()
    y = np.arange(len(left))
    axes[0].barh(
        y,
        left["test_macro_f1_mean"],
        xerr=left["test_macro_f1_std"],
        color=left["color"],
        edgecolor="none",
        error_kw={"elinewidth": 1.2, "capsize": 2.5, "capthick": 1.0},
        zorder=3,
    )
    axes[0].set_yticks(y)
    axes[0].set_yticklabels(left["short"])
    axes[0].set_xlabel("Macro-F1", fontsize=STYLE["label_size"])
    # axes[0].set_title("Strict split ranking", fontsize=STYLE["title_size"])
    axes[0].set_xlim(0.15, 0.44)
    style_axis(axes[0], "x")
    annotate_barh(
        axes[0],
        left["test_macro_f1_mean"].to_numpy(),
        y,
        left["test_macro_f1_std"].to_numpy(),
    )

    right = df.copy()
    right["x_round"] = right["test_accuracy_mean"].round(4)
    right["y_round"] = right["test_macro_f1_mean"].round(4)
    grouped = (
        right.groupby(["x_round", "y_round"], sort=False)
        .agg(
            test_accuracy_mean=("test_accuracy_mean", "mean"),
            test_macro_f1_mean=("test_macro_f1_mean", "mean"),
            label_join=("short", lambda s: " /\n".join(s.tolist())),
            color=("color", "first"),
        )
        .reset_index(drop=True)
    )
    for idx, (_, row) in enumerate(grouped.iterrows()):
        dx = 0.0017
        dy = 0.0018 if idx % 3 == 0 else (-0.0018 if idx % 3 == 1 else 0.0002)
        axes[1].scatter(
            row["test_accuracy_mean"],
            row["test_macro_f1_mean"],
            s=160,
            color=row["color"],
            edgecolor="white",
            linewidth=1.2,
            zorder=3,
        )
        axes[1].text(
            row["test_accuracy_mean"] + dx,
            row["test_macro_f1_mean"] + dy,
            row["label_join"],
            fontsize=10,
            ha="left",
            va="bottom",
        )
    axes[1].axvline(
        right.loc[
            right["label"] == "GERM-BO quantile [0.8,1.2] comp0.27",
            "test_accuracy_mean",
        ].iloc[0],
        color=PALETTE["metadata"],
        linestyle="--",
        linewidth=1.2,
        alpha=0.6,
    )
    axes[1].axhline(
        right.loc[
            right["label"] == "GERM-BO quantile [0.8,1.2] comp0.27",
            "test_macro_f1_mean",
        ].iloc[0],
        color=PALETTE["metadata"],
        linestyle="--",
        linewidth=1.2,
        alpha=0.6,
    )
    axes[1].set_xlabel("Accuracy", fontsize=STYLE["label_size"])
    axes[1].set_ylabel("Macro-F1", fontsize=STYLE["label_size"])
    # axes[1].set_title("Accuracy-Macro-F1 trade-off", fontsize=STYLE["title_size"])
    axes[1].set_xlim(0.325, 0.425)
    axes[1].set_ylim(0.15, 0.43)
    style_axis(axes[1], "both")

    add_figure_letter(fig, "B")
    add_subpanel(axes[0], "(a)")
    add_subpanel(axes[1], "(b)")
    save(fig, "07_splice_strict_full_comparison.pdf")
    return "07_splice_strict_full_comparison.pdf"


def plot_pooled_confirmation() -> str:
    summary = pd.read_csv(RESULTS / "splice_kmer_balanced_pooled_50_59_summary.csv")
    paired = pd.read_csv(RESULTS / "splice_kmer_balanced_pooled_50_59_paired.csv")

    fig, axes = plt.subplots(
        1, 2, figsize=FIGURE_SIZES["08_splice_pooled_confirmation"]
    )

    ax = axes[0]
    metrics = ["Accuracy", "Macro-F1"]
    x = np.arange(len(metrics))
    width = 0.32
    lora = [
        summary.loc[
            summary["method"] == "lora_attention_output_classifier",
            "test_accuracy_mean",
        ].iloc[0],
        summary.loc[
            summary["method"] == "lora_attention_output_classifier",
            "test_macro_f1_mean",
        ].iloc[0],
    ]
    lora_std = [
        summary.loc[
            summary["method"] == "lora_attention_output_classifier", "test_accuracy_std"
        ].iloc[0],
        summary.loc[
            summary["method"] == "lora_attention_output_classifier", "test_macro_f1_std"
        ].iloc[0],
    ]
    germ = [
        summary.loc[
            summary["method"] == "germ_bo_quantile_q08_12_comp027", "test_accuracy_mean"
        ].iloc[0],
        summary.loc[
            summary["method"] == "germ_bo_quantile_q08_12_comp027", "test_macro_f1_mean"
        ].iloc[0],
    ]
    germ_std = [
        summary.loc[
            summary["method"] == "germ_bo_quantile_q08_12_comp027", "test_accuracy_std"
        ].iloc[0],
        summary.loc[
            summary["method"] == "germ_bo_quantile_q08_12_comp027", "test_macro_f1_std"
        ].iloc[0],
    ]
    ax.bar(
        x - width / 2,
        lora,
        width=width,
        color=PALETTE["baseline"],
        yerr=lora_std,
        error_kw={"elinewidth": 1.2, "capsize": 2.5, "capthick": 1.0},
        label="LoRA attn.out+clf",
        zorder=3,
    )
    ax.bar(
        x + width / 2,
        germ,
        width=width,
        color=PALETTE["metadata"],
        yerr=germ_std,
        error_kw={"elinewidth": 1.2, "capsize": 2.5, "capthick": 1.0},
        label="GERM-BO q[0.8,1.2]",
        zorder=3,
    )
    ax.spines["bottom"].set_zorder(10)
    ax.spines["left"].set_zorder(10)
    ax.set_xticks(x)
    ax.set_xticklabels(metrics)
    ax.set_ylim(0.18, 0.49)
    # ax.set_title("Pooled mean performance", fontsize=STYLE["title_size"])
    ax.set_ylabel("Score", fontsize=STYLE["label_size"])
    style_axis(ax, "y")
    ax.legend(frameon=False, fontsize=9.5, loc="upper left")

    ax = axes[1]
    plot = paired.copy()
    plot["metric_name"] = plot["metric"].map(
        {"test_accuracy": "Accuracy\ndelta", "test_macro_f1": "Macro-F1\ndelta"}
    )
    y = np.array([0.38, 1.08])
    colors = [PALETTE["metric_acc"], PALETTE["metric_f1"]]
    for yi, (_, row), color in zip(y, plot.iterrows(), colors):
        ax.hlines(
            yi,
            row["bootstrap_ci95_low"],
            row["bootstrap_ci95_high"],
            color=color,
            linewidth=5,
            alpha=0.25,
        )
        ax.scatter(
            row["mean_delta"],
            yi,
            s=140,
            color=color,
            edgecolor="white",
            linewidth=1.1,
            zorder=3,
        )
        ax.text(
            row["bootstrap_ci95_high"] + 0.004,
            yi,
            f"{row['mean_delta']:+.3f}",
            va="center",
            fontsize=STYLE["annot_size"],
        )
    ax.axvline(0.0, color=PALETTE["neutral"], linestyle="--", linewidth=1.2)
    ax.set_yticks(y)
    ax.set_yticklabels(plot["metric_name"])
    ax.set_ylim(-0.05, 1.45)
    ax.set_xlim(-0.02, 0.16)
    # ax.set_title("Paired improvement with 95% CI", fontsize=STYLE["title_size"])
    ax.set_xlabel("GERM-BO minus LoRA", fontsize=STYLE["label_size"])
    style_axis(ax, "x")
    add_figure_letter(fig, "B")
    add_subpanel(axes[0], "(a)")
    add_subpanel(axes[1], "(b)")
    save(fig, "08_splice_pooled_confirmation.pdf")
    return "08_splice_pooled_confirmation.pdf"


def plot_class_balance() -> str:
    df = pd.read_csv(RESULTS / "splice_kmer_balanced_pooled_per_class_summary.csv")
    methods = [
        "LoRA attention.output + classifier",
        "GERM-BO quantile [0.8,1.2] comp0.27",
    ]
    class_colors = [PALETTE["class0"], PALETTE["class1"], PALETTE["class2"]]

    # Create a figure with the second panel split into a stacked subgrid.
    fig = plt.figure(figsize=FIGURE_SIZES["09_splice_class_balance"])

    # Create a two-column grid; the right column is split into two rows.
    gs = fig.add_gridspec(1, 2, width_ratios=[1, 1], wspace=0.3)

    # Left panel (a).
    ax_left = fig.add_subplot(gs[0])

    # Split the right panel into legend and stacked-bar regions.
    gs_right = gs[1].subgridspec(2, 1, height_ratios=[0.1, 0.9], hspace=0.05)

    # Upper-right panel: legend.
    ax_legend = fig.add_subplot(gs_right[0])
    # Lower-right panel: stacked bars.
    ax_bars = fig.add_subplot(gs_right[1])

    # Draw the left panel.
    x = np.arange(3)
    width = 0.32
    for i, method in enumerate(methods):
        sub = df[df["label"] == method].sort_values("class_label")
        vals = sub["f1_mean"].to_numpy()
        ax_left.bar(
            x + (-width / 2 if i == 0 else width / 2),
            vals,
            width=width,
            color=PALETTE["baseline"] if i == 0 else PALETTE["metadata"],
            alpha=0.92,
            label="LoRA attn.out+clf" if i == 0 else "GERM-BO q[0.8,1.2]",
            zorder=3,
        )
    ax_left.set_xticks(x)
    ax_left.set_xticklabels(SPLICE_CLASS_NAMES)
    ax_left.set_ylim(0, 0.5)
    ax_left.set_ylabel("Mean F1", fontsize=STYLE["label_size"])
    style_axis(ax_left, "y")
    ax_left.legend(frameon=False, fontsize=9, loc="upper left")

    # Use the upper-right panel only for the legend.
    ax_legend.axis("off")
    # Create legend handles.
    legend_handles = [
        Rectangle((0, 0), 1, 1, color=PALETTE["class0"], label=SPLICE_CLASS_NAMES[0]),
        Rectangle((0, 0), 1, 1, color=PALETTE["class1"], label=SPLICE_CLASS_NAMES[1]),
        Rectangle((0, 0), 1, 1, color=PALETTE["class2"], label=SPLICE_CLASS_NAMES[2]),
    ]

    # Add the legend to the legend-only panel.
    ax_legend.legend(
        handles=legend_handles,
        frameon=False,
        fontsize=9,
        loc="center",
        ncol=3,
    )

    # Draw the lower-right stacked bar panel.
    stack_df = df.pivot(
        index="label", columns="class_label", values="predicted_mean"
    ).loc[methods]
    stack_df = stack_df.div(stack_df.sum(axis=1), axis=0)
    ideal = pd.Series([1 / 3, 1 / 3, 1 / 3], index=[0, 1, 2], name="Ideal balance")
    stack_df = pd.concat([stack_df, ideal.to_frame().T])
    x = np.arange(len(stack_df))
    bottom = np.zeros(len(stack_df))
    for cls, color in zip([0, 1, 2], class_colors):
        vals = stack_df[cls].to_numpy()
        ax_bars.bar(
            x,
            vals,
            bottom=bottom,
            color=color,
            width=0.56,
            edgecolor="white",
            linewidth=0.8,
            zorder=3,
        )
        bottom += vals
    ax_bars.set_xticks(x)
    ax_bars.set_xticklabels(["LoRA", "GERM-BO", "Ideal"])
    ax_bars.set_ylim(0, 1.0)
    ax_bars.set_ylabel("Prediction share", fontsize=STYLE["label_size"])
    style_axis(ax_bars, "y")

    # Add figure and subpanel labels.
    add_figure_letter(fig, "A")
    add_subpanel(ax_left, "(a)")
    add_subpanel(ax_bars, "(b)")

    # Adjust the layout.
    fig.tight_layout(pad=0.9, w_pad=1.2, h_pad=1.2, rect=(0.02, 0.02, 0.995, 0.97))
    fig.savefig(FIGURES / "09_splice_class_balance.pdf", bbox_inches="tight")
    plt.close(fig)
    return "09_splice_class_balance.pdf"


def plot_estimator_quality() -> str:
    score = pd.read_csv(RESULTS / "splice_kmer_balanced_estimator_quality_score.csv")
    corr = pd.read_csv(RESULTS / "splice_kmer_balanced_estimator_quality_corr.csv")
    pred = pd.read_csv(
        RESULTS / "splice_kmer_balanced_estimator_quality_prediction.csv"
    )

    fig = plt.figure(figsize=FIGURE_SIZES["10_splice_estimator_quality"])
    gs = fig.add_gridspec(2, 2, width_ratios=[1.2, 1.0], height_ratios=[1.0, 1.0])
    ax_a = fig.add_subplot(gs[:, 0])
    ax_b = fig.add_subplot(gs[0, 1])
    ax_c = fig.add_subplot(gs[1, 1])

    x = np.arange(len(score))
    box_colors = ["#B8D3FF", "#A7E1D2", "#FFD6A5"]
    for i, (_, row) in enumerate(score.iterrows()):
        ax_a.vlines(
            i,
            row["score_min"],
            row["score_max"],
            color=PALETTE["neutral"],
            linewidth=1.2,
            zorder=1,
        )
        rect = Rectangle(
            (i - 0.24, row["score_q25"]),
            0.48,
            row["score_q75"] - row["score_q25"],
            facecolor=box_colors[i],
            edgecolor=PALETTE["neutral"],
            linewidth=1.0,
            zorder=2,
        )
        ax_a.add_patch(rect)
        ax_a.hlines(
            row["score_median"],
            i - 0.24,
            i + 0.24,
            color=PALETTE["neutral"],
            linewidth=1.2,
            zorder=3,
        )
        ax_a.scatter(
            i,
            row["score_mean"],
            s=70,
            color=PALETTE["metadata"],
            edgecolor="white",
            linewidth=0.9,
            zorder=4,
        )
    ax_a.set_xticks(x)
    ax_a.set_xticklabels(score["split"].str.upper())
    ax_a.set_ylim(0.78, 1.22)
    ax_a.set_ylabel("Border score", fontsize=STYLE["label_size"])
    # ax_a.set_title("Score distribution summary", fontsize=STYLE["title_size"])
    style_axis(ax_a, "y")

    heat = corr.pivot(index="split", columns="feature", values="pearson").loc[
        ["train", "val", "test"], ["gc", "entropy3", "max3"]
    ]
    sns.heatmap(
        heat,
        ax=ax_b,
        cmap=sns.diverging_palette(240, 20, as_cmap=True),
        center=0.0,
        annot=True,
        fmt=".3f",
        cbar=False,
        linewidths=1.2,
        linecolor="white",
        annot_kws={"fontsize": STYLE["heat_annot_size"] - 1},
    )
    # ax_b.set_title("Correlation with simple proxies", fontsize=STYLE["title_size"])
    ax_b.set_xlabel("")
    ax_b.set_ylabel("")
    ax_b.set_xticklabels(
        ["GC", "Entropy-3", "Max-3"], rotation=0, fontsize=STYLE["tick_size"]
    )
    ax_b.set_yticklabels(
        ["Train", "Val", "Test"], rotation=0, fontsize=STYLE["tick_size"]
    )

    pred = pred.copy()
    pred["display"] = pred["method"].map(
        {
            "germ_bo_quantile_q08_12_comp027": "GERM-BO",
            "lora_attention_output_classifier": "LoRA",
        }
    )
    pred = pred.sort_values("display")
    y = np.array([0.35, 1.0])
    for yi, (_, row) in zip(y, pred.iterrows()):
        color = (
            PALETTE["metadata"] if row["display"] == "GERM-BO" else PALETTE["baseline"]
        )
        ax_c.plot(
            [row["score_mean_correct"], row["score_mean_wrong"]],
            [yi, yi],
            color=color,
            linewidth=2.8,
            alpha=0.35,
            zorder=1,
        )
        ax_c.scatter(
            row["score_mean_correct"],
            yi,
            s=110,
            color=color,
            edgecolor="white",
            linewidth=1.0,
            zorder=3,
        )
        ax_c.scatter(
            row["score_mean_wrong"],
            yi,
            s=110,
            color=color,
            marker="s",
            edgecolor="white",
            linewidth=1.0,
            zorder=3,
        )
        ax_c.text(
            row["score_mean_wrong"] + 0.0006,
            yi + 0.1,
            f"delta={row['score_mean_wrong'] - row['score_mean_correct']:+.3f}",
            fontsize=STYLE["annot_size"],
        )
    ax_c.set_yticks(y)
    ax_c.set_yticklabels(pred["display"])
    ax_c.set_ylim(-0.05, 1.35)
    ax_c.set_xlim(0.985, 1.018)
    # ax_c.set_title("Score mean by prediction outcome", fontsize=STYLE["title_size"])
    ax_c.set_xlabel("Mean score", fontsize=STYLE["label_size"])
    style_axis(ax_c, "x")
    handles = [
        Line2D(
            [0],
            [0],
            marker="o",
            color="none",
            markerfacecolor=PALETTE["neutral"],
            markeredgecolor="white",
            markersize=7,
            label="correct",
        ),
        Line2D(
            [0],
            [0],
            marker="s",
            color="none",
            markerfacecolor=PALETTE["neutral"],
            markeredgecolor="white",
            markersize=7,
            label="wrong",
        ),
    ]
    ax_c.legend(
        handles=handles, frameon=False, fontsize=9, loc="lower left", handletextpad=0.3
    )

    add_figure_letter(fig, "B")
    add_subpanel(ax_a, "(a)")
    add_subpanel(ax_b, "(b)")
    add_subpanel(ax_c, "(c)")
    save(fig, "10_splice_estimator_quality.pdf")
    return "10_splice_estimator_quality.pdf"


def write_manifest(paths: list[str]) -> None:
    lines = [
        "# Figure Manifest",
        "",
        "Nature-style redraw with CVPR-inspired palette.",
        "",
    ]
    for item in paths:
        lines.append(f"- `{item}`")
    (FIGURES / "FIGURE_MANIFEST.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    outputs = [
        plot_controlled_main(),
        plot_mechanism(),
        plot_border_difficulty(),
        plot_target_module_ablation(),
        plot_external_overview(),
        plot_shortcut_check(),
        plot_strict_full_comparison(),
        plot_pooled_confirmation(),
        plot_class_balance(),
        plot_estimator_quality(),
    ]
    write_manifest(outputs)
    print("Generated:")
    for out in outputs:
        print(out)


if __name__ == "__main__":
    main()
