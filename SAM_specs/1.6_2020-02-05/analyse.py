import numpy as np
from tqdm.auto import tqdm
import os
import sys
import yaml

# I know it looks horrible, but I had to do it to make it work
two_levels_up = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, two_levels_up)
from common_functions import toBinary

version = yaml.safe_load(open(f"{two_levels_up}/config.yaml", "r"))
SPECS = yaml.safe_load(open(f"{two_levels_up}/SAM_specs/{version['version']}/specs.yaml", "r"))

#### Create a fasta header ####
def toFasta(line):
    """
    Create a FASTA formatted head from a read line and its mapping situation.

    Args:
        line (dict): A dictionary containing read information with keys 'qname', 'mapq', 'pos', and 'seq'.

    Returns:
        str: A string header in FASTA format.
    """
    return f">{line[0]} MAPQ:{line[0]} POS:{line[3]}\n{line[9]}\n"

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
            elif char == "D":
                pass
            else:
                depth += [0] * num
            num = 0

    return dico, np.array(depth)

### Analyse the CIGAR = regular expression that summarise each read alignment ###
def percentMutation(dico) -> list:
    total_value = sum(dico.values())
    if total_value == 0:
        return [0.0] * len(SPECS['CIGAR_operations'])
    mut_list = SPECS['CIGAR_operations']
    res = []
    for mut in mut_list:  # Calculated percent of mutation if mut present in the dictionnary, else, percent of mut = 0
        res.append((dico.get(mut, 0.0) * 100) / total_value)
    return res


def globalPercentCigar(payload:list[list], depth, verbose=False):
    """
        Analyze the CIGAR strings and return a DataFrame with the percentage of each mutation type.

        Args:
            payload (list): A list of dictionaries containing read information.
            path (str): The path to the directory (not used in this version).

        Returns:
            pd.DataFrame: A DataFrame with the percentage of each mutation type.
            :param depth: A list of integers containing the depth of each position.
            :param payload: A list of dictionaries containing read information.
            :param verbose: A boolean to display the progress bar
        """
    data = []

    iterator = tqdm(enumerate(payload), desc="Analyzing CIGAR strings", total=len(payload)) if verbose else enumerate(payload)

    for n, line in iterator:
        dico, line_depth = readCigar(line[5])
        percent_mut = percentMutation(dico)

        if sum(percent_mut) == 0:
            pass
        else:
            data.append(percent_mut)

            pos = int(line[3])
            depth[pos:pos + len(line_depth)] += line_depth

    data = np.array(data)

    columns_dict = {}
    for n, mut in enumerate(SPECS['CIGAR_operations']):
        columns_dict[mut] = data[:, n].sum()

    return columns_dict, depth


def main():
    pass


if __name__ == "__main__":
    main()
