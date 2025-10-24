# Type Inference Strategy: No Guessing Allowed

## Core Principle

**Never guess variable types. Either prove the type, or require the programmer to specify it.**

This approach combines:
1. **Explicit DEFDBL switch** - Opt-in to "everything is DOUBLE"
2. **Conservative INTEGER inference** - Automatically detect provably INTEGER variables
3. **Compilation errors** - Force programmer to clarify ambiguous cases

## The Three-Tier Strategy

### Tier 1: Explicit Type Specification (Always Works)

The programmer explicitly specifies types using:

```basic
' Method 1: Type suffixes
100 X% = 10      ' INTEGER
110 Y! = 20.5    ' SINGLE
120 Z# = 30.3    ' DOUBLE
130 S$ = "HI"    ' STRING

' Method 2: DEF statements
10 DEFINT A-Z    ' All variables are INTEGER by default
10 DEFDBL A-Z    ' All variables are DOUBLE by default
10 DEFINT I-N    ' I,J,K,L,M,N are INTEGER (FORTRAN convention)
10 DEFDBL A-H,O-Z ' Rest are DOUBLE
```

**Compiler behavior**: Use the explicitly specified type. No inference needed.

### Tier 2: Automatic INTEGER Inference (High Confidence)

The compiler **proves** a variable must be INTEGER by analyzing:

```basic
' Rule 1: Integer literal assignment (and never reassigned differently)
100 COUNT = 0
110 COUNT = COUNT + 1
' COUNT is provably INTEGER

' Rule 2: Integer arithmetic only
100 A = 10
110 B = 20
120 C = A + B
130 D = C * 2
' A, B, C, D are provably INTEGER

' Rule 3: FOR loop variables with integer bounds
100 FOR I = 1 TO 100
110   PRINT I
120 NEXT I
' I is provably INTEGER

' Rule 4: Integer operations (MOD, \, AND, OR, XOR, NOT)
100 X = 10
110 Y = X MOD 3
120 Z = X \ 2
' X, Y, Z are provably INTEGER

' Rule 5: Array subscripts
100 DIM A(100)
110 I = 5
120 A(I) = 10
' I is used as subscript, must be INTEGER
```

**Compiler behavior**: Automatically infer INTEGER type. No programmer action needed.

### Tier 3: Ambiguous Types (Compilation Error)

When the compiler **cannot prove** the type, it **errors** instead of guessing:

```basic
' Example 1: Unknown input type
100 INPUT X
110 Y = X + 1
' ERROR: Cannot infer type for X
' Fix: Add INPUT X% or add DEFINT X at the top

' Example 2: Mixed-type assignment
100 X = 10        ' INTEGER literal
110 X = 10.5      ' SINGLE literal - TYPE CONFLICT!
' ERROR: Variable X assigned both INTEGER and SINGLE values
' Fix: Use X% = 10 : X! = 10.5 (two different variables)
'   or: Use X# throughout if you need floating-point

' Example 3: Type depends on runtime value
100 A = 1 : B = 2
110 GOSUB 1000
120 A = 1.1 : B = 2.2
130 GOSUB 1000
1000 C = A + B
1010 RETURN
' ERROR: Variable C has inconsistent types across calls
'   First call: C would be INTEGER (1+2)
'   Second call: C would be SINGLE (1.1+2.2)
' Fix: Add C# = A + B to force DOUBLE throughout
'   or: Add DEFDBL A-Z at the top
'   or: Use --defdbl-default compiler flag
```

## Compilation Flags

### `--defdbl-default` (or `-d`)

**Behavior**: Treat all untyped variables as DOUBLE (as if `DEFDBL A-Z` is at the top)

**Use case**: Quick compilation, correctness over performance, modern hardware

```bash
# Compile with DEFDBL default
mbasic compile --defdbl-default program.bas

# Or short form
mbasic compile -d program.bas
```

**Effect**:
- All untyped variables become DOUBLE
- INTEGER inference still applies (for better performance)
- No type ambiguity errors

