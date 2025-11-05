# Sequential File Handling

## Line Ending Differences

### Background

Different operating systems use different line ending conventions:

- **CP/M, DOS, Windows**: CRLF (`\r\n` - two characters: carriage return + line feed)
- **Unix, Linux, Mac OS X**: LF (`\n` - single line feed character)
- **Classic Mac OS (pre-OSX)**: CR (`\r` - single carriage return character)

### Line Ending Support

This MBASIC implementation supports **all three line ending formats** for maximum cross-platform compatibility:

| Line Ending | Format | Support | Example Use |
|-------------|--------|---------|-------------|
| CRLF | `\r\n` | ✅ Yes | CP/M, DOS, Windows files |
| LF | `\n` | ✅ Yes | Linux, Unix, Mac OSX files |
| CR | `\r` | ✅ Yes | Classic Mac OS files |

**Important**: CRLF (`\r\n`) is treated as **one** line ending, not two.

### Behavior Examples

#### Single Line Endings

File with different endings:
```
Line1\n
Line2\r\n
Line3\r
Line4
```

Reads as **4 lines**:
1. "Line1" (LF ending)
2. "Line2" (CRLF ending)
3. "Line3" (CR ending)
4. "Line4" (no ending, at EOF)

#### Double Line Endings (Empty Lines)

File content:
```
Line1\n\nLine3
```

Reads as **3 lines**:
1. "Line1"
2. "" (empty line)
3. "Line3"

**Important**: `\n\n` creates two line endings (empty line between), but `\r\n` is still one line ending.

#### Mixed Line Endings

File content:
```
A\r\n
B\n
C\r
D
```

Reads as **4 lines**: "A", "B", "C", "D"

### Comparison with CP/M MBASIC 5.21

**CP/M MBASIC 5.21** (real hardware):
- **Only** recognizes CRLF (`\r\n`) as line ending
- LF alone or CR alone are **not** recognized as line endings
- Files with LF-only or CR-only endings won't read correctly

**This implementation**:
- Recognizes **all three** formats (CRLF, LF, CR)
- More permissive for cross-platform compatibility
- Can read files created on Linux, Windows, or Mac

**Why the difference?**

CP/M was designed for a single platform with CRLF line endings. This implementation runs on multiple platforms (Linux, Mac, Windows) and needs to handle files from all sources.

### Testing Line Endings

Test program:
```basic
10 OPEN "I", #1, "TESTFILE.TXT"
20 N = 0
30 IF EOF(1) THEN 60
40 LINE INPUT #1, A$
50 N = N + 1: PRINT N; ": ["; A$; "]"
60 IF NOT EOF(1) THEN 30
70 CLOSE #1
80 PRINT "TOTAL LINES:"; N
90 SYSTEM
```

The brackets `[]` make empty lines visible.

## CP/M File Format and ^Z (Control-Z) EOF Marker

### Background

On CP/M 1.x and 2.x systems, files were stored in 128-byte sectors. When a text file did not end exactly on a 128-byte boundary, the remaining bytes in the final sector were filled with padding. To mark the actual end of file, CP/M used a **^Z (Control-Z, ASCII 26)** character as the EOF marker.

### ^Z EOF Behavior

This MBASIC implementation **correctly handles ^Z as EOF** for sequential file input, matching MBASIC 5.21 behavior exactly.

#### When Reading Sequential Files

When using `INPUT #` or `LINE INPUT #` to read from sequential files:

1. **^Z marks end of file** - Reading stops at the first ^Z character encountered
2. **Partial lines returned** - If ^Z appears mid-line, the partial line up to ^Z is returned
3. **Data after ^Z ignored** - Any bytes after ^Z are not read

#### Example: ^Z at End of File

```basic
10 OPEN "I", #1, "DATA.TXT"
20 IF EOF(1) THEN 60
30 LINE INPUT #1, A$
40 PRINT A$
50 GOTO 20
60 CLOSE #1
70 PRINT "EOF reached"
```

If `DATA.TXT` contains:
```
Line 1
Line 2
Line 3
^Z
Junk data
More junk
```

Output:
```
Line 1
Line 2
Line 3
EOF reached
```

