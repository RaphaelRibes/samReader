import re
from analyse import toBinary
import sys


def display_error_context(valist:list, problematic_param:str) -> str:
    # Define the parameter list
    param_list = ["qname", "flag", "rname", "pos", "mapq", "cigar", "rnext", "pnext", "tlen", "seq", "qual"]

    # Check if the problematic parameter is in the list
    if problematic_param not in param_list:
        return f"Parameter {problematic_param} not found in the list"

    # Find the index of the problematic parameter
    index = param_list.index(problematic_param)

    # Define the surrounding parameters (one before and one after)
    left_param = str(valist[index - 1]) if index > 0 else ""
    right_param = str(valist[index + 1]) if index < len(param_list) - 1 else ""
    problematic_value = str(valist[index])

    # Create the first line with parameter names
    first_line = f"{left_param}   {problematic_value}   {right_param}".strip()  # Remove leading and trailing spaces
    first_line = f"{'...   ' if index > 1 else ''}" + first_line
    first_line = f"{first_line}{'   ...' if index < len(param_list)-2 else ''}"

    # Create the second line with carets under the problematic parameter
    caret_position = len(left_param) + (3 if left_param!="" else 0) + (6 if index > 1 else 0)
    caret_line = " " * caret_position + "^" * len(problematic_value)

    # Combine both lines and return
    return f"{first_line}\n{caret_line}"

def payload_tolist(payload:dict) -> list:
    return [val for val in payload.values()]

def line_to_payload(line:list, n:int) -> dict:
    payload = {
        "qname": line[0],
        "flag": line[1],
        "rname": line[2],
        "pos": line[3],
        "mapq": line[4],
        "cigar": line[5],
        "rnext": line[6],
        "pnext": line[7],
        "tlen": line[8],
        "seq": line[9],
        "qual": line[10],
        "line": n
    }
    return payload


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

def check_line(payload:dict, trusted=False) -> None:
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

    :param payload:
    :param trusted:
    :return:
    """
    if trusted:
        return
    payload_values = payload_tolist(payload)

    # col 1 : QNAME -> str() following regex [!-?A-~]{1,254}
    if not qname(payload["qname"]):
        print(f'Error with QNAME line {payload['line']} :'
              f'\n{display_error_context(payload_values, "qname")}\n'
              f'Expected : {payload["qname"]} to be a string following this regex [!-?A-~]{"{1,254}"}')
        sys.exit(2)

    # col 2 : FLAG -> int() following regex [01]{12,16}
    if not flag(payload["flag"]):
        print(f'Error with FLAG line {payload['line']} :'
              f'\n{display_error_context(payload_values, "flag")}\n'
              f'Expected : {payload["flag"]} to be a integer ranging from 0 to 65535')
        sys.exit(2)

    # col 3 : RNAME -> str() following this regex \*|[0-9A-Za-z!#$%&+.\/:;?@^_|~\-^\*=][0-9A-Za-z!#$%&*+.\/:;=?@^_|~-]*
    if not rname(payload["rname"]):
        print(f'Error with RNAME line {payload['line']} :'
              f'\n{display_error_context(payload_values, "rname")}\n'
              f'Expected : {payload["rname"]} to be a string following this regex [0-9A-Za-z!#$%&+./:;?@^_|~-^*=][0-9A-Za-z!#$%&*+./:;=?@^_|~-]*')
        sys.exit(2)

    # col 4 : POS -> int() following this regex [0, 2^{31} - 1] (0 to 2147483647)
    if not pos(payload["pos"]):
        print(f'Error with POS line {payload['line']} :'
              f'\n{display_error_context(payload_values, "pos")}\n'
              f'Expected : {payload["pos"]} to be an integer ranging from 0 to 2147483647 (2^31 - 1)')
        sys.exit(2)

    # col 5 : MAPQ -> int() following this regex [0, 2^{8} - 1] (0 to 255)
    if not mapq(payload["mapq"]):
        print(f'Error with MAPQ line {payload['line']} :'
              f'\n{display_error_context(payload_values, "mapq")}\n'
              f'Expected : {payload["mapq"]} to be an integer ranging from 0 to 255 (2^8 - 1)')
        sys.exit(2)

    # col 6 : CIGAR -> str() following this regex [0-9]+[MIDNSHPX=]
    if not cigar(payload["cigar"]):
        print(f'Error with CIGAR line {payload['line']} :'
              f'\n{display_error_context(payload_values, "cigar")}\n'
              f'Expected : {payload["cigar"]} to be a string following this regex \\*|([0-9]+[MIDNSHPX=])+')
        sys.exit(2)

    # col 7 : RNEXT -> str() following this regex \*|[0-9A-Za-z!#$%&+.\/:;?@^_|~\-^\*=][0-9A-Za-z!#$%&*+.\/:;=?@^_|~-]*
    if not rnext(payload["rnext"]):
        print(f'Error with RNEXT line {payload['line']} :'
              f'\n{display_error_context(payload_values, "rnext")}\n'
              f'Expected : {payload["rnext"]} to be a string following this regex \\*|[0-9A-Za-z!#$%&+./:;?@^_|~-^*=][0-9A-Za-z!#$%&*+./:;=?@^_|~-]*')
        sys.exit(2)

    # col 8 : PNEXT -> int() following this regex [0, 2^{31} - 1] (0 to 2147483647)
    if not pnext(payload["pnext"]):
        print(f'Error with PNEXT line {payload['line']} :'
              f'\n{display_error_context(payload_values, "pnext")}\n'
              f'Expected : {payload["pnext"]} to be an integer ranging from 0 to 2147483647 (2^31 - 1)')
        sys.exit(2)

    # col 9 : TLEN -> int() following this regex [-][0, 2^{31} - 1] (-2147483647 to 2147483647)
    if not tlen(payload["tlen"]):
        print(f'Error with TLEN line {payload['line']} :'
              f'\n{display_error_context(payload_values, "tlen")}\n'
              f'Expected : {payload["tlen"]} to be an integer ranging from -2147483647 to 2147483647 (-2^31 + 1 to 2^31 - 1)')
        sys.exit(2)

    # col 10 : SEQ -> str() following this regex \*|[A-Za-z=.]+
    if not seq(payload["seq"]):
        print(f'Error with SEQ line {payload['line']} :'
              f'\n{display_error_context(payload_values, "seq")}\n'
              f'Expected : {payload["seq"]} to be a string following this regex \\*|[A-Za-z=.]+')
        sys.exit(2)

    # col 11 : QUAL -> str() following this regex [!-~]+
    if not qual(payload["qual"]):
        print(f'Error with QUAL line {payload['line']} :'
              f'\n{display_error_context(payload_values, "qual")}\n'
              f'Expected : {payload["qual"]} to be a string following this regex [!-~]+')
        sys.exit(2)


def main():
    payload_values = ["1", "22222222222", "3", 4]
    print(f'Error line {1} :'
          f'\n{display_error_context(payload_values, "flag")}\n'
         f'Expected : {1} to be a string following this regex [!-?A-~]{"{1,254}"}')
if __name__ == "__main__":
    main()