**Example**:
```basic
' program.bas
100 INPUT X
110 Y = X + 1
120 PRINT Y

# Without flag:
$ mbasic compile program.bas
ERROR: Cannot infer type for variable X at line 100
  Use: INPUT X% (INTEGER), INPUT X! (SINGLE), INPUT X# (DOUBLE)
  Or:  Add DEFDBL A-Z to program
  Or:  Use --defdbl-default compiler flag

# With flag:
$ mbasic compile --defdbl-default program.bas
SUCCESS: Compiled to program.c
  Note: Variables X, Y compiled as DOUBLE (--defdbl-default flag)
```

### `--strict-types` (or `-s`)

**Behavior**: Error on ALL type ambiguities, even with INTEGER inference

**Use case**: Maximum type safety, prepare for future type annotations

```bash
mbasic compile --strict-types program.bas
```

**Effect**:
- INTEGER inference disabled
- All variables must have explicit types
- Forces DEFINT/DEFDBL or type suffixes

## Error Messages

### Error: Cannot Infer Type

```
ERROR at line 100: Cannot infer type for variable 'X'
  Variable 'X' has no type suffix and is not assigned a typed literal

  Possible fixes:
  1. Add type suffix to variable: X%, X!, X#, X$
  2. Add DEFINT/DEFSNG/DEFDBL statement to program
  3. Use --defdbl-default compiler flag for DOUBLE default

  Example:
    100 INPUT X%      ' INTEGER
    100 INPUT X!      ' SINGLE
    100 INPUT X#      ' DOUBLE
```

### Error: Type Conflict

```
ERROR at line 110: Type conflict for variable 'X'
  Line 100: X = 10        (inferred as INTEGER)
  Line 110: X = 10.5      (requires SINGLE or DOUBLE)

  Variables cannot change type after first use.

  Possible fixes:
  1. Use different variables: X% for integer, X# for float
  2. Force DOUBLE throughout: X# = 10, X# = 10.5
  3. Use --defdbl-default flag to make X always DOUBLE
```

### Error: Ambiguous Type Across Paths

```
ERROR at line 1000: Variable 'C' has ambiguous type
  Subroutine at line 1000 is called with different argument types:
    Line 110: GOSUB 1000  (A=1, B=2 → both INTEGER)
    Line 130: GOSUB 1000  (A=1.1, B=2.2 → both SINGLE)

  Variable C would be INTEGER on first call, SINGLE on second call.

  Possible fixes:
  1. Add explicit type: 1000 C# = A + B
  2. Add DEFDBL A-Z to force all variables to DOUBLE
  3. Use --defdbl-default compiler flag
```

## INTEGER Inference Rules (Tier 2 Details)

The compiler proves a variable is INTEGER if **all** of these are true:

### 1. No Explicit Type Suffix

```basic
100 X% = 10   ' Has % suffix - not inferred, explicitly INTEGER
110 Y = 20    ' No suffix - eligible for inference
```

### 2. All Assignments Are INTEGER-Valued

An assignment is INTEGER-valued if:

#### (a) Integer literal

```basic
100 X = 10        ' INTEGER
110 Y = -5        ' INTEGER
120 Z = 0         ' INTEGER
```

**Not INTEGER**:
```basic
100 X = 10.0      ' DOUBLE (has decimal point)
110 Y = 1.5       ' SINGLE/DOUBLE (fractional part)
120 Z = 1E10      ' DOUBLE (scientific notation)
```

#### (b) Integer operation on INTEGER operands

```basic
100 A = 10
110 B = 20
120 C = A + B     ' INTEGER + INTEGER → INTEGER
130 D = C * 2     ' INTEGER * 2 → INTEGER
140 E = D - 1     ' INTEGER - 1 → INTEGER
```

