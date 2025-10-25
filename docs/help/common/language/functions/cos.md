# COS

## Syntax

```basic
COS (X) CSNG (X)
```

**Versions:** SK, Extended, Disk Extended, Disk

## Description

Returns the cosine of X in radians.       The calculation of COS (X) is performed in single precision. Converts X to a single precision number.

## Example

```basic
10 X = 2 *COS ( .4)
             20 PRINT X
             RUN
              1.S42l2
             Ok
3.S   CSNG
10 Ai = 975.3421#
             20 PRINT A#; CSNG{Ai)
             RUN
              975.3421 975.342
             Ok
             See the CINT and CDBL functions for converting
             numbers to the integer and double precision data
             types.
BASIC-80 FUNCTIONS                                        Page 3-6
```

## See Also

*Related functions will be linked here*
