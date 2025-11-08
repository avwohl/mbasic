---
description: Guide to saving and loading BASIC programs in the Curses UI
keywords:
- command
- curses
- error
- file
- for
- if
- line
- next
- number
- operations
title: File Operations in Curses UI
type: guide
---

# File Operations in Curses UI

How to save and load BASIC programs.

## Saving Programs

1. Press **{{kbd:save:curses}}** to save (Ctrl+S unavailable - terminal flow control)
2. Status line prompts: "Save as: _"
3. Type filename (e.g., `myprogram.bas`)
4. Press **Enter**
5. Status shows: "Saved to myprogram.bas"

### Tips

- Include `.bas` extension (recommended)
- Use relative or absolute paths
- If file exists, it will be overwritten
- If save fails, error shows in status line

### Example

```
Press {{kbd:save:curses}}
Type: hello.bas
Press Enter
→ "Saved to hello.bas"
```

## Loading Programs

1. Press **{{kbd:open:curses}}**
2. Status line prompts: "Load file: _"
3. Type filename
4. Press **Enter**
5. Program loads into editor

### What Happens

- Current program is replaced (not merged)
- Parse errors shown in output window
- Successfully loaded lines appear in editor
- Status shows: "Loaded from filename.bas"

### Example

```
Press {{kbd:open:curses}}
Type: hello.bas
Press Enter
→ Program loads into editor
```

## Loading from Command Line

You can also load a program when starting:

```bash
python3 mbasic --ui curses myprogram.bas
```

The program will:
- Load into the editor
- Enter interactive mode (ready to run with {{kbd:run:curses}})

## Creating a New Program

1. Press **{{kbd:new:curses}}**
2. Confirms: "Program cleared"
3. Editor is empty, ready for new program

**Warning:** This clears the current program! Save first if needed.

## File Format

Programs are saved as plain text:

```basic
10 PRINT "Hello, World!"
20 FOR I = 1 TO 10
30   PRINT I
40 NEXT I
50 END
```

Each line must start with a line number.

## Troubleshooting

### "File not found" Error

- Check filename spelling
- Check file exists in current directory
- Try absolute path: `/home/user/programs/test.bas`

### "Parse error" Messages

- Some lines may have syntax errors
- Errors shown in output window
- Valid lines still load
- Fix errors and re-save

### Can't See Filename Prompt

- Look at bottom status line
- It says "Save as: " or "Load file: "
- Type filename there
- If error message is showing, press ESC first

## See Also

- [Editing Programs](editing.md)
- [BASIC Language Reference](../../common/language/statements/index.md)