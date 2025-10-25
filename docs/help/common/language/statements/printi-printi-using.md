# PRINTi AND PRINTi USING

## Syntax

```basic
PRINTt<filenumb~r>,[USING<string      exp>;]<list of exps>
```

**Versions:** Disk

## Purpose

To write data to a sequential disk file.

## Remarks

<file number> is the number used when the file was   OPENed   for   output.    <string. exp> is comprised of formatting characters as described in Section 2.50, PRINT USING. The expressions in <list of expressions>, are the numeric and/or string expressions that will be written to the file. PRINTt does not compress data on the disk.     An image of the data is written to the disk, just as it would be displayed on the terminal with a PRINT statement.    For this reason, care should be taken to delimit the data on the disk, so that it will be input correctly from the disk. In the list of expressions, numeric expressions should be delimited by semicolons. For example, PRINTtl,A;B;C;X;Y;Z (If commas are used as delimiters, the extra blanks that are inserted between print fields will also be written to disk.) String expressions    must   be   separated  by semicolons in the list. To format the string expressions correctly on the disk, use explicit delimiters in the list of expressions. For example, let A$=nCAMERA n   and    B$=n93604-1". The statement PRINTtl,A$;B$ would write CAMERA93604-1 to the disk.   Because there are no delimiters, this could not be input as two separate strings.      To   correct   the problem, insert explicit delimiters into the PRINTi statement as follows: PRINTtl,A$;n,";B$ The image written to disk is CAMERA, 93604-1 BASIC-SO COMMANDS AND STATEMENTS                             Page 2-67 which can    be   read     back    into    two        string variables. If the strings themselves      contain   commas, semicolons, significant leading blanks, carriage returns, or line feeds, write them to disk surrounded    by   explicit   quotation   marks, CHR$ (34) • For example, let A$="CAMERA, AUTOMATIC"                  and B$="  93604-1". The statement PRINTtl,A$;B$ would write the following image to disk: CAMERA, AUTOMATIC        93604-1 and the statement INPUTtl,A$,B$ would     input    "CAMERA"   to     A$     and "AUTOMATIC    93604-1" to B$. To separate these strings properly on the disk, write double quotes to the disk image using CHR$(34}. The statement PRINTtl,CHR$(34} ;A$;CHR$(34) ;CHR$(34} ;B$;CHR$(34) writes the following image to disk: "CAMERA, AUTOMATIC""        93604-1" and the statement INPUTtl,A$,B$ would input "CAMERA, AUTOMATIC"           to     A$      and "   93604-1" to B$. The PRINTt statement may also be used with the USING option to control the format of the disk file. For example: PRINTtl,USING"$$ttt.tt,";J;K;L For more examples using PRINTt, see Appendix B. See also WRITEt, Section 2.6S. BASIC-80 COMMANDS AND STATEMENTS                        Page 2-68

## See Also

*Related statements will be linked here*
