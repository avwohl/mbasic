---
description: Tkinter graphical interface for MBASIC
keywords:
- tk
- tkinter
- gui
- graphical
- windows
title: Tk Interface
type: guide
ui: tk
---

# Tk Interface

The Tkinter (Tk) interface provides a graphical IDE for MBASIC programming.

## Starting the Tk UI

```bash
python3 mbasic --ui tk
```

Or:

```bash
python3 mbasic -t
```

## Window Layout

The Tk UI has three main sections:

```
┌─ MBASIC ────────────────────────────────┐
│ File  Edit  Run  Help               │
├──────────────────────────────────────────┤
│ Editor                                   │
│ 10 PRINT "Hello, World!"                 │
│ 20 END                                   │
│ _                                        │
│                                          │
├──────────────────────────────────────────┤
│ Output                                   │
│ Hello, World!                            │
│                                          │
└──────────────────────────────────────────┘
```

## Menu Bar

### File Menu
- **New** ({{kbd:file_new:tk}}) - Clear program
- **Open** ({{kbd:file_open:tk}}) - Load program file
- **Save** ({{kbd:file_save:tk}}) - Save current program
- **Save As** - Save with new name
- **Exit** - Quit MBASIC

### Edit Menu
- **Cut** ({{kbd:cut:tk}}) - Cut selected text
- **Copy** ({{kbd:copy:tk}}) - Copy selected text
- **Paste** ({{kbd:paste:tk}}) - Paste clipboard
- **Select All** ({{kbd:select_all:tk}}) - Select all text
- **Find** ({{kbd:find:tk}}) - Search in program

### Run Menu
- **Run** ({{kbd:run_program:tk}}) - Execute program
- **Stop** - Interrupt execution (menu only)
- **Clear Output** - Clear output pane

### Help Menu
- **Help Topics** (F1) - Open help browser
- **About** - About MBASIC

## Editor Pane

The top pane is where you write your BASIC program.

**Features:**
- Syntax highlighting (optional)
- Line numbers
- Auto-indentation
- Find and replace

## Output Pane

The bottom pane shows program output:
- PRINT statements
- Error messages
- INPUT prompts

## Writing Programs

1. Click in the editor pane
2. Type your program with line numbers
3. Lines automatically sort by number

**Example:**
```
10 PRINT "Hello, World!"
20 END
```

## Running Programs

Click **Run → Run** or press **{{kbd:run_program:tk}}**.

Output appears in the output pane.

## Input Handling

When your program uses INPUT:

```basic
10 INPUT "Enter your name: ", N$
20 PRINT "Hello, "; N$
```

A dialog box appears for you to type your response.

## Immediate Mode Panel

Some Tk configurations include an immediate mode panel for quick calculations:

```
> PRINT 2 + 2
4
> PRINT "Test"
Test
```

Type expressions without line numbers for immediate execution.

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| **{{kbd:file_new:tk}}** | New program |
| **{{kbd:file_open:tk}}** | Open file |
| **{{kbd:file_save:tk}}** | Save file |
| **{{kbd:run_program:tk}}** | Run program |
| **{{kbd:find:tk}}** | Find |
| **F1** | Help |

## File Operations

**Save your program:**
1. Click **File → Save** (or {{kbd:file_save:tk}})
2. Choose filename and location
3. Click Save

**Load a program:**
1. Click **File → Open** (or {{kbd:file_open:tk}})
2. Select the .bas file
3. Click Open

## Help Browser

Press **F1** or click **Help → Help Topics** to open the built-in help browser.

**Features:**
- Search across all documentation
- Clickable links
- Three-tier help system (Language, MBASIC, UI)
- Right-click to copy or open in new window

## Error Messages

Errors appear in the output pane:

```
?Syntax error in 20
```

Click on line 20 in the editor to fix it.

## Tips

1. **Use {{kbd:file_save:tk}} often** - Save your work frequently
2. **Clear output** - Use Run → Clear Output between runs
3. **Use Find** - {{kbd:find:tk}} to search for variables/statements
4. **Right-click in help** - Copy examples or open new windows
5. **Check output pane** - Errors and PRINT output go here

## Common Issues

**Output not appearing:**
- Check that OUTPUT pane is visible
- Some programs may need UPDATE or FLUSH

**INPUT not working:**
- Wait for dialog box to appear
- Type your response and press OK

**Program won't stop:**
- Use Run → Stop menu
- Add END statement to your program

## Advantages of Tk UI

- **Mouse support** - Click and select text
- **Multiple windows** - Help in separate window
- **File dialogs** - Easy file management
- **Copy/paste** - Standard clipboard operations
- **Visual** - See editor and output simultaneously

## See Also

- [Getting Started](../../getting-started.md)
- [Language Reference](../../language/statements/index.md)
- [Examples](../../examples/hello-world.md)
