# MBASIC Extensions and Modern Features

## About This Implementation

This is **MBASIC-2025**, a modern implementation of Microsoft BASIC-80 5.21 (CP/M era) with carefully chosen extensions for modern development while maintaining 100% compatibility with original MBASIC 5.21 programs.

**Project Names Under Consideration:**
- MBASIC-2025 (emphasizes the modern update)
- Visual MBASIC 5.21 (emphasizes the multiple UIs)
- MBASIC++ (emphasizes extensions)
- MBASIC-X (extended MBASIC)

## Extensions Beyond Original MBASIC 5.21

These features are **NOT** in the original CP/M MBASIC 5.21 from 1981. They are modern additions for improved development experience.

### 🔍 Debugging Commands

**IMPORTANT:** These commands are **NOT in original MBASIC 5.21**. They are modern extensions that may be available in different forms depending on the UI backend.

#### BREAK - Breakpoint Management
```basic
BREAK 100              ' Set breakpoint at line 100
BREAK                  ' List all breakpoints
BREAK CLEAR            ' Clear all breakpoints
BREAK CLEAR 100        ' Clear specific breakpoint
```
**Status:** ⚠️ MBASIC-2025 Extension (Not in MBASIC 5.21)
**Availability:** CLI (command form), Curses (Ctrl+B), Tk (UI controls)

#### STEP - Single-Step Execution
```basic
STEP                   ' Execute one statement
STEP 5                 ' Execute 5 statements
STEP INTO              ' Step into subroutines (planned)
STEP OVER              ' Step over subroutines (planned)
```
**Status:** ⚠️ MBASIC-2025 Extension (Not in MBASIC 5.21)
**Availability:** CLI (command form), Curses (Ctrl+T/Ctrl+K), Tk (UI controls)

#### STACK - Call Stack Display
```basic
STACK                  ' Show full call stack
STACK GOSUB            ' Show only GOSUB stack
STACK FOR              ' Show only FOR loop stack
```
**Status:** ⚠️ MBASIC-2025 Extension (Not in MBASIC 5.21)
**Availability:** CLI (command form), Curses (menu access), Tk (stack window)

### 🖥️ Multiple User Interfaces

Original MBASIC 5.21 only had a command-line interface. This implementation provides:

1. **CLI** - Classic command line (closest to original)
2. **Curses** - Full-screen terminal UI (⚠️ Extension)
3. **Tk** - Desktop GUI with menus (⚠️ Extension)
4. **Web** - Browser-based IDE (⚠️ Extension)

The GUI interfaces (Curses, Tk, Web) are **NOT in MBASIC 5.21**.

### 📝 Editor Enhancements

**Features NOT in original MBASIC 5.21:**
- Full-screen editing (Curses, Tk, Web)
- Syntax highlighting (Tk, Web)
- Find and Replace (Tk only)
- Cut/Copy/Paste (Tk, Web)
- Mouse support (Tk, Web)
- Auto-save to local filesystem (Tk, Curses, CLI only - Web UI files are session-only)

### 🎯 Visual Debugging

**Features NOT in original MBASIC 5.21:**
- Visual breakpoints (click line numbers)
- Variable inspector windows
- Real-time variable updates
- Execution highlighting
- Step-by-step visualization

### 💾 Enhanced File Handling

**More permissive than MBASIC 5.21:**
- Accepts LF, CR, or CRLF line endings (original only CRLF)
- Long filenames (original limited to 8.3)
- Path support (original only drive letters)
- Unicode text files (original only ASCII)

### 🔧 Development Tools

**NOT in original MBASIC 5.21:**
- Parse tree visualization (`utils/show_parse_tree.py`)
- Error analysis tools (`utils/analyze_errors.py`)
- Automatic keyword spacing fix (`utils/fix_keyword_spacing.py`)
- Program detokenizer (`utils/detokenizer.py`)

## Compatibility Notes

### Running Original MBASIC Programs

✅ **100% Compatible**: Any program that runs on CP/M MBASIC 5.21 will run here
- All statements work identically
- All functions produce same results
- All error codes match
- Numeric precision matches

### Using Extensions

⚠️ **Programs using extensions will NOT run on original MBASIC 5.21**

If you use:
- BREAK, STEP, STACK commands
- Visual debugging features
- GUI-specific features
- Modern file paths

Your program becomes **MBASIC-2025 specific** and won't run on vintage systems.

### Compatibility Mode

To ensure compatibility with original MBASIC 5.21:
1. Use only CLI backend
2. Don't use debugging commands
3. Stick to 8.3 filenames
4. Use only CRLF line endings
5. Avoid GUI features

## Feature Comparison

| Feature | MBASIC 5.21 (1981) | MBASIC-2025 | Notes |
|---------|-------------------|-------------|-------|
| **Core BASIC** | ✅ | ✅ | 100% compatible |
| **BREAK command** | ❌ | ✅ | Extension |
| **STEP command** | ❌ | ✅ | Extension |
| **STACK command** | ❌ | ✅ | Extension |
| **GUI interfaces** | ❌ | ✅ | Extension |
| **Syntax highlighting** | ❌ | ✅ | Extension |
| **Find** | ❌ | ✅ (Tk) | Extension |
| **Visual debugging** | ❌ | ✅ | Extension |
| **Long filenames** | ❌ | ✅ | Enhancement |
| **Unicode** | ❌ | ✅ | Enhancement |
| **Cross-platform** | ❌ | ✅ | Enhancement |

## Philosophy

This implementation follows these principles:

1. **100% backward compatibility** - All original programs must run
2. **Careful extensions** - Only add features that don't break compatibility
3. **Modern development** - Provide tools for productive coding
4. **Clear documentation** - Always mark what's an extension
5. **Optional features** - Extensions can be ignored for vintage compatibility

## For Purists

If you want the authentic MBASIC 5.21 experience:
```bash
python3 mbasic --ui cli
```
Then avoid using:
- BREAK, STEP, STACK
- Any GUI features
- Long filenames
- Modern paths

This gives you pure MBASIC 5.21 compatibility.

## For Modern Developers

If you want all the modern conveniences:
```bash
python3 mbasic --ui tk  # or web
```
Use all features freely:
- Visual debugging
- GUI editors
- Modern file handling
- Development tools

## Why These Extensions?

Each extension was carefully chosen:

- **Debugging commands**: Essential for development, don't affect program behavior
- **Multiple UIs**: Accessibility and preference, core interpreter unchanged
- **Visual features**: Productivity boost, optional use
- **File handling**: Necessary for cross-platform operation

## Future Extensions Under Consideration

These are being evaluated but NOT yet implemented:
- DO...LOOP (structured loops)
- SELECT CASE (multi-way branching)
- SUB/FUNCTION procedures
- Local variables
- Long variable names

Each would be optional and wouldn't affect existing programs.

## Reporting Compatibility Issues

If you find a program that works in CP/M MBASIC 5.21 but not here:
1. That's a bug, not a feature
2. Report it with the exact error
3. Include the original program
4. We'll fix it to match MBASIC 5.21 behavior

## See Also

- [Compatibility Guide](compatibility.md) - Detailed compatibility information
- [Not Implemented](not-implemented.md) - Features we intentionally don't support
- [CLI Debugging](../ui/cli/debugging.md) - Using debug commands