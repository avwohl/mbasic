---
category: NEEDS_CATEGORIZATION
description: NEEDS_DESCRIPTION
keywords:
- NEEDS_KEYWORDS
title: LINE INPUT
type: statement
---

# LINE INPUT

## Syntax

```basic
LINE INPUT[i] [<"prompt string">i]<string variable>
```

## Purpose

To input an entire line (up to 254 characters) to   a string variable, without the use of delimiters.

## Remarks

The prompt string is a string literal that is printed   at    the  terminal before input is accepted. A question mark is not printed unless it is part of the prompt string. All input from the end of the prompt to the carriage return is assigned to <string variable>. If LINE INPUT is immediately followed by a semicolon, then the carriage return typed by the user to end the input line does not echo a carriage   return/line    feed sequence at the terminal. A LINE INPUT may be escaped by typing Control-C. BASIC-SO will return to command level and type Ok. Typing CONT resumes execution at the LINE INPUT.

## Example

```basic
See Example, Section 2.32, LINE INPUT#.
BASIC-SO COMMANDS AND STATEMENTS                   Page 2-42
```

## See Also

*Related statements will be linked here*