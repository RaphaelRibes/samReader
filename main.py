#!/usr/bin/env python3.13
#-*- coding : utf-8 -*-


__author__ = "Raphaël RIBES"
__contact__ = "raphael.ribes@etu.umontpellier.fr"
__version__ = "0.0.1"
__date__ = "12/14/2021"
__licence__ ="""This program is free software: you can redistribute it and/or modify
        it under the terms of the GNU General Public License as published by
        the Free Software Foundation, either version 3 of the License, or
        (at your option) any later version.
        This program is distributed in the hope that it will be useful,
        but WITHOUT ANY WARRANTY; without even the implied warranty of
        MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
        GNU General Public License for more details.
        You should have received a copy of the GNU General Public License
        along with this program. If not, see <https://www.gnu.org/licenses/>."""


     
    ### OPTION LIST:
        ## -h or --help : help information
        ## -i or --input: input file (.sam)
        ## -o or --output: output name files (.txt)
        ## -t or --trusted: trusted mode (skip the format check)

    #Synopsis:
        ## samReader.sh -h or --help # launch the help.
        ## samReader.sh -i or --input <file> # Launch samReader to analyze a samtools file (.sam) and print the result in the terminal
        ## samReader.sh -i or --input <file> -o or --output <name> # Launch samReader to analyze a samtools file (.sam) and print the result in the file called <name>
        ## samReader.sh -i or --input <file> -t or --trusted # Launch samReader to analyze a samtools file (.sam) and skip the format check.
  


############### IMPORT MODULES ###############

import os, sys, getopt, json, subprocess
from tqdm.auto import tqdm
from checks import check_line, line_to_payload
from analyse import partiallyMappedOrUnmapped, outputTableCigar, globalPercentCigar
import pandas as pd

############### FUNCTIONS TO :
## 0/ Get options,
def getOptions(argv):
    """
        Get the parsed options
    """
    try:
        opts, args = getopt.getopt(argv, "thi:o:", ["trusted", "help", "input=", "output="])
    except getopt.GetoptError:  # Is there even a way to trigger this error ? Probably not, but it's here just in case
        # execute a bash command
        os.system("samReader.sh -h")  # print the help
        sys.exit(2)

    inputfile = ""
    outputfile = ""
    trusted = False
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print("samReader.sh -i <inputfile> -o <outputfile>")
            sys.exit()
        elif opt in ("-i", "--input"):
            inputfile = arg
        elif opt in ("-o", "--output"):
            outputfile = arg
        elif opt in ("-t", "--trusted"):
            trusted = True
    return inputfile, outputfile, trusted

## 1/ Check, Read and store the data

def checkFormat(file, trusted=False):
    """
        Check the format of the input file
    """
    if file.endswith(".sam"):
        with open(file, "r") as f:
            sam_line = f.readlines()

        # remove the lines who start with @
        # sam_line = [line for line in sam_line if not line.startswith("@")]

        clean = []

        # we're gonna check that every columns follows the right formating
        desc = "Checking the format of the input file and storing the data" if not trusted else "Storing the data"
        for n, line in tqdm(enumerate(sam_line),
                            desc=desc,
                            total=len(sam_line)):

            if line.startswith('@'): continue
            line = line.split('\t')

            payload: dict = line_to_payload(line, n)
            check_line(payload, trusted=trusted)

            clean.append(payload)
            if len(line) > 11:
                clean[-1]['extra'] = line[11:]

        return clean

    else:
        print("The input file is not in the correct format. Please provide a .sam file.")
        sys.exit(2)

## 2/ Analyse
 
#### Summarise the results ####

def Summary(fileName, results, path):
    latex_content = r"""% Preamble
\documentclass[11pt]{{article}}

% Packages
\usepackage{{amsmath}}
\usepackage{{fancyhdr}}
\usepackage{{verbatim}}

\begin{{document}}

% ASCII art at the top of the page
\begin{{verbatim}}
                                 ____                      __
   _____  ____ _   ____ ___    / __ \  ___   ____ _  ____/ /  ___    _____
  / ___/ / __ `/  / __ `__ \  / /_/ / / _ \ / __ `/ / __  /  / _ \  / ___/
 (__  ) / /_/ /  / / / / / / / _, _/ /  __// /_/ / / /_/ /  /  __/ / /
/____/  \__,_/  /_/ /_/ /_/ /_/ |_|  \___/ \__,_/  \__,_/   \___/ /_/
\end{{verbatim}}

\section{{Global cigar mutation observed }}
\begin{{table}}[h]
\centering
\begin{{tabular}}{{|c|c|c|c|c|c|c|c|c|c|}}
\hline
M & I & D & S & H & N & P & X & = \\
\hline
{M} & {I} & {D} & {S} & {H} & {N} & {P} & {X} & {E} \\
\hline
\end{{tabular}}
\end{{table}}
% add text explaining each mutation type
\begin{{itemize}}
\item M: Alignment match (can be a sequence match or mismatch)
\item I: Insertion to the reference
\item D: Deletion from the reference
\item S: Soft clipping (clipped sequences present in SEQ)
\item H: Hard clipping (clipped sequences NOT present in SEQ)
\item N: Skipped region from the reference
\item P: Padding (silent deletion from the padded reference)
\item X: Sequence match
\item =: Sequence mismatch
\end{{itemize}}

\section{{Partially mapped reads}}
The number of partially mapped reads is {partially_mapped}.

\section{{Unmapped reads}}
The number of unmapped reads is {unmapped}.


\end{{document}}""".format(M=results["M"], I=results["I"], D=results["D"], S=results["S"], H=results["H"],
                           N=results["N"], P=results["P"], X=results["X"], E=results["="],
                           partially_mapped=results["partially_mapped"], unmapped=results["unmapped"])

    with open(f"./{path}/{fileName}.tex", "w") as file:
        file.write(latex_content)

    # Compile the .tex file to a .pdf file
    subprocess.run(["latexmk", "-quiet", f"--output-directory=./{path}", "-pdf", f"./{path}/{fileName}.tex"])


#### Main function ####

def main(argv):
    """
        Main function
    """
    inputfile, outputfile, trusted = getOptions(argv)
    # Create a folder to store the output files
    if outputfile == "": outputfile = inputfile
    if not os.path.exists(f"{inputfile} results"):
        os.makedirs(f"{inputfile} results")
    if trusted:
        print("Skipping the format check...")
        clean = checkFormat(inputfile, trusted=trusted)
    else:
        clean = checkFormat(inputfile, trusted=trusted)
    results = {}
    results["partially_mapped"], results["unmapped"] = partiallyMappedOrUnmapped(clean, f"{inputfile} results")
    outputTableCigar(clean, f"{inputfile} results")
    recap = globalPercentCigar(f"{inputfile} results")
    for key, value in recap.items():
        results[key] = value
    Summary(outputfile, results,f"{inputfile} results")

    

############### LAUNCH THE SCRIPT ###############

if __name__ == "__main__":
    main(sys.argv[1:])
