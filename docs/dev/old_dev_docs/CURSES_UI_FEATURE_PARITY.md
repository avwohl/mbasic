# Curses UI Feature Parity Project

## Overview

Bring the curses UI to feature parity with Tk/Web UIs for debugging and development features.

## Current State Comparison

### Variables Window

#### Tk UI ✅ (Reference Implementation)
- ✅ Resource usage display (memory, GOSUB/FOR/WHILE stacks)
- ✅ Sortable columns with click to sort:
  - Variable name (with sub-modes: Last Accessed, Last Written, Last Read, Name)
  - Type
  - Value
- ✅ Sort direction toggle (ascending/descending)
- ✅ Last accessed array cell display: `Array(10x10) [5,3]=42`
- ✅ Natural number formatting (integers without decimals)
- ✅ String values shown with quotes
- ✅ Three-column display: Variable | Type | Value

#### Curses UI ❌ (Missing Features)
- ✅ Resource usage display (HAS THIS)
- ❌ Sortable columns (only sorts by name alphabetically)
- ❌ No sort direction control
- ❌ No last accessed array cell tracking
- ✅ Natural number formatting (HAS THIS)
- ✅ String values with quotes (HAS THIS)
- ❌ Simple single-column display

**Missing from Curses**:
1. Sortable columns with multiple sort modes
2. Sort direction toggle
3. Last accessed array cell display
4. Multi-column tabular display

### Call Stack Window

#### Tk UI ✅
- ✅ Separate window (Ctrl+K)
- ✅ Shows GOSUB stack
- ✅ Shows FOR loops with variable, range, step
- ✅ Shows WHILE loops
- ✅ Formatted display with indentation
- ✅ Shows current values of loop variables

#### Curses UI ✅
- ✅ Separate window (Ctrl+K)
- ✅ Shows GOSUB stack
- ✅ Shows FOR loops
- ✅ Shows WHILE loops
- ✅ Formatted display

**Status**: Feature parity mostly achieved

### Debugger Controls

#### Tk UI ✅
- ✅ Step Line button (execute all statements on line)
- ✅ Step Statement button (execute one statement)
- ✅ Continue button
- ✅ Stop button
- ✅ Run button
- ✅ Menu commands for all

#### Curses UI ❌
- ✅ Step (Ctrl+T) - but which mode?
- ✅ Continue (Ctrl+G)
- ✅ Run (Ctrl+R)
- ❌ No explicit Step Line vs Step Statement distinction
- ❌ Menu shows "Step" but doesn't clarify line vs statement

**Missing from Curses**:
1. Separate Step Line and Step Statement commands
2. Clear indication of which step mode is active

### Breakpoint Management

#### Tk UI ✅
- ✅ Visual breakpoint indicators in editor (●)
- ✅ Click to toggle (Ctrl+B)
- ✅ Clear all breakpoints menu item
- ✅ Breakpoints persist in editor display

#### Curses UI ✅
- ✅ Breakpoint indicators in status column (●)
- ✅ Toggle breakpoint (Ctrl+B)
- ✅ Breakpoints persist

**Status**: Feature parity achieved

### Editor Features

#### All UIs ✅
- ✅ Line number editing in-place
- ✅ Auto-sort on line change
- ✅ Auto-scroll to sorted position
- ✅ Auto-numbering on Enter
- ✅ Syntax error indicators (?)

**Status**: Curses is the reference implementation here!

## Features to Add to Curses UI

### Phase 1: Variables Window Enhancement

#### 1.1 Add Sort Mode Cycling
**Current**: Only alphabetical by name
**Target**: Cycle through sort modes like Tk

**Implementation**:
- Add sort mode state variable
- Bind key to cycle modes (suggest: 's' for sort)
- Display current sort mode in window title or header
- Support modes:
  1. Name (alphabetical)
  2. Last Accessed (timestamp)
  3. Last Written (timestamp)
  4. Last Read (timestamp)
  5. Type
  6. Value

**UI Indication**:
```
Variables (Sort: Last Accessed ↓) (Ctrl+W to toggle)
```

#### 1.2 Add Sort Direction Toggle
**Key binding**: 'd' for direction (or arrow keys)
**Display**: Show ↑ or ↓ in header

#### 1.3 Add Last Accessed Array Cell Display
**Current**: `A%           = Array(10x10)`
**Target**: `A%           = Array(10x10) [5,3]=42`

**Implementation**:
- Runtime already tracks this in `last_accessed_subscripts` and `last_accessed_value`
- Just need to format it in curses display

#### 1.4 Add Multi-Column Display (Optional)
**Current**: Single column format
**Target**: Three columns like Tk

**Consideration**: Terminal width constraints make this challenging
**Alternative**: Keep current format, just add sorting and array cell info

### Phase 2: Debugger Controls

#### 2.1 Add Step Line Command
**New key**: Ctrl+L (Step Line)
**Keep**: Ctrl+T (Step Statement)
**Update menu**: Show both commands

