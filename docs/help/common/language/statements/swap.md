# SWAP

## Syntax

```basic
SWAP <variab1e>,<variab1e>
```

**Versions:** EXtended, Disk

## Purpose

To exchange the values of two variables.

## Remarks

Any type variable may be SWAPped (integer, single precision, dQub1e precision, string), but the two variables must be of the same type or a "Type mismatch" error results.

## Example

```basic
LIST
              10 A$=" ONE " : B$=" ALL " : C$="FOR"
              20 PRINT A$ C$ B$
              30 SWAP A$, B$
              40 PRINT A$ C$ B$
              RUN
              Ok
               ONE FOR ALL
               ALL FOR ONE
              Ok
BASIC-80 COMMANDS AND STATEMENTS                    Page 2-80
```

## See Also

*Related statements will be linked here*
