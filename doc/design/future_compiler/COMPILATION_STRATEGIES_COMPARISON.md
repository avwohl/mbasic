# Compilation Strategies for Dynamic Typing: A Practical Comparison

## The Central Question

**How do we compile BASIC programs with dynamic typing while maintaining reasonable performance and semantic correctness?**

## Strategy 1: Default to DOUBLE (DEFDBL A-Z)

### Proposal

Treat **all untyped variables as DOUBLE** by default, as if the program had `DEFDBL A-Z` at the top.

```basic
' Original program
100 A=1 : B=2
110 C=A+B

' Compiled as if written:
1 DEFDBL A-Z
100 A=1 : B=2
110 C=A+B

' All variables are DOUBLE:
' A# = 1.0#, B# = 2.0#, C# = 3.0#
```

### Implementation

**Code generation**:
```c
// Every untyped variable becomes a double
double A, B, C;

A = 1.0;     // Integer literal promoted to DOUBLE
B = 2.0;
C = A + B;   // DOUBLE + DOUBLE → DOUBLE (3.0)
```

**Typed variables still work**:
```basic
100 X% = 10      ' X% is INTEGER (2 bytes)
110 Y! = 20.5    ' Y! is SINGLE (4 bytes)
120 Z# = 30.3    ' Z# is DOUBLE (8 bytes)
130 W = 40       ' W is DOUBLE (8 bytes) - default
```

### Pros

✅ **Simplest to compile**:
- Single type for all untyped variables
- No runtime type checking needed
- No tagged unions required
- Straightforward code generation

✅ **Predictable performance**:
- All operations use native FPU instructions
- No dispatch overhead
- No type promotion decisions at runtime

✅ **Handles precision correctly**:
- DOUBLE has enough precision for all cases
- No loss of precision from INTEGER→SINGLE→DOUBLE conversions
- Mathematical operations work as expected

✅ **Small code size**:
- No type dispatch code
- No multiple code paths
- Compact compiled output

✅ **Programmer control**:
- Can use `%`, `!`, `#`, `$` suffixes for specific types
- Can add `DEFINT A-Z` for performance (all variables INTEGER)
- Can add `DEFSNG A-Z` for memory savings
- Explicit control when needed

### Cons

❌ **Semantic incompatibility with interpreter**:
```basic
' test_type_change.bas
100 A=1 : B=2
110 C=A+B
120 PRINT C

' Interpreter output: 3 (INTEGER)
' Compiled output:    3.0 (DOUBLE displayed as "3" but stored as DOUBLE)
```

❌ **Memory overhead**:
- Every variable uses 8 bytes (DOUBLE) instead of 2 bytes (INTEGER)
- 4x memory usage for programs that would naturally use INTEGER
- Example: 100 variables = 800 bytes vs 200 bytes

❌ **8080 performance penalty**:
- DOUBLE operations are 500-800x slower than INTEGER on 8080
- Program that should run in INTEGER becomes DOUBLE-heavy
- Massive performance regression on vintage hardware

❌ **Hidden type conversions**:
```basic
100 X% = 10         ' X% is INTEGER
110 Y = 20          ' Y is DOUBLE (not obvious!)
120 Z = X% + Y      ' INTEGER→DOUBLE conversion, result is DOUBLE
```

❌ **Breaks optimization assumptions**:
- Programmers who wrote `A=1` expected INTEGER (fast)
- Compiler makes it DOUBLE (slow on 8080)
- No warning about performance cliff

### When This Works Well

**Good for**:
- Programs already using floating-point math
- Modern hardware (x86-64 with FPU)
- Scientific/mathematical applications
- Programs that need precision

**Example** (good fit):
```basic
100 REM Calculate circle area
110 PI = 3.14159265358979
120 RADIUS = 10
130 AREA = PI * RADIUS * RADIUS
140 PRINT "Area ="; AREA
' All variables are DOUBLE - appropriate here
```

### When This Fails

