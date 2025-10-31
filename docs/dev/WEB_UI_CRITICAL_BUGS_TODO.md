# Web UI Critical Bugs - TODO

⚠️ **Status:** CRITICAL BUGS
**Priority:** HIGH
**Created:** 2025-10-30

## Summary

**Web UI has 8 critical bugs that make it completely unusable:**
1. INPUT doesn't work - can't run interactive programs
2. STOP doesn't work - can't interrupt programs
3. Auto-numbering broken - JavaScript timeout errors
4. **ALL menus broken - ALL items require two clicks** (File, Edit, etc.)
5. **Find/Replace completely broken** - doesn't jump to results, broken state management
6. No way to start new search - Find button disappears after first search
7. **Output console hangs after ~500 lines** - UI freezes, output truncation broken
8. **Ctrl+C doesn't kill web UI process** - must use kill -9, leaves zombie processes

## Critical Issues

### 1. INPUT Statement Doesn't Work
**Severity:** CRITICAL - breaks all interactive programs

**Problem:**
- INPUT statement doesn't stop for user input in web UI
- Program continues running without waiting
- Interactive games/programs completely broken

**Example:**
```basic
10 INPUT "What is your name"; N$
20 PRINT "Hello "; N$
```
Expected: Program stops at line 10 waiting for input
Actual: Program continues without stopping

**Impact:**
- All games in library broken
- Interactive utilities broken
- User cannot run any program that uses INPUT

### 2. STOP Button Doesn't Work
**Severity:** CRITICAL - cannot stop runaway programs

**Problem:**
- STOP/Break button doesn't work during program execution
- Especially fails when program is in a loop printing output
- May not work at all

**Example:**
```basic
10 FOR I = 1 TO 1000000
20 PRINT I
30 NEXT I
```
Expected: STOP button interrupts execution
Actual: STOP button does nothing, must wait for completion or reload page

**Impact:**
- Cannot stop infinite loops
- Cannot interrupt long-running programs
- Bad user experience - must reload page

### 3. Auto-Numbering Still Broken
**Severity:** HIGH - core feature doesn't work

**Problem:**
- Auto-numbering fails with JavaScript timeout error
- Happens when typing simple statements like `k=2<enter>`
- Error: `TimeoutError: JavaScript did not respond within 1.0 s`

**Error trace:**
```
File "/home/wohl/cl/mbasic/src/ui/web/nicegui_backend.py", line 1648, in _on_enter_key
  result = await ui.run_javascript(f'''
  ...
TimeoutError: JavaScript did not respond within 1.0 s
```

**Test case:**
1. Open web UI
2. Type: `k=2`
3. Press Enter
4. Error occurs

**Impact:**
- Cannot type statements without line numbers
- Auto-numbering feature completely broken
- Forces users to manually number every line

**Root cause:**
- `_on_enter_key` makes JavaScript call that times out
- JavaScript timeout set to 1.0 second (too short?)
- JavaScript may not be responding at all
- Async/await handling issue in nicegui_backend.py:1648

**Related files:**
- `/home/wohl/web_autonumber_error.txt` - Full error trace
- `src/ui/web/nicegui_backend.py:1648` - Error location

### 4. ALL Menus Completely Broken - Every Menu Item Requires Two Clicks
**Severity:** CRITICAL - ENTIRE menu system broken

**Problem:**
- **ALL menus** require two clicks for ANY item: File, Edit, Run, Help, etc.
- First click: Menu → Any item - nothing happens
- Second click: Menu → same item - NOW it works
- Affects EVERY menu in the entire UI
- First click fails silently with no feedback

**Confirmed broken menus:**
- File menu (Open, Merge, Save As, etc.)
- Edit menu (Find, Replace, etc.)
- Likely ALL other menus too

**Test case:**
1. Open web UI
2. Click File menu
3. Click ANY item (Open, Merge, Save As, etc.)
4. Nothing happens
5. Click File menu again
6. Click same item again
7. Now it works

