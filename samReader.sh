#!/bin/bash

# Function to display the help message
usage() {
  echo "                                ____                      __              "
  echo "   _____  ______   ____ ___    / __ \  ___   ______  ____/ /  ___    _____"
  echo "  / ___/ / __  /  / __ \`__ \  / /_/ / / _ \ / __  / / __  /  / _ \  / ___/"
  echo " (__  ) / /_/ /  / / / / / / / _, _/ /  __// /_/ / / /_/ /  /  __/ / /    "
  echo "/____/  \____/  /_/ /_/ /_/ /_/ |_|  \___/ \____/  \____/   \___/ /_/     "
  echo
  echo "Usage: $0 [-h|--help] [-i|--input input_file] [-o|--output output_file] [-t|--trusted] [-v|--verbose] [-s|--single]"
  echo
  echo "Options:"
  echo "  -h, --help                Displays this help message"
  echo "  -i, --input <file>        Specifies the input file"
  echo "  -o, --output <file>       Specifies the output directory"
  echo "  -t, --trusted             Skips checking the content of the input file"
  echo "  -v, --verbose             Shows details of each step"
  echo "  -s, --single              Creates only one output file"
  exit
}

# Using getopt to support both short and long options
PARSED_OPTIONS=$(getopt -o "hi:o:tvs" -l "help,input:,output:,trusted,verbose,single" -n "$0" -- "$@")
if [ $? != 0 ]; then
    echo "Error in options"
    exit 1
fi

# Apply the parsed options
eval set -- "$PARSED_OPTIONS"

# Default variables
input_file=""
output_file=""
trusted=false
verbose=false
single_pdf=false

# Parsing options
while true; do
    case "$1" in
        -h|--help)
            usage;;
        -i|--input)
            input_file=$2; shift 2;;
        -o|--output)
            output_file=$2; shift 2;;
        -t|--trusted)
            trusted=true; shift;;
        -v|--verbose)
            verbose=true; shift;;
        -s|--single)
            single_pdf=true; shift;;
        --)
            shift; break;;
        *)
            echo "Unrecognized option"; exit 1;;
    esac
done

# if the file is trusted, we don't check the content
if [ ! -z "$trusted" ]; then
    export USER_START_DIR="$(pwd)"
    python3 "$(dirname "$0")"/main.py -i "$input_file" -o "$output_file" ${trusted:+-t} ${verbose:+-v} ${single_pdf:+-s}
    exit 0
fi

# This script reads the sam file and check if the file is empty or not, containing unauthorized characters or not and then
# starts main.py script to read the sam file and generate the output file.

# Check if the input file is provided or not
if [ -z "$input_file" ]; then
    echo "Please provide the input file."
    exit 1
fi

# Check if the path of the input file is correct or not
if [ ! -f "$input_file" ]; then
    echo "The input file does not exist. Please provide the correct path."
    exit 1
fi

# If there is a output file, check if the path of the output file is correct or not
if [ ! -z "$output_file" -a ! -d "$output_file" ]; then
    # We create the folder
    mkdir -p "$(dirname "$output_file")"
fi

# Check if the sam file is a directory or not
if [ -d "$input_file" -o -d "$output_file" ]; then
    echo "The input file is a directory. Please provide a file."
    exit 1
fi

# Check if the sam file is empty or not
if [ ! -s "$input_file" ]; then
    echo "The input file is empty. Please provide a non-empty file."
    exit 1
fi

# The regex pattern to check if the file is containing unauthorized characters or not is define like
# [0-9A-Za-z!#$%&+./:;?@^_|~-^*=][0-9A-Za-z!#$%&*+./:;=?@^_|~-]*

# Check if the sam file is not containing unauthorized characters
if ! grep -q "[0-9A-Za-z!#$%&+.\/:;?@^_|~\-^\*=][0-9A-Za-z!#$%&*+.\/:;=?@^_|~-]*" "$input_file"; then
    echo "The input file is containing unauthorized characters. Please provide a file in the right format."
    exit 1
fi

# parse the parameters and start the main.py script
### OPTION LIST:
        ##-h or --help : help information
        ##-i or --input: input file (.sam)
        ##-o or --output: output name files (.txt)
# Make sure to include the right path from where the command is executed
export USER_START_DIR="$(pwd)"
python3 "$(dirname "$0")"/main.py -i "$input_file" -o "$output_file" ${trusted:+-t} ${verbose:+-v} ${single_pdf:+-s}
