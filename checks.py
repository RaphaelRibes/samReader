import re
from analyse import toBinary
import sys
import numpy as np


def display_error_context(valist:list, problematic_param:str) -> str:
    """
    Display the context of the error in the problematic parameter
    :param valist: List of values
    :param problematic_param: The problematic parameter
    :return: The context of the error
    """
    # Define the parameter list
    param_list = ["qname", "flag", "rname", "pos", "mapq", "cigar", "rnext", "pnext", "tlen", "seq", "qual"]

    # Check if the problematic parameter is in the list
    if problematic_param not in param_list:
        return f"Parameter {problematic_param} not found in the list"

    # Find the index of the problematic parameter
    index = param_list.index(problematic_param)

    # Define the surrounding parameters (one before and one after)
    left_param = str(valist[index - 1]) if index > 0 else ""  # If index is 0, there is no left parameter
    right_param = str(valist[index + 1]) if index < len(param_list) - 1 else ""  # If index is the last, there is no right parameter
    problematic_value = str(valist[index])

    # Create the first line with parameter names
    first_line = f"{left_param}   {problematic_value}   {right_param}".strip()  # Remove leading and trailing spaces
    first_line = f"{'...   ' if index > 1 else ''}" + first_line  # Add ellipsis if the left parameter is not the first one
    first_line = f"{first_line}{'   ...' if index < len(param_list)-2 else ''}"  # Add ellipsis if the right parameter is not the last one

    # Create the second line with carets under the problematic parameter
    caret_position = len(left_param) + (3 if left_param!="" else 0) + (6 if index > 1 else 0)  # Calculate the position of the caret
    caret_line = " " * caret_position + "^" * len(problematic_value)  # Create the line with the caret

    # Combine both lines and return
    return f"{first_line}\n{caret_line}"

### Check functions ###
# All the check functions return a boolean value
# Based on SAMv1 specifications

def qname(tested: str) -> bool:
    return re.match(r"[!-?A-~]{1,254}", tested) is not None

def flag(tested: str) -> bool:
    if not tested.replace('-', '').isdigit():
        return False
    return re.match(r"[01]{16}", toBinary(tested, 16)) is not None

def rname(tested: str) -> bool:
    return re.match(r"\*|[0-9A-Za-z!#$%&+.\/:;?@^_|~\-^\*=][0-9A-Za-z!#$%&*+.\/:;=?@^_|~-]*", tested) is not None

def pos(tested: str) -> bool:
    if not tested.replace('-', '').isdigit():
        return False
    return re.match(r"[01]{31}", toBinary(tested, 31)) is not None

def mapq(tested: str) -> bool:
    if not tested.replace('-', '').isdigit():
        return False
    return re.match(r"[01]{8}", toBinary(tested, 8)) is not None

def cigar(tested: str) -> bool:
    return re.match(r"\*|([0-9]+[MIDNSHPX=])+", tested) is not None

def rnext(tested: str) -> bool:
    return re.match(r"\*|=|[0-9A-Za-z!#$%&+.\/:;?@^_|~\-^\*=][0-9A-Za-z!#$%&*+.\/:;=?@^_|~-]*", tested) is not None

def pnext(tested: str) -> bool:
    if not tested.isdigit():
        return False
    return re.match(r"[01]{31}", toBinary(tested, 31)) is not None

def tlen(tested: str) -> bool:
    if not tested.replace('-', '').isdigit():
        return False
    return re.match(r"-?[01]{31}", toBinary(tested, 31)) is not None

def seq(tested: str) -> bool:
    return re.match(r"\*|[A-Za-z=.]+", tested) is not None

def qual(tested: str) -> bool:
    return re.match(r"[!-~]+", tested) is not None

