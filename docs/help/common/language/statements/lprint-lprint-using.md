---
category: file-io
description: To print data at the line printer
keywords: ['command', 'data', 'field', 'file', 'for', 'function', 'if', 'line', 'lprint', 'print']
syntax: LPRINT [<list of expressions>]
title: LPRINT AND LPRINT USING
type: statement
---

# LPRINT AND LPRINT USING

## Implementation Note

⚠️ **Not Implemented**: This feature requires line printer hardware and is not implemented in this Python-based interpreter.

**Behavior**: Statement is parsed but no output is sent to a printer

**Why**: Line printers are obsolete hardware. Modern systems use different printing paradigms (print spooling, PDF generation, etc.).

**Alternative**: Use [PRINT](print.md) to output to console or [PRINT#](printi-printi-using.md) to output to a file, then print the file using your operating system's print facilities.

**Historical Reference**: The documentation below is preserved from the original MBASIC 5.21 manual for historical reference.

---

## Syntax

```basic
LPRINT [<list of expressions>]
LPRINT USING <string exp>i<list of expressions>
LSET <string variable> = <string expression>
RSET <string variable> = <string expression>
```

**Versions:** Extended, Disk Disk

## Purpose

To print data at the line printer. To move data from memory to a random file buffer (in preparation for a PUT statement) •

## Remarks


## Example

```basic
150 LSET A$=MKS$(AMT)
              160 LSET D$=DESC($~
              See also Appendix B.
NOTE:         LSET or RSET may also be used with a non-fielded
              string variable to left-justify or right-justify
              a string in a given field.    For example, the
              program lines
                      110 A$=SPACE$(20)
                      120 RSET A$=N$
              right-justify the string N$ in a 20-character
              field.   This can be very handy for formatting
              printed output.
```

## See Also
- [CLOAD THIS COMMAND IS NOT INCLUDED IN THE DEC VT180 VERSION](cload.md) - To load a program or an array from cassette tape into memory
- [CSAVE THIS COMMAND IS NOT INCLUDED IN THE DEC VT180 VERSION](csave.md) - To save the program or an       array   currently     in memory on cassette tape
- [CVI, CVS, CVD](../functions/cvi-cvs-cvd.md) - Convert string values to numeric values
- [DEFINT/SNG/DBL/STR](defint-sng-dbl-str.md) - To declare variable types as integer,        single precision, double precision, or string
- [ERR AND ERL VARIABLES](err-erl-variables.md) - Error code and error line number variables used in error handling
- [INPUT#](input_hash.md) - To read data items from a sequential disk    file and assign them to program variables
- [LINE INPUT](line-input.md) - To input an entire line (up to 254 characters) to   a string variable, without the use of delimiters
- [MKI$, MKS$, MKD$](../functions/mki_dollar-mks_dollar-mkd_dollar.md) - Convert numeric values to string values
- [SPACE$](../functions/space_dollar.md) - Returns a string of spaces of length X
- [TAB](../functions/tab.md) - Spaces to position I on the terminal
