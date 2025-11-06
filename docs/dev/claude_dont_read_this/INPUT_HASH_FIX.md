# INPUT #filenum Implementation - MBASIC 5.21 Compiler

## Summary

Implemented `INPUT #filenum, variables` syntax for reading from files, completing the file I/O statement set alongside `PRINT #filenum`. This resulted in **+1 file successfully parsed** (31.1% → 31.5%, **+0.4%**) and reduced "Expected IDENTIFIER, got HASH" errors from 7 to 1 file (**-85.7% reduction**).

## Implementation Date

2025-10-22

## Problem Analysis

### The Issue

**Error**: "Expected IDENTIFIER, got HASH" (7 files affected before fix)

**Example failing code**:
```basic
200 INPUT #2,RU
300 INPUT #1, NAME$, AGE%, SCORE
```

**Root cause**: INPUT statement didn't support the `#filenum` syntax for reading from files, only keyboard input was supported.

### What is INPUT #filenum?

In MBASIC 5.21, INPUT reads data from keyboard or files:

```basic
' Read from keyboard:
10 INPUT "Enter name"; NAME$

' Read from file:
20 OPEN "DATA.TXT" FOR INPUT AS #1
30 INPUT #1, NAME$, AGE, SCORE
40 CLOSE #1
```

The `#` symbol followed by a file number identifies which file to read from.

---

## Implementation

### Files Modified

1. **ast_nodes.py** (lines 81-93) - Added file_number field to InputStatementNode
2. **parser.py** (lines 992-1064) - Updated parse_input() to handle #filenum

### AST Node Changes

**Before**:
```python
@dataclass
class InputStatementNode:
    """INPUT statement - read from keyboard"""
    prompt: Optional['ExpressionNode']
    variables: List['VariableNode']
    line_num: int = 0
    column: int = 0
```

**After**:
```python
@dataclass
class InputStatementNode:
    """INPUT statement - read from keyboard or file

    Syntax:
        INPUT var1, var2           - Read from keyboard
        INPUT "prompt"; var1       - Read with prompt
        INPUT #filenum, var1       - Read from file
    """
    prompt: Optional['ExpressionNode']
    variables: List['VariableNode']
    file_number: Optional['ExpressionNode'] = None  # For INPUT #n, ...
    line_num: int = 0
    column: int = 0
```

### Parser Implementation

**parse_input() enhancement**:
```python
def parse_input(self) -> InputStatementNode:
    """Parse INPUT statement

    Syntax:
        INPUT var1, var2           - Read from keyboard
        INPUT "prompt"; var1       - Read with prompt
        INPUT #filenum, var1       - Read from file
    """
    token = self.advance()

    # Check for file number: INPUT #n, ...
    file_number = None
    if self.match(TokenType.HASH):
        self.advance()  # Skip #
        file_number = self.parse_expression()
        # Expect comma after file number
        if self.match(TokenType.COMMA):
            self.advance()

    # Optional prompt string (only for keyboard input, not file input)
    prompt = None
    if file_number is None and self.match(TokenType.STRING):
        prompt = StringNode(
            value=self.advance().value,
            line_num=token.line,
            column=token.column
        )
        # Expect semicolon or comma after prompt
        if self.match(TokenType.SEMICOLON, TokenType.COMMA):
            self.advance()

    # Parse variable list
    variables: List[VariableNode] = []
    while not self.at_end_of_line() and not self.match(TokenType.COLON):
        var_token = self.expect(TokenType.IDENTIFIER)

        # Check for array subscripts
        subscripts = None
        if self.match(TokenType.LPAREN):
            self.advance()
            subscripts = []

            # Parse subscript expressions
            while not self.match(TokenType.RPAREN):
                subscripts.append(self.parse_expression())

                if self.match(TokenType.COMMA):
                    self.advance()
                elif not self.match(TokenType.RPAREN):
                    raise ParseError("Expected , or ) in array subscript", self.current())

            self.expect(TokenType.RPAREN)

        variables.append(VariableNode(
            name=var_token.value,
            type_suffix=self.get_type_suffix(var_token.value),
            subscripts=subscripts,
            line_num=var_token.line,
            column=var_token.column
        ))

        if self.match(TokenType.COMMA):
            self.advance()
        else:
            break

    return InputStatementNode(
        prompt=prompt,
        variables=variables,
        file_number=file_number,  # NEW
        line_num=token.line,
        column=token.column
    )
```