**Integer operations**:
- `+`, `-`, `*` when both operands are INTEGER
- `\` (integer division) - always produces INTEGER
- `MOD` (modulo) - always produces INTEGER
- `AND`, `OR`, `XOR`, `NOT`, `EQV`, `IMP` - bitwise (always INTEGER)

**Not INTEGER operations**:
- `/` (floating-point division) - always produces SINGLE/DOUBLE
- `^` (exponentiation) - produces SINGLE/DOUBLE unless proven otherwise
- Any operation involving SINGLE/DOUBLE operands

#### (c) FOR loop variable with integer bounds

```basic
100 FOR I = 1 TO 100          ' I is INTEGER (bounds are integer literals)
110 FOR J = 1 TO 100 STEP 2   ' J is INTEGER (step is integer)
120 FOR K = A TO B            ' K is INTEGER if A and B are INTEGER
```

**Not INTEGER**:
```basic
100 FOR I = 1.0 TO 100.0      ' I is DOUBLE (bounds have decimal points)
110 FOR J = 1 TO 100 STEP 0.5 ' J is SINGLE/DOUBLE (non-integer step)
```

#### (d) Built-in functions that return INTEGER

```basic
100 X = LEN("HELLO")          ' LEN returns INTEGER
110 Y = ASC("A")              ' ASC returns INTEGER
120 Z = INSTR("ABC", "B")     ' INSTR returns INTEGER
130 W = FIX(10.5)             ' FIX returns INTEGER
140 V = INT(10.5)             ' INT returns INTEGER
150 U = CINT(10.5)            ' CINT returns INTEGER
160 T = POS(0)                ' POS returns INTEGER
```

#### (e) Array subscript expressions

```basic
100 DIM A(100)
110 I = 5
120 X = A(I)         ' I is used as subscript
' I must be INTEGER (subscripts are always INTEGER)
```

#### (f) Comparison results

```basic
100 X = 1
110 Y = 2
120 Z = (X < Y)      ' Comparison returns -1 (true) or 0 (false) - INTEGER
```

### 3. Never Used in Floating-Point Context

A variable used in any of these contexts **cannot** be INTEGER:

```basic
' Example 1: Floating-point division
100 X = 10
110 Y = X / 2        ' Y cannot be INTEGER (/ produces float)

' Example 2: Mixed with DOUBLE
100 X = 10
110 Y# = 20.5
120 Z = X + Y#       ' Z cannot be INTEGER (promoted to DOUBLE)

' Example 3: Passed to float function
100 X = 10
110 Y = SIN(X)       ' X is promoted to DOUBLE (SIN requires float)
                     ' But X itself can still be INTEGER!

' Example 4: Comparison with DOUBLE
100 X = 10
110 Y# = 10.5
120 IF X = Y# THEN   ' X is promoted to DOUBLE for comparison
                     ' But X itself remains INTEGER!
