#!/usr/bin/env python3
"""
Dump tokenized MBASIC-80 program (Python translation of detokenizer.go)
"""
import argparse
import sys
from typing import Dict, List


def two_neg_power32(exponent: int) -> float:
    # Match Go behavior exactly (iterative, only positive handled)
    value = 2.0
    f = 1.0
    if exponent == 0:
        return f
    while exponent > 0:
        f = value * f
        exponent -= 1
    f = 1.0 / f
    return f


def two_neg_power64(exponent: int) -> float:
    value = 2.0
    f = 1.0
    if exponent == 0:
        return f
    while exponent > 0:
        f = value * f
        exponent -= 1
    f = 1.0 / f
    return f


def needs_space_before(token: str, prev_token: str) -> bool:
    """Determine if we need a space before this token"""
    if not prev_token:
        return False

    # Operators and delimiters generally don't need spaces before them
    operators = {'+', '-', '*', '/', '^', '\\', '=', '<', '>', '(', ')', ',', ';', ':', '$', '%', '!', '#'}

    # ARK follows REM without space (REM + ARK = REMARK)
    if token == "ARK" and prev_token == "REM":
        return False

    # If current token is an operator, usually no space needed
    if token in operators:
        return False

    # If current token starts with operator-like char (like $ or %), no space
    if token and token[0] in operators:
        return False

    # If previous token was an operator (except closing paren), no space before keyword/identifier
    if prev_token in operators and prev_token not in {')', '}'}:
        return False

    # If previous ends with operator (like TAB( or SPC(), no space
    if prev_token and prev_token[-1] == '(':
        return False

    # Keywords and identifiers need spaces between them
    return True


