# TK UI Feature Audit - Comprehensive Reference

**Date:** 2025-10-28  
**File:** `src/ui/tk_ui.py` (3400+ lines)  
**Purpose:** Complete inventory of all features in the TK UI implementation

This document serves as the authoritative reference for what the TK UI currently supports. Use it when:
- Updating the curses UI to match functionality
- Writing documentation
- Planning new features
- Debugging issues

---

## 1. MENU SYSTEM

### 1.1 File Menu
| Menu Item | Keyboard Shortcut | Function | Method |
|-----------|------------------|----------|---------|
| New | Ctrl+N (configurable) | Clear program, start fresh | `_menu_new()` |
| Open... | Ctrl+O (configurable) | Open file dialog, load program | `_menu_open()` |
| **Recent Files** | (submenu) | List of recently opened files (max 10) | `_update_recent_files_menu()` |
| Save | Ctrl+S (configurable) | Save to current file or prompt | `_menu_save()` |
| Save As... | None | Save to new file | `_menu_save_as()` |
| Exit | Ctrl+Q (configurable) | Quit application | `_menu_exit()` |

**Recent Files Features:**
- Displays up to 10 most recent files
- Shows short filename with tooltip for full path
- "(No recent files)" placeholder when empty
- "Clear Recent Files" option at bottom
- Auto-removes deleted/missing files on access
- Managed by `RecentFilesManager` class (in src/ui/recent_files.py)

### 1.2 Edit Menu
| Menu Item | Keyboard Shortcut | Function | Method |
|-----------|------------------|----------|---------|
| Cut | Ctrl+X | Cut selected text | `_menu_cut()` |
| Copy | Ctrl+C | Copy selected text | `_menu_copy()` |
| Paste | Ctrl+V | Paste from clipboard | `_menu_paste()` |
| Insert Line | Ctrl+I | Smart insert blank line | `_smart_insert_line()` |
| Toggle Breakpoint | Ctrl+B | Toggle breakpoint on current line | `_toggle_breakpoint()` |
| Clear All Breakpoints | None | Remove all breakpoints | `_clear_all_breakpoints()` |
| Settings... | None | Open settings dialog | `_menu_settings()` |

### 1.3 Run Menu
| Menu Item | Keyboard Shortcut | Function | Method |
|-----------|------------------|----------|---------|
| Run Program | Ctrl+R (configurable) | Parse and run program | `_menu_run()` |
| Step Line | None | Execute one full line | `_menu_step_line()` |
| Step Statement | None | Execute one statement | `_menu_step()` |
| Continue | None | Resume execution | `_menu_continue()` |
| Stop | None | Stop execution | `_menu_stop()` |
| List Program | None | Output program listing | `_menu_list()` |
| Clear Output | None | Clear output pane | `_menu_clear_output()` |

### 1.4 View Menu
| Menu Item | Keyboard Shortcut | Function | Method |
|-----------|------------------|----------|---------|
| Variables | Ctrl+W | Toggle variables window | `_toggle_variables()` |
| Execution Stack | Ctrl+K | Toggle stack window | `_toggle_stack()` |

### 1.5 Help Menu
| Menu Item | Keyboard Shortcut | Function | Method |
|-----------|------------------|----------|---------|
| Help Topics | Ctrl+H (configurable) | Open help browser | `_menu_help()` |
| About | None | Show about dialog | `_menu_about()` |

---

## 2. TOOLBAR

Toolbar provides quick access to common operations:

| Button | Function | Method |
|--------|----------|---------|
| New | Clear program | `_menu_new()` |
| Open | Open file | `_menu_open()` |
| Save | Save file | `_menu_save()` |
| Run | Run program | `_menu_run()` |
| Stop | Stop execution | `_menu_stop()` |
| Step | Step one line | `_menu_step_line()` |
| Stmt | Step one statement | `_menu_step()` |
| Cont | Continue execution | `_menu_continue()` |

---

## 3. EDITOR FEATURES

