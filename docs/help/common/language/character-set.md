---
description: BASIC-80 character set and special characters
keywords:
- characters
- character set
- ascii
- special characters
- symbols
title: Character Set
type: reference
---

# Character Set

BASIC-80 uses the ASCII character set.

## Valid Characters

BASIC-80 programs can use:

**Letters:** A-Z (uppercase and lowercase)
**Digits:** 0-9
**Special symbols:** See below

## Special Characters in BASIC

| Character | Name | Usage |
|-----------|------|-------|
| **"** | Quote | String delimiters: `"Hello"` |
| **'** | Apostrophe | Comment: `10 ' Comment` |
| **:** | Colon | Statement separator: `A=5:B=10` |
| **;** | Semicolon | Print separator, statement continuation |
| **,** | Comma | List separator, print tab |
| **.** | Period | Decimal point: `3.14` |
| **+** | Plus | Addition, positive sign |
| **-** | Minus | Subtraction, negative sign |
| **\*** | Asterisk | Multiplication |
| **/** | Slash | Division |
| **\\** | Backslash | Integer division |
| **^** | Caret | Exponentiation: `2^3` |
| **=** | Equals | Assignment, comparison |
| **<** | Less than | Comparison |
| **>** | Greater than | Comparison |
| **(** | Left paren | Grouping, function calls |
| **)** | Right paren | Grouping, function calls |
| **$** | Dollar | String type suffix: `NAME$` |
| **%** | Percent | Integer type suffix: `COUNT%` |
| **!** | Exclamation | Single precision suffix: `X!` |
| **#** | Hash | Double precision suffix: `PI#`, file number |
| **&** | Ampersand | Hexadecimal/octal prefix: `&HFF`, `&O77` |
| **_** | Underscore | Allowed in variable names (some versions) |

## String Characters

Strings can contain any printable ASCII characters (32-126):

```basic
10 A$ = "Hello, World!"
20 B$ = "123 Main St."
30 C$ = "!@#$%^&*()"
```

## Control Characters

BASIC supports some control characters:

| Code | Character | Usage |
|------|-----------|-------|
| 7 | BEL | Bell/beep: `PRINT CHR$(7)` |
| 8 | BS | Backspace |
| 9 | TAB | Tab character |
| 10 | LF | Line feed (new line) |
| 13 | CR | Carriage return (return to line start) |
| 27 | ESC | Escape character |

Use CHR$() to include control characters in strings.

## Reserved Words

Cannot be used as variable names:

- All BASIC statements (PRINT, FOR, IF, etc.)
- All functions (SIN, COS, LEFT$, etc.)
- Reserved keywords (AND, OR, NOT, TO, STEP, etc.)

See: [Statements](statements/index.md), [Functions](functions/index.md)

## Variable Names

Valid variable names:
- Start with a letter (A-Z)
- Can contain letters and digits
- Can end with type suffix ($, %, !, #)
- Maximum length varies by implementation

**Valid:**
```basic
A
X1
NAME$
COUNT%
TOTAL
VALUE123
```

**Invalid:**
```basic
2X          ' Cannot start with digit
A+B         ' Cannot contain operators
FOR         ' Reserved word
PRINT$      ' Reserved word
```

## Case Sensitivity

BASIC-80 is **not case sensitive**:

```basic
10 Print "Hello"     ' Same as PRINT
20 FoR I = 1 To 10   ' Same as FOR and TO
```

Convention: Use UPPERCASE for keywords, mixed case for variables.

## Line Terminators

Programs can use different line endings:
- **CR+LF** (Windows: `\r\n`)
- **LF** (Unix/Linux: `\n`)
- **CR** (Old Mac: `\r`)

MBASIC accepts all formats.

## Comments

Two ways to add comments:

```basic
10 REM This is a comment
20 ' This is also a comment
```

Everything after REM or ' is ignored.

## String Escaping

BASIC does not have escape sequences like `\n` or `\t`.

Use CHR$() instead:

```basic
10 PRINT "Line 1" + CHR$(10) + "Line 2"    ' Newline
20 PRINT "Col1" + CHR$(9) + "Col2"         ' Tab
```

## Hexadecimal and Octal

Use **&H** for hexadecimal, **&O** for octal:

```basic
10 HEX = &HFF      ' 255 in hex
20 OCT = &O77      ' 63 in octal
30 PRINT HEX, OCT
```

## Whitespace

- **Spaces** - Usually ignored, but required between keywords
- **Tabs** - Treated as spaces
- **Blank lines** - Allowed in programs

```basic
10PRINT"OK"           ' Works but hard to read
10 PRINT "Better"     ' Recommended
```

## Special Sequences

**Line continuation:**
Not supported in MBASIC 5.21. Use `:` to combine statements:

```basic
10 A = 1 : B = 2 : C = 3
```

**String concatenation:**
```basic
10 FULLNAME$ = FIRST$ + " " + LAST$
```

## See Also

- [ASCII Codes](appendices/ascii-codes.md) - Complete ASCII table
- [Data Types](data-types.md) - Variable types
- [Operators](operators.md) - Operator symbols
- [String Functions](functions/index.md) - CHR$, ASC, etc.
