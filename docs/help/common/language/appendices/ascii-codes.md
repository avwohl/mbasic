---
description: Complete ASCII character code reference table for BASIC-80
keywords:
- ascii
- character
- codes
- data
- file
- for
- function
- get
- if
- input
title: ASCII Character Codes
type: reference
---

# ASCII Character Codes

Complete ASCII character code reference for BASIC-80.

## Control Characters (0-31)

| Dec | Hex | Abbr | Name | Description |
|-----|-----|------|------|-------------|
| 0 | 00 | NUL | Null | Null character |
| 1 | 01 | SOH | Start of Heading | |
| 2 | 02 | STX | Start of Text | |
| 3 | 03 | ETX | End of Text | |
| 4 | 04 | EOT | End of Transmission | |
| 5 | 05 | ENQ | Enquiry | |
| 6 | 06 | ACK | Acknowledge | |
| 7 | 07 | BEL | Bell | Beep/alert sound |
| 8 | 08 | BS | Backspace | Move cursor left |
| 9 | 09 | HT | Horizontal Tab | Tab character |
| 10 | 0A | LF | Line Feed | New line |
| 11 | 0B | VT | Vertical Tab | |
| 12 | 0C | FF | Form Feed | New page |
| 13 | 0D | CR | Carriage Return | Return to line start |
| 14 | 0E | SO | Shift Out | |
| 15 | 0F | SI | Shift In | |
| 16 | 10 | DLE | Data Link Escape | |
| 17 | 11 | DC1 | Device Control 1 | XON |
| 18 | 12 | DC2 | Device Control 2 | |
| 19 | 13 | DC3 | Device Control 3 | XOFF |
| 20 | 14 | DC4 | Device Control 4 | |
| 21 | 15 | NAK | Negative Acknowledge | |
| 22 | 16 | SYN | Synchronous Idle | |
| 23 | 17 | ETB | End of Block | |
| 24 | 18 | CAN | Cancel | |
| 25 | 19 | EM | End of Medium | |
| 26 | 1A | SUB | Substitute | |
| 27 | 1B | ESC | Escape | Escape character |
| 28 | 1C | FS | File Separator | |
| 29 | 1D | GS | Group Separator | |
| 30 | 1E | RS | Record Separator | |
| 31 | 1F | US | Unit Separator | |

## Printable Characters (32-126)

| Dec | Hex | Char | Dec | Hex | Char | Dec | Hex | Char | Dec | Hex | Char |
|-----|-----|------|-----|-----|------|-----|-----|------|-----|-----|------|
| 32 | 20 | SPACE | 56 | 38 | 8 | 80 | 50 | P | 104 | 68 | h |
| 33 | 21 | ! | 57 | 39 | 9 | 81 | 51 | Q | 105 | 69 | i |
| 34 | 22 | " | 58 | 3A | : | 82 | 52 | R | 106 | 6A | j |
| 35 | 23 | # | 59 | 3B | ; | 83 | 53 | S | 107 | 6B | k |
| 36 | 24 | $ | 60 | 3C | < | 84 | 54 | T | 108 | 6C | l |
| 37 | 25 | % | 61 | 3D | = | 85 | 55 | U | 109 | 6D | m |
| 38 | 26 | & | 62 | 3E | > | 86 | 56 | V | 110 | 6E | n |
| 39 | 27 | ' | 63 | 3F | ? | 87 | 57 | W | 111 | 6F | o |
| 40 | 28 | ( | 64 | 40 | @ | 88 | 58 | X | 112 | 70 | p |
| 41 | 29 | ) | 65 | 41 | A | 89 | 59 | Y | 113 | 71 | q |
| 42 | 2A | * | 66 | 42 | B | 90 | 5A | Z | 114 | 72 | r |
| 43 | 2B | + | 67 | 43 | C | 91 | 5B | [ | 115 | 73 | s |
| 44 | 2C | , | 68 | 44 | D | 92 | 5C | \ | 116 | 74 | t |
| 45 | 2D | - | 69 | 45 | E | 93 | 5D | ] | 117 | 75 | u |
| 46 | 2E | . | 70 | 46 | F | 94 | 5E | ^ | 118 | 76 | v |
| 47 | 2F | / | 71 | 47 | G | 95 | 5F | _ | 119 | 77 | w |
| 48 | 30 | 0 | 72 | 48 | H | 96 | 60 | ` | 120 | 78 | x |
| 49 | 31 | 1 | 73 | 49 | I | 97 | 61 | a | 121 | 79 | y |
| 50 | 32 | 2 | 74 | 4A | J | 98 | 62 | b | 122 | 7A | z |
| 51 | 33 | 3 | 75 | 4B | K | 99 | 63 | c | 123 | 7B | { |
| 52 | 34 | 4 | 76 | 4C | L | 100 | 64 | d | 124 | 7C | \| |
| 53 | 35 | 5 | 77 | 4D | M | 101 | 65 | e | 125 | 7D | } |
| 54 | 36 | 6 | 78 | 4E | N | 102 | 66 | f | 126 | 7E | ~ |
| 55 | 37 | 7 | 79 | 4F | O | 103 | 67 | g |  |  |  |

## Control Character: DEL

| Dec | Hex | Name | Description |
|-----|-----|------|-------------|
| 127 | 7F | DEL | Delete/Rubout |

## Usage in BASIC-80

### Converting Between ASCII and Characters

```basic
10 REM ASCII to character
20 C$ = CHR$(65)        ' Returns "A"
30 PRINT C$

40 REM Character to ASCII
50 N = ASC("A")         ' Returns 65
60 PRINT N
```

### Common ASCII Values

- **Letters**: A-Z = 65-90, a-z = 97-122
- **Digits**: 0-9 = 48-57
- **Space**: 32
- **Newline**: CR=13, LF=10
- **Tab**: 9

### String Functions Using ASCII

- [ASC](../functions/asc.md) - Get ASCII code of first character
- [CHR$](../functions/chr_dollar.md) - Get character from ASCII code
- [INKEY$](../functions/inkey_dollar.md) - Read keyboard (returns ASCII)
- [INPUT$](../functions/input_dollar.md) - Read characters

## See Also

- [CHR$ Function](../functions/chr_dollar.md) - Convert ASCII code to character
- [ASC Function](../functions/asc.md) - Convert character to ASCII code
- [Character Set](../character-set.md) - BASIC-80 character set overview