```

**Important**: Promotion does **not** change the variable's type, only the operation's type.

```basic
100 X% = 10          ' X% is INTEGER
110 Y# = 20.5        ' Y# is DOUBLE
120 Z# = X% + Y#     ' X% promoted to DOUBLE for addition, result is DOUBLE
130 PRINT X%         ' X% is still INTEGER (prints 10, not 10.0)
```

### 4. Analysis Algorithm

```python
def infer_variable_type(var_name: str) -> str:
    """
    Infer the type of a variable.
    Returns: "INTEGER", "DOUBLE", or raises CompilationError
    """

    # Step 1: Check for explicit type suffix
    if var_name.endswith('%'):
        return "INTEGER"
    if var_name.endswith('!'):
        return "SINGLE"
    if var_name.endswith('#'):
        return "DOUBLE"
    if var_name.endswith('$'):
        return "STRING"

    # Step 2: Check for DEFINT/DEFSNG/DEFDBL
    def_type = get_def_type_for_variable(var_name)
    if def_type:
        return def_type  # "INTEGER", "SINGLE", or "DOUBLE"

    # Step 3: Analyze all assignments to this variable
    assignments = get_all_assignments(var_name)

    if not assignments:
        # No assignments found
        raise CompilationError(
            f"Cannot infer type for variable '{var_name}'\n"
            f"  Variable has no assignments and no type suffix\n"
            f"  Add type suffix ({var_name}%, {var_name}!, {var_name}#)\n"
            f"  Or use --defdbl-default flag"
        )

    # Step 4: Check if all assignments are INTEGER-valued
    all_integer = True
    first_non_integer_line = None

    for line_num, expr in assignments:
        if not is_integer_valued_expression(expr):
            all_integer = False
            first_non_integer_line = line_num
            break

    # Step 5: Check for type conflicts
    if not all_integer:
        # Check if some assignments are INTEGER and some are not
        has_integer_assignment = any(
            is_integer_valued_expression(expr)
            for _, expr in assignments
        )

        if has_integer_assignment:
            # Type conflict!
            integer_line = next(
                line for line, expr in assignments
                if is_integer_valued_expression(expr)
            )
            raise CompilationError(
                f"Type conflict for variable '{var_name}'\n"
                f"  Line {integer_line}: Assigned INTEGER value\n"
                f"  Line {first_non_integer_line}: Assigned SINGLE/DOUBLE value\n"
                f"  Variables cannot change type\n"
                f"  Use {var_name}# to force DOUBLE, or --defdbl-default flag"
            )

        # All assignments are non-integer
        return "DOUBLE"  # Conservative default

    # Step 6: All assignments are INTEGER - check usage context
    if is_used_in_float_context(var_name):
        # Used in floating-point operation
        return "DOUBLE"  # Promote to DOUBLE

    # Step 7: Proven to be INTEGER!
    return "INTEGER"


def is_integer_valued_expression(expr) -> bool:
    """Check if an expression produces an INTEGER value"""

    # Integer literal
    if isinstance(expr, NumberNode) and isinstance(expr.value, int):
        return True

    # Integer operation
    if isinstance(expr, BinaryOpNode):
        left_int = is_integer_valued_expression(expr.left)
        right_int = is_integer_valued_expression(expr.right)

        # Both operands must be INTEGER
        if not (left_int and right_int):
            return False

        # Check operator
        if expr.operator in ['+', '-', '*', '\\', 'MOD', 'AND', 'OR', 'XOR']:
            return True

        # / always produces float
        if expr.operator == '/':
            return False

        # ^ might produce float (unless both are small integers)
        if expr.operator == '^':
            return False  # Conservative

    # FOR loop variable
    if is_for_loop_variable(expr.name):
        loop_info = get_for_loop_info(expr.name)
        if (is_integer_valued_expression(loop_info.start) and
            is_integer_valued_expression(loop_info.end) and
            is_integer_valued_expression(loop_info.step)):
            return True

    # Built-in INTEGER functions
    if isinstance(expr, FunctionCallNode):
        if expr.name.upper() in ['LEN', 'ASC', 'INSTR', 'FIX', 'INT',
                                   'CINT', 'POS', 'EOF', 'LOC', 'LOF']:
            return True

    # Variable reference - look up its type
    if isinstance(expr, VariableNode):
        var_type = infer_variable_type(expr.name)
        return var_type == "INTEGER"

    return False
