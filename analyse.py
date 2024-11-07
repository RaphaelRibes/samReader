import re

#### Convert to binary ####
def toBinary(load, exponent):
    flagB = bin(int(load))  # Transform the integer into a binary.
    flagB = flagB.replace('0b', '')  # Remove '0b' Example: '0b1001101' > '1001101'
    flagB = list(flagB)
    starting_index = 0 if flagB[0] != '-' else 1  # We check if the binary is negative.
    if len(flagB) < exponent:  # Size adjustement to exponent
        add = exponent - len(
            flagB)  # We compute the difference between the maximal size and the length of the binary flag.
        for t in range(add):
            flagB.insert(starting_index, '0')  # We insert 0 to complete until the maximal flag size.
    return "".join(flagB)  # We return the flag in binary format.


#### Analyze the unmapped reads (not paired) ####
def unmapped(sam_line):
    unmapped_count = 0
    with open("only_unmapped.fasta", "a+") as unmapped_fasta, open("summary_unmapped.txt", "w") as summary_file:
        for line in sam_line:
            col_line = line.split("\t")
            flag = toBinary(col_line[1], 16)

            if int(flag[-3]) == 1:
                unmapped_count += 1
                unmapped_fasta.write(toBinary(line, 16))

        summary_file.write("Total unmapped reads: " + str(unmapped_count) + "\n")
        return unmapped_count


#### Analyze the partially mapped reads ####
def partiallyMapped(sam_line):
    partially_mapped_count = 0

    with open("only_partially_mapped.fasta", "a+") as partillay_mapped_fasta, open("summary_partially_mapped.txt",
                                                                                   "w") as summary_file:
        for line in sam_line:
            col_line = line.split("\t")
            flag = toBinary(col_line[1], 16)  # We compute the same

            if int(flag[-2]) == 1:
                if col_line[5] != "100M":
                    partially_mapped_count += 1
                    partillay_mapped_fasta.write(toStringOutput(line))

        summary_file.write("Total partially mapped reads: " + str(partially_mapped_count) + "\n")
        return partially_mapped_count


### Analyse the CIGAR = regular expression that summarise each read alignment ###
def readCigar(cigar):
    ext = re.findall('w', cigar)  # split cigar
    key = []
    value = []
    val = ""

    for i in range(0, len(ext)):  # For each numeric values or alpha numeric
        if (ext[i] == 'M' or ext[i] == 'I' or ext[i] == 'D' or ext[i] == 'S' or ext[i] == 'H' or ext[i] == "N" or ext[
            i] == 'P' or ext[i] == 'X' or ext[i] == '='):
            key.append(ext[i])
            value.append(val)
            val = ""
        else:
            val = "" + val + ext[i]  # Else concatenate in order of arrival

    dico = {}
    n = 0
    for k in key:  # Dictionnary contruction in range size lists
        if k not in dico.keys():  # for each key, insert int value
            dico[k] = int(value[n])  # if key not exist, create and add value
            n += 1
        else:
            dico[k] += int(value[n])  # inf key exist add value
            n += 1
    return dico


### Analyse the CIGAR = regular expression that summarise each read alignment ###
def percentMutation(dico):
    totalValue = 0  # Total number of mutations
    for v in dico:
        totalValue += dico[v]

    mutList = ['M', 'I', 'D', 'S', 'H', 'N', 'P', 'X', '=']
    res = ""
    for mut in mutList:  # Calculated percent of mutation if mut present in the dictionnary, else, percent of mut = 0
        if mut in dico.keys():
            res += (str(round((dico[mut] * 100) / totalValue, 2)) + ";")
        else:
            res += ("0.00" + ";")
    return res


def globalPercentCigar():
    """
      Global representation of cigar distribution.
    """

    with open("outpuTable_cigar.txt", "r") as outpuTable, open("Final_Cigar_table.txt", "w") as FinalCigar:
        nbReads, M, I, D, S, H, N, P, X, Egal = [0 for n in range(10)]

        for line in outpuTable:
            mutValues = line.split(";")
            nbReads += 2
            M += float(mutValues[2]) + float(mutValues[12])
            I += float(mutValues[3]) + float(mutValues[13])
            D += float(mutValues[4]) + float(mutValues[14])
            S += float(mutValues[5]) + float(mutValues[15])
            H += float(mutValues[6]) + float(mutValues[16])
            N += float(mutValues[7]) + float(mutValues[17])
            P += float(mutValues[8]) + float(mutValues[18])
            X += float(mutValues[9]) + float(mutValues[19])
            Egal += float(mutValues[10]) + float(mutValues[20])

        FinalCigar.write("Global cigar mutation observed :" + "\n"
                         + "Alignlent Match : " + str(round(M / nbReads, 2)) + "\n"
                         + "Insertion : " + str(round(I / nbReads, 2)) + "\n"
                         + "Deletion : " + str(round(D / nbReads, 2)) + "\n"
                         + "Skipped region : " + str(round(S / nbReads, 2)) + "\n"
                         + "Soft Clipping : " + str(round(H / nbReads, 2)) + "\n"
                         + "Hard Clipping : " + str(round(N / nbReads, 2)) + "\n"
                         + "Padding : " + str(round(P / nbReads, 2)) + "\n"
                         + "Sequence Match : " + str(round(Egal / nbReads, 2)) + "\n"
                         + "Sequence Mismatch : " + str(round(X / nbReads, 2)) + "\n")

        return FinalCigar

def main():
    print(toBinary("-15", 16))


if __name__ == "__main__":
    main()