### 3.1 Core Editor Widget
- **Type:** `LineNumberedText` custom widget (`src/ui/tk_widgets.py`)
- **Layout:** Status column (20px) + text editor + scrollbars
- **Font:** Courier 10pt
- **Undo/Redo:** Enabled (Tk native, unlimited)

### 3.2 Status Column Indicators
| Symbol | Meaning | Color | Priority |
|--------|---------|-------|----------|
| ● | Breakpoint set | Blue | Low |
| ? | Parse/syntax error | Red | High |
| (space) | Normal line | Gray | N/A |

**Status Priority:** Errors (?) always override breakpoints (●)

**Interaction:**
- Click on ● or ? shows info popup
- Use Ctrl+B to toggle breakpoints

### 3.3 Auto-Numbering System

**Configuration:**
- `auto_number_enabled`: Default `True`
- `auto_number_start`: Default `10`
- `auto_number_increment`: Default `10`

**Behavior:**
- Press Enter on a line to auto-number and sort
- If line has no number, validates as BASIC first
- If invalid BASIC, moves to next line without numbering
- Automatically sorts lines numerically after Enter
- Calculates next line number intelligently:
  - At end: current + increment
  - In middle: tries current + increment if room
  - No room: calculates midpoint
  - No midpoint: offers to renumber program

**Smart Features:**
- Blank lines (number only) are deleted on Enter
- Validates syntax before adding number
- Maintains cursor position after sort
- Prevents creation of blank lines

### 3.4 Smart Insert Line (Ctrl+I)

**Purpose:** Insert a blank numbered line between current and next line

**Algorithm:**
1. Parse current line number
2. Find previous line number
3. Calculate midpoint between prev and current
4. If no room, offer to renumber
5. Insert blank line with calculated number
6. Position cursor ready for typing

**Implementation:** `_smart_insert_line()` uses `ui_helpers.calculate_midpoint()`

### 3.5 Auto-Sort on Navigation

**Triggers:**
- Arrow keys (Up/Down)
- Page Up/Page Down
- Mouse click
- Focus out

**Behavior:**
- Detects line change via `_check_line_change()`
- Saves editor to program (filters blank lines)
- Refreshes editor (sorted)
- Attempts to restore cursor to same line number

**Purpose:** Ensures editor is always sorted when moving between lines

### 3.6 Syntax Validation

**Real-Time Validation:**
- Triggered after cursor movement or mouse click
- Validates each numbered line independently
- Shows red ? indicator on error lines
- Displays error message on status column click
- Updates status bar with error count
- Does NOT block editing (errors shown, not enforced)

**Error Display:**
- Status column: Red ? on error lines
- Status bar: "Syntax error(s) in program - cannot run"
- Output pane: List of errors (when multiple)
- Click on ?: Shows error detail popup

**Implementation:** `_validate_editor_syntax()`, `_check_line_syntax()`

### 3.7 Input Sanitization

**Paste Handling:**
- Intercepts all paste operations
- Clears high-bit parity (8th bit)
- Removes control characters
- Shows status message if modified
- Multi-line paste: Auto-numbers unnumbered lines
- Single-line paste: Inline insertion

**Key Press Filtering:**
- Validates each character with `is_valid_input_char()`
- Blocks invalid control characters
- Allows: printable ASCII, Tab, Enter, Backspace, Delete, arrows
- Preserves Ctrl+key shortcuts

**Implementation:** `_on_paste()`, `_on_key_press()`

### 3.8 Blank Line Prevention

**Philosophy:** Editor MUST NEVER contain blank lines

**Enforcement:**
- Blank lines removed on cursor movement (`_on_cursor_move()`)
- Blank lines removed when saving to program
- Enter on blank numbered line deletes the line
- Paste operations filter out blank lines

### 3.9 Context Menu (Right-Click)

**On Editor:**
- Cut (when text selected)
- Copy (when text selected)
- Paste (always enabled)
- Select All

**Implementation:** `_setup_editor_context_menu()`