**Bad for**:
- Integer-heavy programs (counters, loops, array indices)
- 8080 target (huge performance penalty)
- Memory-constrained systems
- Programs expecting INTEGER semantics

**Example** (bad fit):
```basic
100 REM Count to 1000
110 FOR I = 1 TO 1000
120   PRINT I;
130 NEXT I
' I is DOUBLE (8 bytes, slow FP ops on 8080)
' Should be INTEGER (2 bytes, fast native ops)
```

---

## Strategy 2: Default to INTEGER (DEFINT A-Z)

### Proposal

Treat all untyped variables as **INTEGER**, promoting to SINGLE/DOUBLE only when necessary.

```basic
100 A=1 : B=2
110 C=A+B        ' INTEGER + INTEGER → INTEGER (3)

100 A=1.5 : B=2.5
110 C=A+B        ' SINGLE + SINGLE → SINGLE (4.0)
```

### Implementation

**Type inference**:
```c
// Analyze literal types
int16_t A = 1;     // Integer literal → INTEGER
int16_t B = 2;     // Integer literal → INTEGER
int16_t C = A + B; // INTEGER + INTEGER → INTEGER

// But:
float A = 1.5f;    // Float literal → SINGLE
float B = 2.5f;
float C = A + B;   // SINGLE + SINGLE → SINGLE
```

### Pros

✅ **Better 8080 performance**:
- INTEGER operations are fast (native CPU)
- Only promotes when literals force it
- Matches programmer's likely intent

✅ **Memory efficient**:
- INTEGER = 2 bytes vs DOUBLE = 8 bytes
- 4x memory savings for integer-heavy code

✅ **Closer to interpreter behavior**:
- Integers stay integers when possible
- Promotion only when needed

### Cons

❌ **Still wrong for test_type_change.bas**:
```basic
1010 C=A+B
' First call: A=1, B=2 → C is INTEGER (correct!)
' Second call: A=1.1, B=2.2 → C is ???
' Problem: A and B are already declared as some type!
```

❌ **Type inference complexity**:
- Need to analyze all assignments to each variable
- What if `A=1` on line 100, then `A=1.5` on line 200?
- Must detect type conflicts at compile time

❌ **Precision loss**:
```basic
100 X = 10000
110 Y = X * X        ' 100,000,000 overflows 16-bit INTEGER!
120 PRINT Y          ' Wrong result!
```

❌ **Unexpected behavior**:
- Programmer writes `X = 1` thinking it's flexible
- Compiler locks it as INTEGER forever
- Later `X = 1.5` either errors or truncates

---

## Strategy 3: Type Stability Analysis (Hybrid)

### Proposal

**Analyze each variable** to determine if it's type-stable or type-unstable:

- **Type-stable**: Compile as native type (fast)
- **Type-unstable**: Use tagged union (correct but slower)

```basic
100 A=1 : B=2
110 C=A+B           ' A, B, C are type-stable (always INTEGER)

100 INPUT A, B      ' A, B are type-unstable (depends on user input)
110 C=A+B           ' C is type-unstable (depends on A, B types)
```

### Implementation

**Analysis phase**:
```python
def analyze_variable_type_stability(var_name):
    assignments = find_all_assignments(var_name)
    types = [infer_type(expr) for expr in assignments]

    if all(t == types[0] for t in types):
        return TypeStable(types[0])
    else:
        return TypeUnstable()
```

**Code generation**:
```c
// Type-stable variables (fast path)
int16_t X = 10;
int16_t Y = 20;
int16_t Z = X + Y;

// Type-unstable variables (slow path)
typedef struct { uint8_t type; union { int16_t i; float f; double d; } val; } Var;
Var A, B, C;

// Assignment with type checking
void assign_add(Var* dest, Var* src1, Var* src2) {
    if (src1->type == INT && src2->type == INT) {
        dest->type = INT;
        dest->val.i = src1->val.i + src2->val.i;
    } else if (src1->type == SINGLE || src2->type == SINGLE) {
        dest->type = SINGLE;
        dest->val.f = to_single(src1) + to_single(src2);
    } else {
        dest->type = DOUBLE;
        dest->val.d = to_double(src1) + to_double(src2);
    }
}
```

