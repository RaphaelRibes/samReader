import re
import numpy as np

from tqdm.auto import tqdm
import pandas as pd
import os

#### Convert to binary ####
def toBinary(load, exponent):
    flagB = bin(int(load)).replace('0b', '')  # Convert to binary and remove '0b'
    if flagB[0] == '-':
        starting_index = 1  # Start at index 1 if negative
        exponent += 1  # Increment exponent if negative
    else:
        starting_index = 0

    # Adjust size to exponent
    flagB = ['0'] * (exponent - len(flagB)) + list(flagB[starting_index:])
    return "".join(flagB)  # Return binary flag


#### Create a fasta header ####
def toFasta(line, mapping_situation):
    """
    Create a FASTA formatted head from a read line and its mapping situation.

    Args:
        line (dict): A dictionary containing read information with keys 'qname', 'mapq', 'pos', and 'seq'.
        mapping_situation (str): A string describing the mapping situation of the read.

    Returns:
        str: A string header in FASTA format.
    """
    header = f">{line['qname']} {mapping_situation}".strip() + f" MAPQ:{line['mapq']}"
    pos = line['pos']
    header = f"{header} POS:{pos}" if pos != "0" else f"{header}"
    sequence = line['seq']
    fasta_format = f"{header}\n{sequence}\n"
    return fasta_format

#### Analyze the partially mapped or unmapped reads ####
def readMapping(payload, path, single_file=False, verbose=True):
    # Determine file handlers dynamically
    if single_file:
        file_handlers = {
            "partially_mapped": open(f"{path}/all_mapped_reads.fasta", "w"),
            "unmapped": open(f"{path}/all_mapped_reads.fasta", "a"),  # Append to the same file
            "mapped": open(f"{path}/all_mapped_reads.fasta", "a"),
        }
    else:
        file_handlers = {
            "partially_mapped": open(f"{path}/only_partially_mapped.fasta", "w"),
            "unmapped": open(f"{path}/only_unmapped.fasta", "w"),
            "mapped": open(f"{path}/only_mapped.fasta", "w"),
        }

    results = {"s_mapped": 0, "s_partially_mapped": 0, "s_unmapped": 0,
               "p_mapped": 0, "p_partially_mapped": 0, "p_unmapped": 0}

    iterator = list(zip(payload[::2], payload[1::2]))
    if verbose:
        iterator = tqdm(iterator,
                        desc="Analyzing partially mapped and unmapped reads",
                        total=len(iterator))

    try:  # We do it in a try block to ensure that all files are closed properly in case of an exception
        for lines in iterator:
            lines = list(lines)
            pair_mapping = []
            for line in lines:
                # Compute the binary representation of the flag with a length of 16 bits
                flag = toBinary(line["flag"], 16)

                # Check if the read is partially mapped
                if int(flag[-2]) == 1 and line['cigar'] != "100M":
                    results["s_partially_mapped"] += 1  # Increment the count of partially mapped reads
                    # Mark the read as partially mapped
                    pair_mapping.append("p")
                    file_handlers["partially_mapped"].write(toFasta(line, "PARTIALLY MAPPED" if single_file else ""))  # Write to the partially mapped file

                # Check if the read is mapped
                elif int(flag[-2]) == 1:
                    results["s_mapped"] += 1  # Increment the count of mapped reads
                    pair_mapping.append("m")  # Mark the read as mapped
                    file_handlers["mapped"].write(toFasta(line, "MAPPED" if single_file else ""))  # Write to the mapped file

                # Check if the read is unmapped
                elif int(flag[-3]) == 1:
                    results["s_unmapped"] += 1  # Increment the count of unmapped reads
                    pair_mapping.append("u")  # Mark the read as unmapped
                    file_handlers["unmapped"].write(toFasta(line, "UNMAPPED" if single_file else ""))  # Write to the unmapped file

                # Default case (flag 2 and 3 are not activated): mark the read as partially mapped
                else:
                    results["s_partially_mapped"] += 1  # Increment the count of partially mapped reads
                    pair_mapping.append("p")  # Mark the read as partially mapped
                    file_handlers["partially_mapped"].write(toFasta(line, "PARTIALLY MAPPED" if single_file else ""))  # Write to the partially mapped file

            # Check if all reads in the pair are mapped
            if all(m == "m" for m in pair_mapping):
                results["p_mapped"] += 1  # Increment the count of pairs where both reads are mapped

            # Check if all reads in the pair are unmapped
            elif all(m == "u" for m in pair_mapping):
                results["p_unmapped"] += 1  # Increment the count of pairs where both reads are unmapped

            # Default case: mark the pair as partially mapped
            else:
                results["p_partially_mapped"] += 1  # Increment the count of pairs where at least one read is partially mapped

    finally:
        # Ensure all files are closed properly
        for handler in file_handlers.values():
            handler.close()

    # Check that the sum of mapped, partially mapped and unmapped reads is equal to the total number of reads
    assert results["s_mapped"] + results["s_partially_mapped"] + results["s_unmapped"] != len(iterator), \
        (f"Sum of mapped, partially mapped and unmapped reads should be equal to the total number of reads: "
         f"{results['s_mapped']} + {results['s_partially_mapped']} + {results['s_unmapped']} != {len(payload)}")

    return results



