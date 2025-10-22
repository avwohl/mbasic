# Language Changes: Interpreted MBASIC → Compiled BASIC

Beyond DEFINT - A Comprehensive Analysis

---

## 1. Variable Scoping

### MBASIC Interpreter (1981)
```basic
10 X = 100                    ' Global variable
20 GOSUB 1000                ' Call subroutine
30 PRINT X                    ' X = 200 (modified by subroutine)
40 END
1000 X = 200                  ' Modifies global X
1010 RETURN
```

**Characteristics:**
- **All variables are global**
- GOSUB subroutines share all variables with caller
- No local variable support
- No parameter passing mechanism
- No way to hide implementation details

### Compiled BASIC (QuickBASIC Era)
```basic
' Main program
DIM SHARED GlobalX AS INTEGER    ' Explicitly shared
GlobalX = 100
CALL MySub(GlobalX)
PRINT GlobalX                     ' X = 200 (modified via parameter)
END

SUB MySub(X AS INTEGER)
  DIM LocalY AS INTEGER          ' Local to this SUB
  LocalY = X * 2                 ' LocalY not visible outside
  X = 200                        ' Modifies parameter (BYREF)
END SUB
```

**Characteristics:**
- **Lexically scoped local variables** in SUB/FUNCTION
- Parameters can be passed BYVAL or BYREF
- Local variables don't affect caller's namespace
- SHARED keyword makes variables explicitly global
- STATIC keyword preserves local variable values between calls

### FOR Loop Variables

**MBASIC:**
```basic
10 FOR I = 1 TO 10
20   PRINT I
30 NEXT I
40 PRINT I                   ' I = 11 (loop variable is global)
```

**Compiled BASIC (could be):**
```basic
FOR I = 1 TO 10
  PRINT I
NEXT I
' I might not exist here, or be in its own scope
```

**Key Difference:** In interpreted MBASIC, loop variables are global and retain their final value. Modern compilers could make loop variables lexically scoped to the loop body.

---

## 2. Control Flow Structures

### MBASIC - Flat with Line Numbers
```basic
10 INPUT "Enter number: ", N
20 IF N < 0 THEN GOTO 100
30 IF N = 0 THEN GOTO 200
40 PRINT "Positive"
50 GOTO 300
100 PRINT "Negative"
110 GOTO 300
200 PRINT "Zero"
300 PRINT "Done"
```

### Compiled BASIC - Structured
```basic
INPUT "Enter number: ", N
SELECT CASE N
  CASE IS < 0
    PRINT "Negative"
  CASE 0
    PRINT "Zero"
  CASE IS > 0
    PRINT "Positive"
END SELECT
PRINT "Done"
```

**New Constructs in Compiled BASIC:**
- `SELECT CASE` / `CASE` / `END SELECT`
- `DO WHILE` / `DO UNTIL` / `LOOP`
- `EXIT FOR` / `EXIT DO` / `EXIT FUNCTION` / `EXIT SUB`
- Optional line numbers (labels instead)
- Block IF with proper END IF

---

## 3. Subroutines vs Procedures

### MBASIC - GOSUB/RETURN Only
```basic
10 GOSUB 1000                ' No parameters
20 PRINT RESULT              ' Must use global variables
30 END

1000 REM Calculate something
1010 RESULT = X * Y + Z      ' All globals
1020 RETURN
```

**Limitations:**
- No parameters
- No return values (except via globals)
- No local variables
- Can't reuse names
- Can't nest calls easily
- Must remember to avoid name conflicts

### Compiled BASIC - SUB and FUNCTION
```basic
' Main program
DIM X AS INTEGER, Y AS INTEGER
X = 10
Y = 20
PRINT Calculate(X, Y)        ' Pass parameters, get return value
END

FUNCTION Calculate(A AS INTEGER, B AS INTEGER) AS INTEGER
  DIM Temp AS INTEGER        ' Local variable
  Temp = A * B + 5
  Calculate = Temp           ' Return value
END FUNCTION
```

**Advantages:**
- Formal parameters
- Return values (FUNCTION)
- Local variables
- Recursion possible
- Cleaner namespace
- Better code reuse

---

## 4. Array Handling

### MBASIC - Dynamic Everything
```basic
10 INPUT "How many elements"; N
20 DIM A(N)                   ' Dynamic sizing at runtime
30 FOR I = 1 TO N
40   A(I) = I * 10
50 NEXT I
60 ERASE A                    ' Deallocate array
70 DIM A(N * 2)              ' Reallocate with different size
```

### Compiled BASIC - Static by Default
```basic
' Default: Static arrays
CONST MAXSIZE = 1000
DIM A(MAXSIZE)                ' Fixed at compile time

' With metacommand:
REM $DYNAMIC
DIM B()                       ' Declare without size
INPUT "How many"; N
REDIM B(N)                    ' Size at runtime (slower)
```

