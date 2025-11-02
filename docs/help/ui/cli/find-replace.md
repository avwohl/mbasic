# Find and Replace (CLI)

## Current Status

The CLI backend **does not have** built-in Find/Replace commands. The CLI follows the classic MBASIC-80 command set, which did not include these features.

## Alternative Methods

### Finding Text in Your Program

#### Method 1: LIST with Line Ranges
Search visually by listing portions of your program:

```
LIST 100-200     ' List lines 100 to 200
LIST 500-        ' List from line 500 to end
LIST -100        ' List from start to line 100
```

#### Method 2: Save and Search Externally
```
SAVE "TEMP.BAS"
```
Then use shell commands:
```bash
grep "SEARCH_TERM" TEMP.BAS
grep -n "PRINT" TEMP.BAS  # Show line numbers
```

#### Method 3: Use LIST and Visual Scan
```
LIST            ' Show entire program
```
Scroll through output to find text.

### Replacing Text

#### Method 1: Direct Line Replacement
To replace text, retype the entire line:

```
100 PRINT "Old text"    ' Original line
100 PRINT "New text"    ' Type this to replace
```

#### Method 2: Delete and Re-enter
```
100             ' Delete line 100
100 PRINT "New" ' Add new line 100
```

#### Method 3: External Editor
```
SAVE "PROGRAM.BAS"
```
Edit in external editor, then:
```
NEW
LOAD "PROGRAM.BAS"
```

## Batch Operations

### Replacing Variable Names

If you need to rename a variable throughout your program:

1. Save the program:
```
SAVE "ORIGINAL.BAS"
```

2. Use external tools:
```bash
sed 's/OLDVAR/NEWVAR/g' ORIGINAL.BAS > MODIFIED.BAS
```

3. Load modified version:
```
NEW
LOAD "MODIFIED.BAS"
```

### Finding All Occurrences

To find all uses of a variable or statement:

```
SAVE "SEARCH.BAS"
```

In shell:
```bash
grep -n "VARIABLE_NAME" SEARCH.BAS
grep -n "GOSUB" SEARCH.BAS
```

## Using Other UIs

For built-in Find/Replace, use the Tk UI:

```bash
# Start Tk UI instead of CLI
python3 mbasic --ui tk
```

Tk UI provides:
- Ctrl+F for Find dialog
- Ctrl+H for Replace dialog
- F3 for Find Next
- Visual highlighting

## Tips for CLI Users

1. **Use meaningful line numbers** - Group related code
2. **Comment your code** - Makes visual searching easier
3. **Keep procedures together** - Related SUBs in sequence
4. **Use consistent naming** - Easier to find/replace manually

## Why No Find/Replace in CLI?

The CLI maintains compatibility with original MBASIC-80, which predated modern text editing features. The CLI focuses on:
- Authentic classic experience
- Command-line automation
- Batch processing
- Testing and debugging

For modern editing conveniences, we recommend the Tk or Web UIs.

## Examples

### Example: Finding a Subroutine

```
REM Find subroutine at line 1000
LIST 1000-1100
```

### Example: Replacing a PRINT Statement

```
REM Original
250 PRINT "Hello"

REM To replace, just retype:
250 PRINT "Goodbye"
```

### Example: Finding All GOSUBs

```
SAVE "TEMP.BAS"
REM Then in shell: grep GOSUB TEMP.BAS
```

## See Also

- [CLI Commands](index.md) - Basic CLI operations
- [Debugging Commands](debugging.md) - CLI debugging features
- [Tk Features](../tk/features.md) - Modern UI with Find/Replace