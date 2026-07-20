"""Migrate latex/main.tex (IEEE) to Cell Press template main.tex."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "latex" / "main.tex"
OUT = ROOT / "cell-press-latex-template" / "main.tex"
SUPP = ROOT / "cell-press-latex-template" / "supplemental_proofs.tex"

PREAMBLE = r"""%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%% Cell Reports manuscript (Cell Press LaTeX template v1.10)
%%% Migrated from IEEE TMI draft
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

\documentclass[12pt,letterpaper]{article}
\usepackage[a4paper, total={7in, 10in}]{geometry}
\renewcommand{\familydefault}{\sfdefault}
\usepackage{graphicx}
\usepackage{helvet}
\usepackage{authblk}
\usepackage{hyperref}
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{amsthm}
\usepackage{booktabs}
\usepackage{orcidlink}
\usepackage[super,comma,sort&compress]{natbib}
\bibliographystyle{numbered}
\usepackage[right]{lineno}
\linenumbers

\newcommand{\splitname}[1]{\textit{#1}}
\newcommand{\modpath}[1]{\textit{#1}}
\newcommand{\includefigwide}[1]{%
  \includegraphics[width=0.85\linewidth,keepaspectratio]{#1}}

\newtheorem{theorem}{Theorem}
\newtheorem{proposition}[theorem]{Proposition}
\newtheorem{definition}[theorem]{Definition}

\makeatletter
\renewcommand{\maketitle}{\bgroup\setlength{\parindent}{0pt}
\begin{flushleft}
  \textbf{\@title}
  \@author
\end{flushleft}\egroup}
\makeatother

\title{Genomic Encoding with Robust Modeling via Border Optimization for Resource-Efficient Genomic Foundation Models}
\date{}

\author[1]{First Author}
\author[2]{Second Author}
\author[3]{Third Author}
\author[1,*]{Fourth Author}
\author[2,**]{Fifth Author}
\affil[1]{Department, Institution, City, Country}
\affil[2]{Department, Institution, City, Country}
\affil[3]{Department, Institution, City, Country}
\affil[*]{Correspondence: first.author@institution.edu}
\affil[**]{Correspondence: second.author@institution.edu}

\begin{document}
\maketitle
"""

POST_MAIN = r"""
\newpage

\section*{RESOURCE AVAILABILITY}

\subsection*{Lead contact}
Requests for further information and resources should be directed to and will be fulfilled by the lead contact (first.author@institution.edu).

\subsection*{Materials availability}
This study did not generate new unique reagents.

\subsection*{Data and code availability}
\begin{itemize}
  \item Controlled border-aware splits, external splice benchmarks, and result summaries reported in this paper are available from the project repository maintained by the authors. Accession identifiers will be provided upon acceptance.
  \item All original code for GERM-BO training and evaluation is available in the project repository. A permanent archive DOI will be assigned before publication.
  \item Any additional information required to reanalyze the data reported in this paper is available from the lead contact upon request.
\end{itemize}

\section*{ACKNOWLEDGMENTS}
Funding and acknowledgments to be added by the authors.

\section*{AUTHOR CONTRIBUTIONS}
Author contribution statements to be added by the authors.

\section*{DECLARATION OF INTERESTS}
The authors declare no competing interests.

\section*{SUPPLEMENTAL INFORMATION INDEX}
\begin{description}
  \item Document S1. Mathematical proofs and implementation mapping (supplemental\_proofs.pdf)
\end{description}

\bibliography{references}

\newpage

\section*{STAR METHODS}

\subsection*{Experimental model and study participant details}
This is a computational study using publicly available DNA sequence benchmarks and a pretrained DNABERT-2 genomic language model. No human participants or experimental organisms were used.

\subsection*{Method details}

\subsubsection*{Backbone and adapters}
All experiments use DNABERT-2 (117M) with LoRA-style adapters on \modpath{attention.output + classifier} unless otherwise stated. GERM-BO applies sample-level multiplicative compensation on the LoRA branch (Equation~\eqref{eq:implcomp}) using metadata, activation-derived, or sequence-estimated border scores.

\subsubsection*{Controlled and external benchmarks}
Controlled tasks use synthetic border-aware splits (\splitname{border\_easy}, \splitname{border\_medium}, \splitname{border\_hard}, \splitname{hard\_border\_large}). External evaluation uses the strict \splitname{3-mer-balanced} splice split derived from \splitname{splice\_sites\_all}.

\subsubsection*{Training protocol}
Training uses a single GPU, AdamW optimization, early stopping on validation accuracy, and multiple random seeds as reported in each table. Default LoRA rank $r=8$, scaling $\alpha=16$, and compensation strength $\lambda_{\mathrm{comp}}=0.27$ unless varied in sensitivity analyses.

\subsection*{Quantification and statistical analysis}
Binary controlled tasks report test accuracy and F1; the splice benchmark reports accuracy and macro-F1 as mean $\pm$ standard deviation across seeds. Key pairwise comparisons use paired bootstrap 95\% confidence intervals and paired $t$-tests where reported in the Results.

\subsection*{Additional resources}
Project repository: to be specified by the authors before submission.

\end{document}
"""


def extract_body(text: str) -> str:
    start = text.index("\\begin{abstract}")
    end = text.index("\\bibliographystyle{IEEEtran}")
    body = text[start:end]
    # abstract -> summary
    body = body.replace("\\begin{abstract}", "\\section*{SUMMARY}\n\n")
    body = body.replace("\\end{abstract}", "")
    body = body.replace("\\begin{IEEEkeywords}", "\\section*{KEYWORDS}\n\n")
    body = body.replace("\\end{IEEEkeywords}", "")
    # section mapping
    replacements = [
        (r"\\section\{Introduction\}", r"\\section*{INTRODUCTION}"),
        (r"\\section\{Related work\}\s*\n", r""),  # merge into intro
        (r"\\subsection\{Genomic foundation models\}", r""),
        (r"\\subsection\{Outlier free adaptation and efficient fine tuning\}", r""),
        (r"\\subsection\{Repetitive elements and motif structure in genomics\}", r""),
        (r"\\subsection\{Combinatorics of overlapping words\}", r""),
        (r"\\section\{Method\}", r"\\section*{RESULTS}\n\n\\subsection*{Border overlap and burst suppression}"),
        (r"\\subsection\{Problem setting\}", r""),
        (r"\\subsection\{Border geometry of genomic words\}", r""),
        (r"\\subsection\{Overlap induced variance inflation\}", r""),
        (r"\\subsection\{Border burst suppression\}", r""),
        (r"\\subsection\{Border aware compensation\}", r"\\subsection*{GERM-BO border-aware compensation}"),
        (r"\\subsection\{Implementation notes deferred to the appendix\}", r""),
        (r"\\FloatBarrier\s*\n\\section\{Experiments\}", r"\\subsection*{Experimental evaluation}"),
        (r"\\subsection\{Experimental setup\}", r""),
        (r"\\subsection\{Controlled main result\}", r"\\subsubsection*{Controlled border-aware benchmarks}"),
        (r"\\subsection\{Mechanism validation\}", r"\\subsubsection*{Mechanism validation on held-out controlled splits}"),
        (r"\\subsection\{From shortcut-prone external splits to a stricter splice benchmark\}", r"\\subsubsection*{Strict splice benchmark protocol}"),
        (r"\\subsection\{External main result on the strict \\splitname\{3-mer-balanced\} split\}", r"\\subsubsection*{External splice benchmark results}"),
        (r"\\subsection\{Compensation ablation on the strict split\}", r"\\subsubsection*{Compensation ablation on the strict splice split}"),
        (r"\\subsection\{Class recovery analysis\}", r"\\subsubsection*{Class recovery on the strict splice split}"),
        (r"\\subsection\{Hyperparameter sensitivity and resource footprint\}", r"\\subsubsection*{Hyperparameter sensitivity and resource footprint}"),
        (r"\\section\{Limitations and scope\}\\label\{sec:limitations\}", r"\\section*{DISCUSSION}\n\n\\subsection*{Limitations of the study}"),
        (r"\\section\{Conclusion\}", r"\\subsection*{Summary and outlook}"),
    ]
    for old, new in replacements:
        body = re.sub(old, new, body)
    body = body.replace("\\paragraph{", "\\subsubsection*{")
    body = body.replace("\\FloatBarrier", "")
    body = re.sub(r"\\begin\{figure\*\}(\[[^\]]*\])?", r"\\begin{figure}[!htbp]", body)
    body = re.sub(r"\\end\{figure\*\}", r"\\end{figure}", body)
    body = re.sub(r"\\begin\{table\*\}(\[[^\]]*\])?", r"\\begin{table}[!htbp]", body)
    body = re.sub(r"\\end\{table\*\}", r"\\end{table}", body)
    body = re.sub(r"Section~\\ref\{sec:limitations\}", "the Discussion", body)
    body = body.replace(
        "Full proofs are deferred to the appendix.",
        "Full proofs are provided in Document S1.",
    )
    body = re.sub(
        r"Appendix~\\ref\{app:proofcluster\}",
        "Document S1",
        body,
    )
    body = re.sub(
        r"Appendix~\\ref\{app:proofvariance\}",
        "Document S1",
        body,
    )
    body = re.sub(
        r"Appendix~\\ref\{app:prooffisher\}",
        "Document S1",
        body,
    )
    body = re.sub(
        r"Appendix~\\ref\{app:proofgamma\}",
        "Document S1",
        body,
    )
    body = re.sub(
        r"Appendix~\\ref\{app:markov\}",
        "Document S1",
        body,
    )
    body = re.sub(
        r"Appendix~\\ref\{app:implementation\}",
        "Document S1",
        body,
    )
    body = re.sub(
        r"Appendix~\\ref\{app:proofcluster\} through Appendix~\\ref\{app:proofgamma\}",
        "Document S1",
        body,
    )
    body = re.sub(
        r"are placed in the appendix to keep",
        "are provided in Document S1 to keep",
        body,
    )
    body = re.sub(r"\n{3,}", "\n\n", body)
    return body


def extract_appendix(text: str) -> str:
    start = text.index("\\appendices")
    end = text.index("\\end{document}")
    app = text[start:end]
    app = app.replace("\\appendices", "")
    app = re.sub(r"\\section\{", r"\\section*{", app)
    return (
        r"\documentclass[12pt,letterpaper]{article}" "\n"
        r"\usepackage{amsmath,amssymb,amsthm}" "\n"
        r"\newtheorem{theorem}{Theorem}" "\n"
        r"\newtheorem{proposition}[theorem]{Proposition}" "\n"
        r"\begin{document}" "\n"
        r"\section*{Supplemental mathematical proofs}" "\n"
        + app
        + r"\end{document}"
    )


def main():
    text = SRC.read_text(encoding="utf-8")
    body = extract_body(text)
    OUT.write_text(PREAMBLE + body + POST_MAIN, encoding="utf-8")
    SUPP.write_text(extract_appendix(text), encoding="utf-8")
    print("Wrote", OUT)
    print("Wrote", SUPP)


if __name__ == "__main__":
    main()
