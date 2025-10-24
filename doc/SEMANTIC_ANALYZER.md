# BASIC Compiler Semantic Analyzer

The semantic analyzer performs static analysis on BASIC programs to validate compiler requirements and enable advanced features.

## Overview

The semantic analyzer is a **separate phase** from the interpreter. While the interpreter executes programs dynamically, the semantic analyzer validates programs for **compilation** according to the 1980 Microsoft BASIC Compiler requirements.

**Location**: `src/semantic_analyzer.py`

## Key Features

### 1. Runtime Constant Evaluation

**Major Enhancement**: The semantic analyzer tracks variable values as the program is analyzed, allowing DIM statements to use variables as subscripts if those variables have known constant values.

**Original 1980 Compiler**: DIM subscripts must be integer constants only
```basic
DIM A(10)              ' OK
DIM B(N)               ' ERROR - variable not allowed
```

**Our Compiler**: DIM subscripts can be constant expressions OR variables with known constant values
```basic
10 N% = 10             ' N% is now a known constant
20 M% = N% * 2         ' M% is now a known constant (20)
30 DIM A(N%), B(M%)    ' OK! A(10), B(20)
40 DIM C(N%+M%)        ' OK! C(30)
```

### How It Works

The semantic analyzer maintains a **runtime constant table** that tracks which variables have known constant values at each point in the program:

1. **Assignment tracking**: When `N% = 10` is encountered, N% is marked as constant with value 10
2. **Expression evaluation**: When `M% = N% * 2` is encountered, the expression is evaluated using N%'s known value, and M% becomes constant = 20
3. **Conditional evaluation**: When `IF DEBUG% = 1 THEN N% = 10 ELSE N% = 5` is encountered:
   - If DEBUG% has a known value, the condition is evaluated at compile time and only the taken branch is analyzed
   - If DEBUG% is unknown, both branches are analyzed and constants are merged (only kept if same in both)
4. **DIM validation**: When `DIM A(N%)` is encountered, N%'s value (10) is used
5. **Invalidation**: Variables lose their constant status when:
   - Reassigned to a non-constant expression
   - Used as a FOR loop variable
   - Read via INPUT or READ statements

### 2. Constant Expression Evaluator

Evaluates expressions at compile time when all operands are constants or known-constant variables.

**Supported Operations**:
- Arithmetic: `+`, `-`, `*`, `/`, `\` (integer division), `^`, `MOD`
- Relational: `=`, `<>`, `<`, `>`, `<=`, `>=` (return -1 for true, 0 for false)
- Logical: `AND`, `OR`, `XOR`, `EQV`, `IMP`
- Unary: `-`, `+`, `NOT`
- **Math Functions**: `ABS`, `SQR`, `SIN`, `COS`, `TAN`, `ATN`, `EXP`, `LOG`, `INT`, `FIX`, `SGN`, `CINT`, `CSNG`, `CDBL`
- **User-Defined Functions**: `DEF FN` functions can be evaluated if all arguments are constants
  - Supports nested function calls
  - Can use built-in math functions in the body
  - Parameters are bound to constant values during evaluation
- **Excluded (non-deterministic)**:
  - Random/Time: `RND`, `TIMER`
  - File I/O: `EOF`, `LOC`, `LOF`, `INPUT$`, `INKEY$`
  - System: `PEEK`, `INP`, `FRE`, `POS`, `CSRLIN`, `VARPTR`

**Examples**:
```basic
DIM A(2+3)             ' Evaluates to A(5)
DIM B(10*2+5)          ' Evaluates to B(25)
DIM C(100\3)           ' Evaluates to C(33)
N% = 5
DIM D(N%*4)            ' Evaluates to D(20)
DIM E(INT(SQR(100)))   ' Evaluates to E(10)
DIM F(ABS(-25))        ' Evaluates to F(25)

