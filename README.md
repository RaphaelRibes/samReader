
                                    ____                      __              
       _____  ____ _   ____ ___    / __ \  ___   ____ _  ____/ /  ___    _____
      / ___/ / __ `/  / __ `__ \  / /_/ / / _ \ / __ `/ / __  /  / _ \  / ___/
     (__  ) / /_/ /  / / / / / / / _, _/ /  __// /_/ / / /_/ /  /  __/ / /    
    /____/  \__,_/  /_/ /_/ /_/ /_/ |_|  \___/ \__,_/  \__,_/   \___/ /_/     
`samReader` is a Python tool designed to analyze SAM files, providing insights into partially mapped and unmapped reads, as well as detailed CIGAR string analysis.

## Features

- **Partially Mapped and Unmapped Reads Analysis**: Identifies and reports reads that are partially mapped or unmapped.
- **Summary Reports**: Generates comprehensive summaries of the analyses in both text and LaTeX formats.

## Requirements

- Python 3.13 or higher
- Required Python packages:
  - `tqdm`
  - `pandas`
  - `numpy`
  - `matplotlib`
  - `seaborn`
  - `pysam`

## Installation

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/RaphaelRibes/samReader.git
   ```

2. **Navigate to the Directory**:

   ```bash
   cd samReader
   ```

3. **Install Dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

## Usage

To run `samReader`, execute the following command:

```bash
bash samReader.sh -i /path/to/your/mapping.sam
```

### Options

- `-i`: Path to the input SAM file.
- `-o`: (Optional) Specify the output directory. If not provided, the output will be saved in the current directory. Doesn't work right now.
- `-t`: (Optional) Trust the input format without performing format checks.

## Output

The tool generates the following outputs:

- **Partially Mapped Reads**: A FASTA file (`only_partially_mapped.fasta`) containing sequences of partially mapped reads.
- **Unmapped Reads**: A FASTA file (`only_unmapped.fasta`) containing sequences of unmapped reads.
- **Summary Report**: A text file (`summary.pdf`) containing a summary of the analyses.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request with your changes.

## License

This project is licensed under the MIT License. See the [GNU General Public Licence](https://www.gnu.org/licenses/) file for details.

## Acknowledgments

Special thanks to all contributors and the open-source community for their invaluable support.

ASCII art generated with https://patorjk.com/software/taag/
