---
description: CLI (Command-line) interface for MBASIC
keywords:
- cli
- command line
- terminal
- repl
title: CLI Interface
type: guide
ui: cli
---

# CLI Interface

The command-line interface (CLI) provides a traditional BASIC REPL experience.

## Starting the CLI

```bash
python3 mbasic
```

Or run a program directly:

```bash
python3 mbasic program.bas
```

## Command Mode

When you start MBASIC, you see the `Ok` prompt:

```
Ok
_
```

You can type:
- **Direct commands** - Execute immediately (e.g., `PRINT 2+2`)
- **Program lines** - Start with a line number (e.g., `10 PRINT "Hello"`)
- **System commands** - LIST, RUN, NEW, etc.

## Direct Mode

Execute statements immediately without line numbers:

```
Ok
PRINT 2 + 2
 4
Ok
```

## Program Mode

Enter program lines with line numbers:

```
Ok
10 PRINT "Hello, World!"
20 END
Ok
LIST
10 PRINT "Hello, World!"
20 END
Ok
RUN
Hello, World!
Ok
```

## Common Commands

| Command | Description |
|---------|-------------|
| **RUN** | Run the current program |
| **LIST** | Display program lines |
| **NEW** | Clear the program from memory |
| **SAVE "file"** | Save program to disk |
| **LOAD "file"** | Load program from disk |
| **RENUM** | Renumber program lines |
| **AUTO** | Start automatic line numbering |
| **SYSTEM** | Exit MBASIC |

## Line Editing

The CLI includes a line editor accessed with the **EDIT** command:

```
Ok
EDIT 10
```

See: [EDIT Command](../../language/statements/edit.md)

## Automatic Line Numbering

Use **AUTO** to enter lines without typing numbers:

```
Ok
AUTO
10 PRINT "Line 1"
20 PRINT "Line 2"
30 PRINT "Line 3"
40 ^C
Ok
```

Press {{kbd:stop:cli}} to stop AUTO mode.

See: [AUTO Command](../../language/statements/auto.md)

## File Operations

**Save your work:**
```
Ok
SAVE "program.bas"
Ok
```

**Load a program:**
```
Ok
LOAD "program.bas"
Ok
```

**Merge programs:**
```
Ok
MERGE "addon.bas"
Ok
```

## Error Messages

When an error occurs, MBASIC shows the error and line number:

```
Ok
RUN
?Type mismatch in 20
Ok
```

Use **EDIT** to fix line 20.

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| **{{kbd:stop:cli}}** | Interrupt running program |
| **Ctrl+D** | Exit MBASIC (Unix/Linux) |
| **Ctrl+Z** | Exit MBASIC (Windows) |
| **Up/Down** | Command history (if available) |

## Tips

1. **Save often** - Use SAVE after making changes
2. **Use AUTO** - Faster than typing line numbers
3. **LIST before RUN** - Check your program first
4. **RENUM regularly** - Keep line numbers clean

## See Also

- [Getting Started](../../getting-started.md)
- [Language Reference](../../language/statements/index.md)
- [File I/O](../../language/statements/open.md)