**Compiler Restrictions:**
- Array dimensions must be constants (default mode)
- `$DYNAMIC` metacommand allows runtime sizing (overhead)
- OPTION BASE affects all arrays in module
- Multi-dimensional array access optimized at compile time

---

## 5. Type System

### MBASIC - Duck Typing with DEF
```basic
10 X = 5.5                   ' X is single-precision
20 PRINT X                   ' 5.5
30 DEFINT X                  ' Now X is integer
40 X = 5.5                   ' X becomes 6 (rounded)
50 PRINT X                   ' 6
```

### Compiled BASIC - Static Typing
```basic
' All DEFINT/DEFSNG/DEFDBL/DEFSTR collected first
DEFINT I-N                   ' Integer range
DEFSNG A-H, O-Z             ' Single precision ranges

' Variable types fixed at compile time throughout program
DIM X AS DOUBLE              ' Explicit type declaration
DIM Y AS STRING * 20         ' Fixed-length string

TYPE PersonRecord            ' User-defined types
  Name AS STRING * 30
  Age AS INTEGER
  Salary AS SINGLE
END TYPE

DIM Employee AS PersonRecord
```

**Compiler Features:**
- `AS type` explicit type declarations
- User-defined TYPEs (records/structs)
- Fixed-length strings (`STRING * n`)
- Stricter type checking
- Type conversion must be explicit

---

## 6. Line Numbers and Labels

### MBASIC - Line Numbers Required
```basic
10 PRINT "Start"
20 IF X > 0 THEN GOTO 100
30 PRINT "X is not positive"
40 GOTO 110
100 PRINT "X is positive"
110 PRINT "End"
```

### Compiled BASIC - Labels Optional
```basic
PRINT "Start"
IF X > 0 THEN GOTO PositiveBranch
PRINT "X is not positive"
GOTO Done

PositiveBranch:
  PRINT "X is positive"

Done:
  PRINT "End"
```

**Advantages:**
- Meaningful label names
- No need to renumber
- Easier to maintain
- Can still use line numbers if desired
- Line numbers become optional

---

## 7. String Handling

### MBASIC - Fixed or Variable
```basic
10 A$ = "Hello"              ' Variable-length string
20 B$ = "World is long"
30 A$ = A$ + " " + B$       ' Concatenation, reallocation
```

### Compiled BASIC - Fixed Length Option
```basic
' Variable-length (like MBASIC)
DIM A AS STRING
A = "Hello"

' Fixed-length (more efficient in compiled code)
DIM B AS STRING * 80         ' Exactly 80 characters
B = "Hello"                  ' Padded with spaces

' For record structures
TYPE Buffer
  Data AS STRING * 512       ' Fixed allocation
END TYPE
```

**Compiler Advantages:**
- Fixed-length strings avoid heap allocation
- Better for arrays of strings
- Predictable memory layout
- Useful for file I/O buffers

---

## 8. Modular Programming

### MBASIC - Single Monolithic File
```basic
10 REM Everything in one file
20 REM All code is sequential
30 REM All variables global
40 REM Hard to organize large programs
```

### Compiled BASIC - Multiple Modules
```basic
' Module1.BAS
REM $INCLUDE: 'SharedDefs.bi'
DECLARE SUB ProcessData()

DIM SHARED AppData AS DataType

SUB ProcessData
  ' Implementation here
END SUB

' Main.BAS
REM $INCLUDE: 'SharedDefs.bi'
DECLARE SUB ProcessData()

ProcessData                  ' Call from another module
```

**Compiler Features:**
- `$INCLUDE` metacommand
- Separate compilation units
- DECLARE statements for forward references
- Linker combines modules
- Better organization for large projects

---

## 9. Error Handling

### MBASIC - Basic ON ERROR
```basic
10 ON ERROR GOTO 9000
20 INPUT "Enter number: ", N
30 X = 100 / N               ' May cause divide by zero
40 PRINT X
50 END

9000 PRINT "Error: "; ERR, ERL
9010 RESUME NEXT
```

### Compiled BASIC - Enhanced Error Handling
```basic
ON ERROR GOTO ErrorHandler
INPUT "Enter number: ", N
X = 100 / N
PRINT X
END

ErrorHandler:
  SELECT CASE ERR
    CASE 11                  ' Division by zero
      PRINT "Cannot divide by zero"
      RESUME NEXT
    CASE 53                  ' File not found
      PRINT "File missing"
      RESUME
    CASE ELSE
      PRINT "Unexpected error: "; ERR
      END
  END SELECT
```

**Compiler Enhancements:**
- More error codes
- Better error context
- RESUME options (NEXT, line number, label)
- Error handling compiled more efficiently
- May require `/E` compiler flag

