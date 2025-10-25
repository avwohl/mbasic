# SGN

## Syntax

```basic
SGN(X)
```

**Versions:** SK, Extended, Disk

## Description

.    If X>O, SGN(X) returns 1. If X=O, SGN(X) returns O. If X<O, SGN(X) returns -1.

## Example

```basic
ON SGN(X)+2 GOTO 100,200,300 branches to 100 if
             X is negative, 200 if X is 0 and 300 if X is
             positive.
BASIC-80 FUNCTIONS                                   Page 3-19
```

## See Also

*Related functions will be linked here*