**Implementation**:
```python
elif key == 'ctrl l':
    # Step line mode
    state = self.interpreter.tick(mode='step_line', max_statements=100)
```

#### 2.2 Update Help/Menu Display
Show both step commands clearly:
```
Step Statement  Ctrl+T        Step Line       Ctrl+L
Continue        Ctrl+G        Stop            Ctrl+X
```

### Phase 3: Minor Enhancements

#### 3.1 Add Toolbar/Button Bar (Optional)
Like Tk toolbar but text-based:
```
[Run] [Stop] [Step Line] [Step Stmt] [Cont] [Vars] [Stack]
```

**Challenge**: Screen real estate
**Alternative**: Keep current menu-driven approach

## Implementation Plan

### Task Tracking

**Status Legend**: ⬜ Not Started | 🟨 In Progress | ✅ Completed

#### Phase 1: Variables Window Enhancement
- ✅ 1.1 Add sort mode state variables
- ✅ 1.2 Implement sort mode cycling (key: 's')
- ✅ 1.3 Add sort direction toggle (key: 'd')
- ✅ 1.4 Implement accessed timestamp sort
- ✅ 1.5 Implement written timestamp sort
- ✅ 1.6 Implement read timestamp sort
- ✅ 1.7 Implement type sort
- ✅ 1.8 Implement value sort
- ✅ 1.9 Add last accessed array cell display
- ✅ 1.10 Update window header to show sort mode/direction

#### Phase 2: Debugger Controls
- ✅ 2.1 Add Ctrl+L keybinding for Step Line (context-sensitive with List)
- ✅ 2.2 Keep Ctrl+T for Step Statement
- ✅ 2.3 Update menu/help display to show both
- ⬜ 2.4 Test both step modes

#### Phase 3: Testing
- ⬜ 3.1 Test all sort modes
- ⬜ 3.2 Test sort direction toggle
- ⬜ 3.3 Test array cell display
- ⬜ 3.4 Test step line vs step statement
- ⬜ 3.5 Compare with Tk UI behavior
- ⬜ 3.6 Performance test with many variables

#### Phase 4: Documentation
- ⬜ 4.1 Update curses UI help
- ⬜ 4.2 Update quick reference
- ⬜ 4.3 Document new keybindings
- ⬜ 4.4 Update CLAUDE.md with new features

## Implementation Details

### Variables Window Sorting

#### Current Code (src/ui/curses_ui.py:2067-2068)
```python
# Sort by name for consistent display
variables.sort(key=lambda v: v['name'] + v['type_suffix'])
```

#### Enhanced Code
```python
# Sort based on current mode
if self.variables_sort_mode == 'name':
    sort_key = lambda v: v['name'] + v['type_suffix']
elif self.variables_sort_mode == 'accessed':
    def accessed_key(v):
        read_ts = v['last_read']['timestamp'] if v.get('last_read') else 0
        write_ts = v['last_write']['timestamp'] if v.get('last_write') else 0
        return max(read_ts, write_ts)
    sort_key = accessed_key
elif self.variables_sort_mode == 'written':
    sort_key = lambda v: v['last_write']['timestamp'] if v.get('last_write') else 0
elif self.variables_sort_mode == 'read':
    sort_key = lambda v: v['last_read']['timestamp'] if v.get('last_read') else 0
elif self.variables_sort_mode == 'type':
    sort_key = lambda v: v['type_suffix']
elif self.variables_sort_mode == 'value':
    def value_key(v):
        if v['is_array']:
            return (2, 0, '')
        elif v['type_suffix'] == '$':
            return (1, 0, str(v['value']).lower())
        else:
            try:
                return (0, float(v['value']), '')
            except (ValueError, TypeError):
                return (0, 0, '')
    sort_key = value_key

variables.sort(key=sort_key, reverse=self.variables_sort_reverse)
```

### Array Cell Display

#### Current Code (src/ui/curses_ui.py:2074-2077)
```python
if var['is_array']:
    # Array: show dimensions
    dims = 'x'.join(str(d) for d in var['dimensions'])
    line = f"{name:12} = Array({dims})"
```

#### Enhanced Code
```python
if var['is_array']:
    # Array: show dimensions and last accessed cell
    dims = 'x'.join(str(d) for d in var['dimensions'])

    # Check if we have last accessed info
    if var.get('last_accessed_subscripts') and var.get('last_accessed_value') is not None:
        subs = var['last_accessed_subscripts']
        last_val = var['last_accessed_value']

        # Format value
        if var['type_suffix'] != '$' and isinstance(last_val, (int, float)) and last_val == int(last_val):
            last_val_str = str(int(last_val))
        elif var['type_suffix'] == '$':
            last_val_str = f'"{last_val}"'
        else:
            last_val_str = str(last_val)

        subs_str = ','.join(str(s) for s in subs)
        line = f"{name:12} = Array({dims}) [{subs_str}]={last_val_str}"
    else:
        line = f"{name:12} = Array({dims})"
```