The "Junk data" and "More junk" lines after ^Z are **not read**.

#### Example: ^Z Mid-Line

If `DATA.TXT` contains:
```
Line 1
Line 2 has^Z more text
Line 3
```

Output:
```
Line 1
Line 2 has
EOF reached
```

The text " more text" after ^Z is **not read**, and the partial line "Line 2 has" is returned before EOF is signaled.

### Compatibility

This behavior matches:
- ✅ MBASIC 5.21 on CP/M (tested with tnylpo emulator)
- ✅ CP/M text file conventions
- ✅ Most CP/M-era BASIC interpreters

### When ^Z Handling Matters

**You need to be aware of ^Z EOF if:**

1. **Reading CP/M-era files** - Files created on CP/M systems may contain ^Z markers
2. **Binary data in text files** - If byte value 26 (0x1A) appears in data, it will be treated as EOF
3. **Porting from CP/M** - Programs written for CP/M expect this behavior

**You can ignore ^Z if:**

1. **Creating new files** - Modern text files typically don't need ^Z markers
2. **Using random access files** - ^Z is only significant for sequential (text) files
3. **Binary file I/O** - Use random access mode for binary data

### Implementation Details

The ^Z EOF handling is implemented in `_read_line_from_file()` method in the interpreter:

```python
if b == 26:  # ^Z (EOF marker in CP/M)
    file_info['eof'] = True
    if line_bytes:
        return line_bytes.decode('latin-1', errors='replace').rstrip('\r\n')
    return None
```

This ensures:
- Byte value 26 (^Z) triggers EOF
- Partial lines before ^Z are returned
- EOF flag is set to prevent further reads
- Behavior matches CP/M MBASIC 5.21 exactly

### Random Access Files

**Note:** ^Z is **NOT** significant for random access files opened with `OPEN "R"`. Random access files:

- Read/write fixed-length records
- Use `GET` and `PUT` statements
- Treat all bytes (including 26) as data
- Do not recognize EOF markers

### Testing

Test files included in `tests/` directory:

- `ctrlz.txt` - Sequential file with ^Z at end
- `ctrlz2.txt` - Sequential file with ^Z mid-line
- `testeof.bas` - Test program for LINE INPUT
- `testeof2.bas` - Test program for mid-line ^Z

Run tests:
```bash
cd tests/
# Test with our MBASIC
python3 ../mbasic testeof.bas

# Test with real MBASIC 5.21 (requires tnylpo)
(cat testeof.bas && echo "RUN") | tnylpo ../com/mbasic.com
```

Both should produce identical output.

### Summary

| Aspect | Behavior |
|--------|----------|
| **Line Endings** | |
| CRLF support (`\r\n`) | ✅ Yes - CP/M, DOS, Windows |
| LF support (`\n`) | ✅ Yes - Linux, Unix, Mac OSX |
| CR support (`\r`) | ✅ Yes - Classic Mac OS |
| CRLF treated as one ending | ✅ Yes - not counted as two |
| Empty lines (`\n\n`) | ✅ Yes - preserved correctly |
| MBASIC 5.21 line ending compatibility | ⚠️ More permissive (MBASIC only accepts CRLF) |
| **^Z EOF Marker** | |
| ^Z detection | ✅ Yes - triggers EOF immediately |
| Partial line handling | ✅ Returns data up to ^Z |
| Data after ^Z | ❌ Ignored - not read |
| Sequential files | ✅ Applies to INPUT# and LINE INPUT# |
| Random files | ❌ Does not apply (^Z is data) |
| MBASIC 5.21 ^Z compatibility | ✅ Exact match |

### See Also

- [OPEN Statement](../help/common/language/statements/open.md) - Opening files for input/output
- [INPUT# Statement](../help/common/language/statements/input_hash.md) - Reading from sequential files
- [LINE INPUT# Statement](../help/common/language/statements/line-input.md) - Reading lines from sequential files
- [EOF Function](../help/common/language/functions/eof.md) - Checking for end of file
- [File Format Compatibility](FILE_FORMAT_COMPATIBILITY.md) - Line endings and file format compatibility
