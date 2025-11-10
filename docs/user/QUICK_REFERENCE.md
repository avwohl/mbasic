# MBASIC Curses IDE - Quick Reference Card

> **Note:** This reference uses `{{kbd:command}}` notation for keyboard shortcuts (e.g., `{{kbd:run}}` is typically `^R` for Ctrl+R). Actual key mappings are configurable. To see your current key bindings, press the Help key or check `~/.mbasic/curses_keybindings.json` for the full list of default and customized keys.

## Starting the IDE
```bash
python3 mbasic --ui curses [filename.bas]
```

## Editor Commands

| Key | Command | Description |
|-----|---------|-------------|
| `{{kbd:new}}` | New | Clear program, start fresh |
| `{{kbd:open}}` | Load | Load program from file |
| `{{kbd:save}}` | Save | Save program to file |
| `{{kbd:quit}}` | Quit | Exit IDE |
| `{{kbd:help}}` | Help | Open help browser |
| `ESC` | Menu | Open/close menu bar |
| Arrow Keys | Navigate | Move cursor in editor |

## Running Programs

| Key | Command | Description |
|-----|---------|-------------|
| `{{kbd:run}}` | Run | Execute current program |

## Breakpoint Debugging

### Setting Breakpoints
| Key | Command | Description |
|-----|---------|-------------|
| `b` or `F9` | Toggle | Set/clear breakpoint on current line |

Visual indicator: `●` appears next to line number

### At a Breakpoint

Status shows: `BREAKPOINT at line XX - Press 'c' continue, 's' step, 'e' end`

| Key | Command | What Happens |
|-----|---------|--------------|
| `c` or `C` | **Continue** | Run until next breakpoint or end |
| `s` or `S` | **Step** | Execute one line, stop at next |
| `e` or `E` | **End** | Stop execution immediately |
| `ESC` | **End** | Stop execution immediately |

## Screen Layout

```
┌──────────────────────────────────────────┐
│ Menu Bar (ESC to activate)               │
├──────────────────────────────────────────┤
│                                          │
│  Editor Window (70%)                     │
│  - Edit your BASIC program here          │
│  - ● markers show breakpoints            │
│                                          │
│                                          │
├──────────────────────────────────────────┤
│                                          │
│  Output Window (30%)                     │
│  - Shows program output                  │
│  - Shows errors                          │
│                                          │
└──────────────────────────────────────────┘
```

## Typical Workflows

### 1. Write and Run
```
1. Type program in editor
2. {{kbd:run}} to run
3. Check output window
```

### 2. Debug with Breakpoints
```
1. Set breakpoints on key lines (press 'b')
2. {{kbd:run}} to run
3. At each breakpoint:
   - Press 'c' to continue to next breakpoint
   - Press 's' to step through line-by-line
   - Press 'e' to stop
```

### 3. Load, Edit, Save
```
1. {{kbd:open}} to load existing .bas file
2. Edit in editor window
3. {{kbd:run}} to test
4. {{kbd:save}} to save changes
```

## Help System

| Key | Where | What |
|-----|-------|------|
| `{{kbd:help}}` | Anywhere | Open help browser |
| Arrow Keys | In help | Scroll up/down |
| `Space` | In help | Page down |
| `B` | In help | Page up |
| `Enter` | In help | Follow link |
| `U` | In help | Go back/up |
| `Q` or `ESC` | In help | Exit help |

### Help Topics
- Keyboard Shortcuts
- BASIC Language Reference
- Examples

## Debugging Strategy Guide

### Quick Testing (No Breakpoints)
```
{{kbd:run}} → Watch output → Done
```

### Checkpoint Debugging
```
Set breakpoints at phase boundaries
↓
{{kbd:run}} to start
↓
Press 'c' at each breakpoint to jump to next phase
↓
Verify output at each checkpoint
```

### Detailed Investigation
```
Set breakpoint before problem area
↓
{{kbd:run}} to start
↓
Press 'c' to get to breakpoint
↓
Press 's' to step through suspect code
↓
Press 'e' when done
```

### Loop Analysis
```
Set breakpoint at loop start
↓
{{kbd:run}} to start
↓
Press 's' to watch first few iterations
↓
Press 'c' to let rest complete
```

## Tips

✓ **Multiple breakpoints**: Set as many as you need
✓ **Toggle freely**: Press 'b' to add/remove anytime (before running)
✓ **Continue is your friend**: Use 'c' to skip over working code
✓ **Step when uncertain**: Use 's' only in problem areas
✓ **Watch the output**: Output window updates as program runs
✓ **Use help**: Press {{kbd:help}} anytime for full documentation

## Common Issues

**Problem**: Breakpoint not stopping
- **Solution**: Make sure ● is visible next to line number

**Problem**: Can't type in editor
- **Solution**: Press ESC to exit menu mode

**Problem**: Output not visible
- **Solution**: Output window is at bottom; scroll if needed

**Problem**: Pressed 's', now every line stops
- **Solution**: Press 'c' to exit step mode

## Examples

See example programs in the `basic/` directory of the MBASIC installation.

## More Information

- Press {{kbd:help}} within the Curses UI to access the built-in help system
- See `docs/help/` directory for full help documentation
- Visit [CHOOSING_YOUR_UI.md](CHOOSING_YOUR_UI.md) for UI comparison and selection guide

---
**Pro Tip**: Start every debugging session with strategic breakpoints, then use 'c' to jump between them. Only switch to 's' (step) when you find something interesting!
