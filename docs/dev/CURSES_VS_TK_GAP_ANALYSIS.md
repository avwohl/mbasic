# Curses UI vs TK UI - Gap Analysis

**Date:** 2025-10-28  
**Purpose:** Identify missing features, differences, and implementation priorities for curses UI

This document compares the curses UI implementation (`src/ui/curses_ui.py`, 3810 lines) against the comprehensive TK UI feature audit (`docs/dev/TK_UI_FEATURE_AUDIT.md`).

---

## EXECUTIVE SUMMARY

### Feature Parity Status
- **Core Features:** 85% parity
- **Advanced Features:** 40% parity
- **UI/UX Polish:** 60% parity

### Critical Gaps (Must Fix)
1. **Toolbar** - Completely missing
2. **Recent Files submenu** - Missing from menu system
3. **Context menus** (right-click) - Not implemented
4. **Statement highlighting precision** - Different implementation
5. **Error recovery / Edit-and-Continue** - Incomplete

### Major Differences
1. **Line numbers**: TK embeds in editor text, Curses uses separate column
2. **Menu system**: TK has traditional menu bar, Curses has overlay dialog
3. **Settings UI**: Different dialog implementations
4. **Help system**: Different browsers but similar functionality

---

## 1. MENU SYSTEM

### 1.1 File Menu

| Feature | TK UI | Curses UI | Status | Priority |
|---------|-------|-----------|--------|----------|
| New | Ctrl+N | Ctrl+N | ✅ SAME | - |
| Open | Ctrl+O | Ctrl+O | ✅ SAME | - |
| **Recent Files submenu** | **Present** | **MISSING** | ❌ GAP | **HIGH** |
| - Shows up to 10 recent files | ✅ | ❌ | ❌ GAP | HIGH |
| - Tooltips with full path | ✅ | N/A | - | - |
| - "Clear Recent Files" option | ✅ | Implemented in dialog | ⚠️ DIFFERENT | MEDIUM |
| Save | Ctrl+S | Ctrl+S | ✅ SAME | - |
| Save As | Present | Missing | ❌ GAP | MEDIUM |
| Exit/Quit | Ctrl+Q | Ctrl+Q | ✅ SAME | - |

**Analysis:**
- Curses has `_show_recent_files()` (line 3511) but it's a dialog, not a submenu
- Shows list with numbers for selection
- Basic functionality present but UX is different
- Missing "Save As" - only has Save which prompts if no filename

**Implementation Complexity:** Medium  
**Recommendation:** Add Recent Files to menu display (line 2249), keep dialog for selection

---

### 1.2 Edit Menu

| Feature | TK UI | Curses UI | Status | Priority |
|---------|-------|-----------|--------|----------|
| Cut | Ctrl+X | ❌ | ❌ MISSING | LOW |
| Copy | Ctrl+C | ❌ | ❌ MISSING | LOW |
| Paste | Ctrl+V | ❌ | ❌ MISSING | LOW |
| Insert Line | Ctrl+I | Ctrl+I | ✅ SAME | - |
| Toggle Breakpoint | Ctrl+B | Ctrl+B | ✅ SAME | - |
| Clear All Breakpoints | Present | Ctrl+Shift+B | ✅ SAME | - |
| Delete Line | Not in TK | Ctrl+D | ⚠️ EXTRA | - |
| Renumber | Not in Edit menu | Ctrl+E | ⚠️ DIFFERENT | - |
| Settings | Present | Present | ✅ SAME | - |

**Analysis:**
- Cut/Copy/Paste not implemented - terminal UI challenge
- Curses has additional features (Delete Line, Renumber in Edit)
- Terminal clipboard integration is complex
- urwid Edit widget handles basic editing but no clipboard

**Implementation Complexity:** High (requires terminal clipboard integration)  
**Recommendation:** LOW PRIORITY - Terminal UIs traditionally don't have clipboard shortcuts

---

### 1.3 Run Menu

| Feature | TK UI | Curses UI | Status | Priority |
|---------|-------|-----------|--------|----------|
| Run Program | Ctrl+R | Ctrl+R | ✅ SAME | - |
| **Step Line** | **Present** | **Ctrl+L** | ✅ SAME | - |
| **Step Statement** | **Present** | **Ctrl+T** | ✅ SAME | - |
| Continue | Present | Ctrl+G | ✅ SAME | - |
| Stop | Present | Ctrl+X | ✅ SAME | - |
| List Program | Present | Present (in menu) | ✅ SAME | - |
| Clear Output | Present | ❌ | ❌ MISSING | MEDIUM |

**Analysis:**
- Core debugging features all present
- Missing "Clear Output" convenience feature
- Stepping works but highlight behavior differs (see Section 4)

