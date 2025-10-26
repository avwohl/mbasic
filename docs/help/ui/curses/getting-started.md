---
description: NEEDS_DESCRIPTION
keywords:
- NEEDS_KEYWORDS
title: Getting Started with Curses UI
type: guide
---

# Getting Started with Curses UI

Welcome to the MBASIC curses text interface!

## What is the Curses UI?

The curses UI is a full-screen terminal interface that provides:

- **Editor window** (top) - Write your BASIC program
- **Output window** (bottom) - See program output
- **Status line** (bottom) - Commands and messages

## Your First Program

Let's write a simple program:

1. Start MBASIC with curses:
   ```bash
   python3 mbasic.py --backend curses
   ```

2. You'll see the editor window at the top

3. Type your first line:
   ```
   10 PRINT "Hello, World!"
   ```

4. Press **Enter** to save the line

5. Type the next line:
   ```
   20 END
   ```

6. Press **Enter**

7. Press **Ctrl+R** to run

8. Output appears in the bottom window!

## Essential Keys

You don't need to memorize everything. The status line shows common commands:

- **Ctrl+P** - Help (you're here now!)
- **Ctrl+R** - Run program
- **Q** - Quit

No function keys needed!

## Navigation

- **Up/Down arrows** - Move between lines
- **Left/Right arrows** - Move cursor within line
- **Enter** - Save current line

## What's Next?

Now that you've run your first program:

- [Editing Programs](editing.md) - Learn line editing
- [Running Programs](running.md) - More about execution
- [File Operations](files.md) - Save and load programs
- [Keyboard Commands](keyboard-commands.md) - All shortcuts

Or jump to the BASIC language:

- [Getting Started with BASIC](../../getting-started.md) - Language basics
- [BASIC Statements](../../language/statements/index.md) - Full reference

## Tips

- Press **ESC** to clear error messages
- Press **Ctrl+P** to open help
- Status line shows available commands
- Lines auto-increment by 10 for easy editing