#!/bin/bash

# This script reads the sam file and check if the file is empty or not, in the right format or not and then
# starts main.py script to read the sam file and generate the output file.
echo "$@"
# Check if the sam file is a directory or not
if [ -d "$1" ]; then
    echo "The input file is a directory. Please provide a file."
    exit 1
fi

# Check if the sam file is empty or not
if [ ! -s "$1" ]; then
    echo "The input file is empty. Please provide a non-empty file."
    exit 1
fi

# The regex pattern to check if the file is containing unauthorized characters or not is define like
# [0-9A-Za-z!#$%&+./:;?@^_|~-^*=][0-9A-Za-z!#$%&*+./:;=?@^_|~-]*

# Check if the sam file is not containing unauthorized characters
if ! grep -q "[0-9A-Za-z!#$%&+.\/:;?@^_|~\-^\*=][0-9A-Za-z!#$%&*+.\/:;=?@^_|~-]*" "$1"; then
    echo "The input file is containing unauthorized characters. Please provide a file in the right format."
    exit 1
fi

# parse the parameters and start the main.py script
### OPTION LIST:
        ##-h or --help : help information
        ##-i or --input: input file (.sam)
        ##-o or --output: output name files (.txt)
python3 main.py -i $1 -o $2
