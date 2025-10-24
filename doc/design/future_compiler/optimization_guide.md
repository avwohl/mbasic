# MBASIC Compiler - Optimization Guide

This guide explains how to write BASIC code that takes advantage of the compiler's optimizations.

## Table of Contents
1. [Constant Folding](#constant-folding)
2. [Common Subexpression Elimination](#common-subexpression-elimination)
3. [Loop Optimizations](#loop-optimizations)
4. [Strength Reduction](#strength-reduction)
5. [Variable Usage](#variable-usage)
6. [Branch Optimization](#branch-optimization)
7. [Best Practices](#best-practices)

---

## Constant Folding

### What It Does
The compiler evaluates constant expressions at compile time.

### Example
```basic
' Instead of this:
X = 10 + 20 + 30

' The compiler generates code as if you wrote:
X = 60
```

### How to Take Advantage
- Use constant expressions freely - they cost nothing at runtime
- Break complex calculations into steps with constants
- The compiler will fold them all together

```basic
' This is fine - all optimized away:
PI = 3.14159
TWO_PI = 2 * PI
RADIUS = 5
CIRCUMFERENCE = TWO_PI * RADIUS
' Compiler computes: 31.4159 at compile time
```

---

## Common Subexpression Elimination

### What It Does
The compiler detects when you compute the same expression multiple times.

### Example
```basic
' Inefficient:
X = A + B + C
Y = A + B + D
Z = A + B + E

' The compiler notices A+B is computed 3 times
' It suggests using a temporary:
TEMP = A + B
X = TEMP + C
Y = TEMP + D
Z = TEMP + E
```

### How to Take Advantage
- Don't manually optimize common expressions - let the compiler find them
- Write clear code; the compiler will optimize it
- Use the analyzer to see what CSEs were found

```basic
' Run: python3 analyze_program.py myprogram.bas --summary
' to see all detected CSEs
```

---

## Loop Optimizations

### What It Does
The compiler:
- Calculates iteration counts
- Finds loop-invariant expressions (don't change in the loop)
- Detects induction variables
- Identifies strength reduction opportunities

### Loop-Invariant Code Motion

```basic
' Inefficient:
FOR I = 1 TO 100
  X = A * B      ' A*B doesn't change - loop invariant!
  PRINT X + I
NEXT I

' Better - but compiler detects this automatically:
X = A * B        ' Hoist outside loop
FOR I = 1 TO 100
  PRINT X + I
NEXT I
```

### Induction Variable Optimization

```basic
' The pattern I*2 in array subscripts is optimized:
DIM A(200)
FOR I = 1 TO 100
  A(I * 2) = I   ' Compiler uses pointer arithmetic
NEXT I           ' instead of multiplication
```

### How to Take Advantage
- Keep loop bounds constant when possible
- Don't manually hoist invariants - compiler finds them
- Use simple expressions in array subscripts (I*const, I+const)
- Avoid function calls in tight loops (may have side effects)

---

## Strength Reduction

### What It Does
Replaces expensive operations with cheaper ones.

### Transformations
- `X * 2` → `X + X` (addition is cheaper than multiplication)
- `X * 1` → `X` (eliminate operation)
- `X * 0` → `0` (constant)
- `X + 0` → `X` (eliminate operation)
- `X - X` → `0` (constant)

### Example
```basic
' This:
Y = N * 2

' Becomes:
Y = N + N

' And this:
Z = X * 1 + 0

' Becomes:
Z = X
```

### How to Take Advantage
- Write natural expressions
- Compiler will optimize them automatically
- Don't manually optimize - focus on clarity

---

## Variable Usage

### Copy Propagation

```basic
' Instead of:
SRC = 100
DEST = SRC
RESULT = DEST + 1

' Compiler can use SRC directly:
SRC = 100
DEST = SRC
RESULT = SRC + 1  ' Uses SRC instead of DEST
```

### Forward Substitution

```basic
' Single-use temporaries can be eliminated:
TEMP = A + B
PRINT TEMP       ' TEMP used only once

' Compiler suggests:
PRINT A + B      ' Substitute directly
```

### Uninitialized Variables

```basic
' Bad (compiler warns):
PRINT X
X = 10

' Good:
X = 10
PRINT X

' OK (automatically initialized):
FOR I = 1 TO 10  ' I is initialized by FOR
  PRINT I
NEXT I

INPUT A          ' A is initialized by INPUT
PRINT A
```

---

## Branch Optimization

### What It Does
Detects conditions that are always true or false.

### Example
```basic
' Constant condition:
IF 1 THEN PRINT "Always executes"
IF 0 THEN PRINT "Never executes"  ' Dead code!

' With constant propagation:
N = 10
IF N > 5 THEN PRINT "Always true"  ' Compiler knows N=10
```

### How to Take Advantage
- Use constants in conditionals during development/debugging
- Compiler will warn about always-true/false conditions
- Remove dead code identified by the compiler

---

## Best Practices

### 1. Write Clear Code First
```basic
' Don't write:
X = ((A << 1) + (A << 1))  ' Manual optimization

' Write:
X = 2 * A + 2 * A          ' Clear intent

' Compiler will optimize to:
X = A + A + A + A          ' Or: X = 4 * A, then A+A+A+A
```

### 2. Use Meaningful Variable Names
```basic
' Bad:
T1 = X + Y
T2 = T1 * Z
T3 = T2 + W

' Good:
SUBTOTAL = PRICE + TAX
TOTAL = SUBTOTAL * QUANTITY
FINAL = TOTAL + SHIPPING
```

The compiler optimizes both equally, but the second is readable.

### 3. Leverage Analysis Tools
```bash
# See all optimizations found:
python3 analyze_program.py myprogram.bas

# Get a summary:
python3 analyze_program.py myprogram.bas --summary

# Get JSON output for tools:
python3 analyze_program.py myprogram.bas --json
```

### 4. Initialize Variables
```basic
' Always initialize before use:
COUNTER = 0
SUM = 0
MAX = -999999

' Even though BASIC defaults to 0,
' explicit initialization prevents bugs
```

### 5. Use Subroutines Wisely
```basic
' Compiler analyzes what each subroutine modifies:
2000 REM Read-only subroutine
2010 PRINT A + B
2020 RETURN

' Compiler knows this doesn't modify A or B,
' so A+B can still be optimized across the GOSUB
```

### 6. Keep Loops Simple
```basic
' Good - simple bounds:
FOR I = 1 TO 100
  ' loop body
NEXT I

' Also good - constant bounds:
MAX = 100
FOR I = 1 TO MAX
  ' loop body
NEXT I

' Harder to optimize - variable bounds:
INPUT N
FOR I = 1 TO N   ' Unknown iteration count
  ' loop body
NEXT I
```

---

## Analyzing Your Programs

### Command-Line Analysis
```bash
# Full report:
python3 analyze_program.py myprogram.bas

# Summary only:
python3 analyze_program.py myprogram.bas --summary

# JSON format:
python3 analyze_program.py myprogram.bas --json
```

### What to Look For

1. **Dead Stores** - Variables assigned but never used
   - Remove these assignments

2. **Single-Use Temporaries** - Variables used only once
   - Consider inlining the expression

3. **Common Subexpressions** - Repeated calculations
   - Consider using a temporary variable

4. **Loop Invariants** - Calculations that don't change in loops
   - Consider moving outside the loop (compiler detects this)

5. **Uninitialized Variables** - Variables used before assignment
   - Add initialization

6. **Always-True/False Branches** - Dead code in conditionals
   - Remove unreachable code

---

## Performance Tips

### High Impact
1. ✅ Initialize variables (prevents bugs, improves optimization)
2. ✅ Use constant loop bounds when possible
3. ✅ Avoid function calls in tight loops
4. ✅ Remove dead code identified by compiler

### Medium Impact
1. ✅ Use temporary variables for CSEs (if compiler suggests)
2. ✅ Hoist loop invariants (compiler detects, but you can do manually)
3. ✅ Eliminate single-use temporaries

### Low Impact (Compiler Handles)
1. ✅ Constant folding - automatic
2. ✅ Strength reduction - automatic
3. ✅ Algebraic simplification - automatic
4. ✅ Expression reassociation - automatic

---

## Examples

### Example 1: Loop Optimization
```basic
' Original:
DIM A(100)
FOR I = 1 TO 100
  A(I) = I * 10
NEXT I

' Analysis shows:
' - Loop bounds: constant (100 iterations)
' - Induction variable: I
' - Strength reduction: I * 10 (use pointer arithmetic)
```

### Example 2: Common Subexpressions
```basic
' Original:
RESULT1 = (A + B) * C
RESULT2 = (A + B) * D
RESULT3 = (A + B) * E

' Analysis shows:
' - CSE: (A + B) computed 3 times
' - Suggestion: TEMP = A + B, then use TEMP

' Optimized:
TEMP = A + B
RESULT1 = TEMP * C
RESULT2 = TEMP * D
RESULT3 = TEMP * E
```

### Example 3: Constant Propagation
```basic
' Original:
N = 10
M = N * 2
DIM A(M)

' Analysis shows:
' - N = 10 (constant)
' - M = N * 2 = 20 (constant folding)
' - DIM A(M) becomes DIM A(20)
```

---

## Conclusion

The MBASIC compiler performs sophisticated optimizations automatically. Your job is to:

1. Write clear, readable code
2. Use the analysis tools to find optimization opportunities
3. Address warnings (dead stores, uninitialized variables)
4. Let the compiler handle the low-level optimizations

**Focus on correctness and clarity - the compiler will handle performance!**

---

## Resources

- `ACCOMPLISHMENTS.md` - Full list of 18 optimizations
- `OPTIMIZATION_STATUS.md` - Technical details of each optimization
- `analyze_program.py` - Program analysis tool
- `demo_all_optimizations.bas` - Example showcasing all optimizations

For questions or issues: https://github.com/anthropics/claude-code/issues