### Analyse the CIGAR = regular expression that summarise each read alignment ###
def readCigar(cigar):
    if cigar == "*": return {}

    dico = {}
    num = 0

    # we can skip using REGEX here because we verified the format of the CIGAR string
    # it's only faster by 8% and it took me all morning to find a new way ffs
    for char in cigar:
        if char.isdigit():
            # Build the number if the character is a digit
            num = num * 10 + int(char)
        else:
            # Add the operation to the dictionary
            dico[char] = dico.get(char, 0) + num
            num = 0

    return dico

### Analyse the CIGAR = regular expression that summarise each read alignment ###
def percentMutation(dico) -> list:
    total_value = sum(dico.values())
    mut_list = ['M', 'I', 'D', 'S', 'H', 'N', 'P', 'X', '=']
    res = []
    for mut in mut_list:  # Calculated percent of mutation if mut present in the dictionnary, else, percent of mut = 0
        if mut in dico.keys():
            res.append((round((dico[mut] * 100) / total_value, 2)))
        else:
            res.append(0.0)
    return res # We remove the last coma


def globalPercentCigar(payload:list[dict], verbose=True):
    """
        Analyze the CIGAR strings and return a DataFrame with the percentage of each mutation type.

        Args:
            payload (list): A list of dictionaries containing read information.
            path (str): The path to the directory (not used in this version).

        Returns:
            pd.DataFrame: A DataFrame with the percentage of each mutation type.
            :param payload:  A list of dictionaries containing read information.
            :param verbose:  A boolean to display the progress bar
        """
    data = []

    iterator = enumerate(payload)
    if verbose:
        iterator = tqdm(iterator, desc="Analyzing CIGAR strings", total=len(payload))

    for n, line in iterator:
        dico = readCigar(line["cigar"])
        percent_mut = percentMutation(dico)
        if sum(percent_mut) == 100:
            data.append(percentMutation(dico))

    data = np.array(data)
    nb_reads = len(data)

    def format_metric(value):
        """
        Format the metric value as a percentage string.

        Args:
            value (int): The sum of a specific mutation type.

        Returns:
            str: The formatted percentage string.
        """
        mid = str(round(value / nb_reads, 2))
        if value / nb_reads == 0:
            mid = "0"
        elif value / nb_reads < 0.01:
            mid = "$<$0.01"
        return mid + "\\%"

    columns_dict = {
    "M": format_metric(data[:, 0].sum()),
    "I": format_metric(data[:, 1].sum()),
    "D": format_metric(data[:, 2].sum()),
    "S": format_metric(data[:, 3].sum()),
    "H": format_metric(data[:, 4].sum()),
    "N": format_metric(data[:, 5].sum()),
    "P": format_metric(data[:, 6].sum()),
    "X": format_metric(data[:, 7].sum()),
    "=": format_metric(data[:, 8].sum()),
}
    return columns_dict


def main():
    pass


if __name__ == "__main__":
    main()