DEF FN DOUBLE(X) = X * 2
DIM G(FN DOUBLE(5))    ' Evaluates to G(10)
```

### 3. Compile-Time IF/THEN/ELSE Evaluation

The semantic analyzer can evaluate IF conditions at compile time when all operands are known constants.

**How It Works**:

**Case 1: Condition is compile-time constant (evaluates to known value)**
- Only the taken branch is analyzed for constant tracking
- The other branch is completely ignored
- Maximum optimization - dead code elimination

**Example**:
```basic
10 DEBUG% = 1
20 IF DEBUG% = 1 THEN N% = 10 ELSE N% = 5
30 DIM A(N%)                    ' A(10) - only THEN branch taken
```

**Case 2: Condition cannot be evaluated (contains unknown variables)**
- Both branches are analyzed separately
- Constants are merged after the IF
- A variable is only constant after IF if it has the **same value in both branches**

**Example - Merged to constant**:
```basic
10 INPUT X%
20 IF X% > 5 THEN N% = 10 ELSE N% = 10
30 DIM A(N%)                    ' A(10) - both branches set N% = 10
```

**Example - Not constant**:
```basic
10 INPUT X%
20 IF X% > 5 THEN N% = 10 ELSE N% = 5
30 DIM A(N%)                    ' ERROR - N% has different values in branches
```

**Benefits**:
- Enables configuration-based array sizing
- Supports compile-time switches (like C's `#ifdef`)
- Dead code elimination for unused branches
- More flexible than original compiler

### 4. Symbol Tables

Tracks all program symbols with detailed information:

**Variables**:
- Name and type (INTEGER, SINGLE, DOUBLE, STRING)
- Array dimensions (if array)
- First use location (line number)

**Functions** (DEF FN):
- Name and return type
- Parameter list
- Definition location
- Function body expression

**Line Numbers**:
- All line numbers in the program
- Used for validating GOTO/GOSUB targets

### 5. Compiler-Specific Validations

#### Unsupported Commands
Detects commands that don't work in compiled programs:
- `LIST`, `LOAD`, `SAVE`, `MERGE`
- `NEW`, `CONT`, `DELETE`, `RENUM`
- `COMMON` (generates fatal error - not in 1980 compiler)
- `ERASE` (generates fatal error - arrays cannot be redimensioned)

#### Static Loop Nesting
Validates that FOR/NEXT and WHILE/WEND loops are properly nested:
```basic
10 FOR I = 1 TO 10
20   WHILE J < 5
30   WEND             ' OK - proper nesting
40 NEXT I

10 FOR I = 1 TO 10
20   WHILE J < 5
30 NEXT I             ' ERROR - improper nesting
40 WEND
```

#### Array Validation
- Detects redimensioning attempts
- Validates subscripts are constant expressions
- Checks for negative subscripts

### 6. Compilation Switch Detection

Automatically detects when special compilation switches are needed:

- **/E** - Required if program uses `ON ERROR GOTO` with `RESUME <line>`
- **/X** - Required if program uses `RESUME`, `RESUME NEXT`, or `RESUME 0`
- **/D** - Required if program uses `TRON` or `TROFF`

### 7. Line Number Validation

Validates all GOTO/GOSUB/ON...GOTO targets exist:
```basic
10 GOTO 100            ' OK if line 100 exists
20 ON X GOTO 100,200   ' OK if lines 100 and 200 exist
30 IF A > 5 THEN 100   ' OK if line 100 exists
```

## Usage

```python
from semantic_analyzer import SemanticAnalyzer
from lexer import tokenize
from parser import Parser

# Parse program
tokens = tokenize(program_source)
parser = Parser(tokens)
program = parser.parse()

# Analyze
analyzer = SemanticAnalyzer()
success = analyzer.analyze(program)

if success:
    print(analyzer.get_report())
    # Proceed to code generation
else:
    print("Errors found:")
    for error in analyzer.errors:
        print(f"  {error}")
```

### 5. Constant Folding Optimization

**Enhancement**: The semantic analyzer identifies and evaluates all constant subexpressions at compile time, enabling significant optimization opportunities.

**What is Constant Folding?**

