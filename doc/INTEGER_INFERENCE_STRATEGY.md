# Integer Inference Strategy: Automatic Type Optimization

## The Approach

**Analyze the program to detect variables that are provably INTEGER, then compile them efficiently. Everything else defaults to DOUBLE.**

This combines:
- ✅ **Simplicity**: Only two code paths (INTEGER and DOUBLE)
- ✅ **Performance**: Automatic optimization without programmer intervention
- ✅ **Safety**: Defaults to DOUBLE when uncertain (no precision loss)

## Detection Rules

### Rule 1: Integer Literal Assignment

```basic
100 X = 10        ' X is INTEGER (literal 10 is integer)
110 Y = 10.5      ' Y is DOUBLE (literal 10.5 is float)
120 Z = 10#       ' Z is DOUBLE (literal has # suffix)
```

**Analysis**:
- Track all assignments to each variable
- If **all** literals assigned are integers → variable is INTEGER
- If **any** literal is float → variable is DOUBLE

### Rule 2: Integer-Only Operations

```basic
100 X = 10
110 Y = 20
120 Z = X + Y     ' Z is INTEGER (both operands are INTEGER)
130 W = X * 2     ' W is INTEGER (X is INT, 2 is INT)
```

**Analysis**:
- Integer + Integer → Integer
- Integer - Integer → Integer
- Integer * Integer → Integer
- Integer / Integer → **DOUBLE** (division always promotes!)
- Integer \ Integer → Integer (integer division)
- Integer MOD Integer → Integer

### Rule 3: FOR Loop Variables

```basic
100 FOR I = 1 TO 100        ' I is INTEGER (bounds are integer)
110   PRINT I
120 NEXT I

100 FOR J = 1.5 TO 10.5     ' J is DOUBLE (bounds are float)
110   PRINT J
120 NEXT J

100 FOR K = 1 TO N          ' K is ??? (N type unknown)
110   PRINT K
120 NEXT K
```

**Analysis**:
- If START, END, and STEP (if present) are all integer constants → INTEGER
- If START, END, or STEP are float → DOUBLE
- If START, END, or STEP are variables:
  - If those variables are INTEGER → INTEGER
  - Otherwise → DOUBLE (conservative)

**Special case**: Loop variables are **strong candidates for INTEGER**
- Most loops use integer bounds
- Integer loop variables are much faster (especially on 8080)
- Worth warning if loop variable becomes DOUBLE

### Rule 4: Array Subscripts

```basic
100 DIM A(100)
110 I = 10
120 X = A(I)      ' I used as subscript → hint that I is INTEGER
```

**Analysis**:
- Array subscripts **should** be INTEGER (subscript must be integer)
- If variable used as subscript → **strongly suggest INTEGER**
- This is a hint, not a requirement (BASIC auto-converts)

### Rule 5: Comparison and Logical Operations

```basic
100 X = 10
110 IF X > 5 THEN PRINT "Yes"   ' Comparison doesn't change X's type
120 Y = (X > 5)                  ' Y receives boolean result (INTEGER -1 or 0)
```

**Analysis**:
- Comparisons return INTEGER (-1 for true, 0 for false)
- Variables receiving comparison results are INTEGER
- Variables **in** comparisons keep their original type

### Rule 6: INPUT and READ (Conservative)

```basic
100 INPUT X       ' X is DOUBLE (unknown what user will type)
110 READ Y        ' Y depends on DATA values
```

**Analysis**:
- **Conservative approach**: Variables from INPUT are DOUBLE
- Variables from READ: analyze DATA statements
  - If all DATA values are integer → INTEGER
  - If any DATA value is float → DOUBLE
  - If mixed → DOUBLE

### Rule 7: Function Arguments (Conservative)

```basic
100 X = SIN(Y)    ' Y used in SIN → probably DOUBLE
110 Z = ABS(W)    ' W could be INTEGER or DOUBLE
```

**Analysis**:
- **Conservative**: Math functions (SIN, COS, LOG, etc.) → DOUBLE
- **Safe**: ABS, SGN, INT, FIX can work with INTEGER or DOUBLE
  - If argument is INTEGER → result is INTEGER
  - If argument is DOUBLE → result is DOUBLE

### Rule 8: Type Suffix Variables (Explicit)