---

## 4. EXECUTION FEATURES

### 4.1 Tick-Based Execution

**Architecture:**
- Uses `Interpreter.tick()` for non-blocking execution
- Executes max 100 statements per tick
- Schedules next tick with `root.after(1)`
- Allows UI to remain responsive

**State Machine:**
```
'running' → 'paused' / 'at_breakpoint' / 'done' / 'error'
```

**Implementation:** `_execute_tick()`

### 4.2 Breakpoints

**Features:**
- Toggle with Ctrl+B on any line
- Visual indicator: Blue ● in status column
- Stored in `self.breakpoints` set
- Synced with interpreter state
- Clear all breakpoints option

**Breakpoint Behavior:**
- Execution pauses BEFORE statement on breakpoint line
- Status: "Paused at line X"
- Yellow highlight shows next statement
- Variables and stack windows update

### 4.3 Stepping Modes

**Step Line:** Execute entire line (all statements)
- Method: `_menu_step_line()`
- Uses `interpreter.tick(mode='step_line')`

**Step Statement:** Execute single statement
- Method: `_menu_step()`  
- Uses `interpreter.tick(mode='step')`

**Both Modes:**
- Pause after step
- Update variables/stack windows
- Highlight next statement
- Status shows "Paused at line X"

### 4.4 Statement Highlighting

**Purpose:** Show which statement is executing/next

