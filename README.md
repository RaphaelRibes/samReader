                                    ____                      __
       _____  ______   ____ ___    / __ \  ___   ______  ____/ /  ___    _____
      / ___/ / __  /  / __ __  \  / /_/ / / _ \ / __  / / __  /  / _ \  / ___/
     (__  ) / /_/ /  / / / / / / / _, _/ /  __// /_/ / / /_/ /  /  __/ / /
    /____/  \____/  /_/ /_/ /_/ /_/ |_|  \___/ \____/  \____/   \___/ /_/
`samReader` is a Python tool designed to analyze SAM files, providing insights into partially mapped and unmapped reads, as well as detailed CIGAR string analysis.

## Features

- **Partially Mapped and Unmapped Reads Analysis**: Identifies and reports reads that are partially mapped or unmapped.
- **Summary Reports**: Generates comprehensive summaries of the analyses in both text and LaTeX formats.

## Requirements

- Python 3.13 or higher
- Required Python packages described in requirements.txt

## Installation

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/RaphaelRibes/samReader.git
   ```

2. **Navigate to the Directory**:

   ```bash
   cd samReader
   ```

3. **Install Venv**:

   ```bash
   python3 -m venv .venv
   ```

4. **Activate Venv**:

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

### Options

- `-i` or `--input`:        Path to the input SAM file.
- `-o` or `--output`:      (Optional) Specify the output directory. If not provided, the output will be saved in the current directory. Doesn't work right now.
- `-t` or `--trusted`:     (Optional) Trust the input format without performing format checks.
- `-v` or `--verbose`:     (Optional) Enable verbose mode.
- `-a` or `--ask-to-open`: (Optional) Ask to open the summary report after the analysis.
- `-h` or `--help`:         Display the help message.
- 
## Output

The tool generates the following outputs:

- **Mapped Reads**¹: A FASTA file (`only_mapped.fasta`) containing sequences of mapped reads.
- **Partially Mapped Reads**¹: A FASTA file (`only_partially_mapped.fasta`) containing sequences of partially mapped reads.
- **Unmapped Reads**¹: A FASTA file (`only_unmapped.fasta`) containing sequences of unmapped reads.
- **Summary Report**: A text file (`summary.pdf`) containing a summary of the analyses.

[1] : *If you have enabled single fasta file mode, you will only have one fasta file like `mapping.fasta`*


## Contributing

Contributions are welcome! Please fork the repository and submit a pull request with your changes.

## License

This project is licensed under the MIT License. See the [GNU General Public Licence](https://www.gnu.org/licenses/) file for details.

## Acknowledgments

Special thanks to all contributors and the open-source community for their invaluable support.

ASCII art based on this generator https://patorjk.com/software/taag/
