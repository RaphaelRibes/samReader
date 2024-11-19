import re
from sys import flags

from tqdm.auto import tqdm
import pandas as pd
import os

#### Convert to binary ####
def toBinary(load, exponent):
    flagB = bin(int(load))  # Transform the integer into a binary.
    flagB = flagB.replace('0b', '')  # Remove '0b' Example: '0b1001101' > '1001101'
    flagB = list(flagB)

    if flagB[0] == '-':
        starting_index = 1  # We start at the index 1 if the number is negative.
        exponent += 1  # We add 1 to the exponent if the number is negative.
    else:
        starting_index = 0

    if len(flagB) < exponent:  # Size adjustement to exponent
        add = exponent - len(
            flagB)  # We compute the difference between the maximal size and the length of the binary flag.
        for t in range(add):
            flagB.insert(starting_index, '0')  # We insert 0 to complete until the maximal flag size.
    return "".join(flagB)  # We return the flag in binary format.


def toFasta(line, mapping_situation):
    header = f">{line['qname']} {mapping_situation}".strip() + f" MAPQ:{line['mapq']}"
    pos = line['pos']
    header = f"{header} POS:{pos}" if pos != "0" else f"{header}"
    sequence = line['seq']
    fasta_format = f"{header}\n{sequence}\n"
    return fasta_format

def check_all_mapped(l: list):
    flag = toBinary(l[0]["flag"], 16)[-2] == "1" and l[0]['cigar'] == "100M"
    if len(l) == 1:
        return flag
    else:
        l.pop(0)
        return flag and check_all_mapped(l)

def check_all_unmapped(l: list):
    flag = toBinary(l[0]["flag"], 16)[-3] == "1"
    if len(l) == 1:
        return flag
    else:
        l.pop(0)
        return flag and check_all_unmapped(l)

def check_all_partially_mapped(l: list):
    flag = toBinary(l[0]["flag"], 16)[-2] == "1" and l[0]['cigar'] != "100M"
    if len(l) == 1:
        return flag
    else:
        l.pop(0)
        return flag and check_all_partially_mapped(l)

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
    pair_checked = []

    iterator = list(zip(payload[::2], payload[1::2]))
    if verbose:
        iterator = tqdm(iterator,
                        desc="Analyzing partially mapped and unmapped reads",
                        total=len(iterator))

    try:  # We do it in a try block to ensure that all files are closed properly in case of an exception
        for lines in iterator:
            lines = list(lines)
            for line in lines:
                flag = toBinary(line["flag"], 16)  # Compute flag
                if int(flag[-2]) == 1:  # Partially mapped or mapped
                    if line['cigar'] != "100M":
                        results["s_partially_mapped"] += 1
                        if line["qname"] not in pair_checked and check_all_partially_mapped(lines.copy()):
                            results["p_partially_mapped"] += 1
                        file_handlers["partially_mapped"].write(toFasta(line, "PARTIALLY MAPPED" if single_file else ""))
                    else:
                        results["s_mapped"] += 1
                        if line["qname"] not in pair_checked and check_all_mapped(lines.copy()):
                            results["p_mapped"] += 1
                        file_handlers["mapped"].write(toFasta(line, "MAPPED" if single_file else ""))

                elif int(flag[-3]) == 1:  # Unmapped
                    results["s_unmapped"] += 1
                    if line["qname"] not in pair_checked and check_all_unmapped(lines.copy()):
                        results["p_unmapped"] += 1
                    file_handlers["unmapped"].write(toFasta(line, "UNMAPPED" if single_file else ""))

                elif int(flag[-2]) == 0 and int(flag[-3]) == 0:
                    results["s_partially_mapped"] += 1
                    if line["qname"] not in pair_checked and check_all_partially_mapped(lines.copy()):
                        results["p_partially_mapped"] += 1
                    file_handlers["partially_mapped"].write(toFasta(line, "PARTIALLY MAPPED" if single_file else ""))

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
    dico = {}

    if cigar == "*": return dico

    regex = r"\*|([0-9]+[MIDNSHPX=])"
    ext = re.findall(regex, cigar, re.MULTILINE)  # split cigar

    for cig in ext:
        dico[cig[-1]] = int(cig[:-1])
        # cig[-1] gives the type of mutation (M, I, D, S, H, N, P, X, = or *)
        # cig[:-1] gives the number of mutation

    return dico


### Analyse the CIGAR = regular expression that summarise each read alignment ###
def percentMutation(dico):
    totalValue = sum(dico.values())
    mutList = ['M', 'I', 'D', 'S', 'H', 'N', 'P', 'X', '=']
    res = ""
    for mut in mutList:  # Calculated percent of mutation if mut present in the dictionnary, else, percent of mut = 0
        if mut in dico.keys():
            res += (str(round((dico[mut] * 100) / totalValue, 2)) + ",")
        else:
            res += ("0.00" + ",")
    return res[:-1]  # We remove the last coma


def outputTableCigar(payload, path):
    with open(f"{path}/outpuTable_cigar.csv", "w") as outputTable:
        outputTable.write("M,I,D,S,H,N,P,X,=\n")

        for n, line in enumerate(tqdm(payload, desc="Analyzing CIGAR", total=len(payload))):
            dico = readCigar(line["cigar"])
            percentMut = percentMutation(dico) + "\n"
            outputTable.write(percentMut)


def globalPercentCigar(path):
    """
    Global representation of cigar distribution.

    Args:
        path (str): The path to the directory containing the 'outpuTable_cigar.csv' file.

    Returns:
        dict: A dictionary where the keys are the mutation types and the values are the formatted percentages of each mutation type.
    """
    df = pd.read_csv(f"{path}/outpuTable_cigar.csv")  # Read the CSV file into a DataFrame
    nbReads = len(df)  # Get the number of reads
    metrics = {col: df[col].sum() for col in df.columns}  # Calculate the sum of each column

    def format_metric(value):
        """
        Format the metric value as a percentage string.

        Args:
            value (int): The sum of a specific mutation type.

        Returns:
            str: The formatted percentage string.
        """
        mid = str(round(value / nbReads, 2))
        if value / nbReads == 0:
            mid = "0"
        elif value / nbReads < 0.01:
            mid = "$<$0.01"
        return mid + "\\%"

    final = {typ: format_metric(value) for typ, value in metrics.items()}  # Create the final dictionary with formatted metrics

    # Delete outPutTable_cigar.csv
    os.remove(f"{path}/outpuTable_cigar.csv")

    return final


def main():
    pass


if __name__ == "__main__":
    main()
