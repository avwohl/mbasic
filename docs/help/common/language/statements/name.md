# NAME

## Syntax

```basic
NAME <old filename> AS <new filename>
```

**Versions:** Disk

## Purpose

To change the name of a disk file.

## Remarks

<old filename> must exist and <new filename> must not exist; otherwise an error will result. After a NAME command, the file exists on the same disk, in the same area of disk space, with the new name.

## Example

```basic
Ok
              NAME "ACCTS" AS "LEDGER"
              Ok
              In this example, the file that was
              formerly named ACCTS will now be named LEDGER.
BASIC-80 COMMANDS AND STATEMENTS                      Page 2-52
```

## See Also

*Related statements will be linked here*