### Key Bindings

#### New Bindings to Add
```python
# In _handle_input() method
elif key == 's' and self.watch_window_visible:
    # Cycle sort mode in variables window
    self._cycle_variables_sort_mode()

elif key == 'd' and self.watch_window_visible:
    # Toggle sort direction in variables window
    self._toggle_variables_sort_direction()

elif key == 'ctrl l':
    # Step line
    self._step_line()
```

#### Methods to Add
```python
def _cycle_variables_sort_mode(self):
    """Cycle through variable sort modes."""
    modes = ['name', 'accessed', 'written', 'read', 'type', 'value']
    try:
        current_idx = modes.index(self.variables_sort_mode)
        next_idx = (current_idx + 1) % len(modes)
    except ValueError:
        next_idx = 0

    self.variables_sort_mode = modes[next_idx]
    self._update_variables_window()

    mode_names = {
        'name': 'Name',
        'accessed': 'Last Accessed',
        'written': 'Last Written',
        'read': 'Last Read',
        'type': 'Type',
        'value': 'Value'
    }
    self.status_bar.set_text(f"Sorting variables by: {mode_names[self.variables_sort_mode]}")

def _toggle_variables_sort_direction(self):
    """Toggle variable sort direction."""
    self.variables_sort_reverse = not self.variables_sort_reverse
    self._update_variables_window()
    direction = "descending" if self.variables_sort_reverse else "ascending"
    self.status_bar.set_text(f"Sort direction: {direction}")

def _step_line(self):
    """Execute all statements on current line."""
    if not self.interpreter:
        self.status_bar.set_text("No program running")
        return

    state = self.interpreter.tick(mode='step_line', max_statements=100)
    # ... handle state like existing _step() method
```

## Success Criteria

✅ Curses variables window supports all sort modes (name, accessed, written, read, type, value)
✅ Sort direction toggleable (ascending/descending)
✅ Arrays show last accessed cell and value
✅ Clear visual indication of current sort mode
✅ Separate Step Line (Ctrl+L) and Step Statement (Ctrl+T) commands
✅ Updated help/menu displays
✅ Feature parity with Tk UI for debugging
✅ No performance degradation
✅ Consistent behavior across all UIs

## Configuration

Add to curses UI state variables:
```python
# In CursesBackend.__init__()
self.variables_sort_mode = 'name'  # 'name', 'accessed', 'written', 'read', 'type', 'value'
self.variables_sort_reverse = False  # False=ascending, True=descending
```

## Known Issues to Check

### Line Number Formatting and Statement Highlighting

**Issue discovered in Tk UI (2025-10-26)**: Statement highlighting was off by one character because the code was trying to add leading spaces formatting to line numbers, which breaks MBASIC compatibility.

**What was wrong in Tk UI**:
- Attempted to format lines with leading spaces: `f"{line_num:>5} {code}"`
- Example: "20 PRINT I" → "   20 PRINT I" (added 3 leading spaces)
- This broke:
  1. Compatibility with real MBASIC (saved files would have wrong spacing)
  2. Consistency across UIs (different UIs would display differently)
  3. Loop indent nesting (would look different with artificial spacing)
  4. Statement highlighting (char positions didn't account for leading spaces)

**Correct approach**:
- Store lines exactly as entered: "20 PRINT I" (no leading spaces)
- Display lines exactly as stored: "20 PRINT I"
- char_start/char_end from parser are relative to the stored text
- Don't add any formatting that changes line structure

**TODO for Curses UI**: ⬜ NOT CHECKED YET
- [ ] Verify curses UI doesn't add leading spaces to line numbers
- [ ] Check if statement highlighting works correctly
- [ ] Test with breakpoints - does highlighting show correct characters?
- [ ] Verify lines saved from curses UI load correctly in real MBASIC
- [ ] Check consistency: curses display = stored text = saved file

**Location to check**: `src/ui/curses_ui.py`
- ProgramEditorWidget - line formatting/display
- Statement highlighting code
- Line saving/loading code

**Test case**:
1. Enter "20 PRINT I" in curses UI
2. Set breakpoint and run
3. When stopped, verify "PRINT I" is highlighted (not "RINT I" or wrong chars)
4. Save program and verify no extra leading spaces in file
5. Load file in real MBASIC and verify it looks the same

## Future Enhancements

### Advanced Sorting
- Multi-level sorting (primary + secondary sort key)
- Custom sort orders saved in config
- Filter variables by type or pattern

### Visual Improvements
- Color-code variables by type
- Highlight recently changed variables
- Show change indicators (↑ increased, ↓ decreased)

### Performance
- Lazy loading for large variable sets
- Virtual scrolling for thousands of variables
- Incremental updates (only changed variables)

## References

- Tk UI implementation: `src/ui/tk_ui.py:696-786`
- Current curses variables: `src/ui/curses_ui.py:2036-2088`
- Runtime variable tracking: `src/runtime.py`
