import re
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


def toFasta(line):
    header = line['qname']
    pos = line['pos']
    sequence = line['seq']
    fasta_format = f">{header} pos:{pos}\n{sequence}\n" if pos != "0" else f">{header}\n{sequence}\n"
    return fasta_format


#### Analyze the partially mapped or unmapped reads ####
def partiallyMappedOrUnmapped(payload, path):
    partially_mapped_count = 0
    unmapped_count = 0

    with (open(f"{path}/only_partially_mapped.fasta", "w") as partillay_mapped_fasta,
          open(f"{path}/only_unmapped.fasta", "w") as outputTable):
        for line in tqdm(payload, desc="Analyzing partially mapped and unmapped reads", total=len(payload)):
            flag = toBinary(line["flag"], 16)  # We compute the same

            if int(flag[-2]) == 1:
                if line['cigar'] != "100M":
                    partially_mapped_count += 1
                    partillay_mapped_fasta.write(toFasta(line))
            if int(flag[-3]) == 1:
                unmapped_count += 1
                outputTable.write(toFasta(line))

        return partially_mapped_count, unmapped_count


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
            if dico != {}:
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
