# ~   INPUTi

## Syntax

```basic
LINE INPUTi<file number>,<string variable>
```

**Versions:** Disk

## Purpose

To read an entire line (up to 254 characters), without delimiters, from a sequential disk data file to a string variable.

## Remarks

<file number> is the number under which the file was OPENed.    <string variable> is the variable name to which the 'line will be assigned.   LINE INPUTi reads all characters in the sequential file up to a carriage return.    It then skips over the carriage return/line feed sequence, and the next LINE INPUTi reads all characters up to the   next   carriage    return.    (If   a line feed/carriage return sequence is encountered, it is preserved.) LINE INPUTi is especially useful if each line of a data file has been broken into fields, or if a BASIC-SO program saved in ASCII mode is being read as data by another program.

## Example

```basic
10 OPEN "O",l,"LIST"
           20 LINE INPUT "CUSTOMER INFORMATION? " :C$
           30 PRINT iI, C$
           40 CLOSE 1
           50 OPEN "I",l,"LIST"
           60 LINE INPUT iI, C$
           70 PRINT C$
           SO 'CLOSE 1
           RUN
           CUSTOMER INFORMATION? LINDA JONES    234,4    MEMPHIS
           LINDA JONES     234,4   MEMPHIS
           Ok
BASIC-80 COMMANDS AND STATEMENTS                              Page 2-43
```

## See Also

*Related statements will be linked here*
