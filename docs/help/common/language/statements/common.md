# COMMON

## Syntax

```basic
COMMON <list of variables>
```

**Versions:** Disk

## Purpose

To pass variables to a CHAINed program.

## Remarks

The COMMON statement is used in conjunction with the CHAIN statement.     COMMON statements may appear anywhere in a program, though it is recommended that they appear at the beginning. The same variable cannot appear in more than one COMMON statement. Array variables are specified by appending "()" to the variable name.   If all variables are to be passed, use CHAIN with the ALL option and omit the COMMON statement.

## Example

```basic
100 COMMON A,B,C,D(),G$
               110 CHAIN "PROG3",10
                    •
BASIC-80 COMMANDS AND STATEMENTS                    Page 2-10
```

## See Also

*Related statements will be linked here*
