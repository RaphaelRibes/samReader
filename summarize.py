import subprocess, os, shutil, sys

def makeLatex(fileName, results, path):
    latex_content = r"""% Preamble
\documentclass[11pt]{{article}}

% Packages
\usepackage{{amsmath}}
\usepackage{{fancyhdr}}
\usepackage{{verbatim}}

\begin{{document}}

\title{{Report for {read_name}}}
\date{{}}
\maketitle

\section{{Global cigar mutation observed }}
\centering
This section only include mapped and partially mapped CIGAR values since unmapped reads do not have one.
\begin{{table}}[h]
\centering
\begin{{tabular}}{{|l|c|}}
\hline
\textbf{{Mutation Type}} & \textbf{{Count}} \\
\hline
Alignment match & {M} \\
Insertion to the reference & {I} \\
Deletion from the reference & {D} \\
Soft clipping & {S} \\
Hard clipping & {H} \\
Skipped region & {N} \\
Padding & {P} \\
Sequence match & {X} \\
Sequence mismatch & {E} \\
\hline
\end{{tabular}}

% Annotation under the table
\scriptsize
\textcolor{{Note: if there is 100\% of a certain mutation type but $<$0.01\% of any other mutation, the real value of 100\% is less than 100\% due to rounding.}} \\
\end{{table}}
% stop centering
\raggedright
\section{{Read Mapping Summary}}

\noindent
\begin{{minipage}}[t]{{0.45\textwidth}}
\centering
\textbf{{Single Read Summary}} \\
\begin{{tabular}}{{|l|c|}}
\hline
\textbf{{Mapping Type}} & \textbf{{Count}} \\
\hline
Mapped & {s_mapped} \\
Partially Mapped & {s_partially_mapped} \\
Unmapped & {s_unmapped} \\
\hline
Total & {s_total} \\
\hline
\end{{tabular}}
\end{{minipage}}%
\hfill
\begin{{minipage}}[t]{{0.45\textwidth}}
\centering
\textbf{{Pair Read Summary}} \\
\begin{{tabular}}{{|l|c|}}
\hline
\textbf{{Mapping Type}} & \textbf{{Count}} \\
\hline
Mapped & {p_mapped} \\
Partially Mapped & {p_partially_mapped} \\
Unmapped & {p_unmapped} \\
\hline
Total & {p_total} \\
\hline
\end{{tabular}}
\end{{minipage}}
\thispagestyle{{empty}} % Suppress page number on the title page


\end{{document}}""".format(M=results["M"], I=results["I"], D=results["D"], S=results["S"], H=results["H"],
                           N=results["N"], P=results["P"], X=results["X"], E=results["="],read_name=fileName,
                           s_partially_mapped=results["s_partially_mapped"],
                           p_partially_mapped=results["p_partially_mapped"],
                           s_unmapped=results["s_unmapped"],
                           p_unmapped=results["p_unmapped"],
                           s_mapped=results["s_mapped"],
                           p_mapped=results["p_mapped"],
                           s_total=results["s_mapped"] + results["s_partially_mapped"] + results["s_unmapped"],
                           p_total=results["p_mapped"] + results["p_partially_mapped"] + results["p_unmapped"])

    with open(f"{path}/{fileName}.tex", "w") as file:
        file.write(latex_content)

    # Compile the .tex file to a .pdf file
    with open(os.devnull, 'w') as devnull:
        subprocess.run(["latexmk", "-silent", f"--output-directory={path}/temp", "-pdf", f"{path}/{fileName}.tex"],
                       stdout=devnull, stderr=devnull)

    # Move the .pdf file to the main directory
    subprocess.run(["mv", f"{path}/temp/{fileName}.pdf", f"{path}/{fileName}.pdf"])


def summarize(fileName, results, path, verbose=False, ask_to_open=False):
    makeLatex(fileName, results, path)
    # Remove the temp folder
    os.remove(f"{path}/{fileName}.tex")
    shutil.rmtree(f"{path}/temp")

    if verbose:
        print(f'\nThe results are available in the file {path}/{fileName}.pdf')

    if ask_to_open:
        yn = input("Do you want to open the file ? (y/n) ")
        if yn == "y":
            subprocess.run(["xdg-open", f"{path}/{fileName}.pdf"])
        else:
            pass
