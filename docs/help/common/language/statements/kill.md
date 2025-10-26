---
category: file-management
description: NEEDS_DESCRIPTION
keywords:
- NEEDS_KEYWORDS
title: KILL
type: statement
---

# KILL

## Syntax

```basic
KILL <filename>
```

**Versions:** Disk

## Purpose

To delete a file from disk.

## Remarks

If a KILL statement is given for a file that is currently OPEN, a RFile already open R error occurs. KILL is used for all types of disk files: program files, random data files and sequential data files.

## Example

```basic
200 KILL RDATA1R
              See also Appendix B.
BASIC-80 COMMANDS AND STATEMENTS                           Page 2-40
```

## See Also

*Related statements will be linked here*