**Key features**:
- Check for `#` at start of INPUT statement
- Parse file number expression
- Expect comma after file number
- Prompt only allowed for keyboard input (file_number is None)
- Rest of parsing unchanged (variables, arrays)

---

## Test Results

### Before Implementation

**Corpus**: 235 MBASIC-compatible files
- **Successfully parsed**: 73 files (31.1%)
- **Parser errors**: 162 files (68.9%)
- **"Expected IDENTIFIER, got HASH" errors**: 7 files

### After Implementation

**Corpus**: 235 MBASIC-compatible files
- **Successfully parsed**: 74 files (31.5%) ✓ **+1 file**
- **Parser errors**: 161 files (68.5%) ✓ **-1 error**
- **"Expected IDENTIFIER, got HASH" errors**: 1 file ✓ **-6 files (85.7% reduction)**

**Improvement**: **+0.4% success rate**

---

## New Successfully Parsed Files

1 additional file now parses successfully:

1. **star.bas** - Star field simulation program

**Total new statements**: Additional file I/O operations now supported

---

## What Now Works

### Basic File Input

```basic
10 OPEN "INPUT.TXT" FOR INPUT AS #1
20 INPUT #1, A$
30 CLOSE #1
```

### Multiple Variables

```basic
100 INPUT #1, NAME$, AGE, SCORE
110 INPUT #2, X, Y, Z
```

### With Arrays

```basic
200 INPUT #1, A(I), B(J)
```

### Dynamic File Numbers

```basic
300 F = 2
310 INPUT #F, DATA$
```

### Complex Example from Real Code

```basic
' From aircraft.bas (now fixed)
200 INPUT #2,RU

' From star.bas
100 OPEN "STARS.DAT" FOR INPUT AS #1
110 INPUT #1, COUNT
120 FOR I = 1 TO COUNT
130   INPUT #1, X(I), Y(I), BRIGHTNESS(I)
140 NEXT I
150 CLOSE #1
```

---

## Technical Notes

### File I/O Completeness

With this implementation, we now support the core file I/O statement set:

| Statement | Syntax | Status |
|-----------|--------|--------|
| OPEN | `OPEN "file" FOR mode AS #n` | ✅ Supported |
| CLOSE | `CLOSE #n` | ✅ Supported |
| PRINT #n | `PRINT #n, data` | ✅ Supported (prev fix) |
| LPRINT #n | `LPRINT #n, data` | ✅ Supported (prev fix) |
| **INPUT #n** | **`INPUT #n, vars`** | **✅ NEW** |
| LINE INPUT #n | `LINE INPUT #n, var$` | ⚠️ Needs update |
| WRITE #n | `WRITE #n, data` | ⚠️ Not yet implemented |

### Design Decision: Prompt Exclusion

File input doesn't use prompts (keyboard only):
```basic
' Valid:
INPUT "Enter name"; NAME$          ' Keyboard with prompt
INPUT #1, NAME$                    ' File without prompt

' Invalid:
INPUT #1, "prompt"; NAME$          ' Prompts don't make sense for files
```

The parser enforces this: `if file_number is None and self.match(TokenType.STRING)`

### Syntax Consistency

INPUT #filenum follows same pattern as PRINT #filenum:
- `#` immediately before file number
- Comma after file number
- Rest follows normal syntax

