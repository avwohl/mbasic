---
title: Getting Started with MBASIC
type: guide
category: mbasic
keywords:
- getting started
- introduction
- installation
- quick start
- hello world
- first program
description: Introduction to MBASIC interpreter and how to get started
---

# Getting Started with MBASIC

Welcome to MBASIC 5.21! This is a complete Python implementation of MBASIC-80 for CP/M.

## What is MBASIC?

MBASIC 5.21 is a classic BASIC dialect from the CP/M era (late 1970s - early 1980s). This interpreter provides:

- **100% MBASIC 5.21 compatibility** - Runs authentic MBASIC programs
- **Modern interface** - Choice of CLI, Curses, or Tkinter UI
- **Cross-platform** - Works on Linux, macOS, Windows
- **No dependencies** - Pure Python implementation

## Installation

### Requirements

- Python 3.8 or later
- Optional: `urwid` for Curses UI (installed via `pip install urwid`)

### Quick Install

```bash
# Clone the repository
git clone https://github.com/avwohl/mbasic.git
cd mbasic

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install optional dependencies
pip install -r requirements.txt

# Run MBASIC
mbasic
```

## Your First Program

### Method 1: Interactive Mode (Curses UI)

Start MBASIC without arguments for the full-screen editor:

```bash
mbasic
```

Type your program:

```basic
10 PRINT "Hello, World!"
20 END
```

Press **Ctrl+R** to run.

### Method 2: File Mode

Create a file `hello.bas`:

```basic
10 PRINT "Hello, World!"
20 END
```

Run it:

```bash
mbasic hello.bas
```

### Method 3: CLI Mode

Start MBASIC in CLI mode:

```bash
mbasic --ui cli
```

Type your program at the `Ok` prompt:

```
10 PRINT "Hello, World!"
20 END
RUN
```

## Choosing a User Interface

MBASIC supports three interfaces:

### Curses UI (Default)

Full-screen terminal interface with split editor/output:

```bash
mbasic               # or
mbasic --ui curses
```

**Best for:** Interactive program development, debugging

### CLI Mode

Classic MBASIC command-line interface:

```bash
mbasic --ui cli
```

**Best for:** Scripting, automation, authentic MBASIC experience

### Tkinter GUI

Graphical interface with menu bar and toolbar:

```bash
mbasic --ui tk
```

**Best for:** Users who prefer graphical interfaces

## Next Steps

- **Learn the language:** See [Language Reference](../common/language/statements/index.md)
- **Choose your UI:** [CLI](../ui/cli/index.md), [Curses](../ui/curses/index.md), or [Tk](../ui/tk/index.md)
- **Explore features:** [MBASIC Features](features.md)
- **Check compatibility:** [Compatibility Guide](compatibility.md)
- **Understand the architecture:** [Architecture](architecture.md)

## Quick Reference

**Running programs:**
```bash
mbasic program.bas    # Run a file
mbasic                # Interactive mode
```

**Common keyboard shortcuts (Curses UI):**
- `Ctrl+R` - Run program
- `Ctrl+S` - Save program
- `Ctrl+O` - Open program
- `Ctrl+H` - Help
- `Ctrl+Q` - Quit

**Common commands (CLI mode):**
- `RUN` - Execute program
- `LIST` - Show program
- `SAVE "file.bas"` - Save to disk
- `LOAD "file.bas"` - Load from disk
- `NEW` - Clear program
- `SYSTEM` - Exit MBASIC

## Getting Help

- Press **Ctrl+H** in any UI for built-in help
- See [Language Reference](../common/language/statements/index.md) for statement syntax
- Visit [UI-specific guides](../ui/curses/index.md) for interface help