**Affected operations:**
- Open (file picker doesn't appear)
- Merge (file picker doesn't appear)
- Save As (file picker doesn't appear)
- All other File menu items

**Impact:**
- CRITICAL - Cannot use ANY file operations without double-clicking
- Confusing user experience
- Looks like UI is completely broken/unresponsive
- Users may not realize they need to click twice
- Makes web UI unusable for basic file operations

**Root cause:**
- ENTIRE File menu has state management issue
- Event handlers not properly bound on first render
- Menu may close before action completes
- Systematic problem affecting ALL menu items, not just Merge

**Possible issues:**
- Menu items not initialized until second click
- Menu close happens before item click handlers fire
- NiceGUI menu lifecycle issue
- Event handlers attached too late in render cycle
- Race condition in menu component initialization
- Missing await on async operations

**Why this is worse than initially thought:**
- Not just File menu - **ALL MENUS** are broken
- File menu: ALL items broken
- Edit menu: ALL items broken
- Entire menu system is unusable
- Points to systematic NiceGUI menu handling bug affecting entire UI
- This is an architectural problem, not isolated bug

**Related patterns:**
- This is a common NiceGUI/web UI issue
- Menu items with async actions need special handling
- May need to completely rewrite menu event handling
- May need to use different NiceGUI menu pattern

### 5. Find/Replace Completely Broken - Multiple Issues
**Severity:** CRITICAL - Search functionality unusable

**Problem 1: Find doesn't jump to first result**
- Find dialog shows "Found: 3 occurrences"
- Cursor doesn't jump to first match
- User has no idea where matches are
- No visual indication of matches

**Problem 2: Search position is broken**
- "Find Next" implies searching from current position
- But searching from end of file still says "Found: 3"
- Should say "0 found" if past all matches
- Count doesn't account for cursor position

**Problem 3: Find button disappears after first search**
- First time: Dialog has "Find" button
- Second time: Only "Find Next" button, no "Find" button
- Cannot start a new search
- Cannot search for different text
- Must close and reopen dialog to search again

**Problem 4: Cannot perform second search**
- After first search, stuck with "Find Next"
- No way to enter new search term
- Dialog state management broken
- Forces dialog close/reopen for each new search

**Test case:**
```
1. Open web UI
2. Type some code with repeated words:
   10 PRINT "HELLO"
   20 PRINT "HELLO"
   30 PRINT "HELLO"
3. Edit menu → Find (requires 2 clicks)
4. Search for "HELLO"
5. Dialog shows "Found: 3 occurrences"
   BUG: Cursor doesn't jump to first HELLO
6. Move cursor to end of file
7. Click Find again
   BUG: Still shows "Found: 3" (should be 0, past all matches)
8. Close and reopen Find dialog
9. Try to search for something else
   BUG: No "Find" button, only "Find Next"
   BUG: Cannot start new search
```

**Impact:**
- Cannot use Find feature effectively
- No way to navigate to search results
- Must manually scan code for matches
- Cannot perform multiple searches without closing dialog
- Search completely broken for any practical use

**Root causes:**
- Find doesn't set cursor position to first match
- Search position not tracked correctly
- Dialog state not reset between searches
- UI elements (Find button) not properly managed
- State machine for Find/Find Next broken

### 6. Output Console Hangs After ~500 Lines
**Severity:** CRITICAL - programs freeze, UI becomes unresponsive

**Problem:**
- Program prints 0 to 499 successfully
- At ~500 lines, output stops appearing
- UI hangs/freezes
- Program still running but no output shown
- Cannot stop program (STOP button already broken)
- Must reload page to recover

**Test case:**
```basic
10 FOR I = 0 TO 9999999
20 PRINT I
30 NEXT I
```

**Observed behavior:**
- Prints: 0, 1, 2, ... 498, 499
- Then: Nothing (hangs)
- Output window frozen
- Program appears to hang
- STOP button doesn't work anyway

**Root cause hypothesis:**
- Output buffer management broken
- Console supposed to truncate/scroll old lines
- Truncation fails after ~500 lines
- DOM becomes overloaded with elements
- Browser freezes trying to render too many elements
- Output accumulation causes memory/performance issue

**Expected behavior:**
- Should automatically truncate old output
- Keep last N lines (e.g., 1000 lines)
- Remove old DOM elements
- Maintain scrolling performance
- Continue showing new output

**Impact:**
- Cannot run programs with significant output
- UI becomes completely unresponsive
- Must reload page to recover
- Makes testing/debugging impossible
- Any loop with PRINT will freeze UI

**Related issues:**
- Similar to terminal buffer management
- Other UIs (TK, Curses, CLI) handle this correctly
- Web UI output handling fundamentally broken
- May be NiceGUI textarea/scrolling issue

**Workarounds:**
- None (STOP button also broken)
- Must close browser tab
- Cannot limit output from program

### 7. Ctrl+C Doesn't Kill Web UI Process
**Severity:** CRITICAL - cannot stop development server cleanly

**Problem:**
- Running `python3 mbasic --ui web` starts server
- Pressing Ctrl+C does NOT kill the process
- Process continues running in background
- Must use `kill -9` to terminate
- Leaves zombie processes
- Port may remain bound

**Test case:**
```bash
$ python3 mbasic --ui web
# Server starts, browser opens
# Press Ctrl+C
# Expected: Process exits cleanly
# Actual: Process keeps running

# Must do:
$ ps aux | grep mbasic
$ kill -9 <pid>
```

**Impact:**
- Cannot cleanly stop development server
- Accumulates zombie processes
- Port 8080 may remain bound
- Must manually kill processes
- Poor developer experience
- May interfere with restarts

**Root cause:**
- Signal handlers not properly installed
- NiceGUI server doesn't handle SIGINT
- Event loop not responding to interrupts
- Background threads not being stopped
- Async cleanup not happening

**Expected behavior:**
- Ctrl+C should trigger graceful shutdown
- Close all connections
- Stop event loop
- Exit cleanly with status 0
- Free port immediately

**Related issues:**
- Common problem with async Python web servers
- NiceGUI/FastAPI signal handling
- May need explicit signal handler registration
- Should cleanup on exit (atexit handlers)

**Workarounds:**
- Use `kill <pid>` (sends SIGTERM)
- Use `kill -9 <pid>` if SIGTERM doesn't work
- Check for running processes before restart
- Use different port if 8080 blocked

### 8. How Did This Pass Tests?

**Question:** All three features are tested in test suite, how did they pass?

**Hypothesis:**
- Tests may be mocked/stubbed
- Tests may not actually run programs to completion
- Tests may check for component existence, not functionality
- Web UI tests may use different code path than actual execution

**Files to investigate:**
- `tests/regression/ui/test_*.py`
- `tests/playwright/test_web_ui.py`
- `tests/nicegui/test_mbasic_web_ui.py`
- `src/ui/web/nicegui_backend.py` - INPUT/STOP implementation

## Investigation Plan

### Step 1: Reproduce Issues
1. Launch web UI: `python3 mbasic --ui web`
2. Test INPUT:
   ```basic
   10 INPUT "Name"; N$
   20 PRINT N$
   RUN
   ```
3. Test STOP:
   ```basic
   10 FOR I = 1 TO 100000
   20 PRINT I
   30 NEXT I
   RUN
   ```
   Click STOP during execution

### Step 2: Review Test Suite
1. Check `tests/regression/ui/test_*.py` for web INPUT tests
2. Check if tests actually execute or just check structure
3. Identify why tests passed with broken functionality

### Step 3: Review Web UI Implementation
1. Find INPUT implementation in `src/ui/web/nicegui_backend.py`
2. Find STOP button handler
3. Identify why INPUT doesn't block
4. Identify why STOP doesn't interrupt

### Step 4: Compare with Working UIs
1. Review how TK UI handles INPUT (blocking)
2. Review how Curses UI handles INPUT (blocking)
3. Review how CLI handles INPUT (blocking)
4. Identify what web UI is missing

## Technical Background

### INPUT Statement Requirements
- Must BLOCK program execution
- Must show input prompt
- Must wait for user to type and press Enter
- Must store input in variable
- Must continue execution after input received

### STOP Button Requirements
- Must be checked frequently during execution
- Must interrupt execution immediately
- Must preserve program state
- Must allow CONT to resume

### Web UI Challenges
- JavaScript is async/non-blocking
- Cannot block main thread waiting for input
- Need async/await or callback pattern
- Need to pause interpreter, not block UI

## Likely Root Causes

### INPUT Not Working
**Hypothesis:** Web UI runs interpreter synchronously without yielding for input

**Possible issues:**
- `execute_input()` in web backend doesn't actually wait
- Interpreter runs to completion without checking for input state
- Input mechanism not integrated with async execution

**Fix approach:**
- Need to pause interpreter when INPUT encountered
- Show input dialog
- Wait for user response (async)
- Resume interpreter with input value

### STOP Not Working
**Hypothesis:** STOP button doesn't set interrupt flag or flag isn't checked

**Possible issues:**
- STOP button handler doesn't exist or isn't connected
- Interpreter doesn't check `should_stop` flag during execution
- Long-running operations don't yield control
- Print statements in tight loops don't check for interrupts

**Fix approach:**
- Ensure STOP button sets `self.should_stop = True`
- Ensure interpreter checks flag in main loop
- Add interrupt checks in PRINT, FOR/NEXT, etc.
- May need to use worker threads or async execution

## Similar Issues in Other UIs?

Check if other UIs have similar issues:
- ✅ CLI - INPUT works, Ctrl+C stops
- ✅ Curses - INPUT works, interrupt works
- ✅ TK - INPUT works, STOP button works
- ❌ Web - Both broken

This suggests web UI has unique architecture issues.

## Priority

**MUST FIX BEFORE:**
- Games library launch
- Any user testing
- Production release

**Current state:** Web UI is unusable for interactive programs

## Related Files

- `src/ui/web/nicegui_backend.py` - Main web UI implementation
- `src/interpreter.py` - Interpreter INPUT/STOP handling
- `tests/regression/ui/test_*.py` - UI tests that supposedly passed
- `docs/dev/UI_FEATURE_PARITY_TRACKING.md` - Claims features work

## Next Actions

1. **IMMEDIATELY:** Document exact reproduction steps ✅ DONE
2. **CRITICAL:** Fix Ctrl+C signal handling (cannot stop server)
3. **CRITICAL:** Fix output console hang after ~500 lines (DOM overload)
4. **CRITICAL:** Fix ALL menus requiring double-click (architectural issue)
5. **URGENT:** Fix Find/Replace - jump to results, fix state management
6. **URGENT:** Fix Find/Replace - restore Find button for new searches
7. **URGENT:** Fix auto-numbering JavaScript timeout
8. **URGENT:** Fix INPUT blocking/async issue
9. **URGENT:** Fix STOP button interrupt issue
10. **HIGH:** Investigate why tests passed
11. **HIGH:** Add integration tests that actually run programs
12. **MEDIUM:** Update feature parity tracking with accurate status

## Reproduction Steps

### Bug 1: INPUT doesn't work
```bash
python3 mbasic --ui web
# In browser, type:
10 INPUT "Name"; N$
20 PRINT N$
RUN
# Expected: Stops for input at line 10
# Actual: Continues without stopping
```

### Bug 2: STOP doesn't work
```bash
python3 mbasic --ui web
# In browser, type:
10 FOR I = 1 TO 100000
20 PRINT I
30 NEXT I
RUN
# Click STOP button during execution
# Expected: Program stops immediately
# Actual: STOP button does nothing
```

### Bug 3: Auto-numbering broken
```bash
python3 mbasic --ui web
# In browser, type:
k=2
# Press Enter
# Expected: Line auto-numbered as "10 k=2"
# Actual: TimeoutError: JavaScript did not respond within 1.0 s
```

### Bug 4: ALL menus broken - Every item needs two clicks
```bash
python3 mbasic --ui web

# File menu broken:
# 1. Click "File" → "Open" → Nothing happens
# 2. Click "File" → "Open" again → NOW works

# Edit menu broken:
# 1. Click "Edit" → "Find" → Nothing happens
# 2. Click "Edit" → "Find" again → NOW works

# Pattern: ALL menus, ALL items require TWO clicks
```

### Bug 5: Find/Replace completely broken
```bash
python3 mbasic --ui web
# Type code:
10 PRINT "HELLO"
20 PRINT "HELLO"
30 PRINT "HELLO"

# Try Find (requires 2 clicks on Edit menu):
# 1. Edit → Find (click twice)
# 2. Search for "HELLO"
# Result: Shows "Found: 3 occurrences"
# BUG: Cursor doesn't move to first match

# Try from end of file:
# 1. Move cursor to line 30
# 2. Search for "HELLO" again
# BUG: Still shows "Found: 3" (should be 0, past all matches)

# Try second search:
# 1. Close Find dialog
# 2. Open Find dialog again
# BUG: No "Find" button, only "Find Next"
# BUG: Cannot start new search
```

### Bug 6: Output console hangs after ~500 lines
```bash
python3 mbasic --ui web
# Type:
10 FOR I = 0 TO 9999999
20 PRINT I
30 NEXT I
RUN

# Expected: Prints numbers continuously, truncates old output
# Actual:
# - Prints 0 to 499
# - Then hangs/freezes
# - No more output appears
# - UI becomes unresponsive
# - Must reload page to recover
```

### Bug 7: Ctrl+C doesn't kill web UI process
```bash
$ python3 mbasic --ui web
# Server starts on port 8080, browser opens

# Press Ctrl+C
# Expected: Process exits cleanly
# Actual: Nothing happens, process keeps running

# Must manually kill:
$ ps aux | grep mbasic
wohl     12345  ...  python3 mbasic --ui web
$ kill -9 12345

# Or port becomes blocked:
$ python3 mbasic --ui web
# Error: Address already in use
```

---

**Created:** 2025-10-30
**Reporter:** User
**Assigned:** Development team
**Target:** ASAP - blocking games library launch
