---
category: file-io
description: To load a program or an array from cassette tape into memory
keywords: ['array', 'cload', 'command', 'data', 'dec', 'dim', 'execute', 'file', 'for', 'if']
title: CLOAD THIS COMMAND IS NOT INCLUDED IN THE DEC VT180 VERSION
type: statement
---

# CLOAD     THIS COMMAND IS NOT INCLUDED IN THE DEC VT180 VERSION

## Purpose

To load a program or an array from cassette tape into memory.

## Remarks

CLOAD executes a NEW command before it loads the program from cassette tape. <filename> is, the string expression or the first character of the string expression that was specified when the program was CSAVEd. CLOAD? verifies tapes by comparing the program currently in memory with the file on tape that has the same filename. If they are the same, BASIC prints Ok. If not, BASIC prints NO GOOD. CLOAD* loads a numeric array that has been saved on tape.    The data on tape is loaded into the array called <array name> specified when the array was CSAVE*ed. CLOAD and CLOAD? are always entered at command level as direct· mode commands. CLOAD* may be entered at command level or used as a program statement.    Make   sure the array has been DIMensioned before it is loaded.   BASIC always returns to COmmand level after a CLOAD, CLOAD? or CLOAD* is executed.      Before a CLOAD is executed, make sure the cassette recorder is properly connected and in the Play mode, and the tape is possitioned correctly. See also CSAVE, Section 2.9. NOTE:           CLOAD and CSAVE are not           included      in    all implementations of BASIC.

## Example

```basic
CLOAD "MAX2"
                Loads file "M" into memory.
```

## See Also
- [CSAVE THIS COMMAND IS NOT INCLUDED IN THE DEC VT180 VERSION](csave.md) - To save the program or an       array   currently     in memory on cassette tape
- [CVI, CVS, CVD](../functions/cvi-cvs-cvd.md) - Convert string values to numeric values
- [DEFINT/SNG/DBL/STR](defint-sng-dbl-str.md) - To declare variable types as integer,        single precision, double precision, or string
- [ERR AND ERL VARIABLES](err-erl-variables.md) - Error code and error line number variables used in error handling
- [INPUT#](input_hash.md) - To read data items from a sequential disk    file and assign them to program variables
- [LINE INPUT](line-input.md) - To input an entire line (up to 254 characters) to   a string variable, without the use of delimiters
- [LPRINT AND LPRINT USING](lprint-lprint-using.md) - To print data at the line printer
- [MKI$, MKS$, MKD$](../functions/mki_dollar-mks_dollar-mkd_dollar.md) - Convert numeric values to string values
- [SPACE$](../functions/space_dollar.md) - Returns a string of spaces of length X
- [TAB](../functions/tab.md) - Spaces to position I on the terminal