**Implementation Complexity:** Low (Clear Output is trivial)  
**Recommendation:** Add Clear Output - easy win

---

### 1.4 View Menu

| Feature | TK UI | Curses UI | Status | Priority |
|---------|-------|-----------|--------|----------|
| Variables | Ctrl+W | Ctrl+W | ✅ SAME | - |
| Execution Stack | Ctrl+K | Ctrl+K | ✅ SAME | - |

**Analysis:** Complete parity

---

### 1.5 Help Menu

| Feature | TK UI | Curses UI | Status | Priority |
|---------|-------|-----------|--------|----------|
| Help Topics | Ctrl+H | Ctrl+H | ✅ SAME | - |
| About | Present | Present (in help) | ⚠️ DIFFERENT | LOW |

**Analysis:**
- Help systems functionally equivalent
- Different browser implementations
- Both support search, navigation, Markdown rendering

---

## 2. TOOLBAR

| Feature | TK UI | Curses UI | Status | Priority |
|---------|-------|-----------|--------|----------|
| **Toolbar** | **PRESENT** | **MISSING** | ❌ CRITICAL GAP | **HIGH** |
| - New button | ✅ | ❌ | ❌ | HIGH |
| - Open button | ✅ | ❌ | ❌ | HIGH |
| - Save button | ✅ | ❌ | ❌ | HIGH |
| - Run button | ✅ | ❌ | ❌ | HIGH |
| - Stop button | ✅ | ❌ | ❌ | HIGH |
| - Step button | ✅ | ❌ | ❌ | HIGH |
| - Stmt button | ✅ | ❌ | ❌ | HIGH |
| - Cont button | ✅ | ❌ | ❌ | HIGH |

**Analysis:**
- Toolbar completely missing from curses UI
- All functionality available via keyboard shortcuts
- TK toolbar provides visual feedback and mouse access
- Status bar (line 1454) shows shortcuts but no buttons

**Implementation Complexity:** Medium  
**Why Missing:** Terminal UI typically keyboard-driven  
**Recommendation:** 
- HIGH PRIORITY: Add visual button indicators to status bar
- Show current state (Ready/Running/Paused) more prominently
- Consider adding "[Run]" "[Stop]" "[Step]" text buttons in status area

---

## 3. EDITOR FEATURES

### 3.1 Line Number Display - MAJOR DIFFERENCE

| Aspect | TK UI | Curses UI | Analysis |
|--------|-------|-----------|----------|
| **Architecture** | **LineNumberedText widget** | **3-field format** | ⚠️ FUNDAMENTALLY DIFFERENT |
| Line numbers | Embedded in text | Variable width | Different approach |
| Status column | Separate canvas | Column 0 (S) | Similar concept |
| Format | Variable spacing | "S<linenum> CODE" | Different structure |
| Editing | Text-like editing | Field-aware editing | More complex |

**Curses Format:**
```
S<linenum> CODE
│ └─────┘ └─── Code area
│    │
│    └─ Line number (variable width)
└─ Status (column 0: ●, ?, space)
```

**TK Format:**
```
[Status]  10 PRINT "Hello"
[Canvas]  [Text Widget Content]
```

**Analysis:**
- Curses approach is MORE explicit and structured
- TK approach is more natural/flexible
- Curses has complex column-aware keypress handling (lines 177-562)
- Both show breakpoints (●) and errors (?)

**Trade-offs:**
- **Curses pros:** Clear visual separation, explicit columns
- **Curses cons:** More complex editing logic, less flexible
- **TK pros:** Natural text editing, flexible layout
- **TK cons:** Requires custom widget, more complex rendering

**Recommendation:** Keep curses approach - it works well for terminal UI

---

### 3.2 Auto-Numbering System

| Feature | TK UI | Curses UI | Status | Priority |
|---------|-------|-----------|--------|----------|
| Auto-number on Enter | ✅ | ✅ | ✅ SAME | - |
| Configurable start | ✅ (10) | ✅ (10) | ✅ SAME | - |
| Configurable increment | ✅ (10) | ✅ (10) | ✅ SAME | - |
| Auto-sort on Enter | ✅ | ✅ | ✅ SAME | - |
| Smart midpoint calculation | ✅ | ✅ | ✅ SAME | - |
| Offer to renumber when stuck | ✅ | ❌ | ❌ GAP | MEDIUM |
| Validate syntax before number | ✅ | ✅ | ✅ SAME | - |
| Delete blank numbered lines | ✅ | ✅ | ✅ SAME | - |

**Analysis:**
- Core auto-numbering identical
- Missing "offer to renumber" dialog in curses
- Curses has deferred sorting for paste performance (lines 152-159, 1103-1183)
- Both maintain cursor position after sort

