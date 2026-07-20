"""Move inline figures/tables to Cell Press end sections in main.tex."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / "cell-press-latex-template" / "main.tex"
FLOATS = ROOT / "cell-press-latex-template" / "floats_at_end.tex"

FIGURE_BEGIN = r"\begin{figure}[!htbp]"


def extract_blocks(text: str, env: str) -> tuple[str, list[str]]:
    blocks = []
    token_begin = f"\\begin{{{env}}}"
    token_end = f"\\end{{{env}}}"
    while token_begin in text:
        start = text.index(token_begin)
        end = text.index(token_end, start) + len(token_end)
        blocks.append(text[start:end])
        text = text[:start] + text[end:]
    return text, blocks


def first_sentence(text: str) -> str:
    text = text.strip().replace("\n", " ")
    for token in [r"\textbf{", r"\emph{"]:
        idx = text.find(token)
        if idx > 0:
            text = text[:idx].strip()
    for sep in [". ", "."]:
        if sep in text:
            part = text.split(sep)[0].strip()
            if len(part) > 10:
                return part + "."
    return text[:120].strip()


def parse_figure(block: str) -> dict:
    file_m = re.search(r"\\includefigwide\{([^}]+)\}", block)
    cap_m = re.search(r"\\caption\{((?:[^{}]|\{[^{}]*\})*)\}", block, re.DOTALL)
    label_m = re.search(r"\\label\{([^}]+)\}", block)
    raw_caption = cap_m.group(1).strip() if cap_m else ""
    return {
        "file": file_m.group(1) if file_m else "",
        "caption": raw_caption,
        "title": first_sentence(raw_caption),
        "label": label_m.group(1) if label_m else "",
    }


def parse_table(block: str) -> dict:
    cap_m = re.search(r"\\caption\{((?:[^{}]|\{[^{}]*\})*)\}", block, re.DOTALL)
    labels = re.findall(r"\\label\{([^}]+)\}", block)
    body_start = block.find("\\centering")
    if body_start == -1:
        body_start = block.find("\\caption")
    body = block[body_start:]
    body = re.sub(r"\\caption\{((?:[^{}]|\{[^{}]*\})*)\}\s*", "", body, count=1, flags=re.DOTALL)
    body = re.sub(r"\\label\{[^}]+\}\s*", "", body)
    body = re.sub(r"\\end\{table\}.*", "", body, flags=re.DOTALL).strip()
    title = first_sentence(cap_m.group(1).strip()) if cap_m else "Table"
    return {
        "caption": cap_m.group(1).strip() if cap_m else "",
        "title": title,
        "labels": labels,
        "body": body,
    }


def render_figures(figs: list[dict]) -> str:
    out = ["\\newpage", "", "\\section*{MAIN FIGURE TITLES AND LEGENDS}", ""]
    for idx, fig in enumerate(figs, 1):
        out.append(f"\\noindent\\includegraphics[width=0.85\\linewidth]{{{fig['file']}}}")
        out.append("")
        out.append(f"\\subsection*{{Figure {idx}. {fig['title']}}}")
        out.append(f"\\refstepcounter{{figure}}\\label{{{fig['label']}}}")
        out.append(fig["caption"])
        out.append("")
        out.append("\\bigskip")
        out.append("")
    return "\n".join(out)


def render_tables(tabs: list[dict]) -> str:
    out = ["\\newpage", "", "\\section*{MAIN TABLES, INCLUDING TITLES AND LEGENDS}", ""]
    for idx, tab in enumerate(tabs, 1):
        out.append(f"\\subsection*{{Table {idx}. {tab['title']}}}")
        if tab["labels"]:
            out.append("\\refstepcounter{table}")
            out.append("".join(f"\\label{{{lab}}}" for lab in tab["labels"]))
        out.append(tab["body"])
        out.append("")
        out.append("\\bigskip")
        out.append("")
    return "\n".join(out)


def main():
    text = MAIN.read_text(encoding="utf-8")
    text, figures = extract_blocks(text, "figure")
    text, tables = extract_blocks(text, "table")

    fig_data = [parse_figure(b) for b in figures]
    tab_data = [parse_table(b) for b in tables]

    floats_tex = render_figures(fig_data) + "\n" + render_tables(tab_data) + "\n"
    FLOATS.write_text(floats_tex, encoding="utf-8")

    marker_block = (
        "\\section*{SUPPLEMENTAL INFORMATION INDEX}\n"
        "\\begin{description}\n"
        "  \\item Document S1. Mathematical proofs and implementation mapping (supplemental\\_proofs.pdf)\n"
        "\\end{description}\n\n"
        "\\input{floats_at_end.tex}\n\n"
        "\\bibliography{references}"
    )
    old_block = (
        "\\section*{SUPPLEMENTAL INFORMATION INDEX}\n"
        "\\begin{description}\n"
        "  \\item Document S1. Mathematical proofs and implementation mapping (supplemental\\_proofs.pdf)\n"
        "\\end{description}\n\n"
        "\\bibliography{references}"
    )
    if old_block not in text and "\\input{floats_at_end.tex}" in text:
        print("Floats already at end; updated floats_at_end.tex only")
    elif old_block not in text:
        raise RuntimeError("Could not find supplemental/bibliography block to replace")
    else:
        text = text.replace(old_block, marker_block)
        MAIN.write_text(text, encoding="utf-8")
    print(f"Moved {len(figures)} figures and {len(tables)} tables to {FLOATS}")


if __name__ == "__main__":
    main()