```

## Comparison with Other Strategies

| Aspect | Pure DEFDBL | INTEGER Inference | **This Strategy** |
|--------|-------------|-------------------|-------------------|
| **Correctness** | ⭐⭐ (always DOUBLE) | ⭐⭐⭐ (mostly right) | ⭐⭐⭐⭐⭐ (never wrong) |
| **Performance** | ⭐⭐⭐ (on modern HW) | ⭐⭐⭐⭐⭐ (optimizes loops) | ⭐⭐⭐⭐⭐ (optimizes loops) |
| **8080 Performance** | ⭐ (slow) | ⭐⭐⭐⭐ (good) | ⭐⭐⭐⭐⭐ (explicit control) |
| **Ease of Use** | ⭐⭐⭐⭐⭐ (no errors) | ⭐⭐⭐⭐ (mostly works) | ⭐⭐⭐ (errors on ambiguity) |
| **Debugging** | ⭐⭐⭐ (simple) | ⭐⭐⭐⭐ (shows inferences) | ⭐⭐⭐⭐⭐ (explicit types) |
| **Semantic Compatibility** | ❌ (different) | ❌ (different) | ⚠️ (requires types) |

## Implementation Checklist

### Phase 1: Basic INTEGER Inference
- [ ] Implement `is_integer_valued_expression()`
- [ ] Implement `infer_variable_type()` with error on ambiguity
- [ ] Add compilation error messages
- [ ] Test with simple programs (loops, counters)

### Phase 2: DEFDBL Flag
- [ ] Add `--defdbl-default` command-line flag
- [ ] Modify `infer_variable_type()` to return DOUBLE when flag is set
- [ ] Update error messages to suggest flag
- [ ] Test flag behavior

### Phase 3: DEF Statement Support
- [ ] Parse DEFINT/DEFSNG/DEFDBL statements
- [ ] Track DEF ranges (A-Z, I-N, etc.)
- [ ] Use DEF type in inference
- [ ] Test various DEF combinations

### Phase 4: Advanced Inference
- [ ] FOR loop variable inference
- [ ] Array subscript inference
- [ ] Built-in function return type tracking
- [ ] Cross-procedure analysis (GOSUB/RETURN)

### Phase 5: Error Reporting
- [ ] Clear error messages with fix suggestions
- [ ] Show all type conflicts (not just first)
- [ ] Suggest minimal fix (add one suffix vs DEFDBL)
- [ ] Warning for implicit DOUBLE promotion

## Examples

### Example 1: Simple Program (Works)

```basic
100 REM Count to 100
110 FOR I = 1 TO 100
120   PRINT I
130 NEXT I
```

**Analysis**:
- `I`: FOR loop variable with integer bounds → **INTEGER**

**Compiled as**:
```c
int16_t I;
for (I = 1; I <= 100; I++) {
    print_integer(I);
}
```

**Result**: ✅ Compiles successfully

### Example 2: Ambiguous Program (Error)

```basic
100 INPUT X
110 PRINT X * 2
```

**Analysis**:
- `X`: No type suffix, no DEF statement, INPUT gives unknown type

**Error**:
```
ERROR at line 100: Cannot infer type for variable 'X'
  Variable 'X' has no type suffix and is assigned via INPUT

  INPUT can accept INTEGER, SINGLE, or DOUBLE values.
  Compiler cannot determine which type to use.

  Possible fixes:
  1. Add type suffix: INPUT X% (INTEGER), INPUT X# (DOUBLE)
  2. Add DEFDBL A-Z to program
  3. Use --defdbl-default compiler flag
```

### Example 3: With DEFDBL Flag (Works)

```bash
$ mbasic compile --defdbl-default program.bas
```

```basic
100 INPUT X
110 PRINT X * 2
```

**Analysis with `--defdbl-default`**:
- `X`: No type suffix, no DEF, but flag is set → **DOUBLE**

**Compiled as**:
```c
double X;
scanf("%lf", &X);
printf("%f", X * 2.0);
```

**Result**: ✅ Compiles successfully (X is DOUBLE)

### Example 4: Type Conflict (Error)

```basic
100 X = 10
110 X = 10.5
120 PRINT X
```

**Analysis**:
- Line 100: `X = 10` → INTEGER
- Line 110: `X = 10.5` → SINGLE/DOUBLE
- **CONFLICT**: X changes type

**Error**:
```
ERROR at line 110: Type conflict for variable 'X'
  Line 100: X = 10        (inferred as INTEGER)
  Line 110: X = 10.5      (requires SINGLE or DOUBLE)

  Variables cannot change type after first use.

  Possible fixes:
  1. Use X# = 10 and X# = 10.5 (both DOUBLE)
  2. Use --defdbl-default flag to make X always DOUBLE
