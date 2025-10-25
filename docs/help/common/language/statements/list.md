# LIST

**Versions:** 8K, Extended, Disk Format 2:     LIST [<line number>[-[<line number>]]] Extended, Disk

## Purpose

To list all or part of the program currently            in memory at the terminal.

## Remarks

BASIC-80 always returns to command level after a LIST is executed. Format 1: If <line number> is omitted,     the program is listed beginning at the lowest line number.  (Listing is terminated either by the end of the program or by typing Control-C.) If <line number> is included, the 8K version will list the program beginning at that line: and the Extended and Disk versions will list only the specified line. Format 2:    This    format    allows   the     following options: 1.   If only the first number is specified, that line    and all higher-numbered lines are listed. 2.   If only the second number is specified, all lines from the beginning of the program through that line are listed. 3.   If both numbers are      specified,      the   entire range is listed. BASIC-80 COMMANDS AND STATEMENTS                       Page 2-44

## Example

```basic
Format 1:
            LIST            Lists the program currently
                            in memory.
            LIST 500        In the 8K version, lists
                            all programs lines from
                            500 to the end.
                            In Extended and Disk,
                            lists line 500.
            Format 2:
            LIST 150-       Lists all lines from 150
                            to the end.
            LIST -1000      Lists all lines from the
                            lowest number through 1000.
            LIST 150-1000   Lists lines 150 through
                            1000, inclusive.
BASIC-80 COMMANDS AND STATEMENTS                          Page 2-45
```

## See Also

*Related statements will be linked here*
