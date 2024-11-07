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
from tqdm import tqdm
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
        for n, line in enumerate(sam_line):
            clean.append({})
            if line.startswith('@'): continue
            line = line.split('\t')
            payload: dict = line_to_payload(line, n)
            check_line(payload, trusted=trusted)
            clean[-1] = payload
            if len(line) > 11:
                clean[-1]['extra'] = line[11:]

            if clean[-1]['RNAME'] != "*":
                # col 4 : POS -> int() following this regex [0, 2^{31} - 1] (0 to 2147483647)
                pos_isdigit = line[3].replace('-', '').isdigit()
                if not pos_isdigit:
                    l = len(f"Error line {n + 1} : {"\t".join(line[0:3])} ")
                    print(f'Error line {n + 1} : {"\t".join(line[0:3])} {line[3]}    {"\t".join(line[4:6])}  ...\n'
                          f'{" " * l}{"^" * len(line[3])}\n'
                          f'Expected : {line[3]} to be an integer')
                    sys.exit(2)
                clean[-1]['POS'] = int(line[3])
                # we won't check for the range of the integer because it's too long and it has clearly been made so
                # that it's impossible to reach the limit

                # col 6 : CIGAR -> str() following this regex [0-9]+[MIDNSHPX=]
                cigar = []
                if line[5] == "*":
                    cigar = ['*']
                else:
                    for match in re.finditer(r"[0-9]+[MIDNSHPX=]", line[5]):
                        cigar.append(match.group())
                    if len(cigar) == 0:
                        l = len(f"Error line {n + 1} : {"\t".join(line[0:5])} ")
                        print(f'Error line {n + 1} : {"\t".join(line[0:5])} {line[5]}    {"\t".join(line[6:8])}  ...\n'
                              f'{" " * l}{"^" * len(line[5])}\n'
                              f'Expected : {line[5]} to be a string following this regex [0-9]+[MIDNSHPX=]')
                        sys.exit(2)
                clean[-1]['CIGAR'] = cigar
            else:
                clean[-1]['POS'] = 0
                clean[-1]['CIGAR'] = '*'

            # col 5 : MAPQ -> int() following this regex [0, 2^{8} - 1] (0 to 255)
            mapq_isdigit = line[4].replace('-', '').isdigit()
            if not mapq_isdigit:
                l = len(f"Error line {n + 1} : {"\t".join(line[0:4])} ")
                print(f'Error line {n + 1} : {"\t".join(line[0:4])} {line[4]}    {"\t".join(line[5:7])}  ...\n'
                      f'{" " * l}{"^" * len(line[4])}\n'
                      f'Expected : {line[4]} to be an integer')
                sys.exit(2)
            elif 0 < int(line[4]) > 255:
                l = len(f"Error line {n + 1} : {"\t".join(line[0:4])} ")
                print(f'Error line {n + 1} : {"\t".join(line[0:4])} {line[4]}    {"\t".join(line[5:7])}  ...\n'
                      f'{" " * l}{"^" * len(line[4])}\n'
                      f'Expected : {line[4]} to be an integer ranging from 0 to 255')
                sys.exit(2)
            clean[-1]['MAPQ'] = int(line[4])

            # col 7 : RNEXT -> str() following this regex \*|=|[0-9A-Za-z!#$%&+.\/:;?@^_|~\-^\*=][0-9A-Za-z!#$%&*+.\/:;=?@^_|~-]*


    else:
        print("The input file is not in the correct format. Please provide a .sam file.")
        sys.exit(2)

    return clean

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
    with tqdm(total=100, desc="Grapping the options...") as pbar:
        inputfile, outputfile, trusted = getOptions(argv)
        pbar.update(1)
        pbar.set_description("Checking the format of the input file...")
        if trusted:
            pbar.set_description("Skipping the format check...")
            pbar.update(19)
        else:
            clean = checkFormat(inputfile)
            pbar.update(19)
        print(clean)
    

############### LAUNCH THE SCRIPT ###############

if __name__ == "__main__":
    main(sys.argv[1:])
