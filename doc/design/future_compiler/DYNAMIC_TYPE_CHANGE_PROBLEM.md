# Dynamic Type Change Problem in BASIC Compilation

## Historical Context: The 8080 Architecture

Microsoft BASIC (MBASIC) originally ran on the **Intel 8080** processor, which had severe limitations:

- **8-bit CPU**: Only native 8-bit arithmetic operations
- **Limited 16-bit support**: 16-bit operations required multiple instructions
- **No floating-point hardware**: No FPU, no floating-point instructions
- **Software floating-point**: SINGLE and DOUBLE operations implemented as **large subroutines**
  - Addition/subtraction: ~100-200 bytes of code
  - Multiplication/division: ~200-400 bytes of code
  - Transcendental functions (SIN, COS, LOG, EXP): ~500-1000 bytes each

This meant:
- Integer operations were **fast** (native CPU instructions)
- Floating-point operations were **extremely slow** (100-1000x slower)
- Code size was **precious** (typical systems had 16-64KB total memory)
- Type-specific code paths had **huge performance implications**

**Modern compilation challenge**: How do we efficiently compile BASIC for modern CPUs while preserving the semantics of a language designed for an 8-bit interpreter with software floating-point?

## The Problem

In interpreted Microsoft BASIC, **variables can change type at runtime** based on the expression assigned to them. This behavior is fundamental to BASIC's dynamic typing but poses significant challenges for compilation.

## Concrete Example

```basic
100 REM test changing the type of a variable at run time
110 A=1 : B=2
120 GOSUB 1000
130 PRINT C           ' C is INTEGER (3)
140 A=1.1 : B=2.2
150 GOSUB 1000
155 PRINT C           ' C is SINGLE (3.3)
160 X# = 1.11 : Y# = 2.22
170 A=X# : B=Y#
180 GOSUB 1000
190 PRINT C           ' C is DOUBLE (3.33)
200 END
1000 REM do some sort of math we dont know precision
1005 REM note the type of c is different on each call: integer, then float, then double
1010 C=A+B
1020 RETURN
```

### What Happens at Line 1010

The type of `C` changes **dynamically** based on the types of `A` and `B`:

