# CLOSE

## Syntax

```basic
CLOSE[[#]<file number>[,[#]<file number ••• >]]
```

## Purpose

To conclude I/O to a disk file.

## Remarks

<file number> is the number under which the file was OPENed.     A CLOSE with no arguments closes all open files. The association between a particular file and file number terminates upon execution of a CLOSE. The file may then be reOPENed using the same or a different file number; likewise, that file number may now be reused to OPEN any file. A CLOSE for a sequential output file writes       the final buffer of output. The END statement and the NEW command always CLOSE all disk files automatically. (STOP does not close disk files.)

## Example

```basic
See PART II, Chapter 3, Microsoft BASIC       Disk
              I/O, of the Microsoft BASIC User's Guide.
BASIC-80 COMMANDS AND STATEMENTS                         Page 2-9
```

## See Also

*Related statements will be linked here*
