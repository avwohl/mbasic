# Web UI Windows/CRLF End-of-Line Handling

## Issue
Consider scenario where web UI runs on Windows (or OS that uses CRLF for EOL):

1. User creates a .bas file with the web UI editor
2. Web UI saves file to disk
3. User opens the file in the web UI again
4. Does the CRLF normalization (which strips `\r`) make it uneditable?
5. Or do Windows text editors handle LF-only files ok?

## Questions to Research

### File Save Behavior
- When web UI saves a file on Windows, what EOL does it use?
- Does Python's `write()` on Windows automatically convert LF to CRLF?
- Or does our explicit normalization force LF-only files?

### Windows Compatibility
- Do Windows text editors (Notepad, Notepad++, VS Code) handle LF-only files?
- Will users on Windows be confused by "Unix line endings"?
- Should we preserve the original EOL style of loaded files?

### Detection Options
- Is there a JavaScript API to detect the host OS's preferred EOL?
- Can we query `navigator.platform` or similar to detect Windows?
- Should we store EOL preference per-file or per-system?

## Current Behavior

**File Loading (src/ui/web/nicegui_backend.py:526)**
```python
content = content.replace('\r\n', '\n').replace('\r', '\n').replace('\x1a', '')
```
- Normalizes all line endings to LF (`\n`)
- Removes CP/M EOF markers (`\x1a`)

**File Saving**
- Need to check: Does `Path.write_text()` preserve LF or convert to CRLF on Windows?

## Possible Solutions

### Option 1: Detect and Preserve
- Detect original EOL style when loading file
- Store preference in dialog state
- Restore original EOL when saving

### Option 2: OS Detection
- Use JavaScript `navigator.platform` to detect Windows
- Force CRLF on Windows, LF on Unix/Mac
- Might break if web server is on different OS than browser

### Option 3: User Preference
- Add setting in web UI: "Line ending style: LF / CRLF / Auto"
- Save preference in browser localStorage
- Let user choose their preferred format

### Option 4: Do Nothing
- Modern Windows editors handle LF-only files fine
- Notepad (since Windows 10 1809) supports LF
- VS Code, Notepad++ always supported LF
- This might be a non-issue

## Testing Required

1. **Test on Windows**: Run web UI on Windows, create/save/load files
2. **Test EOL preservation**: Load CRLF file, verify what gets saved
3. **Test Python behavior**: Check if `write_text()` auto-converts on Windows
4. **Test editor compatibility**: Open LF-only files in Windows Notepad

## Related Code

- `src/ui/web/nicegui_backend.py:526` - File loading with EOL normalization
- `src/ui/web/nicegui_backend.py:2168` - Editor content with EOL normalization
- `src/input_sanitizer.py:54` - Allows CR (13) in input validation
- `src/editing/manager.py:244` - File loading in Tk/Curses (uses Python's universal newlines)

## Decision (2025-11-01)

**Always use Unix-style EOL (LF) for all files.**

### Rationale:
1. **Modern editor compatibility**: All modern Windows editors (Notepad since Win10 1809, VS Code, Notepad++, etc.) handle LF-only files correctly
2. **Browser/server independence**: Web UI may run on different OS than browser - consistent LF avoids issues
3. **Simplicity**: No need to detect, store, or convert EOL styles
4. **Standard practice**: Web applications typically use LF regardless of platform
5. **BASIC portability**: Files can be moved between Windows/Linux/Mac without EOL issues

### Implementation:
- **File loading**: Continue normalizing to LF (already done in `_save_editor_to_program()`)
- **File saving**: Python's text mode write will use LF on all platforms
- **No changes needed**: Current code already implements this correctly

### If Issues Arise:
If a user on Windows reports problems:
- Check their text editor (suggest modern editor if using old Notepad)
- Most Windows users won't notice - LF is widely supported
- Could add "Convert to CRLF" utility if actually needed (unlikely)

## Status

**RESOLVED** - Decision: Unix-style EOL (LF) for all files. No code changes needed.

## Priority

None - Issue resolved by policy decision.

## Date Created
2025-11-01

## Date Resolved
2025-11-01
