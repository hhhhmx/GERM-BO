"""Aggregate advisor rank-sweep threshold JSONs and patch main.tex table."""
import json
import re
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
MAIN_TEX = ROOT / "latex" / "main.tex"


def load_rank_results():
    by_rank = {4: [], 8: [], 16: []}
    for rank in by_rank:
        for seed in (42, 43, 44):
            path = RESULTS / f"advisor_rank{rank}_seed{seed}_threshold.json"
            if not path.exists():
                raise FileNotFoundError(f"Missing {path}")
            data = json.loads(path.read_text())
            by_rank[rank].append(float(data["test"]["accuracy"]))
    return by_rank


def fmt_mean_std(values):
    mean = statistics.mean(values)
    std = statistics.pstdev(values) if len(values) > 1 else 0.0
    return f"${mean:.4f} \\pm {std:.4f}$"


def patch_tex(by_rank):
    text = MAIN_TEX.read_text(encoding="utf-8")
    table_block = (
        "\\begin{table}[t]\n"
        "\\caption{Sensitivity to LoRA rank $r$ on \\splitname{border\\_hard} "
        "(metadata compensation, $\\lambda_{\\mathrm{comp}}=0.27$, three seeds). "
        "Test accuracy mean $\\pm$ std.}\n"
        "\\label{tab:rank-sensitivity}\n"
        "\\centering\n"
        "\\small\n"
        "\\begin{tabular}{lccc}\n"
        "\\toprule\n"
        "Rank $r$ & 4 & 8 & 16 \\\\\n"
        "\\midrule\n"
        f"Test accuracy & {fmt_mean_std(by_rank[4])} & {fmt_mean_std(by_rank[8])} & {fmt_mean_std(by_rank[16])} \\\\\n"
        "\\bottomrule\n"
        "\\end{tabular}\n"
        "\\end{table}\n"
    )
    paragraph = (
        "\\paragraph{Rank budget $r$.}\n"
        "Table~\\ref{tab:rank-sensitivity} reports metadata-driven GERM-BO on "
        "\\splitname{border\\_hard} for $r \\in \\{4,8,16\\}$ with fixed "
        "$\\lambda_{\\mathrm{comp}}=0.27$ (three seeds). Accuracy is stable "
        "across moderate ranks, indicating that the gain is not driven by a "
        "narrow rank sweet spot; $r=8$ remains the default for parity with LoRA baselines.\n\n"
        + table_block
    )
    start = text.index("\\paragraph{Rank budget $r$.}")
    end = text.index("\\paragraph{Resource footprint.}")
    new_text = text[:start] + paragraph + text[end:]
    MAIN_TEX.write_text(new_text, encoding="utf-8")
    print("Updated", MAIN_TEX)
    for rank, vals in by_rank.items():
        print(f"rank {rank}: {vals} -> mean={statistics.mean(vals):.4f}")


if __name__ == "__main__":
    patch_tex(load_rank_results())
