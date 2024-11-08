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

import os, sys, re, getopt
from tqdm.auto import tqdm
from checks import check_line, payload_tolist, line_to_payload


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

## 1/ Check,

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
            clean.append({})
            if line.startswith('@'): continue
            line = line.split('\t')

            payload: dict = line_to_payload(line, n)
            check_line(payload, trusted=trusted)

            clean[-1] = payload
            if len(line) > 11:
                clean[-1]['extra'] = line[11:]

        return clean

    else:
        print("The input file is not in the correct format. Please provide a .sam file.")
        sys.exit(2)

## 2/ Read, 

## 3/ Store,

## 4/ Analyse
 
#### Summarise the results ####

def Summary(fileName):
    pass
    
   

#### Main function ####

def main(argv):
    """
        Main function
    """
    inputfile, outputfile, trusted = getOptions(argv)
    if trusted:
        print("Skipping the format check...")
        clean = checkFormat(inputfile, trusted=trusted)
    else:
        clean = checkFormat(inputfile, trusted=trusted)
    # print(clean)
    

############### LAUNCH THE SCRIPT ###############

if __name__ == "__main__":
    main(sys.argv[1:])
