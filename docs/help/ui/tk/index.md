---
title: MBASIC Tkinter GUI Help
type: guide
ui: tk
description: Help system for the MBASIC graphical user interface
keywords: [help, tk, tkinter, gui, graphical, interface]
---

# MBASIC Tkinter GUI Help

Welcome to the MBASIC graphical IDE. This help system integrates documentation for the Tkinter GUI, the MBASIC interpreter, and the BASIC-80 language.

## 🎮 Games Library

Browse and run classic BASIC games:

- **[Games Library](../../../library/games/index.md)** - 113 classic CP/M era games ready to run!

## 📘 Tkinter GUI Guide

Learn how to use the graphical interface:

- [Getting Started](getting-started.md) - First steps with the GUI
- [Essential Features](features.md) - Smart Insert, Breakpoints, Variables Window, etc.
- [Keyboard Shortcuts](../../../user/keyboard-shortcuts.md) - Complete keyboard reference (auto-generated)
- [Common Workflows](workflows.md) - Step-by-step guides for typical tasks
- [Settings & Configuration](settings.md) - Variable case, keyword case, and more
- [Tips & Tricks](tips.md) - Best practices and productivity tips

## 📗 MBASIC Interpreter

About this BASIC interpreter:

- [MBASIC Index](../../mbasic/index.md) - Overview and navigation
- [Getting Started](../../mbasic/getting-started.md) - Your first BASIC program
- [Features](../../mbasic/features.md) - What's implemented
- [Compatibility](../../mbasic/compatibility.md) - MBASIC 5.21 differences
- [Architecture](../../mbasic/architecture.md) - How MBASIC works

## 📙 MBASIC Compiler

Compile BASIC programs to native CP/M executables:

- **[Compiler Guide](../../common/compiler/index.md)** - Generate .COM files for 8080 or Z80 systems (100% complete!)
- [Features](../../common/compiler/features.md) - What the compiler supports
- [Getting Started](../../common/compiler/getting-started.md) - Compile your first program
- [Generated Code](../../common/compiler/generated-code.md) - Understanding compiler output

## 📕 BASIC-80 Language Reference

Complete BASIC-80 language documentation:

- [Language Overview](../../common/language/index.md) - Introduction to BASIC-80
- [Operators](../../common/language/operators.md) - Arithmetic, logical, relational
- **Statements** - All 63 BASIC-80 statements
  - [Statements Index](../../common/language/statements/index.md)
  - Organized by category: input-output, control-flow, file-io
- **Functions** - All 40 BASIC-80 functions
  - [Functions Index](../../common/language/functions/index.md)
  - Organized by category: mathematical, string, type-conversion
- **Appendices** - Reference materials
  - [Error Codes](../../common/language/appendices/error-codes.md)
  - [ASCII Table](../../common/language/appendices/ascii-codes.md)

---

## Quick Start

**Start the GUI:**
```bash
mbasic --ui tk [filename.bas]
```

**Your First Program:**
1. Type: `10 PRINT "HELLO, WORLD!"`
2. Press **{{kbd:run_program}}** to run
3. See output in the lower pane

## Help Navigation

Use the help browser to navigate:

- **Links** - Click any blue link to navigate
- **Back button** - Return to previous page
- **Home button** - Return to this page
- **Search** - Find help topics by keyword

## Key Features

The Tkinter GUI provides:

- **Syntax highlighting** - BASIC keywords highlighted
- **Line numbers** - Automatic line numbering in gutter
- **Visual debugger** - Step through code, set breakpoints
- **Variable viewing** - Monitor variable values in real-time
- **Output window** - See program output
- **Error highlighting** - Syntax errors marked in code with **?**
- **Smart Insert** - {{kbd:smart_insert}} inserts lines between existing line numbers
- **Statement highlighting** - See exactly what will execute next

## Tips

- **Smart Insert ({{kbd:smart_insert}})** - Essential for efficient editing
- **Variables Window ({{kbd:toggle_variables}})** - See what your program is doing
- **Breakpoints ({{kbd:toggle_breakpoint}})** - Stop at critical points
- **Save Often ({{kbd:file_save}})** - Protect your work

---

## Beyond the Interpreter

The Tkinter GUI runs programs in **interpreter mode**. To compile BASIC programs to native CP/M executables:

**[MBASIC Compiler →](../../common/compiler/index.md)** - Generate native .COM files for 8080 or Z80 systems (100% complete!)

---

**Welcome to MBASIC!** Choose a section above to get started, or use the search box to find specific topics.