```basic
100 X% = 10       ' X% is INTEGER (explicit suffix)
110 Y! = 20.5     ' Y! is SINGLE (not optimized - use as-is)
120 Z# = 30.3     ' Z# is DOUBLE (explicit)
```

**Analysis**:
- Variables with `%` suffix are **always INTEGER**
- Variables with `!` suffix are **always SINGLE**
- Variables with `#` suffix are **always DOUBLE**
- Variables with `$` suffix are **always STRING**
- **Don't optimize these** - respect programmer's explicit choice

## Algorithm: Integer Inference Analysis

### Phase 1: Collect Variable Assignments

```python
class VariableTypeInference:
    def __init__(self):
        self.var_assignments = {}  # var_name -> [expression_types]
        self.var_uses = {}         # var_name -> [use_contexts]
        self.loop_vars = set()     # Variables used in FOR loops
        self.subscript_vars = set() # Variables used as array subscripts

    def analyze_assignment(self, var_name, expression):
        expr_type = self.infer_expression_type(expression)
        if var_name not in self.var_assignments:
            self.var_assignments[var_name] = []
        self.var_assignments[var_name].append(expr_type)

    def infer_expression_type(self, expr):
        if isinstance(expr, NumberLiteral):
            if expr.has_decimal_point or expr.has_exponent:
                return DOUBLE
            else:
                return INTEGER

        elif isinstance(expr, BinaryOp):
            left_type = self.infer_expression_type(expr.left)
            right_type = self.infer_expression_type(expr.right)

            # Type promotion rules
            if expr.operator == '/':
                return DOUBLE  # Division always promotes
            elif left_type == DOUBLE or right_type == DOUBLE:
                return DOUBLE
            else:
                return INTEGER

        elif isinstance(expr, Variable):
            return self.get_variable_type(expr.name)

        # ... handle other expression types
```

### Phase 2: Classify Variables

```python
def classify_variable_type(self, var_name):
    # Already has type suffix? Use it.
    if var_name.endswith('%'):
        return INTEGER
    if var_name.endswith('!'):
        return SINGLE
    if var_name.endswith('#') or var_name.endswith('$'):
        return DOUBLE if var_name.endswith('#') else STRING

    # No assignments? Default to DOUBLE (conservative)
    if var_name not in self.var_assignments:
        return DOUBLE

    assignment_types = self.var_assignments[var_name]

    # All assignments are INTEGER?
    if all(t == INTEGER for t in assignment_types):
        # Additional checks
        if self.is_used_in_float_context(var_name):
            return DOUBLE  # Used with DOUBLE operands

        if self.is_input_variable(var_name):
            return DOUBLE  # INPUT is conservative

        return INTEGER  # Safe to optimize as INTEGER

    # Any DOUBLE assignment? → DOUBLE
    if any(t == DOUBLE for t in assignment_types):
        return DOUBLE

    # Default to DOUBLE (conservative)
    return DOUBLE
```

### Phase 3: Special Case - FOR Loop Variables

```python
def analyze_for_loop(self, loop_var, start_expr, end_expr, step_expr):
    start_type = self.infer_expression_type(start_expr)
    end_type = self.infer_expression_type(end_expr)
    step_type = self.infer_expression_type(step_expr) if step_expr else INTEGER

    # Mark as loop variable
    self.loop_vars.add(loop_var)

    # If all bounds are INTEGER → loop variable is INTEGER
    if start_type == INTEGER and end_type == INTEGER and step_type == INTEGER:
        self.var_loop_type[loop_var] = INTEGER
        return INTEGER
    else:
        self.var_loop_type[loop_var] = DOUBLE
        return DOUBLE
```

## Code Generation

### Integer-Optimized Variables

```c
// Detected as INTEGER
int16_t I;      // FOR loop variable
int16_t COUNT;  // Counter
int16_t X, Y, Z; // Integer-only arithmetic

// Fast path
I = 1;
while (I <= 100) {
    COUNT = COUNT + 1;
    X = Y + Z;
    I = I + 1;
}
```

### Double-Default Variables

```c
// Default to DOUBLE (unknown or mixed types)
double A, B, C;
double RESULT;

// Still fast on modern hardware
A = 10.0;
B = 20.5;
C = A + B;
RESULT = sin(C);
```

### Mixed Code

