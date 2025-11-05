---
category: file-io
description: To save the program or an array currently in memory on cassette tape
keywords: ['array', 'command', 'csave', 'dec', 'dim', 'execute', 'file', 'for', 'if', 'included']
title: CSAVE - THIS COMMAND IS NOT INCLUDED IN THE DEC VT180 VERSION
type: statement
---

# CSAVE - THIS COMMAND IS NOT INCLUDED IN THE DEC VT180 VERSION

**Versions:** 8K (cassette), Extended (cassette)

## Purpose

To save the program or an array currently in memory on cassette tape.

## Remarks

Each program or array saved         on    tape    is identified by a filename.        When the command CSAVE <string expression> is executed, BASIC-80 saves the program currently in memory on tape and uses the first       character     in   <string expression>    as    the     filename.      <string expression> may be more than one character, but only   the first character is used for the filename. When the command CSAVE* <array variable name> is executed, BASIC-80saves the specified array on tape. The array must be a numeric array.      The elements of a multidimensional array are saved with the leftmost subscript changing fastest. CSAVE may be used as a program statement or as a direct mode command. Before a CSAVE or CSAVE* is executed, make sure the cassette recorder is properly connected and in the Record mode. See also CLOAD, Section 2.5. NOTE:           CSAVE and CLOAD are not included               in   all implementations of BASIC-80.

## Example

```basic
CSAVE "TIMER"
                Saves the program currently in memory on
                cassette under filename "T".
```

## See Also
- [CLOAD THIS COMMAND IS NOT INCLUDED IN THE DEC VT180 VERSION](cload.md) - To load a program or an array from cassette tape into memory
- [CVI, CVS, CVD](../functions/cvi-cvs-cvd.md) - Convert string values to numeric values
- [DEFINT/SNG/DBL/STR](defint-sng-dbl-str.md) - To declare variable types as integer, single precision, double precision, or string
- [ERR AND ERL VARIABLES](err-erl-variables.md) - Error code and error line number variables used in error handling
- [INPUT#](input_hash.md) - To read data items from a sequential disk file and assign them to program variables
- [LINE INPUT](line-input.md) - To input an entire line (up to 254 characters) to   a string variable, without the use of delimiters
- [LPRINT AND LPRINT USING](lprint-lprint-using.md) - To print data at the line printer
- [MKI$, MKS$, MKD$](../functions/mki_dollar-mks_dollar-mkd_dollar.md) - Convert numeric values to string values
- [SPACE$](../functions/space_dollar.md) - Returns a string of spaces of length X
- [TAB](../functions/tab.md) - Spaces to position I on the terminal