**Visual:**
- Yellow background (#ffeb3b)
- Black text
- Exact character range highlighted

**When Active:**
- Stepping (line or statement)
- Paused at breakpoint
- At error (shows error statement)

**Cleared When:**
- Execution resumes
- Program stops
- User clicks in editor (allows text selection)

**Implementation:** `_highlight_current_statement()`, `_clear_statement_highlight()`

### 4.5 Execution States

| State | Status Text | Immediate Mode | Behavior |
|-------|-------------|----------------|----------|
| Ready | "Ready" | Enabled (green) | Can run program |
| Running | "Running..." | Disabled (red) | Program executing |
| Paused | "Paused at line X" | Enabled (yellow) | Can step/continue |
| At Breakpoint | "Paused at line X" | Enabled (yellow) | Can step/continue |
| Error | "Error at line X" | Enabled (yellow) | Can edit & continue |

**Prompt Color:**
- Green "Ok >": Ready to execute
- Red "Ok >": Program running (immediate disabled)
- Yellow "Ok >": Paused/error (immediate enabled, program state accessible)

### 4.6 Error Handling

**On Error:**
1. Stop execution (set `running = False`)
2. Show error message in output
3. Update status: "Error at line X - Edit and Continue, or Stop"
4. Highlight error statement (yellow)
5. Show red ? in status column
6. Allow editing to fix error
7. Continue button retries from error point

**Error Recovery:**
- User can edit the error line
- Press Continue to retry
- Press Stop to end program
- Variables/stack remain accessible

---

## 5. VARIABLES WINDOW (Ctrl+W)

### 5.1 Window Layout

**Components:**
1. Resource usage label (top)
2. Filter entry field
3. Edit button
4. Treeview with 3 columns: Variable, Value, Type

**Geometry:** 400x400px, resizable

### 5.2 Variable Display

**Columns:**
- **Variable:** Name with type suffix (A%, NAME$, X)
- **Value:** Current value (formatted by type)
- **Type:** Integer, String, Single, Double, Array(dims)

**Array Display:**
- Format: `A%(10x10) [5,3]=42`
- Shows dimensions
- Shows last accessed element and value

### 5.3 Sorting System

**Sort Columns:**
- `'accessed'`: Last accessed timestamp (default)
- `'written'`: Last written timestamp
- `'read'`: Last read timestamp  
- `'name'`: Alphabetical by name
- `'type'`: By type suffix
- `'value'`: By value (string comparison)

**Sort Direction:**
- Default: Descending (newest first for timestamps)
- Click arrow area (left 20px): Toggle direction
- Click heading text: Change sort column

**Visual Indicators:**
- ↓ : Descending
- ↑ : Ascending
- Appears in heading of current sort column

**Column Cycling (Variable column only):**
1. Last Accessed (default)
2. Last Written
3. Last Read
4. Name (alphabetical)

**Implementation:** `_on_variable_heading_click()`, `_sort_variables_by()`, `_cycle_variable_sort()`

### 5.4 Filtering

**Features:**
- Type in filter box to search
- Filters variable names (case-insensitive)
- Updates in real-time (KeyRelease)
- Shows only matching variables

**Implementation:** `_on_variable_filter_change()`

### 5.5 Variable Editing

**Triggers:**
- Double-click on variable
- Select variable + click Edit button

**Simple Variables:**
- String: Text input dialog
- Integer: Integer spinbox dialog
- Float: Text input with validation

**Array Variables:**
- Custom dialog with:
  - Subscripts entry (e.g., "1,2,3")
  - Current value display (updates on subscript change)
  - New value entry
  - Shows array dimensions

**Implementation:** `_edit_simple_variable()`, `_edit_array_element()`, `_edit_selected_variable()`

### 5.6 Resource Usage Display

**Shows:**
- Variable count
- Array count
- String space used
- DATA pointer position (if applicable)

**Format:** "Vars: 5, Arrays: 2, Strings: 120 bytes, DATA: line 100"

**Implementation:** `_update_variables()`

---

## 6. EXECUTION STACK WINDOW (Ctrl+K)

### 6.1 Window Layout

**Components:**
- Treeview with 2 columns: Frame, Location

**Geometry:** 400x300px, resizable

### 6.2 Stack Display

**Columns:**
- **Frame:** Type of stack frame
- **Location:** Line number or description

**Frame Types:**
- `GOSUB → line X`: Subroutine call
- `FOR I = 1 TO 10`: FOR loop
- `WHILE condition`: WHILE loop
- `Function call`: User-defined functions (future)

**Order:** Most recent frame at top

**Purpose:**
- Debug infinite loops
- Understand call hierarchy
- See FOR/WHILE nesting

**Implementation:** `_create_stack_window()`, `_update_stack()`

---

## 7. OUTPUT PANE

### 7.1 Features

- **Widget:** ScrolledText (read-only)
- **Font:** Courier 10pt
- **Auto-scroll:** Always shows latest output
- **Word wrap:** Enabled

### 7.2 Context Menu (Right-Click)

**Options:**
- Copy (when text selected)
- Select All

**Implementation:** `_setup_output_context_menu()`

### 7.3 Output Sources

- Program PRINT statements
- Error messages
- Status messages (program start/stop/pause)
- Breakpoint notifications
- LIST command output

---

## 8. IMMEDIATE MODE

### 8.1 UI Layout

**Components:**
- Prompt label: "Ok >" (colored by state)
- Entry field: Single-line input
- Execute button

**No History Display:** History removed in favor of minimal design

### 8.2 Prompt States

| State | Color | Meaning |
|-------|-------|---------|
| Green | Ready | No program running, can execute |
| Red | Running | Program running, immediate disabled |
| Yellow | Paused | Program paused, can access program state |

### 8.3 Features

- Enter key executes command
- Uses same runtime as program
- Access to program variables when paused
- Tab completion (future)

### 8.4 Context Menu (Right-Click)

**Options:**
- Cut
- Copy  
- Paste
- Select All

**Implementation:** Inline in `start()`

### 8.5 Immediate Executor

**Architecture:**
- Separate `ImmediateExecutor` instance
- Shares runtime with program interpreter
- Uses `OutputCapturingIOHandler`
- Results appear in output pane

**Commands:**
- BASIC statements (PRINT, A=5, etc.)
- System commands (LIST, FILES, etc.)
- Can modify program state when paused

---

## 9. FILE MANAGEMENT

### 9.1 Auto-Save System

**Features:**
- Auto-saves every 30 seconds (configurable)
- Managed by `AutoSaveManager` class
- Stores in user's cache directory
- Recovery prompt on open if autosave newer
- Cleans up old autosaves (7+ days) on exit

**Recovery Dialog:**
- Shows modification times
- Shows file sizes
- Yes: Load autosave
- No: Load original file

**Implementation:**
- `AutoSaveManager` in `src/ui/auto_save.py`
- `auto_save.start_autosave()`, `auto_save.stop_autosave()`

### 9.2 Recent Files

**Features:**
- Tracks up to 10 recent files
- Stored in user's config directory
- Displays in File > Recent Files submenu
- Auto-removes missing files on access
- Clear recent files option

**Implementation:**
- `RecentFilesManager` in `src/ui/recent_files.py`
- `recent_files.add_file()`, `recent_files.get_recent_files()`

### 9.3 File Dialogs

**Open:**
- Native Tk file dialog
- Filters: *.bas, *.*
- Checks for autosave recovery

**Save As:**
- Native Tk file dialog
- Default extension: .bas
- Filters: *.bas, *.*

---

## 10. SETTINGS SYSTEM

### 10.1 Settings Dialog

**Window:** Modal dialog, 700x600px

**Layout:**
- Notebook with category tabs
- Scrollable settings per tab
- Buttons: OK, Cancel, Apply, Reset to Defaults

**Categories:**
- Editor
- Interpreter
- Keywords
- Variables
- UI

**Implementation:** `TkSettingsDialog` in `src/ui/tk_settings_dialog.py`

### 10.2 Setting Types

**Boolean:**
- Rendered as checkbox

**Integer:**
- Rendered as spinbox (0-1000)

**String:**
- Rendered as text entry

**Enum:**
- Rendered as dropdown (read-only combobox)

### 10.3 Setting Scopes

- **GLOBAL:** Saved to config file
- **SESSION:** Lost on exit
- **PROGRAM:** Saved with program (future)

---

## 11. HELP SYSTEM

### 11.1 Help Browser

**Window:** 900x700px, non-modal

**Features:**
- Back button (navigation history)
- Home button
- Search entry + Search button
- In-page search (Ctrl+F)
- Clickable links
- Status bar

**Implementation:** `TkHelpBrowser` in `src/ui/tk_help_browser.py`

### 11.2 Three-Tier Help System

**Tiers:**
1. **Language** (📕): BASIC language reference
2. **MBASIC** (📗): MBASIC-specific features
3. **UI** (📘): UI-specific help

**Search:**
- Searches all tiers
- Ranks by tier and relevance
- Fuzzy matching
- Pre-built search indexes

### 11.3 In-Page Search (Ctrl+F)

**Features:**
- Find next/previous
- Match counter ("3/10")
- Yellow highlight on matches
- Orange highlight on current match
- Escape to close

**Implementation:** `_inpage_search_show()`, `_inpage_find_next()`, etc.

### 11.4 Markdown Rendering

**Supported:**
- Headers (# ## ###)
- Bold, italic (limited)
- Code blocks (```...```)
- Inline code (`...`)
- Links `[text](url)` syntax
- Bullet lists

**Macros:**
- `{{KEY(name)}}`: Keyboard shortcut display
- `{{INCLUDE(file)}}`: Include another file

---

## 12. KEYBOARD SHORTCUTS SUMMARY

### 12.1 Configurable Shortcuts

Loaded from `config/keybindings/tk.json`:

| Action | Default | Config Key |
|--------|---------|------------|
| File New | Ctrl+N | menu.file_new |
| File Open | Ctrl+O | menu.file_open |
| File Save | Ctrl+S | menu.file_save |
| File Quit | Ctrl+Q | menu.file_quit |
| Run Program | Ctrl+R | menu.run_program |
| Help Topics | Ctrl+H | menu.help_topics |

### 12.2 Fixed Shortcuts

Not in config file:

| Shortcut | Action | Location |
|----------|--------|----------|
| Ctrl+X | Cut | Edit menu |
| Ctrl+C | Copy | Edit menu |
| Ctrl+V | Paste | Edit menu |
| Ctrl+I | Insert Line | Edit menu, editor |
| Ctrl+B | Toggle Breakpoint | Edit menu, editor |
| Ctrl+W | Variables Window | View menu |
| Ctrl+K | Execution Stack | View menu |
| Ctrl+F | Find in Page | Help browser |
| Enter | Auto-number & sort | Editor |

### 12.3 Special Keys

**Editor:**
- Arrow keys: Navigate + auto-sort on line change
- Page Up/Down: Navigate + auto-sort on line change
- Enter: Auto-number current line, sort, move to next
- Tab: Allowed (not intercepted)

**Immediate Mode:**
- Enter: Execute command
- Ctrl+C/X/V: Cut/copy/paste

---

## 13. ADVANCED FEATURES

### 13.1 Command Methods (Inherited from UIBackend)

These implement system commands:

| Method | Purpose |
|--------|---------|
| `cmd_run()` | RUN - Execute program |
| `cmd_list(args)` | LIST - Show program listing |
| `cmd_new()` | NEW - Clear program |
| `cmd_save(filename)` | SAVE - Save to file |
| `cmd_load(filename)` | LOAD - Load from file |
| `cmd_merge(filename)` | MERGE - Merge program |
| `cmd_delete(args)` | DELETE - Delete line range |
| `cmd_renum(args)` | RENUM - Renumber lines |
| `cmd_cont()` | CONT - Continue execution |
| `cmd_files(filespec)` | FILES - List directory |

### 13.2 TkIOHandler

**Purpose:** Bridge between interpreter and UI

**Methods:**
- `print_line(text)`: Output to output pane
- `input_line(prompt)`: Show input dialog
- `input_char(blocking)`: Character input (future)

**Implementation:** `TkIOHandler` class at end of tk_ui.py

### 13.3 Keybinding Loader

**Purpose:** Load keyboard shortcuts from config

**Features:**
- Per-UI configuration (tk.json, curses.json, etc.)
- Fallback to defaults
- Platform-specific modifiers (Cmd on Mac)
- `get_tk_accelerator()`: Returns menu display string
- `bind_all_to_tk()`: Binds shortcut to callback

**Implementation:** `KeybindingLoader` in `src/ui/keybinding_loader.py`

---

## 14. STATE MANAGEMENT

### 14.1 Execution State Variables

```python
self.running = False              # Program executing?
self.paused_at_breakpoint = False # Paused?
self.breakpoints = set()          # Line numbers with breakpoints
self.tick_timer_id = None         # Pending tick callback
```

### 14.2 Variables Window State

```python
self.variables_window = None      # Toplevel window
self.variables_tree = None        # Treeview widget
self.variables_visible = False    # Window shown?
self.variables_sort_column = 'accessed'  # Current sort
self.variables_sort_reverse = True       # Sort direction
self.variables_filter_text = ""   # Filter string
```

### 14.3 Editor State

```python
self.last_edited_line_index = None  # For auto-sort
self.last_edited_line_text = None   # For change detection
self.auto_number_enabled = True     # Auto-numbering on?
self.auto_number_start = 10         # Starting number
self.auto_number_increment = 10     # Increment
```

---

## 15. WIDGET HIERARCHY

```
root (Tk)
├── menubar (Menu)
│   ├── File menu
│   ├── Edit menu
│   ├── Run menu
│   ├── View menu
│   └── Help menu
├── toolbar (Frame)
│   └── Buttons
├── paned (PanedWindow - vertical)
│   ├── editor_frame (60% weight)
│   │   └── editor_text (LineNumberedText)
│   │       ├── canvas (status column)
│   │       ├── text (Text widget)
│   │       ├── vsb (Scrollbar)
│   │       └── hsb (Scrollbar)
│   ├── output_frame (30% weight)
│   │   └── output_text (ScrolledText)
│   └── immediate_frame (10% weight)
│       └── input_frame
│           ├── immediate_prompt_label
│           ├── immediate_entry
│           └── execute_btn
└── status_label (Label)

variables_window (Toplevel - hidden by default)
├── resource_label (usage stats)
├── search_frame
│   ├── filter_entry
│   └── edit_button
└── variables_tree (Treeview)

stack_window (Toplevel - hidden by default)
└── stack_tree (Treeview)
```

---

## 16. CODE ORGANIZATION

### 16.1 Main Sections

1. **Initialization** (lines 1-286): `__init__()`, `start()`
2. **Menu Creation** (287-369): `_create_menu()`
3. **Toolbar** (370-398): `_create_toolbar()`
4. **Menu Handlers** (402-600): `_menu_*()` methods
5. **Breakpoints** (828-864): Toggle and clear
6. **Variables Window** (866-1564): Create, update, sort, edit
7. **Stack Window** (1565-1710): Create, update
8. **Editor Events** (1864-2244): Navigation, paste, key press
9. **Auto-Numbering** (1928-2106): Enter key handler
10. **Smart Insert** (2390-2513): Ctrl+I handler
11. **Execution** (2613-2764): Tick-based execution
12. **Commands** (2765-3128): cmd_* implementations
13. **Immediate Mode** (3203-3227): Execute immediate
14. **Context Menus** (3246-3360): Right-click menus
15. **TkIOHandler** (3397-end): I/O bridge

### 16.2 Related Files

- `src/ui/tk_widgets.py`: LineNumberedText widget
- `src/ui/tk_help_browser.py`: Help window
- `src/ui/tk_settings_dialog.py`: Settings window
- `src/ui/keybinding_loader.py`: Keyboard config
- `src/ui/recent_files.py`: Recent files manager
- `src/ui/auto_save.py`: Auto-save manager
- `src/ui/ui_helpers.py`: Shared utilities

---

## 17. NOTABLE IMPLEMENTATION DETAILS

### 17.1 Auto-Sort Philosophy

"Editor content should always be sorted when moving between lines."

- Triggered on cursor movement (arrows, mouse, page up/down)
- Triggered on focus out
- Saves to program (filtering blank lines)
- Refreshes from program (sorted)
- Attempts to restore cursor to same line number

### 17.2 Blank Line Philosophy

"Editor must NEVER contain blank lines."

- Enforced in multiple places
- Blank lines removed on cursor movement
- Blank numbered lines deleted on Enter
- Paste operations filter blank lines
- Save to program filters blank lines

### 17.3 Error Recovery Design

"Errors should not block editing or require restart."

- Execution stops but state preserved
- User can edit error line
- Continue retries from error point
- Variables and stack remain accessible
- Status shows helpful guidance

### 17.4 Tick-Based Execution

"UI must remain responsive during execution."

- Execute max 100 statements per tick
- Schedule next tick with 1ms delay
- Allows UI updates between ticks
- Breakpoints checked between ticks
- Output flushed between ticks

---

## 18. FUTURE ENHANCEMENTS (NOT YET IMPLEMENTED)

Based on TODO comments in code:

1. Syntax highlighting (color coding)
2. Tab completion in immediate mode
3. Hover tooltips for variables
4. Drag-and-drop file open
5. Multi-file editing (tabs)
6. Project management
7. Visual debugger timeline
8. Watch expressions
9. Conditional breakpoints
10. Performance profiling

---

## CONCLUSION

The TK UI is a feature-rich, production-ready IDE for MBASIC with:
- 3400+ lines of well-organized code
- 60+ methods for various features
- Comprehensive debugging tools
- Intelligent auto-numbering and sorting
- Real-time syntax validation
- Tick-based non-blocking execution
- Auto-save and recovery
- Recent files tracking
- Searchable help system
- Settings management
- Context menus and keyboard shortcuts

This document provides the complete reference for maintaining, documenting, and extending the TK UI.

