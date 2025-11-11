# MBASIC UI Feature Comparison Guide

> **Note:** This guide uses `{{kbd:action:ui}}` notation for keyboard shortcuts. These are template variables that represent actual key combinations. For specific key mappings, see the Help menu in each UI or the individual UI quick reference guides.

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
| ⚠️ | Partially implemented (see Notes column for details) |
| 📋 | Planned for future implementation (not yet available) |
| ❌ | Not available or not applicable |

**Note:** For ⚠️ entries, check the Notes column to understand which parts are implemented versus planned.

### Core Features

| Feature | CLI | Curses | Tk | Web | Notes |
|---------|-----|--------|----|-----|-------|
| **Run BASIC programs** | ✅ | ✅ | ✅ | ✅ | All UIs run MBASIC-2025 |
| **Edit programs** | ✅ | ✅ | ✅ | ✅ | Different editing styles |
| **Load/Save files** | ✅ | ✅ | ✅ | ✅ | Web uses browser storage |
| **Immediate mode** | ✅ | ✅ | ✅ | ✅ | Direct command execution |
| **Error messages** | ✅ | ✅ | ✅ | ✅ | Standard MBASIC errors |

### File Operations

| Feature | CLI | Curses | Tk | Web | Notes |
|---------|-----|--------|----|-----|-------|
| **New program** | ✅ | ✅ | ✅ | ✅ | NEW command |
| **Open file** | ✅ | ✅ | ✅ | ✅ | LOAD "filename" command or File → Open |
| **Save (interactive)** | ❌ | ✅ | ✅ | ✅ | Keyboard shortcut prompts for filename |
| **Save (command)** | ✅ | ✅ | ✅ | ✅ | SAVE "filename" command |
| **Recent files** | ❌ | ❌ | ✅ | ✅ | Tk: menu, Web: localStorage (filenames only) |
| **Drag & drop** | ❌ | ❌ | ✅ | ✅ | GUI only |
| **Auto-save** | ❌ | ❌ | 📋 | ✅ | Tk: planned, Web: automatic |

### Editing Features

| Feature | CLI | Curses | Tk | Web | Notes |
|---------|-----|--------|----|-----|-------|
| **Line editing** | ✅ | ✅ | ✅ | ✅ | Edit by line number |
| **Full-screen editor** | ❌ | ✅ | ✅ | ✅ | CLI is line-based |
| **Syntax highlighting** | ❌ | ⚠️ | ✅ | ✅ | Curses: basic |
| **Cut/Copy/Paste** | ❌ | ❌ | ✅ | ✅ | GUI clipboard support |
| **Find/Replace** | ❌ | ❌ | ✅ | 📋 | Tk: implemented, Web: planned |
| **Auto-complete** | ❌ | ❌ | ❌ | ✅ | Web suggests keywords |
| **Smart Insert** | ❌ | ❌ | ✅ | ❌ | Tk exclusive feature |

### Debugging Features

| Feature | CLI | Curses | Tk | Web | Notes |
|---------|-----|--------|----|-----|-------|
| **Breakpoints** | ✅ | ✅ | ✅ | ✅ | CLI: BREAK command |
| **Step execution** | ✅ | ✅ | ✅ | ✅ | CLI: STEP command |
| **Variable inspector** | ✅ | ✅ | ✅ | ✅ | CLI: immediate mode print |
| **Edit variables** | ❌ | ⚠️ | ✅ | ✅ | CLI: immediate mode only |
| **Call stack view** | ✅ | ✅ | ✅ | ✅ | CLI: STACK command |
| **Visual breakpoints** | ❌ | ✅ | ✅ | ✅ | Click line numbers |
| **Conditional breaks** | ❌ | ❌ | ❌ | ❌ | Not implemented |
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
| **Resizable panels** | ❌ | ❌ | ✅ | ✅ | Curses: fixed 70/30 split (not user-resizable) |
| **Themes** | ❌ | ❌ | ⚠️ | ✅ | Web: light/dark |
| **Font options** | ❌ | ❌ | ✅ | ✅ | |

## Detailed UI Descriptions

### CLI (Command Line Interface)

**Best for:** Purists, automation, testing, classic experience

**Strengths:**
- Authentic MBASIC-80 experience
- Lightweight and fast
- Perfect for automation/scripting
- NEW debugging commands (BREAK, STEP, STACK)
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
- Find/Replace ({{kbd:find:tk}}/{{kbd:replace:tk}})
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
- Auto-completion
- Theme support
- Touch device support

## Feature Implementation Status

### Recently Added (2025-10-29)
- ✅ CLI: Debugging commands (BREAK, STEP, STACK)
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
| **Run** | {{kbd:run:cli}} | {{kbd:run:curses}} | {{kbd:run_program:tk}} | {{kbd:run:web}} |
| **Stop** | {{kbd:stop:cli}} | {{kbd:stop:curses}}/Esc | Esc | {{kbd:stop:web}} |
| **Save** | {{kbd:save:cli}} | {{kbd:save:curses}} | {{kbd:file_save:tk}} | {{kbd:save:web}} |
| **New** | {{kbd:new:cli}} | {{kbd:new:curses}} | {{kbd:file_new:tk}} | {{kbd:new:web}} |
| **Open** | {{kbd:open:cli}} | {{kbd:open:curses}} | {{kbd:file_open:tk}} | {{kbd:open:web}} |
| **Help** | {{kbd:help:cli}} | {{kbd:help:curses}} | {{kbd:help_topics:tk}} | {{kbd:help:web}} |
| **Quit** | {{kbd:quit:cli}} | {{kbd:quit:curses}} | {{kbd:file_quit:tk}} | N/A |

### Debugging Shortcuts

| Action | CLI | Curses | Tk | Web |
|--------|-----|--------|----|----|
| **Toggle Breakpoint** | {{kbd:toggle_breakpoint:cli}} | {{kbd:toggle_breakpoint:curses}} | {{kbd:toggle_breakpoint:tk}} | {{kbd:toggle_breakpoint:web}} |
| **Step** | {{kbd:step:cli}} | {{kbd:step:curses}} | Menu/Toolbar | {{kbd:step:web}} |
| **Continue** | {{kbd:continue:cli}} | {{kbd:continue:curses}} | Menu/Toolbar | {{kbd:continue:web}} |
| **Variables** | PRINT | (none) | {{kbd:toggle_variables:tk}} | {{kbd:toggle_variables:web}} |

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
- Same MBASIC-2025 interpreter

## Getting Help

- **CLI:** Type {{kbd:help:cli}} or `HELP <topic>`
- **Curses:** Press {{kbd:help:curses}} to open help browser
- **Tk:** Press {{kbd:help_topics:tk}} or use Help menu
- **Web:** Press {{kbd:help:web}} or click Help

## Reporting Issues

Found a bug or missing feature? Report at:
https://github.com/anthropics/mbasic/issues

Include:
- Which UI you're using
- What feature is affected
- Steps to reproduce
- Expected vs actual behavior