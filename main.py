#!/usr/bin/env python3.13
#-*- coding : utf-8 -*-


__author__ = "Raphaël RIBES"
__contact__ = "raphael.ribes@etu.umontpellier.fr"
__version__ = "0.0.1"
__date__ = "11/11/2024"
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
        ## -v or --verbose: verbose mode
        ## -s or --single: single fasta file mode (only one file for output)

    #Synopsis:
        ## samReader.sh -h or --help # launch the help.
        ## samReader.sh -i or --input <file> # Launch samReader to analyze a samtools file (.sam) and print the result in the terminal
        ## samReader.sh -i or --input <file> -o or --output <name> # Launch samReader to analyze a samtools file (.sam) and print the result in the file called <name>
        ## samReader.sh -i or --input <file> -t or --trusted # Launch samReader to analyze a samtools file (.sam) and skip the format check.
        ## samReader.sh -i or --input <file> -v or --verbose # Launch samReader to analyze a samtools file (.sam) and print the result in the terminal with more information.
        ## samReader.sh -i or --input <file> -s or --single # Launch samReader to analyze a samtools file (.sam) and print the result in a single fasta file
  


############### IMPORT MODULES ###############

import os, sys, getopt
from tqdm.auto import tqdm

from checks import check_line
from analyse import readMapping, globalPercentCigar
from summarize import summarize

############### FUNCTIONS TO :
## 0/ Get options,
def getOptions(argv):
    """
    Get the parsed options, supporting both short and long forms
    """
    try:
        opts, args = getopt.getopt(argv, "hi:o:tvsa:", ["help", "input=", "output=", "trusted", "verbose", "single", 'ask-to-open'])
    except getopt.GetoptError:
        os.system("samReader.sh -h")
        sys.exit(2)

    inputfile = ""
    outputfile = ""
    trusted = False
    verbose = False
    single_file = False  # New flag for a single PDF and fasta file
    ask_to_open = False  # New flag to ask if the user wants to open the PDF file
    for opt, arg in opts:
        if opt in ("-i", "--input"):
            inputfile = arg
        elif opt in ("-o", "--output"):
            outputfile = arg
        elif opt in ("-t", "--trusted"):
            trusted = True
        elif opt in ("-v", "--verbose"):
            verbose = True
        elif opt in ("-s", "--single"):
            single_file = True
        elif opt in ("-a", "--ask-to-open"):
            ask_to_open = True
    return inputfile, outputfile, trusted, verbose, single_file, ask_to_open


## Check, Read and store the data

def checkFormat(file, trusted=False, verbose=False):
    """
        Check the format of the input file
    """
    if file.endswith(".sam"):
        with open(file, "r") as f:
            sam_line = f.readlines()

        clean = {}

        # we're gonna check that every columns follows the right formating
        desc = "Checking the format of the input file and storing the data" if not trusted else "Storing the data"
        iterator = tqdm(enumerate(sam_line), desc=desc, total=len(sam_line)) if verbose else enumerate(sam_line)

        for n, line in iterator:
            if line.startswith('@'): continue
            line = line.split('\t')

            check_line(line, trusted=trusted)

            qname = line[0].split('-')
            qname = qname[0] if len(qname) != 1 else  line[0].split('_')[0]

            # Those two lines allows to store the data for each reads that can be found in the sam file
            if qname not in clean: clean[qname] = []  # Create the key if it doesn't exist
            clean[qname].append(line[:11])  # we reduce the size of the data to store

        return clean

    else:
        print("The input file is not in the correct format. Please provide a .sam file.")
        sys.exit(2)

#### Main function ####

def main(argv):
    """
        Main function
    """
    inputfile, outputfile, trusted, verbose, single_file, ask_to_open = getOptions(argv)

    # Create a folder to store the output files
    if outputfile == "": outputfile = os.path.basename(inputfile)[:-4]

    user_start_dir = os.getenv("USER_START_DIR", os.getcwd())  # Get the user start directory
    results_dir = os.path.join(user_start_dir, f"{outputfile}_results")  # Create the results directory

    os.makedirs(results_dir, exist_ok=True)  # Create the directory if it doesn't exist
    clean = checkFormat(inputfile, trusted=trusted, verbose=verbose)  # Check the format of the input file and store the data

    for key, value in clean.items():  # Iterate over the reads
        results = readMapping(value, results_dir, single_file=single_file, verbose=verbose)

        recap = globalPercentCigar(value, verbose=verbose)
        for key1, value1 in recap.items():
            results[key1] = value1

        summarize(key, results, results_dir, verbose=verbose, ask_to_open=ask_to_open)


############### LAUNCH THE SCRIPT ###############

if __name__ == "__main__":
    main(sys.argv[1:])