---

## 10. Metacommands and Compiler Directives

### MBASIC - No Metacommands
```basic
REM Just regular comments
REM No special compiler control
```

### Compiled BASIC - Rich Metacommands
```basic
REM $STATIC                  ' Static array allocation (default)
REM $DYNAMIC                 ' Dynamic array allocation
REM $INCLUDE: 'file.bi'     ' Include file
REM $DEBUG                   ' Include debug info
REM $NODEBUG                 ' Strip debug info
REM $COMPILE                 ' Mark as compilable code
```

**Purpose:**
- Control compilation behavior
- Conditional compilation
- Include external files
- Optimize/debug modes
- Module linking

---

## 11. File I/O

### MBASIC - Sequential and Random
```basic
10 OPEN "DATA.TXT" FOR OUTPUT AS #1
20 PRINT #1, "Hello"
30 CLOSE #1

100 OPEN "R", #2, "RANDOM.DAT", 128
110 FIELD #2, 80 AS N$, 48 AS A$
120 LSET N$ = "John"
130 PUT #2, 1
140 CLOSE #2
```

### Compiled BASIC - Extended I/O
```basic
' Sequential files (same as MBASIC)
OPEN "DATA.TXT" FOR OUTPUT AS #1
PRINT #1, "Hello"
CLOSE #1

' Random access with TYPE (easier)
TYPE PersonRecord
  Name AS STRING * 80
  Address AS STRING * 48
END TYPE

DIM Person AS PersonRecord
Person.Name = "John"

OPEN "RANDOM.DAT" FOR RANDOM AS #2 LEN = LEN(Person)
PUT #2, 1, Person
CLOSE #2

' Binary file access
OPEN "BINARY.DAT" FOR BINARY AS #3
PUT #3, , Person              ' Position auto-increments
CLOSE #3
```

**Compiler Improvements:**
- BINARY file mode
- Direct TYPE support for records
- Better integration with user-defined types
- Automatic length calculation

---

## 12. Optimization Opportunities

### Interpreted MBASIC
- Each line tokenized but still interpreted
- Variable lookup every reference
- No type inference
- No dead code elimination
- No loop optimization

### Compiled BASIC
- **Constant folding**: `X = 5 * 10 + 3` → `X = 53` at compile time
- **Common subexpression elimination**: Reuse computed values
- **Loop optimization**: Hoist invariant code out of loops
- **Inline functions**: Small functions inlined
- **Register allocation**: Keep hot variables in registers
- **Dead code elimination**: Remove unreachable code
- **Peephole optimization**: Local instruction patterns

---

## Summary of Key Changes for Our Compiler

### Must Implement for Basic Compilation:
1. ✓ **Global DEF type statements** - First pass collection
2. ✓ **Static array dimensions** - Constant expressions only
3. ✓ **Fixed variable types** - Type determined at compile time
4. ✓ **Remove interactive commands** - Not applicable to compiled code
5. **Line number to address mapping** - For GOTO/GOSUB
6. **Constant expression evaluation** - For DIM and other compile-time needs

### Should Implement for Better Compiler:
7. **Named labels** - Alternative to line numbers
8. **Local variables in SUB/FUNCTION** - Lexical scoping
9. **Parameter passing** - BYVAL and BYREF
10. **SELECT CASE** - Structured control flow
11. **EXIT FOR/DO/SUB/FUNCTION** - Early exit from blocks
12. **User-defined TYPEs** - Record structures
13. **$INCLUDE metacommand** - Modular compilation
14. **Optimization passes** - Constant folding, CSE, etc.

### Could Implement for Advanced Features:
15. **$DYNAMIC mode** - Runtime array sizing
16. **Separate compilation** - Multiple modules
17. **DECLARE statements** - Forward references
18. **SHARED/STATIC keywords** - Fine-grained scope control
19. **Recursion support** - For FUNCTION/SUB
20. **Block IF/THEN/ELSE/ELSEIF/ENDIF** - Nested conditionals

---

## Impact on Parser Design

Our parser must:

1. **Two-pass minimum**:
   - Pass 1: Collect DEFINT/DEFSNG/DEFDBL/DEFSTR, build type map
   - Pass 2: Parse with type information available

2. **Symbol table with type information**:
   - Variable name → type mapping
   - Array name → dimensions and type
   - Label/line number → code location

3. **Constant expression evaluator**:
   - For DIM array bounds
   - For CONST declarations
   - For optimization

4. **Scope stack (if implementing SUB/FUNCTION)**:
   - Track current scope
   - Local vs module-level variables
   - Parameter lists

5. **Control flow graph**:
   - All GOTO/GOSUB targets
   - Reachable code analysis
   - Loop structure identification