```python
# PRINT implementation (from HASH fix):
if self.match(TokenType.HASH):
    self.advance()  # Skip #
    file_number = self.parse_expression()
    if self.match(TokenType.COMMA):
        self.advance()

# INPUT implementation (this fix):
if self.match(TokenType.HASH):
    self.advance()  # Skip #
    file_number = self.parse_expression()
    if self.match(TokenType.COMMA):
        self.advance()
```

Identical pattern ensures consistency across file I/O statements.

---

## Code Statistics

### Lines Modified

- **ast_nodes.py**: +5 lines (added file_number field and docs)
- **parser.py**: +15 lines (file number handling in parse_input)

**Total**: ~20 lines added

### Code Quality

✅ **Correct** - Follows MBASIC 5.21 INPUT syntax
✅ **Complete** - Handles all INPUT forms (keyboard, prompt, file)
✅ **Consistent** - Matches PRINT #filenum pattern
✅ **No regressions** - All previous tests pass

---

## Comparison to Other Improvements

### Recent Fixes

| Feature | Files Added | Success Rate | Error Reduction | Impact |
|---------|-------------|--------------|-----------------|---------|
| HASH file I/O (PRINT) | +2 | 26.8% | HASH: -82.4% | Medium |
| ELSE keyword | +6 | 29.4% | "EQUAL,NUMBER": -23.5% | High |
| Keyword splitting | +4 | 31.1% | "EQUAL,NEWLINE": -28.6% | Medium-High |
| **INPUT #filenum** | **+1** | **31.5%** | **"ID,HASH": -85.7%** | **Medium** |

**Key achievement**: 85.7% reduction in "Expected IDENTIFIER, got HASH" errors!

---

## Session Progress Summary

### Timeline (Cleaned Corpus)

| Implementation | Success Rate | Files | Change |
|---------------|--------------|-------|---------|
| Corpus cleaned | 17.4% | 41 | baseline |
| INKEY$ + LPRINT | 20.9% | 49 | +8 |
| Mid-statement comments | 22.6% | 53 | +4 |
| DATA unquoted strings | 22.6% | 53 | +0 |
| RUN statement | 26.0% | 61 | +8 |
| CR line endings | 26.0% | 61 | +0 |
| HASH file I/O (PRINT) | 26.8% | 63 | +2 |
| ELSE keyword | 29.4% | 69 | +6 |
| Keyword splitting | 31.1% | 73 | +4 |
| **INPUT #filenum** | **31.5%** | **74** | **+1** |

**Total improvement**: 41 → 74 files (**+80.5% increase**)

**Milestone**: Maintaining 31%+ success rate

---

## Top Remaining Errors

After INPUT #filenum fix:

1. **Expected EQUAL, got NEWLINE (16 files)** - Assignment parsing
2. **Expected EQUAL, got NUMBER (15 files)** - Increased from 13
3. **BACKSLASH (11 files)** - Line continuation or other issues
4. **Expected EQUAL, got IDENTIFIER (11 files)** - Increased from 9
5. **ELSE (10 files)** - Additional ELSE patterns

---

## Why This Matters

### File I/O is Essential

Programs commonly use INPUT #filenum for:
- **Data loading**: Reading configuration files
- **Database access**: Reading records from data files
- **Batch processing**: Processing input files
- **Data import**: Reading CSV, text files

### Example Use Cases

**Configuration file**:
```basic
100 OPEN "CONFIG.DAT" FOR INPUT AS #1
110 INPUT #1, SCREENMODE, BAUDRATE, TIMEOUT
120 CLOSE #1
```

**Data file processing**:
```basic
200 OPEN "SCORES.DAT" FOR INPUT AS #2
210 WHILE NOT EOF(2)
220   INPUT #2, NAME$, SCORE
230   PRINT NAME$; ": "; SCORE
240 WEND
250 CLOSE #2
```