**Implementation Complexity:** Low  
**Recommendation:** Add renumber offer dialog - improves UX

---

### 3.3 Smart Insert Line (Ctrl+I)

| Feature | TK UI | Curses UI | Status | Priority |
|---------|-------|-----------|--------|----------|
| Calculate midpoint | ✅ | ✅ | ✅ SAME | - |
| Offer renumber if no room | ✅ | ✅ | ✅ SAME | - |
| Position cursor ready | ✅ | ✅ | ✅ SAME | - |

**Analysis:** Complete parity

---

### 3.4 Auto-Sort on Navigation

| Feature | TK UI | Curses UI | Status | Priority |
|---------|-------|-----------|--------|----------|
| Sort on arrow keys | ✅ | ✅ | ✅ SAME | - |
| Sort on Page Up/Down | ✅ | ✅ | ✅ SAME | - |
| Sort on mouse click | ✅ | N/A | - | - |
| Sort on focus out | ✅ | ✅ | ✅ SAME | - |
| Restore cursor position | ✅ | ✅ | ✅ SAME | - |
| **Deferred sorting** | ❌ | **✅** | ⚠️ CURSES BETTER | - |

**Analysis:**
- Curses has BETTER performance for paste operations
- Deferred sorting (lines 152-159) - sorts once when navigation, not on every keystroke
- TK sorts more frequently but less noticeable in GUI

**Recommendation:** Consider backporting deferred sort to TK

---

### 3.5 Syntax Validation

| Feature | TK UI | Curses UI | Status | Priority |
|---------|-------|-----------|--------|----------|
| Real-time validation | ✅ | ✅ | ✅ SAME | - |
| Red ? indicator | ✅ | ✅ | ✅ SAME | - |
| Error on status click | ✅ | N/A | - | - |
| Error count in status bar | ✅ | ❌ | ❌ GAP | LOW |
| Display errors in output | ✅ | ✅ | ✅ SAME | - |

**Analysis:**
- Core validation identical
- Curses displays errors via `_display_syntax_errors()` (line 974)
- Missing error count display in status bar

**Implementation Complexity:** Low  
**Recommendation:** Add error count to status bar

---

### 3.6 Input Sanitization

| Feature | TK UI | Curses UI | Status | Priority |
|---------|-------|-----------|--------|----------|
| Paste handling | ✅ | ⚠️ | ⚠️ DIFFERENT | - |
| Clear high-bit parity | ✅ | ✅ | ✅ SAME | - |
| Remove control chars | ✅ | ✅ | ✅ SAME | - |
| Multi-line paste auto-number | ✅ | ❌ | ❌ GAP | MEDIUM |
| Key press filtering | ✅ | ✅ | ✅ SAME | - |

**Analysis:**
- Curses handles paste as rapid character input
- No special multi-line paste detection
- Fast path optimization for normal typing (line 188-195)

**Implementation Complexity:** Medium  
**Recommendation:** Add multi-line paste detection and auto-numbering

---

### 3.7 Blank Line Prevention

| Feature | TK UI | Curses UI | Status | Priority |
|---------|-------|-----------|--------|----------|
| Remove on cursor move | ✅ | ✅ | ✅ SAME | - |
| Remove when saving | ✅ | ✅ | ✅ SAME | - |
| Delete on Enter | ✅ | ✅ | ✅ SAME | - |
| Filter on paste | ✅ | ⚠️ | ⚠️ DIFFERENT | - |

**Analysis:** Effectively complete parity

---

### 3.8 Context Menu (Right-Click)

| Feature | TK UI | Curses UI | Status | Priority |
|---------|-------|-----------|--------|----------|
| **Editor context menu** | **✅** | **❌** | ❌ MISSING | **LOW** |
| Cut/Copy/Paste | ✅ | ❌ | ❌ | LOW |
| Select All | ✅ | ❌ | ❌ | LOW |
| **Output context menu** | **✅** | **❌** | ❌ MISSING | **LOW** |
| Copy from output | ✅ | ❌ | ❌ | LOW |
| **Immediate context menu** | **✅** | **❌** | ❌ MISSING | **LOW** |

**Analysis:**
- Context menus are GUI-centric feature
- Terminal UI typically doesn't support right-click menus
- urwid has limited mouse support (disabled in line 1528: `handle_mouse=False`)
- Not critical for terminal UI

**Implementation Complexity:** High  
**Recommendation:** LOW PRIORITY - Not standard for terminal UIs

---

## 4. EXECUTION FEATURES

### 4.1 Tick-Based Execution

