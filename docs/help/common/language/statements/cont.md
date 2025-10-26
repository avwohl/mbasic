---
category: program-control
description: NEEDS_DESCRIPTION
keywords:
- NEEDS_KEYWORDS
title: CONT
type: statement
---

# CONT

## Syntax

```basic
CONT
```

## Purpose

To continue program execution after a Control-C has been typed, or a STOP or END statement has been executed.

## Remarks

Execution resumes at the point where the break occurred.   If the break occurred after a prompt from an INPUT statement, execution continues with the reprinting of the prompt (7 or prompt string) • CONT is usually used in conjunction with STOP for   debugging.   When execution is stopped, intermediate values may be examined and changed using direct mode statements. Execution may be. resumed with CONT or a direct mode GOTO, which resumes execution at a specified line number. With the Extended and Disk versions, CONT may be used to continue execution after an error. CONT is invalid if the program has been edited during the break.     In 8K BASIC-80, execution cannot be CONTinued if a direct mode error, has occurred during the break.

## Example

```basic
See example Section 2.61, STOP.
BASIC-80 COMMANDS AND STATEMENTS                             Page 2-11
```

## See Also

*Related statements will be linked here*