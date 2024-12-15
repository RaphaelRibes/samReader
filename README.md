                                    ____                      __
       _____  ______   ____ ___    / __ \  ___   ______  ____/ /  ___    _____
      / ___/ / __  /  / __ __  \  / /_/ / / _ \ / __  / / __  /  / _ \  / ___/
     (__  ) / /_/ /  / / / / / / / _, _/ /  __// /_/ / / /_/ /  /  __/ / /
    /____/  \____/  /_/ /_/ /_/ /_/ |_|  \___/ \____/  \____/   \___/ /_/
`samReader` is a Python tool designed to analyze SAM files, providing insights into partially mapped and unmapped reads, as well as detailed CIGAR string analysis.

## Features

- **Summary Reports**: Generates comprehensive summaries of the analyses in both text and LaTeX formats.
- **Detailed CIGAR Analysis**: Provides detailed information about the CIGAR strings of the reads.
- **Chromosome-Specific Analysis**: Generates separate directories for each chromosome, containing mapped, partially mapped, and unmapped reads.
- **FASTA Output**: Outputs the sequences of mapped, partially mapped, and unmapped reads in FASTA format.
- **Depth Analysis**: Calculates the depth of coverage for each chromosome.
- **Evolution of the mapping quality**: Displays the evolution of the mapping quality over the length of the chromosome.
- **Highly Customizable**: Offers a wide range of options to customize the analysis (see how to use config.yaml).

## Requirements

- Python 3.13 or higher
    ```bash
    sudo apt-get install python3.13-full
    ```
- Texlive-full using
    ```bash
    sudo apt-get install texlive-full
    ```
- Required Python packages described in requirements.txt

### Optional
I use xdg open to open the pdf file. If you want to use the `--auto-open` option, you need to install xdg-utils.
```bash
sudo apt-get install xdg-utils
```

## Installation

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/RaphaelRibes/samReader.git
   ```

2. **Navigate to the Directory**:

   ```bash
   cd samReader
   ```

3. **Install the Virtual Environment (venv)**:

   ```bash
   python3.13 -m venv .venv
   ```

4. **Activate the venv**:

   ```bash
   source .venv/bin/activate
   ```
   
5. **Install Requirements**:

   ```bash
    pip install -r requirements.txt
    ```

## Usage

The minimal command to run `samReader` is described like this:

```bash
bash samReader.sh -i /path/to/your/mapping.sam
```

### How to use config.yaml

The config.yaml file is used to customize the analysis. You can change the following parameters:
- **version** (default `1.6_2020-02-05`): The version of the SAM file format. You can see every available version typing `bash samReader.sh -h`.
- **separator** (default `-`): The separator used in the SAM file to dinstinguish the chromosome name from the read number. 
For exemple, in `Clone1-153694`, the separator is `-`.
**Make sure to use the same separator for each chromosome of your `.sam` file**
- **mapq threshold** (default `0`): The minimum mapping quality to consider a read as mapped.
- **significant figures** (default `2`): The number of significant figures to display in the summary report.
- **bins** (default `100`): The number of bins to use for the mapping quality histogram. The higher the number, the more precise the histogram.
- **calculation method** (default for depth `median` and for mapq `mean`): The method used to calculate the depth of coverage and mapping quality. You can choose between `mean` and `median`.
- **n ticks** (default `10`): The number of ticks to display on the x-axis of the mapping quality evolution plot. The higher the number, the more precise the graduation on the x-axis will be.

**The program should work with the default parameters. If you change the parameters, their is no guarantee that the program will work so make sure to use corresponding parameters for your `.sam` file.**
### Options

- `-i` or `--input`:        Path to the input SAM file.
- `-o` or `--output`:      (Optional) Specify the output directory. If not provided, the output will be saved in the current directory. Doesn't work right now.
- `-t` or `--trusted`:     (Optional) Trust the input format without performing format checks.
- `-v` or `--verbose`:     (Optional) Enable verbose mode.
- `-a` or `--auto-open`:   (Optional) Open the summary report after the analysis.
- `-h` or `--help`:         Display the help message.
- 
## Output

The tool generates the following outputs:

- **Summary Report**: A text file (`summary.pdf`) containing a summary of the analyses.

- One directory for each chromosome containing the following files:
  - **Mapped Reads**: A FASTA file (`only_mapped.fasta`) containing sequences of mapped reads.
  - **Partially Mapped Reads**: A FASTA file (`only_partially_mapped.fasta`) containing sequences of partially mapped reads.
  - **Unmapped Reads**: A FASTA file (`only_unmapped.fasta`) containing sequences of unmapped reads.


## Contributing

Contributions are welcome! Please fork the repository and submit a pull request with your changes.

## License

This project is licensed under the MIT License. See the [GNU General Public Licence](https://www.gnu.org/licenses/) file for details.

## Acknowledgments

Special thanks to all contributors and the open-source community for their invaluable support.

ASCII art based on this generator https://patorjk.com/software/taag/