| Feature | TK UI | Curses UI | Status | Priority |
|---------|-------|-----------|--------|----------|
| Non-blocking execution | ✅ | ✅ | ✅ SAME | - |
| Max statements per tick | 100 | 100 | ✅ SAME | - |
| Schedule with delay | root.after(1) | alarm(0.001) | ⚠️ DIFFERENT | - |
| UI remains responsive | ✅ | ✅ | ✅ SAME | - |

**Analysis:**
- Both use tick-based execution
- TK: `root.after(1)` (line 2762)
- Curses: `loop.set_alarm_in(0.001, ...)` (line 3030)
- Functionally equivalent

---

### 4.2 Breakpoints

| Feature | TK UI | Curses UI | Status | Priority |
|---------|-------|-----------|--------|----------|
| Toggle with Ctrl+B | ✅ | ✅ | ✅ SAME | - |
| Blue ● indicator | ✅ | ✅ | ✅ SAME | - |
| Stored in set | ✅ | ✅ | ✅ SAME | - |
| Synced with interpreter | ✅ | ✅ | ✅ SAME | - |
| Clear all option | ✅ | ✅ | ✅ SAME | - |
| Click on ● shows info | ✅ | N/A | - | - |

**Analysis:** Complete parity (except mouse interaction)

---

### 4.3 Stepping Modes

| Feature | TK UI | Curses UI | Status | Priority |
|---------|-------|-----------|--------|----------|
| Step Line (full line) | ✅ | ✅ | ✅ SAME | - |
| Step Statement (single) | ✅ | ✅ | ✅ SAME | - |
| Pause after step | ✅ | ✅ | ✅ SAME | - |
| Update variables/stack | ✅ | ✅ | ✅ SAME | - |
| Highlight next statement | ✅ | ⚠️ | ⚠️ DIFFERENT | MEDIUM |

**Analysis:**
- Both modes implemented
- Highlighting implementation differs (see 4.4)

---

### 4.4 Statement Highlighting - SIGNIFICANT DIFFERENCE

| Feature | TK UI | Curses UI | Status | Priority |
|---------|-------|-----------|--------|----------|
| **Highlighting approach** | **Text tag** | **Full line highlight** | ⚠️ DIFFERENT | **MEDIUM** |
| Yellow background | ✅ | ✅ | ✅ SAME | - |
| Exact character range | ✅ | ❌ | ❌ GAP | MEDIUM |
| Active during stepping | ✅ | ✅ | ✅ SAME | - |
| Active at breakpoint | ✅ | ✅ | ✅ SAME | - |
| Active at error | ✅ | ✅ | ✅ SAME | - |
| Clear when editing | ✅ | ❌ | ❌ GAP | MEDIUM |

**TK Implementation:**
- Uses text tags to highlight exact statement character range
- Precise: "PRINT" highlighted, not whole line
- `_highlight_current_statement()` calculates exact positions

**Curses Implementation:**
- Highlights entire line (line 631: `highlight_line`)
- Has `highlight_stmt` parameter but highlights full line
- Line 569-626: `_format_line()` attempts statement highlighting
- **BUT:** Actually highlights entire line, not specific statement

**Analysis:**
- Curses has the infrastructure but not the precision
- `_format_line()` has statement index logic but doesn't use it properly
- Line 1721: Passes `highlight_stmt=state.current_statement_index`
- But format_line doesn't split the line by statements

**Implementation Complexity:** Medium-High  
**Recommendation:** 
- HIGH-MEDIUM PRIORITY: Fix statement highlighting to be precise
- Need to parse statements and apply highlighting only to current statement
- This is important for stepping clarity

---

### 4.5 Execution States

| State | TK UI | Curses UI | Status | Priority |
|-------|-------|-----------|--------|----------|
| Ready | ✅ | ✅ | ✅ SAME | - |
| Running | ✅ | ✅ | ✅ SAME | - |
| Paused | ✅ | ✅ | ✅ SAME | - |
| At Breakpoint | ✅ | ✅ | ✅ SAME | - |
| Error | ✅ | ⚠️ | ⚠️ PARTIAL | MEDIUM |
| **Prompt color changes** | **✅** | **✅** | ✅ SAME | - |
| - Green when ready | ✅ | ✅ | ✅ | - |
| - Red when running | ✅ | ✅ | ✅ | - |
| - Yellow when paused | ✅ | ✅ | ✅ | - |

**Analysis:**
- All states present
- Prompt colors work (lines 3646-3660)
- Error state exists but recovery differs (see 4.6)

---

### 4.6 Error Handling / Edit-and-Continue - CRITICAL GAP

