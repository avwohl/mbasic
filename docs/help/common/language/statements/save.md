# SAVE

## Syntax

```basic
SAVE <filename> [,A   I ,P]
```

**Versions:** Disk

## Purpose

To save a program file on disk.

## Remarks

<filename> is a quoted string that conforms to your   operating   system"'s   requirements  for filenames.  (With CP/M, the default extension .BAS is supplied.) If <filename> already exists, the file will be written over. Use the A option to save the file in ASCII format.   Otherwise, BASIC saves the file in a compressed binary format.   ASCII format takes more space on the disk, but some disk access requires that files be in ASCII format.      For instance, the MERGE command requires and ASCII format file, and some operating system commands such as LIST may require an ASCII format file. Use the P option to protect the file by saving it   in   an encoded binary format.    When a protected file is later RUN (or LOADed), any attempt to list or edit it will fail.

## Example

```basic
SAVE nCOM2 n ,A
              SAVEnpRoo n , P
              See also Appendix B.
BASIC-80 COMMANDS AND STATEMENTS                            Page 2-78
```

## See Also

*Related statements will be linked here*