```c
// Realistic example
int16_t I;       // Loop variable (optimized)
int16_t N;       // Bounds (optimized)
double SUM;      // Accumulator (might have fractions)
double AVERAGE;  // Result (definitely float)

N = 100;
SUM = 0.0;
for (I = 1; I <= N; I++) {
    SUM = SUM + (double)I;  // Promote I to DOUBLE for addition
}
AVERAGE = SUM / (double)N;
```

## Examples

### Example 1: Integer-Only Program

```basic
100 REM Count and sum
110 COUNT = 0
120 SUM = 0
130 FOR I = 1 TO 100
140   COUNT = COUNT + 1
150   SUM = SUM + I
160 NEXT I
170 PRINT "Count:"; COUNT
180 PRINT "Sum:"; SUM
190 END
```

**Analysis**:
- `COUNT`: All assignments are INTEGER (0, COUNT+1) → **INTEGER**
- `SUM`: Assignments are INTEGER (0, SUM+I) → **INTEGER**
- `I`: FOR loop with integer bounds → **INTEGER**

**Generated Code**:
```c
int16_t COUNT = 0;
int16_t SUM = 0;
int16_t I;

for (I = 1; I <= 100; I++) {
    COUNT = COUNT + 1;
    SUM = SUM + I;
}
printf("Count: %d\n", COUNT);
printf("Sum: %d\n", SUM);
```

**Performance**: All INTEGER - fast on all platforms!

### Example 2: Mixed Integer/Double

```basic
100 REM Calculate average
110 SUM = 0
120 FOR I = 1 TO 100
130   SUM = SUM + I
140 NEXT I
150 AVERAGE = SUM / 100
160 PRINT "Average:"; AVERAGE
170 END
```

**Analysis**:
- `I`: FOR loop with integer bounds → **INTEGER**
- `SUM`: Assignments are INTEGER (0, SUM+I) → **INTEGER**
- `AVERAGE`: Assignment is DOUBLE (division result) → **DOUBLE**

**Generated Code**:
```c
int16_t I;
int16_t SUM = 0;
double AVERAGE;

for (I = 1; I <= 100; I++) {
    SUM = SUM + I;
}
AVERAGE = (double)SUM / 100.0;  // Division promotes to DOUBLE
printf("Average: %f\n", AVERAGE);
```

**Performance**: Loop is INTEGER (fast), only division is DOUBLE

### Example 3: test_type_change.bas (The Challenge)

```basic
100 REM test changing the type of a variable at run time
110 A=1 : B=2
120 GOSUB 1000
130 PRINT C
140 A=1.1 : B=2.2
150 GOSUB 1000
155 PRINT C
160 X# = 1.11 : Y# = 2.22
170 A=X# : B=Y#
180 GOSUB 1000
190 PRINT C
200 END
1000 REM do some sort of math we dont know precision
1010 C=A+B
1020 RETURN
```