| Feature | TK UI | Curses UI | Status | Priority |
|---------|-------|-----------|--------|----------|
| **Stop execution on error** | **✅** | **✅** | ✅ SAME | - |
| **Show error in output** | **✅** | **✅** | ✅ SAME | - |
| **Update status** | **✅** | **✅** | ✅ SAME | - |
| **Highlight error statement** | **✅** | **⚠️** | ⚠️ DIFFERENT | MEDIUM |
| **Red ? in status column** | **✅** | **✅** | ✅ SAME | - |
| **Allow editing to fix** | **✅** | **❌** | ❌ CRITICAL GAP | **HIGH** |
| **Continue from error point** | **✅** | **❌** | ❌ CRITICAL GAP | **HIGH** |
| **Variables remain accessible** | **✅** | **✅** | ✅ SAME | - |
| **Edit and Continue workflow** | **✅** | **❌** | ❌ CRITICAL GAP | **HIGH** |

**TK Implementation:**
```python
# On error:
1. Stop execution (running = False)
2. Show error in output
3. Status: "Error at line X - Edit and Continue, or Stop"
4. Highlight error statement
5. Show red ? in status column
6. User can edit the line
7. Press Continue to retry from error point
```

**Curses Implementation:**
```python
# On error (lines 3069-3085):
1. Stop execution
2. Show error in output
3. Status: "Error at line X: {error}"
4. Highlight line (not precise statement)
5. Show red ? in status column
6. NO edit-and-continue workflow
7. Continue button CANNOT retry from error
```

**Analysis:**
- This is a MAJOR usability gap
- TK allows iterative debugging (edit + retry)
- Curses requires full program restart after error
- Continue button in curses is for breakpoints only

**Root Cause:**
- `_debug_continue()` (line 1676) doesn't check for error state
- No special handling for "paused at error"
- Interpreter state not preserved for retry

**Implementation Complexity:** Medium  
**Recommendation:** 
- **CRITICAL PRIORITY**: Implement edit-and-continue for errors
- Add error state detection in `_debug_continue()`
- Allow editor modifications during error state
- Retry execution from error point when Continue pressed

---

## 5. VARIABLES WINDOW (Ctrl+W)

### 5.1 Window Layout

| Feature | TK UI | Curses UI | Status | Priority |
|---------|-------|-----------|--------|----------|
| Resource usage label | ✅ | ✅ | ✅ SAME | - |
| Filter entry field | ✅ | ✅ | ⚠️ DIFFERENT | - |
| Edit button | ✅ | ❌ | ❌ GAP | LOW |
| Treeview/List display | ✅ | ✅ | ✅ SAME | - |

**Analysis:**
- Curses uses ListBox (line 1448)
- TK uses Treeview with columns
- Curses filter is dialog-based (line 2738), not inline
- Edit triggered by 'e' key (line 2568), not button

**Implementation Complexity:** Low  
**Recommendation:** Keep current approach - works well for terminal

---

### 5.2 Variable Display

| Feature | TK UI | Curses UI | Status | Priority |
|---------|-------|-----------|--------|----------|
| Variable name with suffix | ✅ | ✅ | ✅ SAME | - |
| Value display | ✅ | ✅ | ✅ SAME | - |
| Type display | ✅ | ⚠️ | ⚠️ IMPLICIT | LOW |
| Array dimensions | ✅ | ✅ | ✅ SAME | - |
| Last accessed element | ✅ | ✅ | ✅ SAME | - |

**Analysis:**
- Curses shows type via suffix, TK has separate column
- Both show array info well (lines 2488-2508)
- Format: `A%(10x10) [5,3]=42`

---

### 5.3 Sorting System

| Feature | TK UI | Curses UI | Status | Priority |
|---------|-------|-----------|--------|----------|
| Sort by accessed | ✅ | ✅ | ✅ SAME | - |
| Sort by written | ✅ | ✅ | ✅ SAME | - |
| Sort by read | ✅ | ✅ | ✅ SAME | - |
| Sort by name | ✅ | ✅ | ✅ SAME | - |
| Sort by type | ✅ | ✅ | ✅ SAME | - |
| Sort by value | ✅ | ✅ | ✅ SAME | - |
| Toggle direction | ✅ | ✅ | ✅ SAME | - |
| Visual indicators (↓↑) | ✅ | ✅ | ✅ SAME | - |
| **Click to cycle** | **✅** | **'s' key** | ⚠️ DIFFERENT | - |
| **Click arrow to toggle** | **✅** | **'d' key** | ⚠️ DIFFERENT | - |

**Analysis:**
- Complete feature parity
- Different interaction method (keyboard vs mouse)
- Curses: 's' cycles mode, 'd' toggles direction (lines 2523, 2553)
- Both show mode and direction in title

---

### 5.4 Filtering