Constant folding is the process of evaluating expressions at compile time when all operands are constants. This eliminates runtime computation for constant expressions.

**Examples of Constant Folding**:

```basic
10 X = 2 + 3           ' Folded to: X = 5
20 Y = (5 * 6) - 1     ' Folded to: Y = 29
30 Z = SQR(64)         ' Folded to: Z = 8
40 W = SIN(0)          ' Folded to: W = 0
50 N% = 10
60 M% = N% * 2         ' Folded to: M% = 20 (using runtime constant)
70 DEF FN DOUBLE(X) = X * 2
80 A = FN DOUBLE(5)    ' Folded to: A = 10
```

**Types of Expressions Folded**:
- Arithmetic expressions: `(2 + 3) * 4`
- Math function calls: `SQR(16)`, `INT(3.7)`, `SIN(0)`
- Relational operations: `5 = 5`, `10 > 5`
- Logical operations: `-1 AND -1`, `NOT 0`
- User-defined functions: `FN SQUARE(5)` where `DEF FN SQUARE(X) = X * X`
- Runtime constant expressions: `N% + M%` where both have known values

**Benefits**:
1. **Reduced code size**: Constant expressions become single values
2. **Faster execution**: No runtime computation needed
3. **Better optimization**: Enables further optimizations (e.g., dead code elimination)
4. **Analysis visibility**: Report shows all folded expressions for review

**Tracking and Reporting**:

The semantic analyzer tracks all constant folding optimizations and reports them in the analysis output. This helps developers understand what optimizations are being applied.

## Output Example

```
======================================================================
SEMANTIC ANALYSIS REPORT
======================================================================

Symbol Table Summary:
  Variables: 9
  Functions: 1
  Line Numbers: 19

Variables:
  A(10) : SINGLE (line 60)
  B(5,20) : SINGLE (line 60)
  C(5) : SINGLE (line 60)
  D(30) : SINGLE (line 80)
  I : SINGLE (line 120)
  M : SINGLE (line 40)
  N : SINGLE (line 30)
  TOTAL : SINGLE (line 70)
  X : SINGLE (line 100)

Functions:
  FNDOUBLE(X) : SINGLE (line 100)

Constant Folding Optimizations:
  Line 40: (n * 2.0) → 20
  Line 70: (n + m) → 30
  Line 160: SQR(16.0) → 4
  Line 200: (((2.0 + 3.0) * 4.0) - 1.0) → 19

Required Compilation Switches:
  /E

Warnings:
  Required compilation switches: /E
======================================================================
```

## Detailed Examples

### Example 1: Basic Runtime Constants

```basic
10 ROWS% = 10
20 COLS% = 20
30 DIM MATRIX(ROWS%, COLS%)     ' Creates MATRIX(10,20)
```

**Analysis**:
- Line 10: ROWS% becomes constant = 10
- Line 20: COLS% becomes constant = 20
- Line 30: Uses both constants to create 10×20 matrix

### Example 2: Computed Constants

```basic
10 N% = 5
20 M% = N% * 2
30 TOTAL% = N% + M%
40 DIM A(N%), B(M%), C(TOTAL%)  ' Creates A(5), B(10), C(15)
```

**Analysis**:
- Line 10: N% = 5
- Line 20: M% = 5 * 2 = 10
- Line 30: TOTAL% = 5 + 10 = 15
- Line 40: All subscripts evaluated from known constants

### Example 3: Constant Invalidation

```basic
10 N% = 10
20 DIM A(N%)                    ' OK - A(10)
30 INPUT N%                     ' N% no longer constant
40 DIM B(N%)                    ' ERROR - N% has no known value
```

**Analysis**:
- Line 10: N% = 10 (constant)
- Line 20: Uses N% = 10 ✓
- Line 30: INPUT clears N%'s constant status
- Line 40: ERROR - N% value unknown

### Example 4: FOR Loop Invalidation

```basic
10 N% = 10
20 FOR I% = 1 TO N%             ' OK - uses N% = 10
30 NEXT I%
40 DIM A(I%)                    ' ERROR - I% not constant (used in FOR)
```

