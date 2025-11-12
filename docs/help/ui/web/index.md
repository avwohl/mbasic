---
title: MBASIC Web IDE Help
type: guide
ui: web
description: Help system for the MBASIC web-based interface
keywords: [help, web, browser, ide, interface]
---

# MBASIC Web IDE Help

Welcome to the MBASIC web-based IDE. This help system integrates documentation for the Web UI, the MBASIC interpreter, and the BASIC-80 language.

## 🎮 Games Library

Browse and download classic BASIC games:

- **[Games Library](../../../library/games/index.md)** - 113 classic CP/M era games to download and load!

## 📘 Web IDE Guide

Learn how to use the web interface:

- [Getting Started](getting-started.md) - First steps with the Web IDE
- [Web Interface](web-interface.md) - Editor, menus, and components
- [Features](features.md) - Auto-numbering, command area, file I/O
- [Debugging Guide](debugging.md) - Debug tools and features
- [Keyboard Shortcuts](../../../user/keyboard-shortcuts.md) - Complete keyboard reference (auto-generated)
- [Settings & Configuration](settings.md) - Customize your experience

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

**Access the Web IDE:**
```
https://your-server/mbasic
```

**Your First Program:**
1. Type in editor: `PRINT "HELLO, WORLD!"`
2. Press Enter (becomes line 10 automatically)
3. Click **Run** → **Run Program**
4. See output in the middle pane

## Help Navigation

Use the help browser to navigate:

- **Links** - Click any blue link to navigate
- **Back button** - Return to previous page
- **Home button** - Return to this page
- **Search** - Find help topics by keyword

## Key Features

The Web IDE provides:

- **Three-pane interface** - Editor, Output, Command areas
- **Automatic line numbering** - Press Enter to auto-number in editor
- **Command area** - Execute immediate BASIC commands
- **In-memory filesystem** - File I/O within browser session
- **Syntax error reporting** - See errors in output area
- **Example programs** - Load samples to learn
- **Session isolation** - Private, sandboxed environment

## Tips

- **Editor vs Command** - Editor builds programs (auto-numbered), Command runs immediately
- **Quick calculations** - Use Command area for testing: `PRINT 2+2`
- **Load Examples** - File → Load Example to see sample programs
- **File I/O** - Files stored in memory, persist during session only

---

## Beyond the Interpreter

The Web IDE runs programs in **interpreter mode**. To compile BASIC programs to native CP/M executables:

**[MBASIC Compiler →](../../common/compiler/index.md)** - Generate native .COM files for 8080 or Z80 systems (100% complete!)

---

**Welcome to MBASIC!** Choose a section above to get started, or use the search box to find specific topics.