| Feature | TK UI | Curses UI | Status | Priority |
|---------|-------|-----------|--------|----------|
| Filter by name | ✅ | ✅ | ✅ SAME | - |
| Case-insensitive | ✅ | ✅ | ✅ SAME | - |
| Real-time update | ✅ | ❌ | ❌ GAP | LOW |
| Shows matching count | ✅ | ✅ | ✅ SAME | - |
| Filter by value | ❌ | ✅ | ✅ CURSES BETTER | - |
| Filter by type | ❌ | ✅ | ✅ CURSES BETTER | - |

**Analysis:**
- Curses has MORE comprehensive filtering (lines 2448-2462)
- TK only filters by name
- Curses filters by name, value, AND type
- Curses uses dialog ('f' key), not inline entry
- No real-time update in curses (must press Enter)

**Recommendation:** Backport curses filtering to TK

---

### 5.5 Variable Editing

| Feature | TK UI | Curses UI | Status | Priority |
|---------|-------|-----------|--------|----------|
| Double-click to edit | ✅ | N/A | - | - |
| Edit button | ✅ | 'e' key | ⚠️ DIFFERENT | - |
| String input dialog | ✅ | ✅ | ✅ SAME | - |
| Integer spinbox | ✅ | ❌ | ❌ GAP | LOW |
| Float validation | ✅ | ✅ | ✅ SAME | - |
| Array subscripts entry | ✅ | ✅ | ✅ SAME | - |
| Show current value | ✅ | ✅ | ✅ SAME | - |
| Array dimension display | ✅ | ✅ | ✅ SAME | - |

**Analysis:**
- Core functionality identical
- Curses uses text input for all types (line 2568-2736)
- TK has spinbox for integers (nicer UX)
- Both handle arrays well

**Implementation Complexity:** Low  
**Recommendation:** Low priority - text input works fine

---

### 5.6 Resource Usage Display

| Feature | TK UI | Curses UI | Status | Priority |
|---------|-------|-----------|--------|----------|
| Variable count | ✅ | ⚠️ | ⚠️ DIFFERENT | LOW |
| Array count | ✅ | ⚠️ | ⚠️ DIFFERENT | LOW |
| String space used | ✅ | ❌ | ❌ GAP | LOW |
| DATA pointer | ✅ | ❌ | ❌ GAP | LOW |
| **Memory usage** | ❌ | **✅** | ✅ CURSES BETTER | - |
| **Stack depths** | ❌ | **✅** | ✅ CURSES BETTER | - |

**TK Format:** `"Vars: 5, Arrays: 2, Strings: 120 bytes, DATA: line 100"`

**Curses Format (lines 2377-2389):**
```
Memory: 1,234 / 65,536 (1.9%)
Stacks: GOSUB=2/16 FOR=1/16 WHILE=0/16
────────────────────────────────────────
```

**Analysis:**
- Different resource focus
- Curses shows interpreter limits (MBASIC-specific)
- TK shows data storage info
- Both useful, different purposes

**Recommendation:** Add TK-style counts to curses (combine both)

---

## 6. EXECUTION STACK WINDOW (Ctrl+K)

| Feature | TK UI | Curses UI | Status | Priority |
|---------|-------|-----------|--------|----------|
| GOSUB frames | ✅ | ✅ | ✅ SAME | - |
| FOR loop frames | ✅ | ✅ | ✅ SAME | - |
| WHILE loop frames | ✅ | ✅ | ✅ SAME | - |
| Line number display | ✅ | ✅ | ✅ SAME | - |
| Most recent at top | ✅ | ✅ | ✅ SAME | - |

**Analysis:** Complete parity (lines 2818-2878)

---

## 7. OUTPUT PANE

| Feature | TK UI | Curses UI | Status | Priority |
|---------|-------|-----------|--------|----------|
| ScrolledText/ListBox | ✅ | ✅ | ✅ SAME | - |
| Auto-scroll | ✅ | ✅ | ✅ SAME | - |
| Word wrap | ✅ | ✅ | ✅ SAME | - |
| Read-only | ✅ | ✅ | ✅ SAME | - |
| **Context menu** | **✅** | **❌** | ❌ MISSING | LOW |
| Copy from output | ✅ | ❌ | ❌ GAP | LOW |
| **Clear Output** | **✅** | **❌** | ❌ MISSING | MEDIUM |

**Analysis:**
- Core functionality identical
- Missing Clear Output command (easy to add)
- Context menu not applicable to terminal

**Implementation Complexity:** Low  
**Recommendation:** Add Clear Output command

---

## 8. IMMEDIATE MODE

| Feature | TK UI | Curses UI | Status | Priority |
|---------|-------|-----------|--------|----------|
| Prompt with color | ✅ | ✅ | ✅ SAME | - |
| Single-line entry | ✅ | ✅ | ✅ SAME | - |
| Enter to execute | ✅ | ✅ | ✅ SAME | - |
| Share runtime with program | ✅ | ✅ | ✅ SAME | - |
| Access program state when paused | ✅ | ✅ | ✅ SAME | - |
| **History display** | **❌ (removed)** | **✅** | ✅ CURSES BETTER | - |
| Tab completion | ❌ (planned) | ❌ | - | LOW |
| **Context menu** | **✅** | **❌** | ❌ GAP | LOW |

