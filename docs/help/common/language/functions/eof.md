---
category: file-io
description: Returns -1 (true) if the end of a sequential file has been reached
keywords: ['data', 'eof', 'error', 'file', 'for', 'function', 'goto', 'if', 'input', 'number']
syntax: EOF(file number)
title: EOF
type: function
---

# EOF

## Syntax

```basic
EOF(file number)
```

**Versions:** Disk

## Description

Returns -1 (true) if the end of a sequential file has been reached. Use EOF to test for end-of-file while INPUTting, to avoid "Input past end" errors.

## Example

```basic
10 OPEN "I", 1, "DATA"
20 C = 0
30 IF EOF(1) THEN 100
40 INPUT #1, M(C)
50 C = C + 1 : GOTO 30
100 CLOSE #1
```

## See Also
- [OPEN](../statements/open.md) - Open a file for input
- [INPUT#](../statements/input_hash.md) - Read data from sequential file
- [LINE INPUT#](../statements/inputi.md) - Read entire line from file
- [CLOSE](../statements/close.md) - Close file when done
- [LOC](loc.md) - Get current file position
- [LOF](lof.md) - Get file length
