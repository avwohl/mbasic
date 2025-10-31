# Manual Test Procedures - Settings System

This document provides step-by-step manual testing procedures for the Settings system across all MBASIC UIs.

## Test Environment Setup

Before testing, ensure you have:
- Clean MBASIC installation
- All UI dependencies installed (`pip install -r requirements.txt`)
- Fresh settings (or backup your `~/.mbasic/settings.json` file)

## Test 1: TK UI Settings Dialog

### Objective
Verify that the TK (Tkinter) settings dialog opens, displays settings, saves changes, and affects program behavior.

### Steps

1. **Launch TK UI**
   ```bash
   python3 mbasic --ui tk
   ```

2. **Open Settings Dialog**
   - Click `File` → `Settings` (or use keyboard shortcut if available)
   - ✓ Settings dialog opens in a new window
   - ✓ Dialog contains multiple tabs (Editor, Interpreter, Keywords, Variables, UI)

3. **Navigate Editor Settings**
   - Click on `Editor` tab
   - ✓ See "Auto Number" checkbox
   - ✓ See "Auto Number Step" spinbox
   - ✓ See "Tab Size" spinbox
   - ✓ See "Show Line Numbers" checkbox

4. **Modify Auto-Numbering Settings**
   - Change "Auto Number Step" from 10 to 100
   - Click `Apply`
   - ✓ Success message appears
   - Click `OK` to close dialog

5. **Test Auto-Numbering Behavior**
   - In the editor, type without line numbers:
     ```
     PRINT "Hello"
     PRINT "World"
     ```
   - ✓ Lines are auto-numbered with step 100 (e.g., 100, 200)

6. **Verify Persistence**
   - Close MBASIC
   - Reopen MBASIC (`python3 mbasic --ui tk`)
   - Open Settings → Editor tab
   - ✓ Auto Number Step still shows 100

7. **Test Cancel Button**
   - Change Auto Number Step to 50
   - Click `Cancel`
   - Reopen Settings
   - ✓ Auto Number Step still shows 100 (change was not saved)

8. **Test Reset to Defaults**
   - Open Settings → Editor tab
   - Click `Reset to Defaults`
   - ✓ All settings return to defaults (Auto Number Step = 10)
   - Click `OK`

### Expected Results
- ✅ Settings dialog opens and displays all settings
- ✅ Changes can be applied and persisted
- ✅ Cancel discards changes
- ✅ Reset restores defaults
- ✅ Auto-numbering behavior reflects settings

---

## Test 2: Curses UI Settings Widget

### Objective
Verify that the Curses (terminal) settings widget works correctly.

### Steps

1. **Launch Curses UI**
   ```bash
   python3 mbasic --ui curses
   ```

2. **Open Settings Widget**
   - Press `Ctrl+,` (or the configured settings key)
   - ✓ Settings widget opens with scrollable list

3. **Navigate Settings**
   - Use arrow keys to scroll through categories
   - ✓ See EDITOR section
   - ✓ See INTERPRETER section
   - ✓ See KEYWORDS section
   - ✓ See VARIABLES section
   - ✓ See UI section

4. **Modify Boolean Setting**
   - Navigate to "Auto Number" checkbox
   - Press `Space` to toggle
   - ✓ Checkbox toggles on/off

5. **Modify Integer Setting**
   - Navigate to "Auto Number Step" field
   - Enter `100`
   - ✓ Value updates

6. **Modify Enum Setting**
   - Navigate to "Case Style" under KEYWORDS
   - Select `force_upper` radio button
   - ✓ Radio button selection changes

7. **Apply Settings**
   - Navigate to `Apply` button
   - Press `Enter`
   - ✓ Settings applied (status message shown)

8. **Test Cancel**
   - Change a setting
   - Navigate to `Cancel` button
   - Press `Enter`
   - ✓ Settings widget closes without saving

9. **Test ESC Key**
   - Open settings
   - Press `ESC`
   - ✓ Settings widget closes (cancels)

### Expected Results
- ✅ Settings widget opens in curses UI
- ✅ All setting types are editable (boolean, integer, enum, string)
- ✅ Apply saves changes
- ✅ Cancel discards changes
- ✅ ESC closes widget

---

## Test 3: Web UI Settings Dialog

### Objective
Verify that the Web (NiceGUI) settings dialog works correctly.

### Steps

1. **Launch Web UI**
   ```bash
   python3 mbasic --ui web
   ```
   - Open browser to `http://localhost:8080`

2. **Open Settings Dialog**
   - Click settings icon/button in navigation
   - ✓ Settings dialog appears as modal overlay

