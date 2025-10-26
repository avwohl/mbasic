---
category: NEEDS_CATEGORIZATION
description: To print data at the line printer
keywords:
- command
- data
- field
- file
- for
- function
- if
- line
- lprint
- print
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

Same as PRINT and PRINT USING, except output goes to the line printer. See Section 2.49 and Section 2.50. LPRINT assumes a l32-character-wide printer. NOTE:         LPRINT and LLIST are not         included    in   all implementations of BASIC-80. BASIC-80 COMMANDS AND STATEMENTS                      Page 2-48 2 • 37   LSET AND RSET If <string expression> requires fewer bytes than were   FIELDed   to    <string    variable>, LSET left-justifies the string in the field, and RSET right-justifies the string.    (Spaces are used to pad the extra positions.) If the string is too long for the field, characters are dropped from the right. Numeric values must be converted to strings before they are LSET or RSET. See the MKI$, MKS$, MKD$ functions, Section 3.25.

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
BASIC-80 COMMANDS AND STATEMENTS                         Page 2-49
```

## See Also

*Related statements will be linked here*