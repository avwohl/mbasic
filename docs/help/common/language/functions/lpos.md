---
category: file-io
description: NEEDS_DESCRIPTION
keywords:
- NEEDS_KEYWORDS
title: LPOS
type: function
---

# LPOS

## Syntax

```basic
LPOS(X)
```

**Versions:** Extended, Disk

## Description

Returns the current position of the line printer print head within the line printer buffer. Does not necessarily give the physical position of the print head. X is a dummy argument.

## Example

```basic
100 IF LPOS(X) >60 THEN LPRINT CHR$(13)
BASIC-80 FUNCTIONS                                    Page 3-15
```

## See Also

*Related functions will be linked here*