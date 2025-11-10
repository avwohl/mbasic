---
description: Editing programs in the Curses UI
keywords:
- editing
- curses
- terminal
- text editor
- program entry
title: Editing Programs
type: guide
ui: curses
---

# Editing Programs

The Curses UI provides a full-screen text editor for writing BASIC programs.

## Editor Layout

```
┌─ MBASIC Editor ─────────────────────────┐
│ 10 PRINT "Hello, World!"                │
│ 20 END                                   │
│ _                                        │
│                                          │
│                                          │
│                                          │
│                                          │
│                                          │
│                                          │
└─ [{{kbd:run:curses}}: Run] [{{kbd:parse:curses}}: Help] ─────────┘
```

## Entering Programs

1. Type line numbers followed by BASIC statements
2. Press Enter to add each line
3. Lines are automatically sorted by number

**Example:**
```
10 PRINT "Hello"_    (press Enter)
20 END_              (press Enter)
```

## Line Numbers

- **Required** - Every program line needs a number
- **Range** - 0 to 65529
- **Convention** - Use multiples of 10 (10, 20, 30...)
- **Sorting** - Lines are automatically sorted by number

## Editing Existing Lines

To change a line, just retype it with the same number:

```
10 PRINT "Old text"
```

Change to:
```
10 PRINT "New text"_
```

The new version replaces the old one.

## Deleting Lines

Type just the line number and press Enter:

```
20_    (press Enter - deletes line 20)
```

Or use the DELETE command:
```
DELETE 20
DELETE 10-30
```

## Inserting Lines

Use line numbers between existing lines:

```
10 PRINT "First"
30 PRINT "Third"
```

Insert line 20:
```
20 PRINT "Second"_
```

Result:
```
10 PRINT "First"
20 PRINT "Second"
30 PRINT "Third"
```

## Navigation

| Key | Action |
|-----|--------|
| **Arrow Keys** | Move cursor |
| **Home/End** | Start/end of line |
| **Page Up/Down** | Scroll editor |

## Keyboard Shortcuts

See your UI's keyboard shortcuts documentation for the complete list.

Common shortcuts:
- **{{kbd:run:curses}}** - Run program
- **{{kbd:new:curses}}** - New program (clear)
- **{{kbd:save:curses}}** - Save program
- **{{kbd:open:curses}}** - Load program
- **{{kbd:parse:curses}}** - Help

## Renumbering Lines

Use **RENUM** to renumber your program:

```
RENUM        (renumber starting from 10, step 10)
RENUM 100    (start from 100)
RENUM 100,20 (start from 100, step 20)
```

See: [RENUM Command](../../language/statements/renum.md)

## Auto-Numbering

Type **AUTO** to start automatic line numbering:

```
AUTO
10 PRINT "Line 1"    (number added automatically)
20 PRINT "Line 2"    (number added automatically)
30 PRINT "Line 3"    (number added automatically)
```

Exit AUTO mode with {{kbd:continue:curses}} or by typing a line number manually.

See: [AUTO Command](../../language/statements/auto.md)

## Line Editing with EDIT

The **EDIT** command is supported for compatibility with traditional BASIC, but the Curses UI provides full-screen editing capabilities that make it unnecessary. You can directly navigate to any line and edit it in the full-screen editor.

See: [EDIT Command](../../language/statements/edit.md) for traditional usage

## Direct Mode

Lines without numbers execute immediately:

```
PRINT 2 + 2
 4
```

This is useful for testing expressions.

## Multiple Statements Per Line

Use colon (`:`) to separate statements:

```
10 A = 5 : B = 10 : PRINT A + B
```

## Comments

Use REM or apostrophe for comments:

```
10 REM This is a comment
20 ' This is also a comment
30 PRINT "Hello"  ' Comment at end of line
```

## Tips

1. **Use 10 increments** - Leaves room to insert lines
2. **RENUM periodically** - Keep numbers clean
3. **Save often** - Don't lose your work
4. **Use comments** - Document your code
5. **Test as you go** - Run small sections first

## Common Mistakes

**Forgetting line numbers:**
```
PRINT "Hello"    ← Executes immediately, not saved
```

**Line numbers out of order:**
```
30 PRINT "Second"
10 PRINT "First"
```
The editor automatically sorts them as 10, 30.

**Typos in line numbers:**
```
10 PRINT "Test"
1O PRINT "Oops"   ← Letter O instead of zero
```
This is a syntax error! The parser will reject "1O" as an invalid line number.

## See Also

- [Running Programs](../../../ui/curses/running.md)
- [AUTO Command](../../language/statements/auto.md)
- [DELETE Command](../../language/statements/delete.md)
- [RENUM Command](../../language/statements/renum.md)
- [Getting Started](../../getting-started.md)