def dump_ascii(line_number: int, data: bytes, table: Dict[int, str], table2: Dict[int, str], prefix: int) -> int:
    # Print line number like Go
    print(f"{line_number} ", end="")

    count = 0
    done = False
    prev_token = ""  # Track previous token for smart spacing

    while not done:
        if count>=len(data):
            break
        b = data[count]
        b16 = int(b)

        handled = False

        # 0x0F - 1-byte integer as decimal
        if b == 0x0F:
            i = int(data[count + 1])
            print(f"{i}", end="")
            count += 1
            handled = True

        # 0x0E - 2-byte integer as decimal
        if b == 0x0E:
            i = int(data[count + 2]) * 256 + int(data[count + 1])
            print(f"{i}", end="")
            count += 2
            handled = True

        # 0x0C - 2-byte integer as hexadecimal
        if b == 0x0C:
            i = int(data[count + 2]) * 256 + int(data[count + 1])
            print(f"&H{i:02X}", end="")
            count += 2
            handled = True

        # 0x0B - 2-byte integer as octal
        if b == 0x0B:
            i = int(data[count + 2]) * 256 + int(data[count + 1])
            print(f"&O{i:03o}", end="")
            count += 2
            handled = True

        # 0x1C - 2-byte integer as decimal (duplicate of 0x0E in Go code)
        if b == 0x1C:
            i = int(data[count + 2]) * 256 + int(data[count + 1])
            print(f"{i}", end="")
            count += 2
            handled = True

        # 0x1D - 4-byte float as decimal
        if b == 0x1D:
            bt1 = int(data[count + 1])
            bt2 = int(data[count + 2])
            bt3 = int(data[count + 3])
            bt4 = int(data[count + 4])

            f1a = float(bt1) * two_neg_power32(23)
            f1b = float(bt2) * two_neg_power32(15)
            f1c = float(bt3) * two_neg_power32(7)
            f1 = f1a + f1b + f1c + 1.0
            f2 = two_neg_power32(129 - bt4)
            f = f1 * f2

            # Match Go's %g formatting roughly via repr with strip
            out = f"{f:g}"
            print(out, end="")

            count += 4
            handled = True

        # 0x1F - 8-byte float as decimal
        if b == 0x1F:
            bt1 = int(data[count + 1])
            bt2 = int(data[count + 2])
            bt3 = int(data[count + 3])
            bt4 = int(data[count + 4])
            bt5 = int(data[count + 5])
            bt6 = int(data[count + 6])
            bt7 = int(data[count + 7])
            bt8 = int(data[count + 8])

            f1a = float(bt1) * two_neg_power64(55)
            f1b = float(bt2) * two_neg_power64(47)
            f1c = float(bt3) * two_neg_power64(39)
            f1d = float(bt4) * two_neg_power64(31)
            f1e = float(bt5) * two_neg_power64(23)
            f1f = float(bt6) * two_neg_power64(15)
            f1g = float(bt7) * two_neg_power64(7)
            f1 = f1a + f1b + f1c + f1d + f1e + f1f + f1g + 1.0
            f2 = two_neg_power64(129 - bt8)
            f = f1 * f2

            print(f"{f:g}", end="")

            count += 8
            handled = True

        # 0xFF - 2-byte token
        if b == 0xFF:
            code = int(data[count + 1])
            s = table2.get(code)
            if s is not None:
                # Smart spacing
                if needs_space_before(s, prev_token):
                    print(" ", end="")
                print(f"{s}", end="")
                prev_token = s
            else:
                print(f"[0xFF][{code:02X}]", end="")
                prev_token = ""
            count += 1
            handled = True

        # 0x80 to 0xFE - 1-byte token
        if 0x80 <= b16 <= 0xFE and not handled:
            s = table.get(b16)
            if s is not None:
                # Smart spacing
                if needs_space_before(s, prev_token):
                    print(" ", end="")
                print(f"{s}", end="")
                prev_token = s
            else:
                print(f"[{b16:02X}]", end="")
                prev_token = ""
            handled = True

        # 0x20 to 0x7F - plain character
        if 0x20 <= b <= 0x7F and not handled:
            ch = chr(b16)
            print(ch, end="")
            prev_token = ch  # Track character for spacing
            handled = True

        # byte of zero is end of line
        if b16 == 0:
            done = True
            handled = True

        # 0x01 to 0x31 - certain tokens or a 1-byte integer (special cases)
        if b == 0x07 and not handled:  # BEL
            print("\\a", end="")
            handled = True

        if b == 0x08 and not handled:  # BS
            print("\\b", end="")
            handled = True

        if b == 0x09 and not handled:  # TAB
#            print("\\t", end="")
            print(" ", end="")
            handled = True

        if b == 0x0A and not handled:  # LF
            print("\n", end="")
            handled = True

        if b == 0x0D and not handled:  # CR
#            print("\\r", end="")
#            print("\\n", end="")
            handled = True

        if not handled:
            if b16 >= 0x11:
                # 1-byte numeric as decimal
                n = b16 - 0x11
                print(f"{n}", end="")
            else:
                # 1-byte ASCII control character
                print(f"0x{b16:02X}", end="")

        count += 1

    return count