def check_line(line:list, trusted=False) -> None:
    """
    Check all the fields of the payload
    The payload is a dictionary with the following keys
    - qname: str
    - flag: int
    - rname: str
    - pos: int
    - mapq: int
    - cigar: str
    - rnext: str
    - pnext: int
    - tlen: int
    - seq: str
    - qual: str
    - line: int

    :param line: The payload to check
    :param trusted: If the payload is trusted or not
    :return:
    """
    if trusted: return
    
    # col 1 : QNAME -> str() following regex [!-?A-~]{1,254}
    if not qname(line[0]):
        print(f'Error with QNAME line {line[-1]} :'
              f'\n{display_error_context(line, "qname")}\n'
              f'Expected : {line[0]} to be a string following this regex [!-?A-~]{"{1,254}"}')
        sys.exit(2)

    # col 2 : FLAG -> int() following regex [01]{12,16}
    if not flag(line[1]):
        print(f'Error with FLAG line {line[-1]} :'
              f'\n{display_error_context(line, "flag")}\n'
              f'Expected : {line[1]} to be a integer ranging from 0 to 65535')
        sys.exit(2)

    # col 3 : RNAME -> str() following this regex \*|[0-9A-Za-z!#$%&+.\/:;?@^_|~\-^\*=][0-9A-Za-z!#$%&*+.\/:;=?@^_|~-]*
    if not rname(line[2]):
        print(f'Error with RNAME line {line[-1]} :'
              f'\n{display_error_context(line, "rname")}\n'
              f'Expected : {line[2]} to be a string following this regex [0-9A-Za-z!#$%&+./:;?@^_|~-^*=][0-9A-Za-z!#$%&*+./:;=?@^_|~-]*')
        sys.exit(2)

    # col 4 : POS -> int() following this regex [0, 2^{31} - 1] (0 to 2147483647)
    if not pos(line[3]):
        print(f'Error with POS line {line[-1]} :'
              f'\n{display_error_context(line, "pos")}\n'
              f'Expected : {line[3]} to be an integer ranging from 0 to 2147483647 (2^31 - 1)')
        sys.exit(2)

    # col 5 : MAPQ -> int() following this regex [0, 2^{8} - 1] (0 to 255)
    if not mapq(line[4]):
        print(f'Error with MAPQ line {line[-1]} :'
              f'\n{display_error_context(line, "mapq")}\n'
              f'Expected : {line[4]} to be an integer ranging from 0 to 255 (2^8 - 1)')
        sys.exit(2)

    # col 6 : CIGAR -> str() following this regex [0-9]+[MIDNSHPX=]
    if not cigar(line[5]):
        print(f'Error with CIGAR line {line[-1]} :'
              f'\n{display_error_context(line, "cigar")}\n'
              f'Expected : {line[5]} to be a string following this regex \\*|([0-9]+[MIDNSHPX=])+')
        sys.exit(2)

    # col 7 : RNEXT -> str() following this regex \*|[0-9A-Za-z!#$%&+.\/:;?@^_|~\-^\*=][0-9A-Za-z!#$%&*+.\/:;=?@^_|~-]*
    if not rnext(line[6]):
        print(f'Error with RNEXT line {line[-1]} :'
              f'\n{display_error_context(line, "rnext")}\n'
              f'Expected : {line[6]} to be a string following this regex \\*|[0-9A-Za-z!#$%&+./:;?@^_|~-^*=][0-9A-Za-z!#$%&*+./:;=?@^_|~-]*')
        sys.exit(2)

    # col 8 : PNEXT -> int() following this regex [0, 2^{31} - 1] (0 to 2147483647)
    if not pnext(line[7]):
        print(f'Error with PNEXT line {line[-1]} :'
              f'\n{display_error_context(line, "pnext")}\n'
              f'Expected : {line[7]} to be an integer ranging from 0 to 2147483647 (2^31 - 1)')
        sys.exit(2)

    # col 9 : TLEN -> int() following this regex [-][0, 2^{31} - 1] (-2147483647 to 2147483647)
    if not tlen(line[8]):
        print(f'Error with TLEN line {line[-1]} :'
              f'\n{display_error_context(line, "tlen")}\n'
              f'Expected : {line[8]} to be an integer ranging from -2147483647 to 2147483647 (-2^31 + 1 to 2^31 - 1)')
        sys.exit(2)

    # col 10 : SEQ -> str() following this regex \*|[A-Za-z=.]+
    if not seq(line[9]):
        print(f'Error with SEQ line {line[-1]} :'
              f'\n{display_error_context(line, "seq")}\n'
              f'Expected : {line[9]} to be a string following this regex \\*|[A-Za-z=.]+')
        sys.exit(2)

    # col 11 : QUAL -> str() following this regex [!-~]+
    if not qual(line[10]):
        print(f'Error with QUAL line {line[-1]} :'
              f'\n{display_error_context(line, "qual")}\n'
              f'Expected : {line[10]} to be a string following this regex [!-~]+')
        sys.exit(2)


def main():
    pass

if __name__ == "__main__":
    main()