**Analysis**:
- Line 10: N% = 10 (constant)
- Line 20: FOR uses N%, but I% loses constant status
- Line 40: ERROR - I% was modified by FOR loop

## Comparison with Interpreter

| Feature | Interpreter | Semantic Analyzer |
|---------|------------|-------------------|
| **When executed** | Runtime, dynamically | Compile-time, static |
| **DIM subscripts** | Any expression (evaluated at runtime) | Constant expressions or known-constant variables |
| **Loop nesting** | Dynamic validation | Static validation required |
| **ERASE** | Supported | Not supported (fatal error) |
| **Type checking** | Runtime | Compile-time inference |
| **Error reporting** | Line numbers always available | May report addresses unless /D switch used |

## Error Messages

### Helpful Error Messages

The analyzer provides detailed error messages:

**Unknown variable in DIM**:
```
Line 30: Array subscript in A uses variable N which has no known constant value at this point
```

**Negative subscript**:
```
Line 40: Array subscript cannot be negative in B (evaluated to -5)
```

**Improper nesting**:
```
Line 50: NEXT found but current loop is WHILE (started at line 30)
```

**Undefined line**:
```
Line 60: Undefined line 1000 in ON...GOTO
```

## Implementation Notes

### Runtime Constant Tracking

The `ConstantEvaluator` class maintains a dictionary of known constant values:

```python
runtime_constants = {
    'N': 10,
    'M': 20,
    'TOTAL': 30
}
```

When a variable is assigned:
1. Evaluate the expression
2. If it evaluates to a constant, add to runtime_constants
3. If it doesn't evaluate to a constant, remove from runtime_constants

When a variable is used in FOR, INPUT, READ:
1. Remove from runtime_constants

### Expression Evaluation

The evaluator recursively evaluates expressions:
- Literals → return value
- Variables → look up in runtime_constants
- Binary ops → evaluate operands, apply operation
- Unary ops → evaluate operand, apply operation
- Cannot evaluate → return None

### Example 7: Compile-Time Math Functions

```basic
10 REM Math function evaluation at compile time
20 RADIUS = 10
30 PI = 3.14159
40 REM Trigonometric calculations
50 ANGLE = 0
60 SINE = INT(SIN(ANGLE) * 100)
70 COSINE = INT(COS(ANGLE) * 100)
80 REM Square root calculations
90 PERFECT = 144
100 SIDE = INT(SQR(PERFECT))
110 REM Absolute value and sign
120 NEG = -50
130 POSITIVE = ABS(NEG)
140 SIGN = SGN(NEG)
150 REM Create arrays with computed sizes
160 DIM TRIG(SINE + COSINE), GEOM(SIDE), VALUES(POSITIVE)
```

**Analysis**:
- Line 60: `SIN(0) * 100 = 0` (evaluated at compile time)
- Line 70: `COS(0) * 100 = 100` (evaluated at compile time)
- Line 100: `SQR(144) = 12` (evaluated at compile time)
- Line 130: `ABS(-50) = 50` (evaluated at compile time)
- Line 140: `SGN(-50) = -1` (evaluated at compile time)
- Line 160: Creates `TRIG(100)`, `GEOM(12)`, `VALUES(50)`

**Note**: Non-deterministic functions are NOT evaluated at compile time:
```basic
10 N = INT(RND(1) * 10)
20 DIM A(N)              ' ERROR - RND cannot be evaluated at compile time

10 OPEN "DATA" FOR INPUT AS 1
20 N = LOC(1)
30 DIM A(N)              ' ERROR - LOC depends on runtime file state

10 N = PEEK(1000)
20 DIM A(N)              ' ERROR - PEEK depends on runtime memory state
```

These functions are excluded because their values:
- Cannot be known until the program runs (file position, memory contents, random values)
- May change during program execution (timer, file position)
- Depend on external state (files, hardware ports, system memory)

### Example 8: User-Defined Function Evaluation