| Call | A Type | B Type | Expression `A+B` Type | Resulting C Type |
|------|--------|--------|-----------------------|------------------|
| 1st  | INTEGER (1) | INTEGER (2) | INTEGER | INTEGER (value: 3) |
| 2nd  | SINGLE (1.1) | SINGLE (2.2) | SINGLE | SINGLE (value: 3.3) |
| 3rd  | DOUBLE (1.11#) | DOUBLE (2.22#) | DOUBLE | DOUBLE (value: 3.33) |

**Key observation**: The variable `C` has **no type suffix**, yet it holds different types at different times during program execution!

## BASIC Type System Rules

### Variables Without Type Suffixes

In BASIC without `DEFINT`, `DEFDBL`, etc., variables without suffixes are **dynamically typed**:

```basic
X = 10        ' X becomes INTEGER
X = 10.5      ' X becomes SINGLE
X = 10.5#     ' X becomes DOUBLE (promoted from SINGLE literal)
X$ = "text"   ' ERROR: Can't assign string to numeric variable
```

### Variables With Type Suffixes

Variables with suffixes have **fixed types**:

```basic
X% = 10       ' X% is always INTEGER
X% = 10.5     ' X% becomes 11 (rounded to INTEGER)
X! = 10       ' X! is always SINGLE
X# = 10       ' X# is always DOUBLE
X$ = "text"   ' X$ is always STRING
```

### Expression Type Promotion Rules

BASIC promotes expression types using a hierarchy:

```
INTEGER < SINGLE < DOUBLE
```

Rules:
1. **INTEGER + INTEGER** → **INTEGER**
2. **INTEGER + SINGLE** → **SINGLE** (INTEGER promoted)
3. **INTEGER + DOUBLE** → **DOUBLE** (INTEGER promoted)
4. **SINGLE + DOUBLE** → **DOUBLE** (SINGLE promoted)
5. **Any operation with DOUBLE** → **DOUBLE**

### Assignment Type Coercion

When assigning to a typed variable:
```basic
X% = 10.9     ' Rounds to 11 (INTEGER)
X! = 10       ' Converts to 10.0 (SINGLE)
X# = 10       ' Converts to 10.0# (DOUBLE)
```

When assigning to an untyped variable:
```basic
X = <expr>    ' X takes the type of <expr>
```

## Why This Complicates Compilation

### Problem 1: Storage Size

Different types require different storage:
- **INTEGER**: 2 bytes (16-bit)
- **SINGLE**: 4 bytes (32-bit IEEE 754)
- **DOUBLE**: 8 bytes (64-bit IEEE 754)
- **STRING**: Variable length (pointer + length)

**Compiler challenge**: How much stack/memory to allocate for `C`?

### Problem 2: Calling Conventions

When passing `C` to a function or subroutine:
```basic
GOSUB 1000    ' What type is C here?
```

**Compiler challenge**: The callee needs to know the type to:
- Read the correct number of bytes
- Use the right floating-point operations
- Handle the value correctly

### Problem 3: Type-Specific Operations

Different types use different CPU operations:

**On modern CPUs (x86-64)**:
- **INTEGER**: `ADD`, `SUB`, `IMUL`, `IDIV` (native integer ALU)
- **SINGLE**: `ADDSS`, `SUBSS`, `MULSS`, `DIVSS` (SSE scalar single)
- **DOUBLE**: `ADDSD`, `SUBSD`, `MULSD`, `DIVSD` (SSE scalar double)

**On the original 8080**:
- **INTEGER**: `ADD`, `SUB` (8-bit), `DAD` (16-bit add via register pairs)
- **SINGLE**: `CALL FADD` → 100+ byte subroutine using 8-bit operations
- **DOUBLE**: `CALL DADD` → 200+ byte subroutine with even more precision

This created a **massive performance cliff**:
```basic
X% = 100 + 200     ' ~10 clock cycles on 8080 (native 16-bit add)
X! = 100 + 200     ' ~5000 clock cycles (software FP conversion + addition)
X# = 100 + 200     ' ~8000 clock cycles (double precision software FP)
```

**Compiler challenge**:
- Modern systems: What SSE/FPU instruction to emit for `PRINT C`?
- 8080 systems: What subroutine to call? (each call uses precious stack space)
- Performance varies **500-800x** between INTEGER and DOUBLE on 8080!

### Problem 4: Optimization Barriers

Type changes prevent many optimizations:
```basic
C = A + B     ' Can't know result type at compile time
D = C * 2     ' Can't optimize: is this integer or FP multiply?
```

**Compiler challenge**: Can't perform:
- Constant folding (don't know type of intermediate results)
- Register allocation (register size varies)
- Strength reduction (depends on type)
- Common subexpression elimination (different types = different values)

### Why Did the Interpreter Use Dynamic Typing?

Given the huge performance cost of floating-point on the 8080, **why allow type changes at all?**

**Interpreter advantages** on 8080:
1. **Simplicity for programmers**: No type declarations needed, just use `%`, `!`, `#`, `$` when you want specific types
2. **Memory efficiency**: Store value + 1-byte type tag = 9 bytes max (vs. always allocating 8 bytes for DOUBLE)
3. **Runtime flexibility**: Promote to DOUBLE only when needed (most computations stay INTEGER)
4. **Tokenized code**: Interpreter stores program as tokens, variable types discovered at runtime
5. **Small interpreter**: Type dispatch code shared across all operations (~1KB overhead)

**Compiler disadvantages** on 8080:
1. **Code explosion**: Need type-specific code for every operation → large binaries
2. **Stack pressure**: Deep call chains (FP subroutines) use precious stack
3. **No optimization**: Can't inline FP operations (they're huge subroutines)

**Key insight**: On an 8080 with 16KB-64KB total RAM, the interpreter's **memory overhead was acceptable** (~2-4KB for interpreter + type dispatch), while a compiler's **code size explosion was not** (could easily exceed available memory).

**Modern perspective**: On modern CPUs with hardware FPU and MB/GB of RAM, these tradeoffs are **completely reversed**:
- Compiled code size doesn't matter (we have MB of cache)
- Tagged unions waste cache lines (bad for performance)
- Hardware FP is as fast as integer (no 500x penalty)
- JIT compilation can specialize hot paths

## Compilation Strategies

### Strategy 1: Tagged Unions (Interpreter Approach)

Store every variable as a discriminated union:

```c
typedef struct {
    enum { INTEGER, SINGLE, DOUBLE, STRING } type;
    union {
        int16_t i;
        float f;
        double d;
        struct { char* ptr; int len; } s;
    } value;
} BasicValue;
```

**Pros**:
- Handles all type changes correctly
- Matches interpreter behavior exactly
- Simple to implement

**Cons**:
- **Huge memory overhead**: 12-16 bytes per variable (vs 2-8 bytes)
- **Slow**: Every operation needs type checking
- **No optimization**: Can't use native CPU operations efficiently
- **Cache unfriendly**: Large structures, poor locality

### Strategy 2: Static Type Inference with Runtime Checks

Analyze program flow to infer types, add runtime checks where needed:

```c
// Infer that C is usually INTEGER
int C = A + B;  // Fast path

// Add runtime check if types might vary
if (typeof(A) != INTEGER || typeof(B) != INTEGER) {
    // Fall back to dynamic typed operation
    C_as_variant = dynamic_add(A_variant, B_variant);
}
```

**Pros**:
- Fast for common cases
- Smaller code size than pure interpreter
- Can optimize type-stable code

**Cons**:
- Complex analysis required
- Runtime overhead for checks
- Still needs variant representation as fallback
- Hard to get right (soundness vs completeness tradeoff)

### Strategy 3: Multiple Specialized Versions

Generate multiple versions of subroutines for different type combinations:

```c
// Version 1: C as INTEGER
void sub1000_III() {  // A=INT, B=INT, C=INT
    C = A + B;
}

// Version 2: C as SINGLE
void sub1000_SSS() {  // A=SINGLE, B=SINGLE, C=SINGLE
    C = A + B;
}

// Version 3: C as DOUBLE
void sub1000_DDD() {  // A=DOUBLE, B=DOUBLE, C=DOUBLE
    C = A + B;
}

// Dispatch based on runtime types
void gosub_1000() {
    if (type(A) == INT && type(B) == INT)
        sub1000_III();
    else if (type(A) == SINGLE && type(B) == SINGLE)
        sub1000_SSS();
    else if (type(A) == DOUBLE && type(B) == DOUBLE)
        sub1000_DDD();
    else
        sub1000_mixed();  // Handle mixed types
}
```

**Pros**:
- Fast execution (each version is optimized)
- No runtime type checks within specialized code
- Can optimize each version independently

**Cons**:
- **Code explosion**: O(T^N) versions where T=types, N=variables
- Still needs dispatch logic
- Larger binary size
- Compilation time increases exponentially

### Strategy 4: Type Specialization with Tracing JIT

Runtime profiling to identify hot paths, then JIT compile:

```
1. Start with interpreter
2. Profile to find hot code (e.g., subroutine 1000)
3. Observe actual types used (C is INTEGER 90% of the time)
4. JIT compile specialized version for INTEGER
5. Add guards: if types differ, fall back to interpreter
```

**Pros**:
- Best of both worlds: fast for hot code, correct for rare cases
- Only compiles what's actually used
- Adapts to runtime behavior

**Cons**:
- Complex to implement (JIT compiler + runtime)
- Higher memory usage (code cache)
- Startup overhead
- Overkill for simple BASIC programs

### Strategy 5: Require Type Declarations (Modern Approach)

Extend BASIC with type declaration requirements:

```basic
DEFINT A-Z          ' All variables default to INTEGER
DIM C AS SINGLE     ' Explicitly declare C as SINGLE
```

**Pros**:
- Compile-time type checking
- Optimal code generation
- All standard compiler optimizations apply
- Smallest and fastest code

**Cons**:
- **Not compatible with original BASIC**
- Breaks existing programs
- Requires programmer discipline
- Loses BASIC's simplicity

### Strategy 6: Conservative Static Typing

Assume **SINGLE** for all untyped variables:

```basic
C = A + B    ' Treat C as SINGLE by default
```

If programmer wants other types, they must use suffixes:
```basic
C% = A% + B%    ' INTEGER
C# = A# + B#    ' DOUBLE
```

**Pros**:
- Simple and predictable
- Good performance (no runtime checks)
- Small code size
- Enables optimizations

**Cons**:
- **Incorrect behavior** for the test case!
- First call produces 3.0 instead of 3
- Not compatible with interpreter semantics
- May break programs that rely on type promotion

## The Fundamental Tradeoff

There is an **inherent tension** between:

1. **Compatibility**: Match interpreter behavior exactly
2. **Performance**: Generate fast, optimized code
3. **Simplicity**: Keep compiler implementation manageable

**You can pick at most 2 of these 3.**

## Recommended Approach for MBASIC Compiler

Given the goals of the project (faithful BASIC compilation for vintage systems), I recommend:

### Hybrid Strategy: Static Analysis + Tagged Storage

1. **Detect type-stable variables**: Use dataflow analysis to find variables that never change type
   - Example: `X% = 10` then only used in integer contexts
   - Compile these as native types (fast path)

2. **Use tagged unions for type-unstable variables**: Variables that might change type
   - Example: `C` in the test case
   - Store with type tag (interpreter-like)

3. **Optimize the common case**: Most BASIC programs don't exploit dynamic typing
   - Variables typically have one type throughout execution
   - Detection rate should be >90% in typical programs

4. **Document the limitation**: Be upfront about edge cases
   - Programs that heavily rely on type changes may run slower
   - Provide `DEFINT`/`DEFSNG`/`DEFDBL` as optimization hints

### Implementation Details

```basic
' Compiler analysis determines:
X = 10        ' X is type-stable (INTEGER) → compile as int16_t
Y = 10.5      ' Y is type-stable (SINGLE) → compile as float
C = A + B     ' C is type-unstable → compile as BasicValue (tagged union)

' Code generation:
' Fast path (type-stable):
int16_t X = 10;
float Y = 10.5f;

' Slow path (type-unstable):
BasicValue C;
if (A.type == INTEGER && B.type == INTEGER) {
    C.type = INTEGER;
    C.value.i = A.value.i + B.value.i;
} else if (A.type == SINGLE || B.type == SINGLE) {
    C.type = SINGLE;
    C.value.f = promote_to_single(A) + promote_to_single(B);
} else {
    C.type = DOUBLE;
    C.value.d = promote_to_double(A) + promote_to_double(B);
}
```

### Detection Algorithm

**Type Stability Analysis** (dataflow analysis):

```
For each variable V:
1. Collect all assignments to V
2. Determine type of each RHS expression
3. If all types are the same → V is type-stable
4. If types differ → V is type-unstable
5. If any assignment depends on runtime input → conservative (unstable)
```

**Example**:
```basic
100 X = 10           ' RHS type: INTEGER
110 X = X + 1        ' RHS type: INTEGER (X is INTEGER)
120 X = X * 2        ' RHS type: INTEGER
' Result: X is type-stable (INTEGER)

100 C = A + B        ' RHS type: depends on A and B types
110 GOSUB 1000
120 PRINT C
' Result: C is type-unstable (depends on runtime values)
```

## Testing Strategy

Create comprehensive tests for:

1. **Type-stable variables** (should compile efficiently)
   ```basic
   X% = 10 : Y% = 20 : Z% = X% + Y%
   ```

2. **Type-unstable variables** (should work correctly)
   ```basic
   ' test_type_change.bas - your example
   ```

3. **Edge cases**:
   - Type changes in loops
   - Type changes across GOSUBs
   - Mixed typed and untyped variables
   - String to numeric conversion errors

4. **Performance benchmarks**:
   - Compare type-stable vs type-unstable code
   - Measure overhead of tagged unions
   - Profile hot paths

## Conclusion

**Dynamic type changes are a fundamental feature of interpreted BASIC** that creates significant compilation challenges. There is no perfect solution—only tradeoffs.

The recommended hybrid approach:
- ✅ Preserves semantic compatibility
- ✅ Optimizes the common case (type-stable variables)
- ✅ Keeps implementation manageable
- ⚠️ Accepts some overhead for type-unstable variables

**Key insight**: The test case `test_type_change.bas` represents an **edge case** that exploits BASIC's dynamic typing. Most real BASIC programs don't change variable types like this, so optimizing for the common case is the right tradeoff.

### 8080 Compilation Implications

If targeting the **original 8080** architecture, additional considerations apply:

**Memory constraints**:
- Total RAM: 16KB-64KB (including program, variables, stack)
- Code size critical: Every byte counts
- No virtual memory: Can't page code in/out

**Performance characteristics**:
- INTEGER operations: 10-50 clock cycles (fast)
- SINGLE operations: 5,000-10,000 clock cycles (very slow - software FP)
- DOUBLE operations: 8,000-15,000 clock cycles (extremely slow)
- Type dispatch overhead: ~50-100 clock cycles (negligible compared to FP)

**Recommended 8080 strategy**:
1. **Aggressive type stability analysis**: Even more important on 8080
2. **Prefer INTEGER when possible**: 500x performance difference matters!
3. **Warn on type promotion**: Alert programmer when INTEGER → SINGLE/DOUBLE
4. **Minimal tagged union overhead**: Use 3-byte encoding (1 type byte + 2 value bytes for INT, reuse space for FP pointers)
5. **Share FP subroutines**: Don't inline - call existing MBASIC FP library
6. **Optimize INTEGER paths**: Emit native 8080 code for type-stable INTEGER variables

**Code generation example** (8080):
```asm
; Type-stable INTEGER (fast path)
LDA  A_VAR      ; Load A (low byte)
MOV  L, A
LDA  A_VAR+1    ; Load A (high byte)
MOV  H, A
XCHG            ; HL -> DE
LDA  B_VAR      ; Load B
MOV  L, A
LDA  B_VAR+1
MOV  H, A
DAD  D          ; HL = HL + DE (16-bit add)
SHLD C_VAR      ; Store result
; Total: ~60 clock cycles

; Type-unstable (slow path)
LXI  H, A_VAR   ; Load address of A
LXI  D, B_VAR   ; Load address of B
LXI  B, C_VAR   ; Address for result
CALL ADD_VAR    ; Call generic add routine
                ; Checks types, promotes, calls FP subroutines
                ; 5000-10000 clock cycles for FP
```

**8080-specific tradeoff**: Tagged unions acceptable because:
- Type dispatch (~100 cycles) is negligible vs. FP operations (5000+ cycles)
- Sharing FP subroutines saves more code space than it costs in dispatch
- Most programs are type-stable anyway (stay in INTEGER fast path)

## Future Work

1. **Implement type stability analysis** in semantic analyzer
2. **Detect and warn** about type-unstable variables
3. **Provide optimization hints**: Suggest using type suffixes
4. **Measure impact**: Profile real BASIC programs to see how often types change
5. **Consider dialect flag**: `--strict-types` mode for modern code

---

**Related Files**:
- `tests/test_type_change.bas` - Demonstrates the problem
- `src/semantic_analyzer.py` - Type inference implementation
- `doc/OPTIMIZATION_STATUS.md` - Optimization documentation
