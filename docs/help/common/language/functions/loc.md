# LOC

## Syntax

```basic
LOC«file number»
```

**Versions:** Disk

## Description

With random disk files, LOC returns the next record number to be used if a GET or PUT (without a record number)   is executed.  With sequential files, LOC returns the number of sectors (128 byte blocks) read from or written to the file since it was OPENed.

## Example

```basic
200 IF LOC(l) >50 THEN STOP
BASIC-80 FUNCTIONS                                      Page 3-14
```

## See Also

*Related functions will be linked here*
