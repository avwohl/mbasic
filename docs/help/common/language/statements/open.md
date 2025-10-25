# OPEN

## Syntax

```basic
OPEN <mode>, [#]<file number>,<filename>, [<reclen>]
```

**Versions:** Disk

## Purpose

To allow I/O to a disk file.

## Remarks

A disk file must be OPENed before any disk I/O operation can be performed on that file. OPEN allocates a buffer for I/O to the file and determines the mode of access that will be used with the buffer. <mode> is a string expression whose          first character is one of the following: o        specifies sequential output mode I       specifies sequential input mode R        specifies random input/output mode <file number> is an integer expression whose value is between one and fifteen. The number is then associated with the file for as long as it is OPEN and is used to refer other disk I/O statements to the file. <filename> is a string expression containing a name that conforms to your operating system~s rules for disk filenames. <reclen> is an integer expression which, if included, sets the record length for random files. The default record length is 128 bytes. See also page A-3. NOTE:          A file can be OPENed for sequential input or random access on more than one file number at a time. A file may be OPENed for output, however, on only one file number at a time.

## Example

```basic
10 OPEN "I",2,"INVEN"
               See also Appendix B.
BASIC-80 COMMANDS AND STATEMENTS                         Page 2-57
```

## See Also

*Related statements will be linked here*
