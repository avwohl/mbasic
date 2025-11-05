# File Format Compatibility

## Line Endings (Newlines)

MBASIC saves all program files using **Unix-style line endings** (`\n`, also called LF).

### What This Means

- **Loading files**: MBASIC automatically handles files with any line ending style:
  - Unix (`\n` / LF)
  - Windows (`\r\n` / CRLF)
  - Classic Mac (`\r` / CR)

- **Saving files**: MBASIC always saves with Unix line endings (`\n`)

### Why Unix Line Endings?

- **Cross-platform compatibility**: Modern text editors on all platforms (Windows, Mac, Linux) handle LF correctly
- **Modern Windows support**: Windows Notepad (since Windows 10 1809), VS Code, Notepad++, and other editors all support LF
- **Web UI consistency**: Browser-based editing works the same on all operating systems
- **Git-friendly**: Standard for version control systems

### Using Files with CP/M Emulators

If you want to transfer saved BASIC files to a **CP/M emulator** (such as `tnylpo`), you may need to convert the line endings from LF (`\n`) to CRLF (`\r\n`), as CP/M systems expect CRLF line endings.

#### Converting to CP/M Format

**On Linux/Mac:**
```bash
# Convert LF to CRLF
unix2dos yourfile.bas

# Or using sed
sed -i 's/$/\r/' yourfile.bas

# Or using Python
python3 -c "import sys; data=open('yourfile.bas','rb').read(); open('yourfile.bas','wb').write(data.replace(b'\n',b'\r\n'))"
```

**On Windows (PowerShell):**
```powershell
# Using PowerShell to convert
(Get-Content yourfile.bas) | Set-Content yourfile.bas
```

**Using a utility script:**

MBASIC includes a utility script for CP/M conversion:
```bash
# Convert a file to CP/M format (CRLF line endings)
python3 utils/convert_to_cpm.py yourfile.bas
```

### Assembly Source Files (.mac)

**Note**: Assembly source files (`.mac`) in the `docs/history/original_mbasic_src/` directory retain their original CRLF line endings because they are intended for use with the CP/M M80 assembler, which requires CRLF format.

## Character Encoding

MBASIC uses **UTF-8** encoding for all files. However, when loading files:

- **Parity bits are cleared**: High bit (bit 7) is stripped from characters
- **Control characters are filtered**: Most control characters are removed (except CR, LF, TAB)
- **CP/M EOF markers removed**: Ctrl+Z (`\x1a`) end-of-file markers are stripped

This ensures compatibility with files created on vintage systems that may have used 7-bit ASCII with parity or included CP/M-specific markers.

## File Extensions

MBASIC recognizes these file extensions:

- `.bas` - Standard BASIC program files (recommended)
- `.BAS` - Uppercase variant (also supported)
- `.txt` - Plain text files containing BASIC code

All are treated identically when loading.

## Line Number Format

BASIC program lines must start with a line number (1-65535) followed by at least one space:

```basic
10 PRINT "HELLO"
20 FOR I=1 TO 10
30 PRINT I
40 NEXT I
```

Lines without line numbers are ignored when loading files.

## Compatibility Notes

### From Real MBASIC 5.21

Files created with the original Microsoft MBASIC 5.21 (from CP/M systems) can be loaded directly. MBASIC will:
- Convert CRLF line endings to LF automatically
- Strip any CP/M EOF markers (`^Z`)
- Clear parity bits if present

### To Real MBASIC 5.21

To transfer files TO a real MBASIC 5.21 system or CP/M emulator:
1. Save the file in MBASIC
2. Convert line endings to CRLF (see "Converting to CP/M Format" above)
3. Optionally add CP/M EOF marker: `echo -e '\x1a' >> yourfile.bas`

### Other BASIC Dialects

MBASIC implements the Microsoft MBASIC 5.21 dialect. Files from other BASIC interpreters (GW-BASIC, QBASIC, etc.) may load but could have syntax differences. See the language documentation for specifics.