**Analysis**:
- `A`: Assignments are INTEGER (1), DOUBLE (1.1), DOUBLE (X#) → **DOUBLE** (mixed)
- `B`: Assignments are INTEGER (2), DOUBLE (2.2), DOUBLE (Y#) → **DOUBLE** (mixed)
- `C`: Assignment type depends on A+B → **DOUBLE** (conservative)
- `X#`: Explicit suffix → **DOUBLE**
- `Y#`: Explicit suffix → **DOUBLE**

**Generated Code**:
```c
double A, B, C;
double X, Y;  // Note: # suffix stripped in C

// First call
A = 1.0;
B = 2.0;
C = A + B;  // 3.0 (DOUBLE, not INTEGER!)
printf("%f\n", C);

// Second call
A = 1.1;
B = 2.2;
C = A + B;  // 3.3
printf("%f\n", C);

// Third call
X = 1.11;
Y = 2.22;
A = X;
B = Y;
C = A + B;  // 3.33
printf("%f\n", C);
```

**Result**: **Semantically different from interpreter!**
- First PRINT: Shows 3.0 (or "3") instead of INTEGER 3
- But behavior is **consistent** across all three calls
- All operations use DOUBLE (predictable)

**Tradeoff**: Accepts semantic difference for consistency and simplicity

### Example 4: Loop with Hint

```basic
100 REM Process array
110 DIM A(100)
120 FOR I = 1 TO 100
130   A(I) = I * 2
140 NEXT I
150 END
```

**Analysis**:
- `I`: FOR loop with integer bounds → **INTEGER**
- `I` used as array subscript → **strong INTEGER hint**
- `A(I)`: Assignment is INTEGER (I*2) → array elements are DOUBLE by default

**Generated Code**:
```c
double A[101];  // Arrays are DOUBLE by default (or based on element analysis)
int16_t I;      // Loop variable optimized to INTEGER

for (I = 1; I <= 100; I++) {
    A[I] = (double)(I * 2);  // Integer multiply, then promote to DOUBLE
}
```

**Performance**: Loop is INTEGER (fast), array stores DOUBLE (safe)

## Optimization Opportunities

### Detected INTEGER Variables (Fast Path)

Variables that the analysis **proves** are INTEGER-only:

1. **FOR loop counters** (most common)
   ```basic
   FOR I = 1 TO 100  ' I is INTEGER
   ```

2. **Boolean flags**
   ```basic
   FLAG = 0          ' FLAG is INTEGER
   IF X > 10 THEN FLAG = -1
   ```

3. **Counters and indexes**
   ```basic
   COUNT = 0
   COUNT = COUNT + 1  ' COUNT is INTEGER
   ```

4. **Integer arithmetic chains**
   ```basic
   X = 10
   Y = 20
   Z = X + Y          ' All INTEGER
   W = Z * 2          ' Still INTEGER
   ```

### Conservative DOUBLE (Safe Default)

Variables that become DOUBLE:

1. **Mixed-type assignments**
   ```basic
   X = 10            ' First assignment: INTEGER
   X = 10.5          ' Second assignment: DOUBLE → X is DOUBLE
   ```

2. **Division results**
   ```basic
   X = 10
   Y = X / 2         ' Division → Y is DOUBLE
   ```

3. **INPUT variables**
   ```basic
   INPUT A           ' A is DOUBLE (user might enter 1.5)
   ```

4. **Math function results**
   ```basic
   X = SIN(Y)        ' X is DOUBLE
   ```

5. **Uncertain contexts**
   ```basic
   GOSUB 1000        ' Variables modified in subroutine → conservative DOUBLE
   ```

## Implementation in Semantic Analyzer

Add new analysis pass:

```python
class IntegerInferenceAnalysis:
    """Detect variables that can be safely compiled as INTEGER"""

    def __init__(self):
        self.integer_vars = set()      # Variables proven to be INTEGER
        self.double_vars = set()       # Variables that must be DOUBLE
        self.var_assignments = {}      # Track all assignments
        self.loop_vars = {}            # FOR loop variables and their types

    def analyze(self, program):
        # Pass 1: Collect all assignments
        for line in program.lines:
            for stmt in line.statements:
                self._collect_assignments(stmt)

        # Pass 2: Analyze FOR loops
        for line in program.lines:
            for stmt in line.statements:
                if isinstance(stmt, ForStatementNode):
                    self._analyze_for_loop(stmt)

        # Pass 3: Classify each variable
        for var_name in self.var_assignments.keys():
            if self._is_provably_integer(var_name):
                self.integer_vars.add(var_name)
            else:
                self.double_vars.add(var_name)

        # Pass 4: Report findings
        self._report_optimizations()

    def _is_provably_integer(self, var_name):
        """Check if variable can be proven to be INTEGER-only"""

        # Has explicit type suffix?
        if var_name.endswith('%'):
            return True  # Explicit INTEGER
        if var_name.endswith('!') or var_name.endswith('#') or var_name.endswith('$'):
            return False  # Explicit non-INTEGER type

        # Check all assignments
        assignments = self.var_assignments.get(var_name, [])
        if not assignments:
            return False  # Unknown - default to DOUBLE

        # All assignments must be INTEGER
        for expr_type in assignments:
            if expr_type != INTEGER:
                return False

        # Additional checks
        if self._is_input_variable(var_name):
            return False  # INPUT is conservative → DOUBLE

        if self._used_in_division(var_name):
            return False  # Division results are DOUBLE

        # Passed all checks!
        return True
```

## Diagnostic Output

Provide helpful information to programmers:

```
Integer Inference Analysis:
  Optimized to INTEGER (fast): 15 variables
    I, J, K (FOR loop variables)
    COUNT, TOTAL, N (counters)
    X, Y, Z (integer arithmetic)
    FLAG, DONE (boolean flags)
    INDEX, POS, LEN (array indices)
    ROW, COL (2D array indices)

  Default to DOUBLE (safe): 8 variables
    AVERAGE (division result)
    SUM (might accumulate fractions)
    A, B, C (mixed types in assignments)
    RESULT (receives math function result)
    INPUT_VAL (from INPUT statement)
    DATA_VAL (from READ statement)

  Performance estimate:
    85% of operations use INTEGER (fast path)
    15% of operations use DOUBLE (safe path)

  Suggestions:
    Line 150: Variable 'SUM' could be INTEGER if division moved outside loop
    Line 200: Variable 'A' has mixed assignments (1, 1.5) - consider using A% or A# explicitly
```

## Benefits

### 1. Automatic Optimization

✅ **No programmer effort required**
- FOR loops automatically optimized
- Counters automatically optimized
- Integer arithmetic chains automatically optimized

### 2. Safe Defaults

✅ **Conservative when uncertain**
- Unknown types → DOUBLE (no precision loss)
- Mixed types → DOUBLE (handles all cases)
- INPUT/READ → DOUBLE (handles user input)

### 3. Best of Both Worlds

✅ **Performance where it matters**
- Loop variables are INTEGER (huge win on 8080)
- Counters and indices are INTEGER
- Integer arithmetic is fast

✅ **Correctness where needed**
- Math operations default to DOUBLE
- Division always produces DOUBLE
- Floating-point inputs handled correctly

### 4. Progressive Enhancement

The analysis can be improved over time:

**Version 1.0**: Basic literal analysis + FOR loops
**Version 1.1**: Add range analysis (detect overflow)
**Version 1.2**: Add dataflow analysis (track through GOSUBs)
**Version 1.3**: Add user hints (`REM $INTEGER: X, Y, Z`)

## Limitations

### Still Semantically Different

```basic
' test_type_change.bas
110 A=1 : B=2
130 PRINT C           ' Interpreter: 3 (INTEGER)
                      ' Compiler:    3.0 (DOUBLE)
```

**Accept this**: Document the difference, provide workarounds

### Conservative Analysis

Some INTEGER variables may be missed:

```basic
100 X = 10
110 IF Y > 5 THEN X = 20 ELSE X = 30
120 PRINT X
' Analysis sees: X = 10, 20, 30 (all INTEGER)
' But if any branch is uncertain → might default to DOUBLE
```

**Solution**: Improve analysis over time, add warnings

### Overflow Not Detected

```basic
100 X = 30000
110 Y = X + X         ' Overflows 16-bit INTEGER!
```

**Solution**: Add range analysis to detect potential overflow → promote to DOUBLE

## Comparison with Other Strategies

| Feature | DEFDBL A-Z | INTEGER Inference | Type Stability |
|---------|-----------|------------------|----------------|
| Implementation Complexity | ⭐⭐⭐⭐⭐ Simple | ⭐⭐⭐⭐ Moderate | ⭐⭐ Complex |
| FOR Loop Performance | ⭐⭐ (DOUBLE) | ⭐⭐⭐⭐⭐ (INTEGER) | ⭐⭐⭐⭐⭐ (INTEGER) |
| Counter Performance | ⭐⭐ (DOUBLE) | ⭐⭐⭐⭐⭐ (INTEGER) | ⭐⭐⭐⭐⭐ (INTEGER) |
| Math Precision | ⭐⭐⭐⭐⭐ (DOUBLE) | ⭐⭐⭐⭐⭐ (DOUBLE) | ⭐⭐⭐⭐⭐ (varies) |
| Semantic Correctness | ⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| Programmer Control | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| Diagnostic Output | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

## Recommendation: **Use INTEGER Inference**

This is **better than pure DEFDBL A-Z** because:

1. ✅ **Automatic optimization** of the most critical paths (loops, counters)
2. ✅ **Still simple** - only two types (INTEGER and DOUBLE)
3. ✅ **Huge performance win on 8080** (loops are 500x faster)
4. ✅ **Helpful diagnostics** - shows what was optimized
5. ✅ **Same safety** - defaults to DOUBLE when uncertain
6. ⚠️ **Slightly more complex** - but worth it for the performance gains

---

**Related Files**:
- `doc/DYNAMIC_TYPE_CHANGE_PROBLEM.md` - Problem analysis
- `doc/COMPILATION_STRATEGIES_COMPARISON.md` - Strategy comparison
- `tests/test_type_change.bas` - Edge case test
