                                        ____                      __              
           _____  ____ _   ____ ___    / __ \  ___   ____ _  ____/ /  ___    _____
          / ___/ / __ `/  / __ `__ \  / /_/ / / _ \ / __ `/ / __  /  / _ \  / ___/
         (__  ) / /_/ /  / / / / / / / _, _/ /  __// /_/ / / /_/ /  /  __/ / /    
        /____/  \__,_/  /_/ /_/ /_/ /_/ |_|  \___/ \__,_/  \__,_/   \___/ /_/     
                                                                                  

does not even start yet don't look at this for now

## Abstract

Next-generation sequencing (NGS) technologies have revolutionized genomics by enabling the analysis of short DNA sequences (reads).
This project focuses on the analysis of Sequence Alignment/Map (SAM) files, which store the results of aligning these reads to a reference genome. 
The aim of this project is to develop a hybrid Python/Shell script that efficiently extracts and summarizes key information from SAM files.

The objectives are:
1. **Mapping Read Counts**: Determine how many reads are mapped by counting reads based on their mapping status as indicated by SAM flags.
2. **Read Mapping Patterns**: Analyze how reads (and pairs of reads) are mapped by categorizing them according to different SAM flags, revealing patterns of proper or improper alignment.
3. **Read Distribution Across the Genome**: Assess the distribution of reads along the reference genome, including per-chromosome read counts, to evaluate the uniformity of mapping.
4. **Mapping Quality**: Evaluate the quality of read alignments by analyzing mapping scores, either as discrete values or within score ranges, to understand the confidence in each alignment.

This project will provide a clear summary of the mapping characteristics, enabling a deeper understanding of the sequence alignment process, which is critical for various applications in genomics and bioinformatics.

## Usage

The main script `sam_reader.sh` is a shell script that calls a Python script `sam_reader.py` to process SAM files.
The script can take the following arguments:
- -h or --help : help information
- -i or --input: input file (.sam)
- -o or --output: output name files (.txt)
- -t or --trusted: assumes the input file is trusted and skips the verification step (optional)

## Installation

To use this script, you need to have Python installed on your system.
You can download the script directly from this repository or clone the repository using the following command:

```bash
git clone https://github.com/RaphaelRibes/SamReader.git
```

Install the required Python packages using the following command:

```bash
pip install -r requirements.txt
```

## Example

To run the script, use the following command:

```bash
bash sam_reader.sh -i example.sam -o example_output
```

This command will process the `example.sam` file and generate output files with the prefix `example_output`.

## Aknowledgements

ASCII art generated with https://patorjk.com/software/taag/

## License

This program is free software: you can redistribute it and/or modify
        it under the terms of the GNU General Public License as published by
        the Free Software Foundation, either version 3 of the License, or
        (at your option) any later version.
        This program is distributed in the hope that it will be useful,
        but WITHOUT ANY WARRANTY; without even the implied warranty of
        MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
        GNU General Public License for more details.
        You should have received a copy of the GNU General Public License
        along with this program. If not, see <https://www.gnu.org/licenses/>.