3. **Navigate Tabs**
   - Click `Editor` tab
   - ✓ See auto-numbering settings
   - Click `Limits` tab
   - ✓ See resource limits (view-only)

4. **Modify Auto-Numbering**
   - In Editor tab, toggle "Enable auto-numbering" checkbox
   - Change "Line number increment" to 100
   - ✓ Inputs update visually

5. **Save Settings**
   - Click `Save` button
   - ✓ Success notification appears
   - ✓ Dialog closes

6. **Test Auto-Numbering**
   - In web editor, type lines without numbers
   - ✓ Lines auto-number with step 100

7. **Test Persistence (Browser LocalStorage)**
   - Reload page (F5)
   - Open Settings
   - ✓ Settings still show step 100

8. **Test Cancel**
   - Change step to 50
   - Click `Cancel`
   - Reopen settings
   - ✓ Step still shows 100

### Expected Results
- ✅ Settings dialog opens in web UI
- ✅ Tabs work correctly
- ✅ Settings save and persist in browser
- ✅ Auto-numbering behavior updates
- ✅ Cancel discards changes

---

## Test 4: CLI Settings Commands

### Objective
Verify that SHOWSETTINGS and SETSETTING commands work in CLI mode.

### Steps

1. **Launch CLI Mode**
   ```bash
   python3 mbasic
   ```

2. **Test SHOWSETTINGS (All)**
   ```basic
   Ok
   SHOWSETTINGS
   ```
   - ✓ Displays all settings with current values
   - ✓ Format: `key = value`
   - ✓ All settings from settings_definitions.py shown

3. **Test SHOWSETTINGS (Filtered)**
   ```basic
   Ok
   SHOWSETTINGS editor
   ```
   - ✓ Shows only editor.* settings
   - ✓ Lists: editor.auto_number, editor.auto_number_step, etc.

4. **Test SETSETTING (Valid)**
   ```basic
   Ok
   SETSETTING editor.auto_number_step 100
   ```
   - ✓ Success message: "Setting updated: editor.auto_number_step = 100"
   - Verify with:
   ```basic
   Ok
   SHOWSETTINGS editor.auto_number_step
   ```
   - ✓ Shows new value: `editor.auto_number_step = 100`

5. **Test SETSETTING (Invalid Key)**
   ```basic
   Ok
   SETSETTING invalid.key value
   ```
   - ✓ Error message: "Unknown setting 'invalid.key'"

6. **Test SETSETTING (Invalid Value)**
   ```basic
   Ok
   SETSETTING editor.auto_number_step -5
   ```
   - ✓ Error message about validation failure
   - ✓ Value remains unchanged

7. **Test Settings Persistence in CLI**
   - Set a value:
   ```basic
   Ok
   SETSETTING editor.auto_number_step 100
   ```
   - Exit and restart CLI
   - Run:
   ```basic
   Ok
   SHOWSETTINGS editor.auto_number_step
   ```
   - ✓ Value still shows 100

8. **Test HELP Commands**
   ```basic
   Ok
   HELP SHOWSETTINGS
   ```
   - ✓ Shows help for SHOWSETTINGS

   ```basic
   Ok
   HELP SETSETTING
   ```
   - ✓ Shows help for SETSETTING

### Expected Results
- ✅ SHOWSETTINGS displays all/filtered settings
- ✅ SETSETTING updates settings
- ✅ Validation catches invalid keys and values
- ✅ Settings persist across CLI sessions
- ✅ HELP works for settings commands

---

## Test 5: Settings Affect Program Behavior

### Objective
Verify that changing settings actually affects MBASIC behavior.

### Test Cases

#### 5.1 Auto-Numbering Step

1. Set step to 10:
   ```basic
   SETSETTING editor.auto_number_step 10
   ```

2. Type unnumbered lines:
   ```basic
   PRINT "A"
   PRINT "B"
   ```

3. ✓ Lines numbered: 10, 20

4. Set step to 100:
   ```basic
   SETSETTING editor.auto_number_step 100
   ```

5. Type more lines:
   ```basic
   PRINT "C"
   ```

6. ✓ Line numbered: 100 (or next increment by 100)

#### 5.2 Keyword Case Style

1. Set to force_upper:
   ```basic
   SETSETTING keywords.case_style force_upper
   ```

2. Type:
   ```basic
   10 print "hello"
   ```

3. LIST:
   ```basic
   10 PRINT "hello"
   ```
   - ✓ Keywords shown in UPPERCASE

