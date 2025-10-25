# REM

## Syntax

```basic
REM <remark>
```

## Purpose

To allow explanatory remarks to be inserted in a program.

## Remarks

REM statements are not executed but are output exactly as entered when the program is listed. REM statements may be branched into (from a GOTO or GOSUB statement), and execution will continue with the first executable statement after the REM statement. In the Extended and Disk versions, remarks may be added to the end of a line by preceding the remark with a single quotation mark instead of : REM.

## Example

```basic
..
             120 REM CALCULATE AVERAGE VELOCITY
             130 FOR I=1 TO 20
             140 SUM=SUM + V(I)
             or, with Extended and Disk versions:
             120 FOR I=l TO 20     ~CALCULATE   AVERAGE VELOCITY
             130 SUM=SUM+V(I)
             140 NEXT I
BASIC-80 COMMANDS AND STATEMENTS                          Page 2-73
```

## See Also

*Related statements will be linked here*