### Pros

✅ **Semantically correct**:
- Handles test_type_change.bas correctly
- Type-unstable variables can change types
- Matches interpreter behavior exactly

✅ **Optimizes common case**:
- Most variables are type-stable (90%+ in typical programs)
- Fast path for the common case
- Slow path only where needed

✅ **Best of both worlds**:
- Fast for well-typed code
- Correct for dynamic code

### Cons

❌ **Complex implementation**:
- Requires sophisticated dataflow analysis
- Must handle all control flow (IF, GOTO, GOSUB)
- Edge cases are tricky (what about ON...GOTO?)

❌ **Runtime overhead**:
- Tagged unions are 12-16 bytes (vs 2-8 bytes native)
- Type checking on every operation for unstable variables
- Dispatch overhead (even if small)

❌ **Code size**:
- Need both fast and slow path implementations
- Type dispatch machinery
- Larger compiled binaries

❌ **Debugging complexity**:
- Hard to predict which variables are stable
- Performance can vary unexpectedly
- Need good diagnostic output

---

## Strategy 4: Conservative SINGLE Default

### Proposal

Use **SINGLE** (4-byte float) as the default type - a middle ground between INTEGER and DOUBLE.

```basic
100 A=1 : B=2
110 C=A+B
' A, B, C are all SINGLE
' A = 1.0f, B = 2.0f, C = 3.0f
```

### Pros

✅ **Reasonable compromise**:
- 4 bytes vs 8 bytes (DOUBLE) - 50% memory savings
- Still handles floating-point
- Still semantically incorrect, but less wrong than DOUBLE

✅ **IEEE 754 single precision**:
- Good enough for most BASIC programs
- 7 decimal digits of precision
- Faster than DOUBLE on some systems

### Cons

❌ **Still semantically wrong**:
- Same issues as DEFDBL A-Z
- Just uses 4 bytes instead of 8

❌ **Precision issues**:
```basic
100 X = 10000000      ' 10 million
110 Y = X + 1         ' Lost in FP precision!
120 PRINT Y           ' Still 10000000 (SINGLE only has ~7 digits)
```

❌ **8080 still slow**:
- SINGLE is still software FP on 8080
- Still 500x slower than INTEGER
- Memory savings vs DOUBLE, but still slow

---

## Recommendation: DEFDBL A-Z (Strategy 1)

### Why This is the Best Choice

Given the constraints and goals, **DEFDBL A-Z** is recommended:

**Primary reason**: **Simplicity**

1. **Compilation complexity**: Simple and straightforward
2. **Code generation**: Clean, no special cases
3. **Debugging**: Predictable behavior
4. **Maintenance**: Easy to understand and modify

**Secondary reasons**:

1. **Modern target assumption**:
   - Modern CPUs have hardware FPU
   - DOUBLE operations are fast (same speed as SINGLE on x86-64)
   - Memory is abundant (8 bytes vs 2 bytes doesn't matter)

2. **Programmer control**:
   - Programmers can add `DEFINT A-Z` if they want INTEGER
   - Can use `%` suffix on variables for performance
   - Can use `!` for SINGLE if memory matters
   - **Opt-in optimization** rather than forcing everyone into complexity

3. **Precision is safer than performance**:
   - DOUBLE never loses precision
   - INTEGER can overflow silently
   - Better to be slow and correct than fast and wrong

4. **Documentation**:
   - Easy to document: "All untyped variables are DOUBLE"
   - Clear migration path: "Add DEFINT A-Z for performance"
   - Simple mental model

### Recommended Implementation Plan

**Phase 1**: Basic compiler with DEFDBL A-Z default
```basic
' Default behavior
100 X = 10      ' X is DOUBLE
110 Y = 20      ' Y is DOUBLE
120 Z = X + Y   ' Z is DOUBLE
```

**Phase 2**: Honor DEFINT/DEFSNG/DEFDBL statements
```basic
10 DEFINT A-Z   ' Override: all variables are INTEGER
100 X = 10      ' X is INTEGER
110 Y = 20      ' Y is INTEGER
120 Z = X + Y   ' Z is INTEGER
```

**Phase 3**: Warning system for performance
```
Warning: Variable 'I' in FOR loop is DOUBLE. Consider using I% for better performance.
Warning: 100 untyped variables detected. Consider adding DEFINT A-Z.
```

**Phase 4** (optional): Type stability analysis for automatic optimization
```
Info: Variable 'X' is type-stable (always INTEGER). Optimizing to native int16_t.
Info: 95% of variables are type-stable. Fast path used for 95% of operations.
```

### How to Use It

**For programmers who care about performance**:
```basic
10 DEFINT A-Z        ' All variables INTEGER by default
20 PI# = 3.14159     ' Explicit DOUBLE for precision where needed
30 FOR I = 1 TO 100  ' I is INTEGER (fast)
40   X = I * I       ' X is INTEGER (fast)
50 NEXT I
```

**For programmers who want correctness**:
```basic
' Just write code - everything is DOUBLE
100 FOR I = 1 TO 100
110   X = I * 3.14159
120 NEXT I
' Works correctly, maybe slower on 8080, but correct
```

**For test_type_change.bas compatibility**:
```basic
' Add explicit type suffixes
100 A#=1 : B#=2
110 C#=A#+B#
' Or accept that compiled version doesn't match interpreter exactly
' (document this limitation)
```

### Documented Limitations

Be upfront about the semantic differences:

```markdown
## Compiler Behavior: Type Defaults

The MBASIC compiler treats **all untyped variables as DOUBLE** by default.

This differs from the interpreter, which uses dynamic typing.

### Examples

```basic
' Interpreter: A is INTEGER (2 bytes)
' Compiler:    A is DOUBLE (8 bytes)
100 A = 10

' Interpreter: Type depends on runtime value
' Compiler:    Always DOUBLE
100 INPUT A
```

### Workarounds

1. **Use type suffixes** for specific types:
   ```basic
   100 X% = 10     ' INTEGER
   100 Y! = 10.5   ' SINGLE
   100 Z# = 10.5   ' DOUBLE
   ```

2. **Use DEF statements** to change defaults:
   ```basic
   10 DEFINT A-Z   ' All variables INTEGER
   10 DEFSNG A-Z   ' All variables SINGLE
   ```

3. **Accept the tradeoff**: DOUBLE is slower on 8080 but always correct.
```

---

## Comparison Matrix

| Strategy | Simplicity | Performance (Modern) | Performance (8080) | Semantic Correctness | Code Size |
|----------|-----------|---------------------|-------------------|---------------------|-----------|
| DEFDBL A-Z | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| DEFINT A-Z | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| Type Stability | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| DEFSNG A-Z | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ |

**Legend**: More stars = better

---

## Conclusion

**Default to DEFDBL A-Z** is the recommended approach because:

1. ✅ Simplest to implement and maintain
2. ✅ Best performance on modern hardware
3. ✅ Never loses precision
4. ✅ Gives programmers control via DEF/suffixes
5. ⚠️ Semantic incompatibility is **documented and acceptable**
6. ⚠️ 8080 performance penalty is **known limitation**

The key insight: **Perfect semantic compatibility is not worth the implementation complexity** for a compiler. The interpreter already exists for perfect compatibility. The compiler's job is to produce **fast, correct code** with a **simple, maintainable implementation**.

Programs that absolutely need dynamic typing can use the interpreter. Programs that want compilation can accept the DEFDBL default or add explicit type annotations.

---

**Related Files**:
- `doc/DYNAMIC_TYPE_CHANGE_PROBLEM.md` - Technical deep dive
- `tests/test_type_change.bas` - Edge case demonstration
- `src/semantic_analyzer.py` - Type inference implementation
