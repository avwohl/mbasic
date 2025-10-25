# CALL

## Syntax

```basic
CALL <variable name>[«argument list»]
```

## Purpose

To call an assembly language subroutine.

## Remarks

The CALL statement is one way to transfer program flow to an assembly language subroutine. (See also the OSR function, Section 3.40) <variable name> contains an address that is the starting point in memory of the subroutine. <variable name> may not be an array variable name.   <argument list> contains the arguments that are passed to the       assembly   language subroutine.   <argument list> may not contain literals. The CALL statement generates the same calling sequence used by Microsoft~s FORTRAN, COBOL and BASIC compilers.

## Example

```basic
110 MYROOT=&HDOOO
             120 CALL MYROOT(I,J,K)
BASIC-SO COMMANDS AND STATEMENTS                             Page 2-4
```

## See Also

*Related statements will be linked here*
