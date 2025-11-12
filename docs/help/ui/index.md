---
title: MBASIC User Interfaces
description: Overview of all available user interfaces for MBASIC
keywords: [ui, interface, curses, cli, tk, web, gui]
---

# MBASIC User Interfaces

MBASIC offers four different user interfaces to suit different workflows and preferences.

## Available Interfaces

### 📟 [Curses UI](curses/index.md)

Full-screen terminal interface with split editor/output panes.

**Best for:** Interactive development, debugging, terminal workflows

**Start with:**
```bash
mbasic                # Default UI
mbasic --ui curses
```

**Features:**
- Split editor/output view
- Syntax highlighting
- Real-time variable viewing
- Visual debugger with breakpoints
- Menu system (Ctrl+M)

---

### 💻 [CLI Mode](cli/index.md)

Classic MBASIC command-line REPL interface.

**Best for:** Scripting, automation, authentic MBASIC experience

**Start with:**
```bash
mbasic --ui cli
```

**Features:**
- Authentic MBASIC 5.21 command interface
- Direct mode execution
- Program mode with line numbers
- File I/O operations
- Classic `Ok` prompt

---

### 🖼️ [Tkinter GUI](tk/index.md)

Native graphical interface with menus and toolbars.

**Best for:** Users who prefer graphical interfaces

**Start with:**
```bash
mbasic --ui tk
```

**Features:**
- Native GUI widgets
- Menu bar and toolbar
- Syntax highlighting
- Variable inspection window
- Visual debugger

---

### 🌐 [Web IDE](web/index.md)

Browser-based interface accessible from any device.

**Best for:** Remote access, shared environments, cross-platform use

**Start with:**
```bash
mbasic --ui web
```

Then open: **http://localhost:8080**

**Features:**
- Access from any browser
- Three-pane layout (editor/output/command)
- Automatic line numbering
- In-memory filesystem
- Session isolation

---

## Comparison

| Feature | Curses | CLI | Tkinter | Web | Notes |
|---------|--------|-----|---------|-----|-------|
| Visual Editor | ✓ | ✗ | ✓ | ✓ | |
| Split View | ✓ | ✗ | ✓ | ✓ | |
| Debugger | ✓ | ✗ | ✓ | Limited | Web: breakpoints, step, basic variable inspection (planned: advanced panels, watch expressions) |
| Variables Window | ✓ | ✗ | ✓ | ✓ | Web: popup dialog, not persistent panel |
| Remote Access | ✗ | ✗ | ✗ | ✓ | |
| Syntax Highlighting | ✓ | ✗ | ✓ | ✓ | |
| Terminal Required | ✓ | ✓ | ✗ | ✗ | |
| Browser Required | ✗ | ✗ | ✗ | ✓ | |

## Choosing an Interface

**For learning BASIC:**
- Start with **Curses UI** - full-featured and easy to use

**For running existing programs:**
- Use **CLI mode** for authentic MBASIC experience

**For GUI preference:**
- Try **Tkinter GUI** for native desktop experience

**For remote/web access:**
- Use **Web IDE** for browser-based development

---

## Beyond the Interpreter: The Compiler

All interfaces above run BASIC programs in **interpreter mode**. For generating native CP/M executables, see:

**🔧 [MBASIC Compiler](../common/compiler/index.md)** - Compile BASIC to native .COM files for 8080 or Z80 CP/M systems

The compiler is 100% feature complete and generates real machine code with hardware access!

---

Click any interface above to view detailed documentation, keyboard shortcuts, and feature guides.
