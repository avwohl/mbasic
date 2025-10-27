# Input Sanitization TODO

## Date: 2025-10-26
## Status: ✅ COMPLETED - 2025-10-26

## Issues to Address

### 1. Control Character Filtering

**Problem**: Control characters (ASCII 0-31, except newline/tab) can be inserted into the editor, which could cause issues.

**Examples of unwanted control chars**:
- Ctrl+A through Ctrl+Z (except valid shortcuts like Ctrl+C, Ctrl+V)
- Escape sequences
- Bell character (^G)
- Backspace (^H) when not intended
- Other non-printable characters

**Where to check**:
- Text widget input handlers in all UIs (Tk, Curses, Web)
- Paste operations
- File loading

**Solution approaches**:
1. Filter on input - only allow printable chars + newline + valid control sequences
2. Sanitize on paste - strip control chars from pasted text
3. Validate on save/load - warn if control chars detected

### 2. Parity Bit Clearing

**Problem**: Incoming characters might have parity bit set (bit 7), which could cause issues with character comparison and display.

**Background**:
- ASCII is 7-bit (0-127)
- Bit 7 is sometimes used for parity checking in serial communication
- Characters with bit 7 set would be in range 128-255
- This could cause 'A' (65) to be confused with 'A'+128 (193)

**Where to check**:
- Terminal input in curses UI
- Any serial/socket input
- File loading (especially from old systems)

**Solution**:
```python
# Clear parity bit (bit 7) on all incoming characters
char = chr(ord(char) & 0x7F)
```

### 3. Implementation Locations

#### Tk UI
- **File**: `src/ui/tk_ui.py`
- **Text input**: Editor text widget event handlers
- **Paste**: May need custom paste handler
- **Filter**: Add to text widget validation

#### Curses UI
- **File**: `src/ui/curses_ui.py`
- **Text input**: `handle_key()` methods
- **Parity**: Apply `& 0x7F` to all character input
- **Filter**: Check character value before processing

#### Web UI
- **File**: `src/ui/web/web_ui.py`
- **Text input**: JavaScript event handlers
- **Paste**: HTML textarea paste events
- **Filter**: Client-side JavaScript validation

### 4. Proposed Implementation

#### Control Character Filter
```python
def is_valid_input_char(char: str) -> bool:
    """Check if character is valid for editor input.

    Args:
        char: Single character to check

    Returns:
        True if character is allowed, False otherwise
    """
    if len(char) != 1:
        return False

    code = ord(char)

    # Allow printable ASCII (32-126)
    if 32 <= code <= 126:
        return True

    # Allow newline (10), tab (9)
    if code in (9, 10):
        return True

    # Reject everything else (control chars, extended ASCII)
    return False

def sanitize_input(text: str) -> str:
    """Remove invalid characters from input text.

    Args:
        text: Input text to sanitize

    Returns:
        Sanitized text with only valid characters
    """
    return ''.join(c for c in text if is_valid_input_char(c))
```

#### Parity Bit Clearing
```python
def clear_parity(char: str) -> str:
    """Clear parity bit (bit 7) from character.

    Args:
        char: Single character

    Returns:
        Character with parity bit cleared
    """
    if len(char) != 1:
        return char

    # Clear bit 7 to remove parity
    code = ord(char) & 0x7F
    return chr(code)

def clear_parity_all(text: str) -> str:
    """Clear parity bits from all characters in text.

    Args:
        text: Input text

    Returns:
        Text with parity bits cleared
    """
    return ''.join(clear_parity(c) for c in text)
```

### 5. Integration Points

#### On User Input (Typing)
```python
# In text widget event handler
def on_key_press(self, event):
    char = event.char

    # Clear parity bit
    char = clear_parity(char)

    # Filter control characters
    if not is_valid_input_char(char):
        return 'break'  # Prevent insertion

    # Allow character
    return None
```

#### On Paste
```python
# In paste handler
def on_paste(self, event):
    clipboard_text = self.clipboard_get()

    # Clear parity bits
    clipboard_text = clear_parity_all(clipboard_text)

    # Sanitize control characters
    clipboard_text = sanitize_input(clipboard_text)

    # Insert sanitized text
    self.insert(clipboard_text)
    return 'break'
```

#### On File Load
```python
# In file loading code
def load_file(self, filename):
    with open(filename, 'r') as f:
        content = f.read()

    # Clear parity bits
    content = clear_parity_all(content)

    # Sanitize (or warn about) control characters
    sanitized = sanitize_input(content)
    if len(sanitized) != len(content):
        # Warn user that control characters were removed
        self.show_warning("File contained invalid characters that were removed")

    return sanitized
```

### 6. Testing

**Test cases**:
1. Type control characters - verify they don't appear in editor
2. Paste text with control characters - verify they're filtered
3. Load file with control characters - verify they're filtered or warned
4. Load file with parity bits set - verify they're cleared
5. Type extended ASCII (128-255) - verify filtered or parity cleared

**Test files to create**:
- `tests/control_chars.bas` - File with various control characters
- `tests/parity_set.bas` - File with parity bits set
- `tests/mixed_invalid.bas` - File with both issues

### 7. Priority

**High Priority**:
- Control character filtering (prevents corruption)
- Paste sanitization (common attack vector)

**Medium Priority**:
- Parity bit clearing (less common in modern systems)
- File load sanitization (user can fix manually)

**Low Priority**:
- Extended warning messages
- Detailed logging of filtered characters

## Related Issues

- Ctrl+I tab insertion bug (fixed by binding to text widget)
- Other control key shortcuts that might conflict
- Copy/paste maintaining exact format

## References

- ASCII table: https://www.asciitable.com/
- Parity bits: https://en.wikipedia.org/wiki/Parity_bit
- Tk text widget validation: https://tkdocs.com/tutorial/text.html

## Implementation Status

- ✅ Control character filtering (completed - src/input_sanitizer.py)
- ✅ Parity bit clearing (completed - src/input_sanitizer.py)
- ✅ Paste sanitization (completed - Tk UI, Web UI, Curses UI)
- ✅ File load sanitization (completed - all UIs via ProgramManager)
- ✅ Test cases (completed - tests/test_input_sanitization.py)

## Implementation Complete

See commit b2b1686 for full implementation details.
