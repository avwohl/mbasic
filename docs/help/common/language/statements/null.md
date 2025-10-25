# NULL

## Syntax

```basic
NULL <integer expression>
```

## Purpose

To set the number of nulls to be printed at   the end of each line.

## Remarks

For    10-character-per-second  tape    punches, <integer expression> should be >=3. When tapes are not being punched, <integer expression> should    be   0   or    1  for  Teletypes   and Teletype-compatible CRTs. <integer expression> should be 2 or 3 for 30 cps hard copy printers. The default value is O.

## Example

```basic
Ok
              NULL 2
              Ok
              100 INPUT X
              200 IF X<50 GOTO 800
              Two null characters will be printed after each
              line.
BASIC-SO COMMANDS AND STATEMENTS                    Page 2-54
```

## See Also

*Related statements will be linked here*
