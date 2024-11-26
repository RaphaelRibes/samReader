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
