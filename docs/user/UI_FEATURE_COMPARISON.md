# MBASIC UI Feature Comparison Guide

This guide helps you choose the right UI for your needs and understand the feature differences between MBASIC's user interfaces.

## Quick UI Selection Guide

### Which UI Should I Use?

| If you want... | Use this UI | Why |
|----------------|------------|-----|
| **Classic BASIC experience** | CLI | Authentic MBASIC-80 command line |
| **Full-featured IDE** | Tk | Most complete feature set |
| **Terminal-based IDE** | Curses | Works over SSH, no GUI needed |
| **Browser-based access** | Web | No installation, works anywhere |
| **Quick testing** | CLI | Simplest, fastest startup |
| **Advanced debugging** | Tk or Web | Visual breakpoints and inspectors |
| **Automated testing** | CLI | Best for scripts and automation |
| **Teaching/Learning** | Web | Easy sharing, no setup required |

## Feature Availability Matrix

### Legend

| Symbol | Meaning |
|--------|---------|
| ✅ | Fully implemented and available |
| ⚠️ | Partially implemented or planned (see Notes column) |
| ❌ | Not available or not applicable |

### Core Features

| Feature | CLI | Curses | Tk | Web | Notes |
|---------|-----|--------|----|-----|-------|
| **Run BASIC programs** | ✅ | ✅ | ✅ | ✅ | All UIs run MBASIC 5.21 |
| **Edit programs** | ✅ | ✅ | ✅ | ✅ | Different editing styles |
| **Load/Save files** | ✅ | ✅ | ✅ | ✅ | Web uses browser storage |
| **Immediate mode** | ✅ | ✅ | ✅ | ✅ | Direct command execution |
| **Error messages** | ✅ | ✅ | ✅ | ✅ | Standard MBASIC errors |

### File Operations

| Feature | CLI | Curses | Tk | Web | Notes |
|---------|-----|--------|----|-----|-------|
| **New program** | ✅ | ✅ | ✅ | ✅ | NEW command |
| **Open file** | ✅ | ✅ | ✅ | ✅ | LOAD "filename" command or File → Open |
| **Save (interactive)** | ❌ | ✅ | ✅ | ✅ | Ctrl+S prompts for filename |
| **Save (command)** | ✅ | ✅ | ✅ | ✅ | SAVE "filename" command |
| **Recent files** | ❌ | ❌ | ✅ | ⚠️ | Tk: menu, Web: localStorage |
| **Drag & drop** | ❌ | ❌ | ✅ | ✅ | GUI only |
| **Auto-save** | ❌ | ❌ | ⚠️ | ✅ | Tk: planned/optional, Web: automatic |

### Editing Features

| Feature | CLI | Curses | Tk | Web | Notes |
|---------|-----|--------|----|-----|-------|
| **Line editing** | ✅ | ✅ | ✅ | ✅ | Edit by line number |
| **Full-screen editor** | ❌ | ✅ | ✅ | ✅ | CLI is line-based |
| **Syntax highlighting** | ❌ | ⚠️ | ✅ | ✅ | Curses: basic |
| **Cut/Copy/Paste** | ❌ | ❌ | ✅ | ✅ | GUI clipboard support |
| **Find/Replace** | ❌ | ❌ | ✅ | ⚠️ | Tk: implemented, Web: planned |
| **Auto-complete** | ❌ | ❌ | ❌ | ✅ | Web suggests keywords |
| **Smart Insert** | ❌ | ❌ | ✅ | ❌ | Tk exclusive feature |

### Debugging Features

| Feature | CLI | Curses | Tk | Web | Notes |
|---------|-----|--------|----|-----|-------|
| **Breakpoints** | ✅ | ✅ | ✅ | ✅ | CLI: BREAK command |
| **Step execution** | ✅ | ✅ | ✅ | ✅ | CLI: STEP command |
| **Variable inspector** | ✅ | ✅ | ✅ | ✅ | CLI: WATCH command |
| **Edit variables** | ❌ | ⚠️ | ✅ | ✅ | CLI: immediate mode only |
| **Call stack view** | ✅ | ✅ | ✅ | ✅ | CLI: STACK command |
| **Visual breakpoints** | ❌ | ✅ | ✅ | ✅ | Click line numbers |
| **Conditional breaks** | ❌ | ❌ | ❌ | ✅ | Web only |
| **Execution trace** | ❌ | ✅ | ✅ | ✅ | Show execution path |

### Help System

| Feature | CLI | Curses | Tk | Web | Notes |
|---------|-----|--------|----|-----|-------|
| **Built-in help** | ✅ | ✅ | ✅ | ✅ | All have help |
| **Context help** | ❌ | ✅ | ✅ | ✅ | Curses/Web: F1; Tk: menu |
| **Searchable help** | ✅ | ✅ | ✅ | ✅ | HELP SEARCH |
| **External browser** | ❌ | ❌ | ✅ | N/A | Tk opens browser |

### User Interface

| Feature | CLI | Curses | Tk | Web | Notes |
|---------|-----|--------|----|-----|-------|
| **Mouse support** | ❌ | ⚠️ | ✅ | ✅ | Curses: limited, terminal-dependent |
| **Menus** | ❌ | ✅ | ✅ | ✅ | CLI: commands only |
| **Keyboard shortcuts** | ⚠️ | ✅ | ✅ | ✅ | CLI: limited |
| **Resizable panels** | ❌ | ⚠️ | ✅ | ✅ | |
| **Themes** | ❌ | ❌ | ⚠️ | ✅ | Web: light/dark |
| **Font options** | ❌ | ❌ | ✅ | ✅ | |

## Detailed UI Descriptions

### CLI (Command Line Interface)

**Best for:** Purists, automation, testing, classic experience