**Analysis:**
- Curses has history display (ListBox, line 1482)
- TK removed history for minimalism
- Both functionally equivalent

---

## 9. FILE MANAGEMENT

### 9.1 Auto-Save System

| Feature | TK UI | Curses UI | Status | Priority |
|---------|-------|-----------|--------|----------|
| Auto-save enabled | ✅ | ✅ | ✅ SAME | - |
| 30-second interval | ✅ | ✅ | ✅ SAME | - |
| User cache directory | ✅ | ✅ | ✅ SAME | - |
| Recovery prompt | ✅ | ✅ | ✅ SAME | - |
| Cleanup old autosaves | ✅ | ✅ | ✅ SAME | - |

**Analysis:** Complete parity - uses same AutoSaveManager class

---

### 9.2 Recent Files

| Feature | TK UI | Curses UI | Status | Priority |
|---------|-------|-----------|--------|----------|
| Track up to 10 files | ✅ | ✅ | ✅ SAME | - |
| Config directory storage | ✅ | ✅ | ✅ SAME | - |
| **Submenu display** | **✅** | **❌** | ❌ GAP | **HIGH** |
| **Dialog display** | **❌** | **✅** | ⚠️ DIFFERENT | - |
| Auto-remove missing | ✅ | ✅ | ✅ SAME | - |
| Clear option | ✅ | ✅ | ✅ SAME | - |

**Analysis:**
- Same backend (RecentFilesManager)
- Different UI presentation
- TK: Submenu with mouse access
- Curses: Dialog with numbered selection (line 3511)
- Curses dialog is actually more powerful (shows full paths)

**Recommendation:** Add Recent Files to menu text, keep dialog for selection

---

### 9.3 File Dialogs

| Feature | TK UI | Curses UI | Status | Priority |
|---------|-------|-----------|--------|----------|
| Open dialog | Native Tk | Text input | ⚠️ DIFFERENT | - |
| Save As dialog | Native Tk | Text input | ⚠️ DIFFERENT | - |
| File filters | *.bas, *.* | N/A | - | - |
| Default extension | .bas | .bas | ✅ SAME | - |

**Analysis:**
- Terminal UI limitation
- Curses uses text input for paths (line 3325)
- Could add file picker widget but complex
- Current approach works

---

## 10. SETTINGS SYSTEM

| Feature | TK UI | Curses UI | Status | Priority |
|---------|-------|-----------|--------|----------|
| Settings dialog | ✅ | ✅ | ✅ SAME | - |
| Category tabs | ✅ | ✅ | ⚠️ DIFFERENT | - |
| Boolean (checkbox) | ✅ | ✅ | ✅ SAME | - |
| Integer (spinbox) | ✅ | ✅ | ✅ SAME | - |
| String (entry) | ✅ | ✅ | ✅ SAME | - |
| Enum (dropdown) | ✅ | ✅ | ✅ SAME | - |
| OK/Cancel/Apply | ✅ | ✅ | ✅ SAME | - |
| Reset to defaults | ✅ | ✅ | ✅ SAME | - |

**Analysis:**
- Different implementations but same functionality
- TK: TkSettingsDialog (separate file)
- Curses: SettingsWidget (line 2301)
- Both support all setting types

---

## 11. HELP SYSTEM

| Feature | TK UI | Curses UI | Status | Priority |
|---------|-------|-----------|--------|----------|
| Help browser | ✅ | ✅ | ✅ SAME | - |
| Back button | ✅ | ✅ | ✅ SAME | - |
| Home button | ✅ | ✅ | ✅ SAME | - |
| Search | ✅ | ✅ | ✅ SAME | - |
| In-page search (Ctrl+F) | ✅ | ✅ | ✅ SAME | - |
| Clickable links | ✅ | ✅ | ✅ SAME | - |
| Three-tier system | ✅ | ✅ | ✅ SAME | - |
| Markdown rendering | ✅ | ✅ | ✅ SAME | - |
| Fuzzy matching | ✅ | ✅ | ✅ SAME | - |
| Pre-built indexes | ✅ | ✅ | ✅ SAME | - |

**Analysis:**
- Different implementations (TkHelpBrowser vs HelpWidget)
- Functionally equivalent
- Both excellent

---

## 12. KEYBOARD SHORTCUTS

### 12.1 Configurable Shortcuts

