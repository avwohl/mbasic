# Auto-Numbering Implementation

## Overview
Implemented classic BASIC auto-numbering behavior in the TK UI, allowing users to type programs without manually entering line numbers.

## Features Implemented

### 1. Auto-Numbering on Enter
When you press Enter on a line without a line number:
- Validates the line is valid BASIC code
- Auto-assigns the next line number (starting at 10, incrementing by 10)
- Saves the line to the program
- Shows the next line number prompt

Example:
```
Type: j=23
Press Enter
Result: 10 j=23
        20 
```

### 2. Line Number Prompts
After pressing Enter on a valid line, the next line number is pre-filled:
- Shows "20 " after entering line 10
- Shows "30 " after entering line 20
- Etc.

### 3. Blank Line Prevention
The editor cannot contain blank lines:
- Pressing Enter on a blank numbered line (e.g., "20 ") removes it
- Lines with only a number are not saved to the program
- `_save_editor_to_program()` filters out lines with only numbers

### 4. Auto-Numbering Pasted Code
When pasting code without line numbers:
- Each line is validated as BASIC
- Valid lines get auto-numbered
- Invalid lines are rejected
- Status message shows what was modified

### 5. Syntax Error Handling
Lines with syntax errors are preserved:
- Pressing Enter on an error line does NOT delete it
- Editor refresh is skipped when errors exist
- User can fix the error without losing their work
- Red "?" marker shows which lines have errors

## Key Files Modified

### src/ui/tk_ui.py
- `_on_enter_key()` - Main auto-numbering logic (lines 1917-2023)
- `_on_paste()` - Auto-number pasted code (lines 2006-2160)
- `_save_editor_to_program()` - Filter blank lines (lines 1712-1755)
- `_remove_blank_lines()` - Remove blank lines from editor (lines 1873-1918)

### src/editing/manager.py
- No changes needed - already filters blank lines on save

## Configuration

Auto-numbering settings in `TkUI.__init__()`:
```python
self.auto_number_enabled = True  # Enable/disable auto-numbering
self.auto_number_start = 10      # Starting line number
self.auto_number_increment = 10  # Increment between lines
```

## User Workflow

### Typing a New Program
1. Open MBASIC with TK UI
2. Type first statement (e.g., "print hello")
3. Press Enter
4. Line becomes "10 print hello"
5. Cursor shows "20 " prompt
6. Type next statement, press Enter
7. Continues with 30, 40, 50, etc.

### Editing Existing Programs
- Auto-numbering works alongside manual line numbers
- New lines continue from the highest existing line number
- Can mix auto-numbered and manually numbered lines

### Pasting Code
- Paste code with or without line numbers
- Lines without numbers get auto-numbered
- Lines with numbers are kept as-is
- Invalid lines are rejected with status message

## Edge Cases Handled

1. **Blank Line on Enter**: Pressing Enter on "20 " removes it
2. **Syntax Errors**: Error lines preserved, not deleted
3. **Mixed Numbering**: Auto-numbering continues from highest existing line
4. **Paste with Blanks**: Blank lines removed automatically
5. **Invalid BASIC**: Invalid lines not auto-numbered

## Version History

- **1.0.58** - Initial auto-numbering for pasted code
- **1.0.59** - Fix: Check existing program lines when auto-numbering
- **1.0.61** - Add auto-numbering for typed lines (on Enter)
- **1.0.62** - Filter blank lines when saving to program
- **1.0.63-1.66** - Blank line removal experiments
- **1.0.67** - Simplified Enter handler
- **1.0.70** - Add line number prompts (classic BASIC)
- **1.0.71** - Prevent blank lines when pressing Enter on numbered line
- **1.0.72** - Don't delete syntax error lines

## Testing

Test the following scenarios:
1. Type program from scratch with auto-numbering
2. Paste code without line numbers
3. Paste code with line numbers
4. Mix typed and pasted code
5. Create syntax errors and verify they're not deleted
6. Press Enter multiple times on blank lines
7. Load existing program and add new lines

All scenarios should work without creating blank lines in the program.