**Strengths:**
- Authentic MBASIC-80 experience
- Lightweight and fast
- Perfect for automation/scripting
- NEW debugging commands (BREAK, STEP, WATCH, STACK)
- Extensive test coverage
- Works everywhere Python runs

**Limitations:**
- No visual editor (line-based only)
- No mouse support
- Limited UI features
- No interactive save prompt (must use SAVE "filename" command)

**Unique Features:**
- Direct command-line debugging
- Best for batch processing
- Scriptable via stdin/stdout

### Curses (Terminal UI)

**Best for:** SSH access, terminal lovers, remote development

**Strengths:**
- Full-screen terminal interface
- Works over SSH
- Good keyboard support
- Visual debugging
- Split-screen layout
- No GUI required

**Limitations:**
- Limited mouse support
- No clipboard integration
- Terminal color limitations
- Partial variable editing

**Unique Features:**
- Terminal-based IDE
- Works in console mode
- Resource efficient

### Tk (Desktop GUI)

**Best for:** Desktop development, full IDE experience

**Strengths:**
- Most complete feature set
- Native desktop application
- Full mouse and keyboard
- Find/Replace functionality
- Smart Insert feature
- Variable editing
- Recent files list

**Limitations:**
- Requires Tkinter installation
- Desktop only (no remote)
- Heavier resource usage

**Unique Features:**
- Find/Replace (Ctrl+F/H)
- Smart Insert mode
- Most UI polish
- Native file dialogs
- Web browser help integration

### Web (Browser-based)

**Best for:** Education, sharing, no-install access

**Strengths:**
- No installation required
- Works on any device with browser
- Modern interface
- Auto-save to browser
- Shareable programs
- Best debugging visuals

**Limitations:**
- Requires web server
- Browser storage limits
- No local file system access
- Session-based storage

**Unique Features:**
- Browser-based IDE
- Conditional breakpoints
- Auto-completion
- Theme support
- Touch device support

## Feature Implementation Status

### Recently Added (2025-10-29)
- ✅ CLI: Debugging commands (BREAK, STEP, WATCH, STACK)
- ✅ Tk: Find/Replace functionality
- ✅ Curses: Save As support
- ✅ Tk: Web browser help launcher

### Coming Soon
- ⏳ DATA/READ/RESTORE statements (all UIs)
- ⏳ ON GOTO/GOSUB support (all UIs)
- ⏳ Variable editing in Curses
- ⏳ Find/Replace in Web UI

### Known Gaps
- CLI: No interactive save prompt (use SAVE "filename" command instead)
- Web: No Find/Replace yet
- Curses: Limited variable editing
- All: No collaborative editing

## Keyboard Shortcuts Comparison

### Common Shortcuts

| Action | CLI | Curses | Tk | Web |
|--------|-----|--------|----|----|
| **Run** | RUN | Ctrl+R | Ctrl+R | Ctrl+R/F5 |
| **Stop** | Ctrl+C | Ctrl+C/Esc | Esc | Esc |
| **Save** | SAVE "file" | Ctrl+S | Ctrl+S | Ctrl+S |
| **New** | NEW | Ctrl+N | Ctrl+N | Ctrl+N |
| **Open** | LOAD "file" | Ctrl+O | Ctrl+O | Ctrl+O |
| **Help** | HELP | Ctrl+H/F1 | Ctrl+? | F1 |
| **Quit** | SYSTEM | Ctrl+Q | Ctrl+Q | N/A |

### Debugging Shortcuts

| Action | CLI | Curses | Tk | Web |
|--------|-----|--------|----|----|
| **Toggle Breakpoint** | BREAK line | F9 | Ctrl+B | F9 |
| **Step** | STEP | F10 | Menu/Toolbar | F10 |
| **Continue** | CONT | F5 | Menu/Toolbar | F5 |
| **Variables** | WATCH | Ctrl+W | Ctrl+W | Ctrl+Alt+V |

## Performance Comparison

| Aspect | CLI | Curses | Tk | Web |
|--------|-----|--------|----|----|
| **Startup time** | Fastest | Fast | Medium | Slow |
| **Memory usage** | Lowest | Low | Medium | High |
| **Large files** | Best | Good | Good | Limited |
| **Execution speed** | Fastest | Fast | Fast | Good |

## Choosing Your UI

### For Beginners
**Recommended: Web UI**
- No installation needed
- Modern, familiar interface
- Good documentation
- Visual debugging

### For Power Users
**Recommended: Tk UI**
- Most features
- Best editing tools
- Complete IDE experience
- Efficient workflow

### For Remote Work
**Recommended: Curses UI**
- SSH friendly
- Low bandwidth
- Terminal-based
- Full featured

### For Automation
**Recommended: CLI**
- Scriptable
- Fast execution
- Minimal overhead
- Batch processing

## Migration Between UIs

### Moving from CLI to GUI
1. Your .bas files work in any UI
2. Learn visual debugging tools
3. Explore menu options
4. Use keyboard shortcuts

### Moving from GUI to CLI
1. Learn command syntax
2. Use HELP frequently
3. Master line-based editing
4. Learn debugging commands

### Sharing Between UIs
- All UIs use same .bas format
- Programs are 100% compatible
- Only UI features differ
- Same MBASIC 5.21 interpreter

## Getting Help

- **CLI:** Type `HELP` or `HELP <topic>`
- **Curses:** Press F1 or Ctrl+H
- **Tk:** Press Ctrl+? or use Help menu
- **Web:** Press F1 or click Help

## Reporting Issues

Found a bug or missing feature? Report at:
https://github.com/anthropics/mbasic/issues

Include:
- Which UI you're using
- What feature is affected
- Steps to reproduce
- Expected vs actual behavior