```basic
10 REM User-defined functions with compile-time evaluation
20 DEF FN DOUBLE(X) = X * 2
30 DEF FN SQUARE(Y) = Y * Y
40 DEF FN AREA(R) = INT(3.14159 * R * R)
50 DEF FN HYPOTENUSE(A, B) = INT(SQR(A*A + B*B))
60 DEF FN COMBO(Z) = FN DOUBLE(Z) + FN SQUARE(Z)
70 REM Use functions with constants
80 SIZE1 = FN DOUBLE(10)
90 SIZE2 = FN AREA(5)
100 SIZE3 = FN HYPOTENUSE(3, 4)
110 SIZE4 = FN COMBO(6)
120 DIM A(SIZE1), B(SIZE2), C(SIZE3), D(SIZE4)
```

**Analysis**:
- Line 80: `FN DOUBLE(10)` = 20
- Line 90: `FN AREA(5)` = INT(3.14159 * 5 * 5) = 78
- Line 100: `FN HYPOTENUSE(3, 4)` = INT(SQR(9 + 16)) = 5
- Line 110: `FN COMBO(6)` = FN DOUBLE(6) + FN SQUARE(6) = 12 + 36 = 48
- Line 120: Creates `A(20)`, `B(78)`, `C(5)`, `D(48)`

**Key Features**:
- DEF FN functions are evaluated if all arguments are constant
- Nested function calls work (COMBO calls DOUBLE and SQUARE)
- Can use built-in math functions (SQR, INT)
- Parameters are substituted with constant values during evaluation

**Limitations**:
```basic
10 DEF FN BADSUM(X) = X + GLOBAL
20 INPUT N
30 SIZE = FN BADSUM(N)
40 DIM A(SIZE)          ' ERROR - N is not constant (from INPUT)
```

### Example 9: Compile-Time Configuration

```basic
10 REM Compile-time configuration
20 COMPILE% = 1
30 DEBUG% = 0
40 VERSION% = 3
50 REM Conditional sizing
60 IF COMPILE% = 1 THEN BUFSIZE% = 1024 ELSE BUFSIZE% = 256
70 IF DEBUG% = 1 THEN LOGSIZE% = 100 ELSE LOGSIZE% = 10
80 REM Version-specific multiplier
90 IF VERSION% = 1 THEN MULT% = 1
100 IF VERSION% = 2 THEN MULT% = 2
110 IF VERSION% = 3 THEN MULT% = 3
120 TABLESIZE% = BUFSIZE% * MULT%
130 REM Arrays with compile-time evaluated sizes
140 DIM BUFFER(BUFSIZE%), LOGTABLE(LOGSIZE%), WORKTABLE(TABLESIZE%)
```

**Analysis**:
- Line 60: COMPILE% = 1 → BUFSIZE% = 1024 (THEN branch)
- Line 70: DEBUG% = 0 → LOGSIZE% = 10 (ELSE branch)
- Line 110: VERSION% = 3 → MULT% = 3
- Line 120: TABLESIZE% = 1024 * 3 = 3072
- Line 140: Creates BUFFER(1024), LOGTABLE(10), WORKTABLE(3072)

This enables compile-time configuration similar to C preprocessor directives!

## Future Enhancements

Potential improvements:
1. ~~**Flow analysis**: Track constants through branches (IF/THEN/ELSE)~~ ✓ **IMPLEMENTED**
2. **Type checking**: Detect type mismatches at compile time
3. **Dead code detection**: Identify unreachable code
4. **Optimization hints**: Suggest integer variables for performance
5. **Array bounds tracking**: Validate array accesses at compile time
6. **GOTO/GOSUB flow analysis**: Track constants across line jumps
7. **Multi-line IF/THEN/ELSE**: Support structured IF blocks

## References

- [Compiler vs Interpreter Differences](COMPILER_VS_INTERPRETER_DIFFERENCES.md)
- Microsoft BASIC Compiler User's Manual (1980)
- BASIC-80 Reference Manual Version 5.21
