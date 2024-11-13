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
% stop centering
\end{{table}}

\section{{Read Mapping Summary}}
\begin{{table}}[h]
\centering
\begin{{tabular}}{{|l|c|}}
\hline
\textbf{{Mapping Type}} & \textbf{{Count}} \\
\hline
Mapped & {mapped} \\
Partially Mapped & {partially_mapped} \\
Unmapped & {unmapped} \\
\hline
\end{{tabular}}
\end{{table}}


\end{{document}}""".format(M=results["M"], I=results["I"], D=results["D"], S=results["S"], H=results["H"],
                           N=results["N"], P=results["P"], X=results["X"], E=results["="],read_name=fileName,
                           partially_mapped=results["partially_mapped"], unmapped=results["unmapped"], mapped=results["mapped"])

    with open(f"{path}/{fileName}.tex", "w") as file:
        file.write(latex_content)

    # Compile the .tex file to a .pdf file
    subprocess.run(["latexmk", "-quiet", f"--output-directory={path}/temp", "-pdf", f"{path}/{fileName}.tex"])
    # Move the .pdf file to the main directory
    subprocess.run(["mv", f"{path}/temp/{fileName}.pdf", f"{path}/{fileName}.pdf"])


def summarize(fileName, results, path):
    makeLatex(fileName, results, path)
    # Remove the temp folder
    os.remove(f"{path}/{fileName}.tex")
    shutil.rmtree(f"{path}/temp")

    print(f'\nThe results are available in the file {path}/{fileName}.pdf')
    yn = input("Do you want to open the file ? (y/n) ")
    if yn == "y":
        subprocess.run(["xdg-open", f"{path}/{fileName}.pdf"])
    else:
        # exit
        sys.exit(0)