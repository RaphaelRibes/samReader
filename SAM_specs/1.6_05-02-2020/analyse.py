import numpy as np
from tqdm.auto import tqdm
import os
import sys

# I know it looks horrible, but I had to do it to make it work
two_levels_up = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, two_levels_up)
from common_functions import toBinary

#### Create a fasta header ####
def toFasta(line):
    """
    Create a FASTA formatted head from a read line and its mapping situation.

    Args:
        line (dict): A dictionary containing read information with keys 'qname', 'mapq', 'pos', and 'seq'.
        mapping_situation (str): A string describing the mapping situation of the read.

    Returns:
        str: A string header in FASTA format.
    """
    header = f">{line[0]} MAPQ:{line[0]}"
    header = f"{header} POS:{line[3]}" if line[3] != "0" else f"{header}"
    fasta_format = f"{header}\n{line[9]}\n"
    return fasta_format

#### Analyze the partially mapped or unmapped reads ####
def readMapping(payload, path, verbose=True):
    # Determine file handlers dynamically
    os.makedirs(path, exist_ok=True)
    file_handlers = {
        "partially_mapped": open(f"{path}/only_partially_mapped.fasta", "w"),
        "unmapped": open(f"{path}/only_unmapped.fasta", "w"),
        "mapped": open(f"{path}/only_mapped.fasta", "w"),
    }

    results = {"s_mapped": 0, "s_partially_mapped": 0, "s_unmapped": 0,
               "p_mapped": 0, "p_partially_mapped": 0, "p_unmapped": 0}

    iterator = list(zip(payload[::2], payload[1::2]))  # Pair reads together
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
                flag = toBinary(line[1], 16)

                # Check if the read is partially mapped
                if int(flag[-2]) == 1 and line[5] != f"{len(line[9])}M":
                    results["s_partially_mapped"] += 1  # Increment the count of partially mapped reads
                    # Mark the read as partially mapped
                    pair_mapping.append("p")
                    file_handlers["partially_mapped"].write(toFasta(line))  # Write to the partially mapped file

                # Check if the read is mapped
                elif int(flag[-2]) == 1:
                    results["s_mapped"] += 1  # Increment the count of mapped reads
                    pair_mapping.append("m")  # Mark the read as mapped
                    file_handlers["mapped"].write(toFasta(line))  # Write to the mapped file

                # Check if the read is unmapped
                elif int(flag[-3]) == 1:
                    results["s_unmapped"] += 1  # Increment the count of unmapped reads
                    pair_mapping.append("u")  # Mark the read as unmapped
                    file_handlers["unmapped"].write(toFasta(line))  # Write to the unmapped file

                # Default case (flag 2 and 3 are not activated): mark the read as partially mapped
                else:
                    results["s_partially_mapped"] += 1  # Increment the count of partially mapped reads
                    pair_mapping.append("p")  # Mark the read as partially mapped
                    file_handlers["partially_mapped"].write(toFasta(line))  # Write to the partially mapped file

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
    if cigar == "*": return {}, np.array([])

    dico = {}
    num = 0
    depth = []

    # we can skip using REGEX here because we verified the format of the CIGAR string
    # it's only faster by 8% and it took me all morning to find a new way ffs
    for char in cigar:
        if char.isdigit():
            # Build the number if the character is a digit
            num = num * 10 + int(char)
        else:
            # Add the operation to the dictionary
            dico[char] = dico.get(char, 0) + num
            if char == "M":
                depth += [1] * num
            else:
                depth += [0] * num
            num = 0

    return dico, np.array(depth)

### Analyse the CIGAR = regular expression that summarise each read alignment ###
def percentMutation(dico) -> list:
    total_value = sum(dico.values())
    mut_list = ['M', 'I', 'D', 'S', 'H', 'N', 'P', 'X', '=']
    res = []
    for mut in mut_list:  # Calculated percent of mutation if mut present in the dictionnary, else, percent of mut = 0
        if mut in dico.keys():
            res.append((round((dico[mut] * 100) / total_value, 5)))
        else:
            res.append(0.0)
    return res


def globalPercentCigar(payload:list[list], depth, verbose=False):
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

    iterator = tqdm(enumerate(payload), desc="Analyzing CIGAR strings", total=len(payload)) if verbose else enumerate(payload)

    for n, line in iterator:
        dico, line_depth = readCigar(line[5])
        percent_mut = percentMutation(dico)

        if round(sum(percent_mut), 4) == 100:
            data.append(percent_mut)

            pos = int(line[3])
            depth[pos:pos + len(line_depth)] += line_depth

        elif sum(percent_mut) == 0:
            pass
        else:
            raise ValueError(f"Sum of mutation percentages should be equal to 100: {sum(percent_mut)}")

    data = np.array(data)
    nb_reads = len(data)

    columns_dict = {
    "M": data[:, 0].sum(),
    "I": data[:, 1].sum(),
    "D": data[:, 2].sum(),
    "S": data[:, 3].sum(),
    "H": data[:, 4].sum(),
    "N": data[:, 5].sum(),
    "P": data[:, 6].sum(),
    "X": data[:, 7].sum(),
    "=": data[:, 8].sum(),
}
    return columns_dict, depth


def main():
    pass


if __name__ == "__main__":
    main()