4. Set to force_lower:
   ```basic
   SETSETTING keywords.case_style force_lower
   ```

5. LIST:
   ```basic
   10 print "hello"
   ```
   - ✓ Keywords shown in lowercase

#### 5.3 Strict Mode

1. Enable strict mode:
   ```basic
   SETSETTING interpreter.strict_mode True
   ```

2. Run program with undefined variable:
   ```basic
   10 PRINT UndefinedVar
   RUN
   ```
   - ✓ Error about undefined variable (if strict mode catches this)

3. Disable strict mode:
   ```basic
   SETSETTING interpreter.strict_mode False
   ```

4. Run same program:
   - ✓ Runs without error (or default behavior)

### Expected Results
- ✅ Auto-numbering step affects line numbering
- ✅ Keyword case style affects LIST output
- ✅ Strict mode affects error checking

---

## Test 6: Edge Cases and Error Handling

### Objective
Test unusual scenarios and error conditions.

### Test Cases

#### 6.1 Invalid JSON in Settings File

1. Manually corrupt `~/.mbasic/settings.json`:
   ```json
   {invalid json
   ```

2. Launch MBASIC
   - ✓ Warning message about corrupt settings
   - ✓ Uses default values
   - ✓ Does not crash

#### 6.2 Missing Settings File

1. Delete `~/.mbasic/settings.json`
2. Launch MBASIC
   - ✓ Creates new settings file with defaults
   - ✓ All settings have default values

#### 6.3 Read-Only Settings File

1. Make settings file read-only:
   ```bash
   chmod 444 ~/.mbasic/settings.json
   ```

2. Try to save settings
   - ✓ Error message about inability to save
   - ✓ Does not crash

3. Restore permissions:
   ```bash
   chmod 644 ~/.mbasic/settings.json
   ```

#### 6.4 Very Large Values

1. Try setting very large value:
   ```basic
   SETSETTING editor.auto_number_step 999999
   ```
   - ✓ Validation rejects (max is 1000)

#### 6.5 Type Coercion

1. Try setting boolean with integer:
   ```basic
   SETSETTING editor.auto_number 1
   ```
   - ✓ Rejected (requires true/false)

### Expected Results
- ✅ Handles corrupt settings gracefully
- ✅ Creates missing files
- ✅ Reports I/O errors clearly
- ✅ Validates ranges correctly
- ✅ Enforces type constraints

---

## Test 7: Multi-UI Consistency

### Objective
Verify that settings set in one UI are available in another.

### Steps

1. **Set in CLI**
   ```bash
   python3 mbasic
   ```
   ```basic
   SETSETTING editor.auto_number_step 100
   ```
   Exit

2. **Check in TK UI**
   ```bash
   python3 mbasic --ui tk
   ```
   - Open Settings → Editor
   - ✓ Auto Number Step shows 100

3. **Change in TK UI**
   - Set Auto Number Step to 50
   - Click OK
   - Close MBASIC

4. **Check in CLI**
   ```bash
   python3 mbasic
   ```
   ```basic
   SHOWSETTINGS editor.auto_number_step
   ```
   - ✓ Shows 50

5. **Check in Web UI**
   ```bash
   python3 mbasic --ui web
   ```
   - Open Settings
   - ✓ Shows 50 (if using same settings file, not localStorage)

### Expected Results
- ✅ Settings are shared across UIs
- ✅ Changes in one UI appear in others
- ✅ Persistence mechanism works globally

---

## Test Summary Checklist

After completing all tests, verify:

- [ ] TK settings dialog works completely
- [ ] Curses settings widget works completely
- [ ] Web settings dialog works completely
- [ ] CLI SHOWSETTINGS command works
- [ ] CLI SETSETTING command works
- [ ] Settings affect program behavior
- [ ] Edge cases handled gracefully
- [ ] Settings persist correctly
- [ ] Settings shared across UIs
- [ ] All validation rules work
- [ ] Help documentation accessible

---

## Reporting Issues

If any test fails, report with:
1. Test number and name
2. Steps to reproduce
3. Expected result
4. Actual result
5. MBASIC version
6. UI being tested
7. OS and environment

Example:
```
Test 2.4: Curses UI - Modify Boolean Setting
Steps: Open curses UI, navigate to Auto Number checkbox, press Space
Expected: Checkbox toggles
Actual: Checkbox does not respond to Space key
Version: MBASIC 1.0.0
UI: curses
OS: Linux 6.17.0-6-generic
```

---

**Document Version:** 1.0
**Last Updated:** 2025-10-30
**Author:** MBASIC Development Team
