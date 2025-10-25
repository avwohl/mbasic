# WRITE

## Syntax

```basic
WRITE[<list of expressions»
Ver~ion:       Disk
```

## Purpose

To output data at the terminal. Remark$.:      If <list of expressions> is omitted, a blank line is output.      If <list of expressions> is included, the values of te expressions are output at thee terminal. The expressions in the list may be numeric and/or string expressions, and they mu~t be separated by commas. When the printed items are output, each item will be separated from the last by a comma. Printed strings will be delimited by quotation marks.   After the last item in the list is printed, BASIC inserts a carriage return/line feed. WRITE output~ numeric values using the same format as the PRINT statement, Section 2.49.

## Example

```basic
10 A:;SO:B=90:C$="THAT'-S ALL"
               20 WRITE A,B,C$
               RUN
                SO,   90,"THAT~S   ALL"
               Ok
BASIC-80 COMMANDS AND STATEMENTS                          Page 2-85
```

## See Also

*Related statements will be linked here*
