---
description: Introduction and first steps for using the MBASIC Curses text interface
keywords:
- getting started
- introduction
- tutorial
- first program
- hello world
- curses
ui: curses
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
   mbasic --ui curses
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

7. Press **{{kbd:run:curses}}** to run

8. Output appears in the bottom window!

## Essential Keys

You don't need to memorize everything. The status line shows common commands:

- **{{kbd:help:curses}}** - Help (you're here now!)
- **{{kbd:run:curses}}** - Run program
- **{{kbd:quit:curses}}** - Quit

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
- [Keyboard Shortcuts](../../../user/keyboard-shortcuts.md) - All shortcuts

Or jump to the BASIC language:

- [Getting Started with BASIC](../../common/getting-started.md) - Language basics
- [BASIC Statements](../../common/language/statements/index.md) - Full reference

## Tips

- Press **ESC** to clear error messages
- Press **{{kbd:help:curses}}** to open help
- Status line shows available commands
- Lines auto-increment by 10 for easy editing