#!/usr/bin/env python3.13
#-*- coding : utf-8 -*-


__author__ = "Raphaël RIBES"
__contact__ = "raphael.ribes@etu.umontpellier.fr"
__version__ = "1.0.0"
__date__ = "10/12/2024"
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

import os, sys, getopt, yaml, importlib.util
from tqdm.auto import tqdm
import numpy as np
import shutil

from plotit import plot_depth_mapq, plot_mapping_ratio
from common_functions import toBinary

## 0/ Get options,
def getOptions(argv):
    """
    Get the parsed options, supporting both short and long forms
    """
    try:
        opts, args = getopt.getopt(argv, "hi:o:tva", ["help", "input=", "output=", "trusted", "verbose", "ask-to-open"])
    except getopt.GetoptError:
        os.system("samReader.sh -h")
        sys.exit(2)

    inputfile = ""
    outputfile = ""
    trusted = False
    verbose = False
    autoopen = False  # New flag to ask if the user wants to open the PDF file
    for opt, arg in opts:
        if opt in ("-i", "--input"):
            inputfile = arg
        elif opt in ("-o", "--output"):
            outputfile = arg
        elif opt in ("-t", "--trusted"):
            trusted = True
        elif opt in ("-v", "--verbose"):
            verbose = True
        elif opt in ("-a", "--ask-to-open"):
            autoopen = True
    return inputfile, outputfile, trusted, verbose, autoopen


## Check, Read and store the data
def checkFormat(file, check_line, trusted=False, verbose=False, separator='-', maq_threshold=0):
    """
        Check the format of the input file
    """
    if file.endswith(".sam"):
        with open(file, "r") as f:
            sam_line = f.readlines()

        formated = {}
        maxpos = {}
        total_lines = {}
        # Checks that every column follows the right formating
        desc = "Checking the format of the input file and storing the data" if not trusted else "Storing the data"
        iterator = tqdm(enumerate(sam_line), desc=desc, total=len(sam_line)) if verbose else enumerate(sam_line)

        for n, line in iterator:
            if line.startswith('@'): continue
            line = line.split('\t')
            qname = line[0].split(separator)[0]
            line[1] = toBinary(line[1], 16)

            if qname not in total_lines: total_lines[qname] = 0  # Create the key if it does not exist
            total_lines[qname] += 1

            check_line(line, trusted=trusted)

            if int(line[4]) >= maq_threshold:
                # Those two lines allow storing the data for each read that can be found in the sam file
                if qname not in formated: formated[qname] = []  # Create the key if it does not exist
                if qname not in maxpos: maxpos[qname] = (0, )  # Create the key if it does not exist
                formated[qname].append(line[:11])  # Reduces the size of the data to store
                if int(line[3]) > maxpos[qname][0] and line[5] != '*':
                    maxpos[qname] = (int(line[3]), line[5])

        return formated, maxpos, total_lines

    else:
        print("The input file is not in the correct format. Please provide a .sam file.")
        sys.exit(2)

#### Main function ####

def main(argv):
    """
        Main function
    """
    inputfile, outputfile, trusted, verbose, autoopen = getOptions(argv)

    # Create a folder to store the output files
    if outputfile == "": outputfile = os.path.basename(inputfile)[:-4]

    results_dir = os.path.join(os.getcwd(), f"{outputfile}_results")  # Create the results directory

    local_directory = os.path.dirname(os.path.abspath(__file__))  # Get the directory of the script

    os.makedirs(results_dir, exist_ok=True)  # Create the directory if it doesn't exist

    config = yaml.safe_load(open(f"{local_directory}/config.yaml", "r")) # Load the version from the config file
    modules = {"analyse": None,
               "checks": None,
               "summarize": None}

    # We import the right modules for the selected version of SAM
    for module in modules:
        file_path = os.path.join(local_directory, "SAM_specs", config['version'] , f"{module}.py")  # Define the path to the module
        spec = importlib.util.spec_from_file_location(module, file_path)  # Create the spec
        modules[module] = importlib.util.module_from_spec(spec)  # Create the module
        spec.loader.exec_module(modules[module])  # Execute the module

    # Check the format of the input file and store the data
    formated, maxpos, total_lines = checkFormat(inputfile, trusted=trusted, verbose=verbose,
                                                check_line=modules['checks'].check_line,
                                                separator=config['separator'],
                                                maq_threshold=config['mapq threshold'])

    os.makedirs(os.path.join(os.getcwd(), "temp"), exist_ok=True)
    total = None
    for chromosome, reads in formated.items():  # Iterate over the reads
        reads = np.array(reads)  # Convert the list to a numpy array

        print(maxpos[chromosome])
        length = maxpos[chromosome][0] + len(modules['analyse'].readCigar(maxpos[chromosome][1])[1])
        mapq = np.zeros(length, dtype=np.int16)  # Create an array of zeros to store the mapq
        depth = np.zeros(length, dtype=np.int16)  # Create an array of zeros to store the depth

        results = modules["analyse"].readMapping(reads, os.path.join(results_dir, chromosome), verbose=verbose)

        cigar, depth, mapq = modules["analyse"].globalPercentCigar(reads, depth, mapq, verbose=verbose)

        plot_depth_mapq(depth, mapq, bins=config['bins'],
                        depth_median=config['calculation method']['depth'] == "median",
                        mapq_median=config['calculation method']['mapq'] == "median",
                        n_ticks=config['n ticks'])

        for mutation, total_value in cigar.items():
            results[mutation] = total_value
        results['total'] = total_lines[chromosome]
        results['qual'] = config['mapq threshold']

        modules["summarize"].summarize(chromosome, results, results_dir, verbose=verbose)

        if total is None: total = results
        else: total = {chromosome: total[chromosome] + results[chromosome] for chromosome in total}

    plot_mapping_ratio(results_dir)
    total['chromosomes'] = formated.keys()
    modules["summarize"].summarize(outputfile, total, results_dir, verbose=verbose, genome=True)

    # remove the temp directory
    shutil.rmtree(os.path.join(os.getcwd(), "temp"))

    if autoopen:
        os.system(f"xdg-open \"{os.path.join(results_dir, outputfile)}.pdf\"")

############### LAUNCH THE SCRIPT ###############

if __name__ == "__main__":
    main(sys.argv[1:])
