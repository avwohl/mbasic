# USR

## Description

Calls the user's assembly language subroutine with the argument X. <digit> is allowed in the Extended and Disk versions only. <digit> is in the range 0 to 9 and corresponds to the digit supplied with the DEF USR statement for that routine.    If   <digit> is omitted, USRO is assumed. See Appendix x.

## Example

```basic
40 B = T*SIN (Y)
             50 C = USR (B/2)
             60 D = USR(B/3)
```

## See Also

*Related functions will be linked here*
