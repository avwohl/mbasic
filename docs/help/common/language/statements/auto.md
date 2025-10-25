# AUTO

## Syntax

```basic
AUTO [<line number>[,<increment>]]
```

## Purpose

To generate a line number   automatically     after every carriage return.

## Remarks

AUTO begins numbering at <line number> and increments   each   subsequent line number by <increment>. The default for -both values is 10. If <line number> is followed by a comma but <increment> is not specified, the last increment specified in an AUTO command is assumed. If AUTO generates a line number that is already being used, an asterisk is printed after the number to warn the user that any input will replace the existing line. However, typing a carriage return immediately after the asterisk will save the line and generate the next line number. AUTO is terminated by typing Control-C.    The line in which Control-C is typed is not saved. After Control-C is typed, BASIC returns to command level.

## Example

```basic
AUTO 100,50      Generates line numbers 100,
                              150, 200 •••
             AUTO             Generates line numbers 10,
                              20,30,40 •••
BASIC-SO COMMANDS AND STATEMENTS                        Page 2-3
```

## See Also

*Related statements will be linked here*
