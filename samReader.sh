#!/bin/bash

# Variables pour stocker les chemins d'entrée et de sortie
input_file=""
output_file=""
trusted=""

# Fonction pour afficher l'aide
usage() {
  echo "                                ____                      __              "
  echo "   _____  ____ _   ____ ___    / __ \  ___   ____ _  ____/ /  ___    _____"
  echo "  / ___/ / __ \`/  / __ \`__ \  / /_/ / / _ \ / __ \`/ / __  /  / _ \  / ___/"
  echo " (__  ) / /_/ /  / / / / / / / _, _/ /  __// /_/ / / /_/ /  /  __/ / /    "
  echo "/____/  \__,_/  /_/ /_/ /_/ /_/ |_|  \___/ \__,_/  \__,_/   \___/ /_/     "



  echo "Usage: $0 [-h|--help] [-i|--input input_file] [-o|--output output_file]"
  echo
  echo "Options:"
  echo "  -h, --help                Affiche ce message d'aide"
  echo "  -i, --input <fichier>     Spécifie le fichier d'entrée"
  echo "  -o, --output <fichier>    Spécifie le fichier de sortie"
  echo "  -t, --trusted             Ne vérifie pas le contenu du fichier d'entrée"
  exit 1
}

# Traitement des options
while [[ "$1" != "" ]]; do
    case $1 in
        -h | --help )   usage
                        exit
                        ;;
        -i | --input)   shift
                        input_file=$1
                        ;;
        -o | --output)  shift
                        output_file=$1
                        ;;
        # this option does not require an argument
        -t | --trusted) trusted="true"
                        ;;
        * )             usage
                        exit 1
    esac
    shift
done

# if the file is trusted, we don't check the content
if [ ! -z "$trusted" ]; then
    python3 main.py -i "$input_file" -o "$output_file" -t
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
    echo "The output file does not exist. Please provide the correct path."
    exit 1
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
python3 main.py -i "$input_file" -o "$output_file"
