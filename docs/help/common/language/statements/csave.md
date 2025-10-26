---
category: NEEDS_CATEGORIZATION
description: NEEDS_DESCRIPTION
keywords:
- NEEDS_KEYWORDS
title: CSAVE THIS COMMAND IS NOT INCLUDED IN THE DEC VT180 VERSION
type: statement
---

# CSAVE      THIS COMMAND IS NOT INCLUDED IN THE DEC VT180 VERSION

**Versions:** 8K (cassette), Extended (cassette)

## Purpose

To save the program or an       array   currently     in memory on cassette tape.

## Remarks

Each program or array saved         on    tape    is identified by a filename.        When the command CSAVE <string expression> is executed, BASIC-80 saves the program currently in memory on tape and uses the first       character     in   <string expression>    as    the     filename.      <string expression> may be more than one character, but only   the first character is used for the filename. When the command CSAVE* <array variable name> is executed, BASIC-80saves the specified array on tape. The array must be a numeric array.      The elements of a multidimensional array are saved with the leftmost subscript changing fastest. CSAVE may be used as a program statement or as a direct mode command. Before a CSAVE or CSAVE* is executed, make sure the cassette recorder is properly connected and in the Record mode. See also CLOAD, Section 2.5. NOTE:           CSAVE and CLOAD are not included               in   all implementations of BASIC-80.

## Example

```basic
CSAVE "TIMER"
                Saves the program currently in memory on
                cassette under filename "T".
BASIC-80 COMMANDS AND STATEMENTS                      Page 2-12
```

## See Also

*Related statements will be linked here*