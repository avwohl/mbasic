# INKEY$

## Syntax

```basic
INKEY$
```

## Description

Returns either a one-character string cont~ining a character read from the terminal or a null string if no character is pending at          the terminal.    No characters will be echoed and all characters are passed through tto the program except    for Contro1-C, which terminates the program.   (With the BASIC Compiler, Contro1-C is also passed through to the program.)

## Example

```basic
1000 ~TlMED INPUT SUBROUTINE
                1010 RESPONSE$=""
                1020 FOR I%=l TO TIMELIMIT%
                1030 A$=INKEY$ : IF LEN(A$)=O THEN 1060
                1040 IF ASC(A$)=13 THEN TIMEOUT%=O : RETURN
                1050 RESPONSE$=RESPONSE$+A$
                1060 NEXT I%
                1070 TIMEOUT%=l : RETURN
```

## See Also

*Related functions will be linked here*
