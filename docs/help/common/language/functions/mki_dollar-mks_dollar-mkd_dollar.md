# MKI$, MKS$, MKD$

## Syntax

```basic
MKI$«integer expression» MKS$«single precision expression» MKD$«double precision expression» OCT$ (X) PEEK (I)
```

**Versions:** Disk Extended, Disk SK, Extended, Disk

## Description

Convert numeric values to string values.    Any numeric value that is plac'ed in a random file buffer with an LSET or RSET statement must be converted to a string. MKI$ converts an integer to a 2-byte string.    MKS$ converts a single precision number to a 4-byte string.       MKD$ converts a double precision number to an 8-byte string. Returns a string which represents the octal value of the decimal argument. X is rounded to an integer before OCT$(X) is evaluated. Returns the byte (decimal integer in the range a to 255)   read from memory location I. With the SK version of BASIC-SO, I must be less than 3276S.   To PEEK at a memory location above 3276S, subtract 65536 from the desired address. With Extended and Disk BASIC-SO, I must be in the range a to 65536. PEEK is the complementary function to the POKE statement, Section 2.4S.

## Example

```basic
90 AMT= (K+T)
               100 FIELD #1, 8 AS D$, 20 AS N$
               110 LSET D$ = MKS$(AMT)
               120 LSET N$ = A$
               130 PUT #1
               See also CVI, CVS, CVD, Section 3.9 and Appendix
               B.
BASIC-SO FUNCTIONS                                    Page 3-16
              3.27   OCT$
PRINT OCT$ (24)
               30
              Ok
              See   the   HEX $    function   for   hexadecimal
              conversion.
3.2S   PEEK
A=PEEK (&H5AOO)
BASIC-80 FUNCTIONS                                       Page 3-17
```

## See Also

*Related functions will be linked here*