**Record reading**:
```basic
300 OPEN "RECORDS.TXT" FOR INPUT AS #3
310 FOR I = 1 TO N
320   INPUT #3, ID(I), NAME$(I), VALUE(I)
330 NEXT I
340 CLOSE #3
```

---

## Historical Context

### CP/M File Operations

In CP/M systems (1970s-1980s), file I/O was critical:
- **Floppy disks**: 8", 5.25" disks were primary storage
- **Sequential files**: Text files with line-by-line data
- **Random access**: FIELD/GET/PUT for binary data
- **Standard pattern**: OPEN → INPUT/PRINT → CLOSE

**Typical CP/M program structure**:
```basic
10 ' Open input and output files
20 OPEN "I", #1, "INPUT.DAT"
30 OPEN "O", #2, "OUTPUT.DAT"
40 ' Process data line by line
50 WHILE NOT EOF(1)
60   INPUT #1, DATA$
70   PRINT #2, PROCESS$(DATA$)
80 WEND
90 CLOSE #1, #2
```

### MBASIC 5.21 File I/O

MBASIC-80 version 5.21 (1981) supported:
- **Sequential files**: INPUT #n, PRINT #n, LINE INPUT #n
- **Random access**: FIELD, GET, PUT
- **File numbers**: 1-15 typical range
- **Mixed operations**: Could read and write multiple files simultaneously

---

## Remaining File I/O Work

### Still Need Implementation

1. **LINE INPUT #n, variable$** - Read entire line from file
   - Currently: LINE INPUT only works for keyboard
   - Need: Add #filenum support like INPUT

2. **WRITE #n, expressions** - Formatted write with quotes/commas
   - Similar to PRINT but adds formatting
   - Used for CSV-style output

3. **INPUT #n with EOF handling** - Better end-of-file detection
   - Many programs use: `WHILE NOT EOF(1) : INPUT #1, ... : WEND`
   - EOF function already supported, just needs testing

### Future Enhancements

1. **Random access file I/O**:
   - FIELD #n, width1 AS var1$, width2 AS var2$
   - GET #n, record_number
   - PUT #n, record_number

2. **Additional file functions**:
   - LOC(n) - Current position
   - LOF(n) - Length of file
   - CVS/CVD/MKS$/MKD$ - Convert binary data

---

## Conclusions

### Key Achievements

1. **INPUT #filenum support** ✓ Can now read from files
2. **1 new file parsing** ✓ star.bas
3. **85.7% error reduction** ✓ "Expected IDENTIFIER, got HASH" 7 → 1 file
4. **File I/O nearly complete** ✓ Core operations now supported
5. **Zero regressions** ✓ All previous tests still pass

### What This Enables

With INPUT #filenum support, programs can now:
- ✅ Read data from files
- ✅ Process sequential data files
- ✅ Load configuration from files
- ✅ Import data for processing

**Critical component of complete file I/O support!**

---

## Related Implementations

This fix completes a trilogy of file I/O implementations:

### 1. PRINT #filenum (HASH_FILE_IO_FIX.md)
- Write data to files
- `PRINT #1, "output"`
- +2 files, -82.4% HASH errors

### 2. LPRINT #filenum (HASH_FILE_IO_FIX.md)
- Printer output to files
- `LPRINT #2, "report"`
- Same fix as PRINT

### 3. INPUT #filenum (this fix)
- Read data from files
- `INPUT #1, variable`
- +1 file, -85.7% "Expected IDENTIFIER, got HASH" errors

Together, these provide the core I/O operations needed for most MBASIC programs.

---

**Implementation Date**: 2025-10-22
**Files Modified**: 2 (ast_nodes.py, parser.py)
**Lines Added**: ~20
**Success Rate**: 31.1% → 31.5% (+0.4%)
**Files Added**: 1 (+1.4%)
**"Expected IDENTIFIER, got HASH" Errors**: 7 → 1 (-85.7%)
**Status**: ✅ Complete and Tested
