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
    return f">{line[0]} MAPQ:{line[0]} POS:{line[3]}\n{line[9]}\n"

#### Analyze the partially mapped or unmapped reads ####
def readMapping(payload, path, verbose=True):
    """
    Analyze the partially mapped or unmapped reads from the payload and write them to separate FASTA files.

    Args:
        payload (list): A list of read information.
        path (str): The directory path where the output FASTA files will be saved.
        verbose (bool): If True, display a progress bar.

    Returns:
        dict: A dictionary with counts of single and paired reads in different mapping categories.
    """
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
            cigar_mutations, _ = readCigar(line[5])

            # Check if the read is partially mapped
            if int(flag[-2]) == 1 and list(cigar_mutations.keys()) != ["M"]:
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

def readCigar(cigar):
    """
    Parse a CIGAR string and calculate the depth of the read.

    Args:
        cigar (str): A CIGAR string representing the alignment of the read.

    Returns:
        tuple: A dictionary with the count of each CIGAR operation and a numpy array representing the depth of the read.
    """
    if cigar == "*":  # If the read is unmapped
        return {}, np.array([])

    dico = {}
    num = 0
    depth = []

    # Parsing the CIGAR string
    for char in cigar:
        if char.isdigit():
            # Build a number if the character is a digit
            num = num * 10 + int(char)
        else:
            # Update the dictionary to count each operation
            dico[char] = dico.get(char, 0) + num

            # Handle different operations
            if char in "M=X":  # Alignment (match or mismatch)
                depth += [1] * num  # Add to depth
            elif char in "DN":  # Deletion or skipped region
                depth += [0] * num  # Add zeros for bases missing in the query
            elif char in "I":  # Insertion
                # Insertion only consumes the query, so it's ignored here
                pass
            elif char in "S":  # Soft clipping
                # Ignore soft clipping (bases present but not aligned)
                pass
            elif char in "H":  # Hard clipping
                # Ignore hard clipping (bases completely excluded)
                pass
            elif char in "P":  # Padding
                # Ignore padding (silent deletion)
                pass

            # Reset the counter for the next operator
            num = 0

    # Convert the depth list to a numpy array
    return dico, np.array(depth)

### Analyse the CIGAR = regular expression that summarise each read alignment ###
def percentMutation(dico) -> list:
    """
    Calculate the percentage of each mutation type based on the provided dictionary.

    Args:
        dico (dict): A dictionary where keys are mutation types and values are their counts.

    Returns:
        list: A list of percentages for each mutation type defined in SPECS['CIGAR_operations'].
              If the total count of mutations is zero, returns a list of zeros.
    """
    total_value = sum(dico.values())
    if total_value == 0:
        return [0.0] * len(SPECS['CIGAR_operations'])

    mut_list = SPECS['CIGAR_operations']
    result = []
    for mut in mut_list:
        # Calculate the percentage of mutation if present in the dictionary, else percentage is 0
        result.append((dico.get(mut, 0.0) * 100) / total_value)

    return result


def globalPercentCigar(payload: list[list], depth, verbose=False):
    """
    Analyze the CIGAR strings from the payload and calculate the global percentage of each mutation type.

    Args:
        payload (list[list]): A list of lists, where each inner list contains read information.
        depth (numpy.ndarray): A numpy array representing the depth of the reads.
        verbose (bool): If True, display a progress bar.

    Returns:
        tuple: A dictionary with the sum of each mutation type and the updated depth array.
    """
    data = []

    # Create an iterator with a progress bar if verbose is True
    iterator = tqdm(enumerate(payload), desc="Analyzing CIGAR strings", total=len(payload)) if verbose else enumerate(payload)

    for n, line in iterator:
        # Parse the CIGAR string and get the depth of the read
        dico, line_depth = readCigar(line[5])
        # Calculate the percentage of each mutation type
        percent_mut = percentMutation(dico)

        if sum(percent_mut) != 0:
            data.append(percent_mut)

            pos = int(line[3])
            tlen = int(line[8])

            if tlen == 0:  # If there is nothing to map
                continue

            if tlen < 0:  # If the read is reversed
                line_depth = line_depth[::-1]  # Reverse the depth list

            # Add the depth of the read to the global depth
            depth[pos:pos+len(line_depth)] += line_depth

    # Convert the data list to a numpy array
    data = np.array(data)

    # Create a dictionary to store the sum of each mutation type
    columns_dict = {}
    for n, mut in enumerate(SPECS['CIGAR_operations']):
        columns_dict[mut] = data[:, n].sum()

    return columns_dict, depth


def main():
    pass


if __name__ == "__main__":
    main()
