#!/bin/bash

RED='\e[0;31m'
WHITE='\e[0;37m'

# Function to display the help message
usage() {
  echo -e "${WHITE}"
  echo "                                ____                      __              "
  echo "   _____  ______   ____ ___    / __ \  ___   ______  ____/ /  ___    _____"
  echo "  / ___/ / __  /  / __ \`__ \  / /_/ / / _ \ / __  / / __  /  / _ \  / ___/"
  echo " (__  ) / /_/ /  / / / / / / / _, _/ /  __// /_/ / / /_/ /  /  __/ / /    "
  echo "/____/  \____/  /_/ /_/ /_/ /_/ |_|  \___/ \____/  \____/   \___/ /_/     "
  echo
  echo "Usage: $0 -i|--input input_file <input.sam> [-o|--output <output_directory>] [-t|--trusted] [-v|--verbose][-h|--help]"
  # if version is "UNDEFINED PLEASE CONFIGURE IT IN config.yaml"
  if [ "$version" = "UNDEFINED PLEASE CONFIGURE IT IN config.yaml" ]; then
      echo -e "${RED}SAM Version: $version"
  else
      echo -e "SAM Version: $version"
  fi
  sam_versions
  echo
  echo -e "${WHITE}Options:"
  echo "  -i, --input <file>        Specifies the input file"
  echo "  -o, --output <directory>  (optional) Specifies the output directory (by default the current directory)"
  echo "  -t, --trusted             (optional) Skips checking the content of the input file"
  echo "  -v, --verbose             (optional) Shows details of each step"
  echo "  -a, --auto-open           (optional) Open the output file at the end of the analysis"
  exit
}

sam_versions() {
    echo -e "${WHITE}"
    echo "The available versions are:"
    for version in "$(dirname "$0")"/SAM_specs/*; do
        echo "  - $(basename "$version")"
    done
}

# Using getopt to support both short and long options
PARSED_OPTIONS=$(getopt -o "hi:o:tva" -l "help,input:,output:,trusted,verbose,ask-to-open" -n "$0" -- "$@")

# Open the config.yaml file and get the version
version=$(grep -oP "[0-9]+\.[0-9]+_[0-9]{4}-[0-9]{2}-[0-9]{2}" "$(dirname "$0")"/config.yaml)

# if version is "UNDEFINED PLEASE CONFIGURE IT IN config.yaml"
if [ -z "$version" ]; then
    version="UNDEFINED PLEASE CONFIGURE IT IN config.yaml";
    usage;
fi

# if version doesn't exist in SAM_specs folder
if [ ! -d "$(dirname "$0")/SAM_specs/$version" ]; then
    echo "The version of the script is not found in the SAM_specs folder. Please provide the version in the config.yaml file."
    usage;
fi

# Check if getopt ran successfully.
# $?: The exit status of the last command. If it is 0, then the command was successful.
if [ $? != 0 ]; then
    echo "Error in options"
    usage
fi

# Apply the parsed options
eval set -- "$PARSED_OPTIONS"

# Default variables
input_file=""
output_file=""
trusted=
verbose=
auto_open=

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
        -a|--ask-to-open)
            auto_open=true; shift;;
        --)
            shift; break;;
        *)
            echo "Unrecognized option"; usage;;
    esac
done

# This script reads the sam file and check if the file is empty or not, containing unauthorized characters or not and then
# starts main.py script to read the sam file and generate the output file.

# Check if the input file is provided or not
if [ -z "$input_file" ]; then
    echo "Please provide the input file."
    usage;
fi

# Check if the path of the input file is correct or not
if [ ! -f "$input_file" ]; then
    echo "The input file does not exist. Please provide the correct path."
    usage;
fi

# If there is a output file, check if the path of the output file is correct or not
if [ ! -z "$output_file" -a ! -d "$output_file" ]; then
    # We create the folder
    mkdir -p "$(dirname "$output_file")"
fi

# Check if the sam file is a directory or not
if [ -d "$input_file" -o -d "$output_file" ]; then
    echo "The input file is a directory. Please provide a file."
    usage;
fi

# Check if the sam file is empty or not
if [ ! -s "$input_file" ]; then
    echo "The input file is empty. Please provide a non-empty file."
    usage;
fi

# if the file is trusted, we don't check the content
if [ ! -z "$trusted" ]; then
    python3 "$(dirname "$0")"/main.py -i "$input_file" -o "$output_file" ${trusted:+-t} ${verbose:+-v} ${auto_open:+-a}
    exit 0
fi

# Check if the sam file is not containing unauthorized characters
query=$(grep 'GLOBAL: ' "$(dirname "$0")/SAM_specs/$version/specs.yaml" | cut -d ' ' -f 2)
if ! grep -q "$query" "$input_file"; then
    echo "The input file is containing unauthorized characters. Please provide a file in the right format ($query)."
    usage;
fi

# parse the parameters and start the main.py script
python3 "$(dirname "$0")"/main.py -i "$input_file" -o "$output_file" ${trusted:+-t} ${verbose:+-v} ${auto_open:+-a}