```

### Example 5: Mixed Types (Works with Explicit Types)

```basic
100 X% = 10         ' INTEGER
110 Y# = 10.5       ' DOUBLE
120 Z# = X% + Y#    ' Result is DOUBLE
130 PRINT Z#
```

**Analysis**:
- `X%`: Explicit INTEGER suffix → **INTEGER**
- `Y#`: Explicit DOUBLE suffix → **DOUBLE**
- `Z#`: Explicit DOUBLE suffix → **DOUBLE**
- Line 120: INTEGER + DOUBLE → DOUBLE (X% promoted, but stays INTEGER)

**Result**: ✅ Compiles successfully

### Example 6: Loop with Float (Error)

```basic
100 FOR I = 1.0 TO 100.0
110   PRINT I
120 NEXT I
```

**Analysis**:
- `I`: FOR loop variable, but bounds are `1.0` and `100.0` (DOUBLE literals)
- Cannot infer as INTEGER

**Error**:
```
ERROR at line 100: Loop variable 'I' has ambiguous type
  FOR loop bounds are DOUBLE (1.0, 100.0)
  Loop variable type is unclear (INTEGER vs DOUBLE)

  Possible fixes:
  1. Use integer bounds: FOR I = 1 TO 100
  2. Add type suffix: FOR I# = 1.0 TO 100.0 (explicit DOUBLE)
  3. Use --defdbl-default flag
```

### Example 7: test_type_change.bas (Error)

```basic
100 A=1 : B=2
110 GOSUB 1000
120 A=1.1 : B=2.2
130 GOSUB 1000
1000 C=A+B
1010 RETURN
```

**Analysis**:
- Line 100: `A=1`, `B=2` → both INTEGER
- Line 120: `A=1.1`, `B=2.2` → both SINGLE/DOUBLE
- **CONFLICT**: A and B change type

**Error**:
```
ERROR at line 120: Type conflict for variable 'A'
  Line 100: A = 1     (inferred as INTEGER)
  Line 120: A = 1.1   (requires SINGLE or DOUBLE)

  Variables cannot change type after first use.

  Possible fixes:
  1. Use A# = 1 and A# = 1.1 (both DOUBLE)
  2. Use different variables for different types
  3. Add DEFDBL A-Z to program
  4. Use --defdbl-default compiler flag

ERROR at line 120: Type conflict for variable 'B'
  Line 100: B = 2     (inferred as INTEGER)
  Line 120: B = 2.2   (requires SINGLE or DOUBLE)

  [Same fix suggestions]
```

**Fix 1**: Add DEFDBL
```basic
10 DEFDBL A-Z
100 A=1 : B=2
110 GOSUB 1000
120 A=1.1 : B=2.2
130 GOSUB 1000
1000 C=A+B
1010 RETURN
```
✅ Compiles (all variables are DOUBLE)

**Fix 2**: Use type suffixes
```basic
100 A#=1 : B#=2
110 GOSUB 1000
120 A#=1.1 : B#=2.2
130 GOSUB 1000
1000 C#=A#+B#
1010 RETURN
```
✅ Compiles (all variables explicitly DOUBLE)

**Fix 3**: Use flag
```bash
$ mbasic compile --defdbl-default test_type_change.bas
```
✅ Compiles (flag makes all untyped variables DOUBLE)

## Summary

This strategy provides:

1. **No guessing**: Compiler never invents a type
2. **Automatic optimization**: Loops and counters are fast (INTEGER)
3. **Clear errors**: Programmer knows exactly what to fix
4. **Escape hatch**: `--defdbl-default` flag for quick compilation
5. **Performance control**: Programmer can optimize by adding types
6. **Correctness**: Compiled program behaves exactly as specified

**The key insight**: Requiring explicit types (or the DEFDBL flag) is better than silently guessing wrong. The compiler's job is to help the programmer write correct, fast code - not to hide problems.

---

**Related Files**:
- `doc/DYNAMIC_TYPE_CHANGE_PROBLEM.md` - Problem analysis
- `doc/COMPILATION_STRATEGIES_COMPARISON.md` - Strategy comparison
- `doc/INTEGER_INFERENCE_STRATEGY.md` - Pure inference approach
- `tests/test_type_change.bas` - Edge case that requires explicit types