def build_tables():
    table: Dict[int, str] = {}

    # need BASE

    table[0x81] = "END"       # 8K
    table[0x82] = "FOR"       # 8K
    table[0x83] = "NEXT"      # 8K
    table[0x84] = "DATA"      # 8K
    table[0x85] = "INPUT"     # 8K
    table[0x86] = "DIM"       # 8K
    table[0x87] = "READ"      # 8K
    table[0x88] = "LET"       # 8K
    table[0x89] = "GOTO"      # 8K
    table[0x8A] = "RUN"       # ? 8K
    table[0x8B] = "IF"        # 8K
    table[0x8C] = "RESTORE"   # 8K
    table[0x8D] = "GOSUB"     # 8K
    table[0x8E] = "RETURN"    # 8K
    table[0x8F] = "REM"       # 8K
    table[0x90] = "STOP"      # 8K
    table[0x91] = "PRINT"     # 8K
    table[0x92] = "CLEAR"     # 8K
    table[0x93] = "LIST"      # ? 8K
    table[0x94] = "NEW"       # ? 8K
    table[0x95] = "ON"        # 8K
    table[0x96] = "NULL"      # 8K
    table[0x97] = "WAIT"      # 8K
    table[0x98] = "DEF"       # 8K
    table[0x99] = "POKE"      # 8K
    table[0x9A] = "CONT"      # 8K
    table[0x9B] = "LPRINT"    # Ext
    table[0x9D] = "OUT"       # 8K
    table[0x9F] = "LLIST"     # ? Ext
    table[0xA0] = "NOTRACE"   # is this a command
    table[0xA1] = "WIDTH"     # Ext
    table[0xA2] = "ELSE"      # Ext
    table[0xA3] = "TRON"      # Ext
    table[0xA4] = "TROFF"     # Ext
    table[0xA5] = "SWAP"      # Ext
    table[0xA6] = "ERASE"     # Ext
    table[0xA7] = "EDIT"      # ? Ext
    table[0xA8] = "ERROR"     # Ext
    table[0xA9] = "RESUME"    # Ext
    table[0xAA] = "DELETE"    # Ext
    table[0xAB] = "AUTO"      # ? Ext
    table[0xAC] = "RENUM"     # ? Ext
    table[0xAD] = "DEFSTR"    # Ext
    table[0xAE] = "DEFINT"    # Ext
    table[0xAF] = "DEFSNG"    # Ext
    table[0xB0] = "DEFDBL"    # Ext
    table[0xB1] = "LINE"      # Ext
    table[0xB2] = "WRITE"     # Disk one is wrong
    table[0xB3] = "COMMON"    # Disk one is wrong
    table[0xB4] = "WHILE"     # Ext
    table[0xB5] = "WEND"      # Ext
    table[0xB6] = "CALL"      # Ext
    table[0xB7] = "WRITE"     # Disk one is wrong
    table[0xB8] = "COMMON"    # Disk one is wrong
    table[0xB9] = "CHAIN"     # Disk
    table[0xBA] = "OPTION"    # 8K
    table[0xBB] = "RANDOMIZE" # Ext
    # table[0xBC] = "CLOSE"     # Disk one is wrong
    table[0xBD] = "SYSTEM"  # is this a command
    table[0xBE] = "MERGE"   # Disk one is wrong
    table[0xBF] = "OPEN"    # Disk
    table[0xC0] = "FIELD"   # Disk
    table[0xC1] = "GET"     # Disk
    table[0xC2] = "PUT"     # Disk
    table[0xC3] = "CLOSE"   # Disk
    table[0xC4] = "LOAD"    # ? Disk
    table[0xC5] = "MERGE"   # Disk one is wrong
    table[0xC6] = "FILES"   # Disk
    table[0xC7] = "NAME"    # Disk
    table[0xC8] = "KILL"    # Disk
    table[0xC9] = "LSET"    # Disk
    table[0xCA] = "RSET"    # Disk
    table[0xCB] = "SAVE"    # ? Disk
    table[0xCC] = "RESET"   # is this a command?
    table[0xCE] = "TO"      # 8K
    table[0xCF] = "THEN"    # 8K
    table[0xD0] = "TAB("    # 8K
    table[0xD1] = "STEP"    # 8K
    table[0xD2] = "USR"     # 8K
    table[0xD3] = "FN"      # 8K
    table[0xD4] = "SPC("    # 8K
    table[0xD5] = "NOT"     # 8K
    table[0xD6] = "ERL"     # Ext
    table[0xD7] = "ERR"     # Ext
    table[0xD8] = "STRING$" # Ext
    table[0xD9] = "USING"   # Ext
    table[0xDA] = "INSTR"   # Ext
    table[0xDB] = "ARK"     # Ext - Combines with REM to make REMARK
    table[0xDC] = "VARPTR"  # Ext
    table[0xDD] = "INKEY$"  # Ext
    table[0xEF] = ">"   # 8K
    table[0xF0] = "="   # 8K
    table[0xF1] = "<"   # 8K
    table[0xF2] = "+"   # 8K
    table[0xF3] = "-"   # 8K
    table[0xF4] = "*"   # 8K
    table[0xF5] = "/"   # 8K
    table[0xF6] = "^"   # 8K
    table[0xF7] = "AND" # 8K
    table[0xF8] = "OR"  # 8K
    table[0xF9] = "XOR" # 8K
    table[0xFA] = "EQV" # 8K
    table[0xFB] = "IMP" # 8K
    table[0xFC] = "\\"  # 8K
    table[0xFD] = "MOD" # 8K

    table2: Dict[int, str] = {}

    # need INPUT$(X[,#F]) // Disk

    table2[0x81] = "LEFT$"  # 8K
    table2[0x82] = "RIGHT$" # 8K
    table2[0x83] = "MID$"   # 8K
    table2[0x84] = "SGN"    # 8K
    table2[0x85] = "INT"    # 8K
    table2[0x86] = "ABS"    # 8K
    table2[0x87] = "SQR"    # 8K
    table2[0x88] = "RND"    # 8K
    table2[0x89] = "SIN"    # 8K
    table2[0x8A] = "LOG"    # 8K
    table2[0x8B] = "EXP"    # 8K
    table2[0x8C] = "COS"    # 8K
    table2[0x8D] = "TAN"    # 8K
    table2[0x8E] = "ATN"    # 8K
    table2[0x8F] = "FRE"    # 8K
    table2[0x90] = "INP"    # 8K
    table2[0x91] = "POS"    # 8K
    table2[0x92] = "LEN"    # 8K
    table2[0x93] = "STR$"   # 8K
    table2[0x94] = "VAL"    # 8K
    table2[0x95] = "ASC"    # 8K
    table2[0x96] = "CHR$"   # 8K
    table2[0x97] = "PEEK"   # 8K
    table2[0x98] = "SPACE$" # Ext
    table2[0x99] = "OCT$"   # Ext
    table2[0x9A] = "HEX$"   # Ext
    table2[0x9B] = "LPOS"   # Ext
    table2[0x9C] = "CINT"   # Ext
    table2[0x9D] = "CSNG"   # Ext
    table2[0x9E] = "CDBL"   # Ext
    table2[0x9F] = "FIX"    # Ext
    # table2[0xAA] = ""
    table2[0xAB] = "CVI" # Disk
    table2[0xAC] = "CVS" # Disk
    table2[0xAD] = "CVD" # Disk
    table2[0xAE] = "EOF" # Disk
    # table2[0xAF] = ""
    table2[0xB0] = "LOC"  # Disk
    table2[0xB1] = "LOF"  # is this a function?
    table2[0xB2] = "MKI$" # Disk
    table2[0xB3] = "MKS$" # Disk
    table2[0xB4] = "MKD$" # Disk

    return table, table2


def main(argv: List[str]) -> int:
    parser = argparse.ArgumentParser(description="Dump tokenized MBASIC-80 program")
    parser.add_argument("-hex", action="store_true", dest="include_bytes", help="Include hex bytes")
    parser.add_argument("file", nargs="?", help="Tokenized MBASIC file to read")
    args = parser.parse_args(argv)

    if not args.file:
        print("No file specified")
        return 1

    with open(args.file, "rb") as f:
        data = f.read()

    table, table2 = build_tables()

    # Go code skips the first byte
    contents = data[1:]

    done = False
    while not done:
        if len(contents) < 5:
            break
        # 2 bytes for line number (little endian) at offsets 2 and 3
        line_number = int(contents[3]) * 256 + int(contents[2])

        if line_number == 0:
            done = True
        else:
            payload = contents[4:]

            # print the untokenized line
            count = dump_ascii(line_number, payload, table, table2, 0xFF)
            print()

            if args.include_bytes:
                # dump bytes (including NULL) as hex and ascii
                line_count = count + 4
                line = contents[:line_count]
                print(" ".join(f"{b:02X}" for b in line))
                print()

            contents = payload[count:]
            if len(contents) < 5:
                done = True

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
