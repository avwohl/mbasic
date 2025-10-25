# RND

## Syntax

```basic
RND [ (X) ]
```

**Versions:** SK, Extended, Disk

## Description

Returns a random number between 0 and 1.    The same sequence of random numbers is generated each time the program is RUN unless the random number generator is reseeded     (see RANDOMIZE, Section 2.53). However, X<O always restarts the same sequence for any given X. X>O or X omitted generates the next random number in the sequence. x=o repeats the last number generated.

## Example

```basic
10 FOR I=l TO 5
             20 PRINT INT(RND*100);
             30 NEXT
             RUN
              24 30 31 51 5
             Ok
```

## See Also

*Related functions will be linked here*