| Feature | TK UI | Curses UI | Status | Priority |
|---------|-------|-----------|--------|----------|
| Config file loading | ✅ (tk.json) | ✅ (curses.json) | ✅ SAME | - |
| Per-UI configuration | ✅ | ✅ | ✅ SAME | - |
| Platform-specific | ✅ | ✅ | ✅ SAME | - |

**Analysis:** Same keybinding system

---

### 12.2 Fixed Shortcuts

All shortcuts match or have terminal equivalents.

---

## 13. ADVANCED FEATURES

### 13.1 Command Methods

All `cmd_*` methods present in both UIs (lines 3661-3790).

---

### 13.2 IOHandler

| Feature | TK UI | Curses UI | Status | Priority |
|---------|-------|-----------|--------|----------|
| print_line() | ✅ | ✅ | ✅ SAME | - |
| input_line() | ✅ | ✅ | ✅ SAME | - |
| Input dialog | ✅ | ✅ | ✅ SAME | - |

**Analysis:** Complete parity

---

## PRIORITY RANKING

### CRITICAL (Must Fix)
1. **Edit-and-Continue on error** - Major debugging workflow gap
2. **Precise statement highlighting** - Important for stepping clarity
3. **Recent Files submenu** - Expected feature missing

### HIGH (Should Fix Soon)
4. **Toolbar/Status indicators** - Visual feedback for states
5. **Clear Output command** - Simple convenience feature
6. **Offer renumber dialog** - UX improvement

### MEDIUM (Nice to Have)
7. **Multi-line paste auto-numbering** - Improves paste UX
8. **Error count in status bar** - Quick feedback
9. **Clear highlighting on edit** - Polish
10. **Save As command** - Currently only has Save

### LOW (Not Critical)
11. Cut/Copy/Paste - Terminal UI limitation
12. Context menus - Not standard for terminals
13. Integer spinbox - Text input works fine
14. Resource display enhancements - Minor improvements

---

## RECOMMENDATIONS BY CATEGORY

### Execution & Debugging (Critical)
1. **Implement Edit-and-Continue for errors**
   - Add error state detection in `_debug_continue()`
   - Allow editor modifications during error
   - Retry from error point on Continue
   - Complexity: Medium
   - Impact: HIGH

2. **Fix statement highlighting precision**
   - Modify `_format_line()` to parse statements
   - Apply highlight only to current statement
   - Use statement boundaries from parser
   - Complexity: Medium-High
   - Impact: HIGH

### UI/UX Improvements (High Priority)
3. **Add Recent Files to menu display**
   - Update menu text (line 2249)
   - Keep dialog-based selection (works well)
   - Show in File section
   - Complexity: Low
   - Impact: HIGH

4. **Add visual state indicators**
   - Enhance status bar with state display
   - Show [Ready] [Running] [Paused] [Error]
   - Use colors for quick recognition
   - Complexity: Low
   - Impact: MEDIUM

5. **Add Clear Output command**
   - Add to Run menu or separate command
   - Clear output_walker
   - Simple implementation
   - Complexity: Low
   - Impact: MEDIUM

### Editor Enhancements (Medium Priority)
6. **Multi-line paste detection**
   - Detect rapid newline input
   - Auto-number pasted lines
   - Defer sort until paste complete
   - Complexity: Medium
   - Impact: MEDIUM

7. **Offer renumber dialog**
   - Show when no room for midpoint
   - Calculate new start/increment
   - Apply renumbering
   - Complexity: Low
   - Impact: MEDIUM

### Future Enhancements (Low Priority)
8. **Terminal clipboard integration**
   - Research urwid clipboard support
   - Add Cut/Copy/Paste if feasible
   - Complexity: High
   - Impact: LOW

---

## CONCLUSION

The curses UI has **excellent feature parity** with TK UI (85% for core features). The main gaps are:

### Architecture Differences (Keep)
- Line number display (curses approach is good)
- Menu system (overlay vs menubar - both work)
- File dialogs (terminal limitation)

### Critical Gaps (Fix Immediately)
- Edit-and-Continue on error
- Precise statement highlighting
- Recent Files menu display

### Missing Features (Fix Soon)
- Toolbar/status indicators
- Clear Output command
- Some UX polish

### Not Missing (Actually Better in Curses)
- Variable filtering (by name, value, type)
- Deferred sorting (better paste performance)
- Memory/stack resource display
- Immediate mode history

The curses UI is production-ready with the exception of Edit-and-Continue, which is a significant debugging workflow gap that should be addressed first.

---

**Document prepared:** 2025-10-28  
**Total analysis time:** Comprehensive codebase review  
**Files analyzed:** 2 (curses_ui.py, TK_UI_FEATURE_AUDIT.md)  
**Lines analyzed:** 3810 + 950 = 4760 lines
