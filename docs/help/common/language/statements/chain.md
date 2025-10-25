# CHAIN

## Syntax

```basic
CHAIN [MERGE] <filename>[,[<line number exp>]
[,ALL] [,DELETE<range>]]
```

**Versions:** Disk

## Purpose

To call a program and pass variables to it            from the current program.

## Remarks

<filename> is the name of the       program    that     is called. Example: CHAIN"PROGI" <line number exp> is a line number or an expression that evaluates to a line number in the called program. It is the starting point for execution of the called program. If it is omitted, execution begins at the first line. Example: CHAIN"PROGI",IOOO <line number exp> is not       affected   by   a   RENUM command. With the ALL option, every variable in the current program is passed to the called programo If the ALL option is omitted, the current program must contain a COMMON statement to list the variables that are passed. See Section 2.7. Example: CHAIN"PROGl",IOOO,ALL If the MERGE option is included, it allows a subroutine to be brought into the BASIC program as an overlay. That is, a MERGE operation is performed with the current program and the called program. The called program must be an ASCII file if it is to be MERGEd. Example: CHAIN MERGE"OVRLAY",lOOO After an overlay is brought in, it is usually desirable to delet~ it so that a new overlay may be brought in.   To do this, use the DELETE option. Example: CHAIN MERGE"OVRLAY2",1000,DELETE 1000-5000 The line numbers in <range> are affected by            the RENUM command. BASIC-SO COMMANDS AND STATEMENTS                    Page 2-5 NOTE:       The Microsoft BASIC compiler does not support the ALL, MERGE, and DELETE options to CHAIN.  If you wish to maintain compatibility with the BASIC compiler, it is recommended that COMMON be used to pass variables and that overlays not be used. NOTE:       The CHAIN statement with MERGE option leaves the files open and preserves the current OPTION BASE setting. NOTE:       If the MERGE option is omitted, CHAIN does not preserve    variable   types   or   user-defined functions for use by the chained program.   That is, any DEFINT, DEFSNG, DEFDBL, DEFSTR, or DEFFN statements containing shared variables must be restated in the chained program. BASIC-SO COMMANDS AND STATEMENTS                            Page 2-6

## See Also

*Related statements will be linked here*
