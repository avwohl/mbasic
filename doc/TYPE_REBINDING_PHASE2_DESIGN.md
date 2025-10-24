# Type Rebinding Phase 2: Promotion Analysis

## Overview

**Phase 2** extends Phase 1 by allowing variables to be **promoted** from INTEGER to DOUBLE when needed, with explicit conversion tracking. This enables more aggressive optimization while maintaining correctness.

## The Problem Phase 2 Solves

Phase 1 detects when variables can safely *change* types between program points, but is conservative:

**Problem Example:**
```basic
100 X = 10        ' X is INTEGER
110 Y = X + 1     ' Y depends on X (INTEGER)
120 X = 10.5      ' X becomes DOUBLE
130 Z = Y + X     ' Y (INTEGER) + X (DOUBLE) - requires promotion!
```

**Phase 1 behavior:**
- Detects X changes from INTEGER → DOUBLE
- Detects Y depends on X
- **Conclusion**: Cannot optimize (Y depends on old X value)

**Phase 2 goal:**
- Detect that Y was computed from INTEGER X
- Allow Y to be INTEGER at line 110
- At line 130, explicitly promote Y to DOUBLE for the addition
- Result: Y can be INTEGER (fast) until promotion needed

## Key Concepts

### 1. Type Promotion vs Type Rebinding

**Type Rebinding** (Phase 1):
- Variable completely changes type at a program point
- Old value is NOT carried forward
- Example: `I=22.1; FOR I=0 TO 10` - I is DOUBLE then INTEGER (fresh value)

**Type Promotion** (Phase 2):
- Variable is widened (INT→DOUBLE) while keeping value
- Old value IS carried forward
- Example: `X=10; Y=X+0.5` - X is promoted from INT to DOUBLE

### 2. Safe Promotion Points

A variable can be promoted from INTEGER to DOUBLE when:
1. **Mixed-type expression**: INTEGER used in DOUBLE context
2. **Explicit conversion**: INT(), FIX() remove fractional part
3. **Value-preserving**: All integers fit exactly in DOUBLE

**BASIC's type system guarantees:**
- Every INTEGER can be exactly represented as DOUBLE
- DOUBLE has 64-bit mantissa, INTEGER is 16-bit
- No precision loss on promotion

### 3. Explicit vs Implicit Promotion

**Implicit promotion** (automatic):
```basic
X% = 10         ' X is INTEGER
Y = X% + 1.5    ' X promoted to DOUBLE for addition
```

**Explicit promotion** (tracked by compiler):
```basic
X = 10          ' X is INTEGER
Y = CDBL(X)     ' Explicit CDBL() conversion
```

## Phase 2 Capabilities

### Detection

**What Phase 2 can detect:**
1. Variables that start as INTEGER and need promotion
2. Program points where promotion occurs
3. Whether promotion is safe (value-preserving)
4. Expressions that trigger promotion

**Example:**
```basic
100 N = 100                    ' N is INTEGER
110 FOR I = 1 TO N             ' I is INTEGER
120   X = I * 2                ' X is INTEGER (2 is INTEGER)
130   Y = X + 0.5              ' X promoted to DOUBLE (0.5 is DOUBLE)
140 NEXT I
```

**Phase 2 analysis:**
- N: INTEGER (constant)
- I: INTEGER (FOR loop bounds)
- X: INTEGER at line 120, promoted to DOUBLE at line 130
- Y: DOUBLE (result of DOUBLE addition)

### Tracking

**Promotion points:**
```python
@dataclass
class TypePromotion:
    line: int
    variable: str
    from_type: VarType  # INTEGER
    to_type: VarType    # DOUBLE
    reason: str         # "Mixed-type expression", "Explicit conversion", etc.
    expression: str     # The expression causing promotion
```

**Example tracking:**
```
Type Promotions Found:
  X:
    Line 130: INTEGER → DOUBLE
    Reason: Mixed-type expression (INTEGER + DOUBLE)
    Expression: X + 0.5
```

## Implementation Strategy

### Step 1: Extend TypeBinding with Promotion Info

```python
@dataclass
class TypeBinding:
    line: int
    variable: str
    var_type: VarType
    context: str
    depends_on_self: bool
    promotion_from: Optional[VarType] = None  # NEW: promoted from this type
    promotion_reason: str = ""                 # NEW: why promoted
```

### Step 2: Add Promotion Detection

```python
def _detect_type_promotions(self, program: ProgramNode):
    """
    Detect where INTEGER variables need promotion to DOUBLE.

    Promotion occurs when:
    1. INTEGER used in DOUBLE expression (X + 0.5)
    2. INTEGER assigned to DOUBLE variable (Y# = X%)
    3. INTEGER passed to function expecting DOUBLE
    """
    for stmt in program.statements:
        if isinstance(stmt, AssignmentNode):
            self._check_expression_for_promotions(stmt.expression, stmt.line)
```

### Step 3: Promotion-Safe Analysis

```python
def _can_promote_safely(self, var_name: str, from_type: VarType, to_type: VarType) -> bool:
    """
    Check if promotion is safe (value-preserving).

    INTEGER → DOUBLE: Always safe (all integers fit exactly)
    SINGLE → DOUBLE: Always safe (DOUBLE has more precision)
    DOUBLE → INTEGER: NOT safe (fractional part lost)
    """
    if from_type == VarType.INTEGER and to_type == VarType.DOUBLE:
        return True
    if from_type == VarType.SINGLE and to_type == VarType.DOUBLE:
        return True
    return False
```

### Step 4: Mixed-Type Expression Analysis

```python
def _analyze_mixed_type_expression(self, expr: ExpressionNode) -> VarType:
    """
    Determine result type of mixed-type expression.

    Rules (BASIC type coercion):
    - INTEGER op INTEGER → INTEGER
    - INTEGER op DOUBLE → DOUBLE (INTEGER promoted)
    - DOUBLE op DOUBLE → DOUBLE
    - STRING op STRING → STRING (concatenation)
    """
    left_type = self._infer_expression_type(expr.left)
    right_type = self._infer_expression_type(expr.right)

    # Promotion rule: wider type wins
    if left_type == VarType.DOUBLE or right_type == VarType.DOUBLE:
        # Record promotion if needed
        if left_type == VarType.INTEGER:
            self._record_promotion(expr.left, VarType.INTEGER, VarType.DOUBLE)
        if right_type == VarType.INTEGER:
            self._record_promotion(expr.right, VarType.INTEGER, VarType.DOUBLE)
        return VarType.DOUBLE

    return VarType.INTEGER
```

## Code Generation Strategy (Future)

### Versioning with Promotion

**Source:**
```basic
100 X = 10        ' X is INTEGER
110 Y = X + 1     ' Y is INTEGER (from INTEGER X)
120 X = 10.5      ' X becomes DOUBLE
130 Z = Y + X     ' Promote Y to DOUBLE for addition
```

**Generated code (conceptual):**
```c
// Version 1: X as INTEGER
int16_t X_v1 = 10;
int16_t Y = X_v1 + 1;     // INTEGER arithmetic (fast!)

// Version 2: X as DOUBLE
double X_v2 = 10.5;

// Promote Y for mixed-type expression
double Z = (double)Y + X_v2;  // Explicit promotion
```

**Key insight:**
- Y stays INTEGER (2 bytes, fast)
- Only promoted when needed (line 130)
- Promotion is explicit cast, not type change

### Optimization Opportunity

**Without promotion analysis:**
```c
double Y = (double)10 + 1;  // Y is DOUBLE from start (8 bytes, slow)
double Z = Y + 10.5;
```

**With promotion analysis:**
```c
int16_t Y = 10 + 1;         // Y is INTEGER (2 bytes, fast)
double Z = (double)Y + 10.5; // Promote only when needed
```

**Savings:**
- 6 bytes memory per variable
- Fast integer arithmetic for Y
- Only one conversion (INT→DOUBLE) instead of multiple DOUBLE ops

## Examples

### Example 1: Simple Promotion

**Source:**
```basic
100 X = 10
110 Y = X + 0.5
```

**Phase 2 analysis:**
```
Type Bindings:
  X: INTEGER (line 100)
  Y: DOUBLE (line 110)

Type Promotions:
  X: INTEGER → DOUBLE at line 110
    Reason: Mixed-type expression (INTEGER + DOUBLE literal)
    Expression: X + 0.5
```

**Code generation:**
```c
int16_t X = 10;
double Y = (double)X + 0.5;  // Explicit promotion
```

### Example 2: Promotion in Loop

**Source:**
```basic
100 FOR I = 1 TO 100
110   X = I * 2            ' INTEGER
120   Y = X + 0.5          ' Promotion needed
130 NEXT I
```

**Phase 2 analysis:**
```
Type Bindings:
  I: INTEGER (FOR loop)
  X: INTEGER (line 110)

Type Promotions:
  X: INTEGER → DOUBLE at line 120
    Reason: Mixed-type expression
    Expression: X + 0.5
```

**Code generation:**
```c
for (int16_t I = 1; I <= 100; I++) {
    int16_t X = I * 2;        // Fast INTEGER multiply
    double Y = (double)X + 0.5; // Promote only here
}
```

### Example 3: Multiple Promotions

**Source:**
```basic
100 A% = 10       ' Explicit INTEGER
110 B% = 20       ' Explicit INTEGER
120 C = A% + B%   ' INTEGER result
130 D = C + 3.14  ' Promotion needed
```

**Phase 2 analysis:**
```
Type Bindings:
  A%: INTEGER (explicit suffix)
  B%: INTEGER (explicit suffix)
  C: INTEGER (line 120 - INTEGER + INTEGER)

Type Promotions:
  C: INTEGER → DOUBLE at line 130
    Reason: Mixed-type expression
    Expression: C + 3.14
```

## Benefits of Phase 2

### Performance

1. **More INTEGER usage**: Variables stay INTEGER longer
2. **Fewer conversions**: Only promote when necessary
3. **Better cache**: Smaller data (2 bytes vs 8 bytes)
4. **Fast arithmetic**: INTEGER ops until promotion

### Memory

- INTEGER: 2 bytes
- DOUBLE: 8 bytes
- **Savings: 6 bytes per variable** that can be INTEGER

For a program with 100 variables, 50 of which can be INTEGER:
- Without Phase 2: 800 bytes (all DOUBLE)
- With Phase 2: 500 bytes (50 INT + 50 DOUBLE)
- **Savings: 300 bytes (37.5%)**

### 8080 Performance

On Intel 8080 (2 MHz):
- INTEGER add: 10 cycles (5 microseconds)
- DOUBLE add: 10,000 cycles (5 milliseconds)
- **1000x speedup** for INTEGER arithmetic

## Implementation Plan

### Phase 2A: Detection Only

1. Extend `TypeBinding` with promotion fields
2. Add `_detect_type_promotions()` method
3. Track promotion points in analysis
4. Add promotion section to report

### Phase 2B: Mixed-Type Analysis

1. Implement `_analyze_mixed_type_expression()`
2. Add type coercion rules (INT+DOUBLE → DOUBLE)
3. Detect implicit promotions
4. Track promotion reasons

### Phase 2C: Validation

1. Ensure all promotions are safe
2. Check for precision loss warnings
3. Verify promotion order (DAG)
4. Test on real programs

### Phase 2D: Code Generation (Future)

1. Generate explicit casts in C code
2. Create promoted variable versions
3. Insert conversions at promotion points
4. Optimize away redundant promotions

## Test Cases

### Test 1: Simple Promotion
```basic
X = 10: Y = X + 0.5
```
Expected: X is INTEGER, promoted to DOUBLE at Y assignment

### Test 2: No Promotion Needed
```basic
X = 10: Y = X + 5
```
Expected: X is INTEGER, no promotion (all INTEGER)

### Test 3: Multiple Promotions
```basic
X = 10: Y = X + 1: Z = Y + 0.5
```
Expected: X INTEGER, Y INTEGER, Y promoted at Z assignment

### Test 4: Loop with Promotion
```basic
FOR I = 1 TO 10: X = I * 2: Y = X + 0.5: NEXT I
```
Expected: I INTEGER, X INTEGER (promoted each iteration)

### Test 5: Explicit Type Suffix
```basic
X% = 10: Y = X% + 0.5
```
Expected: X% stays INTEGER, promoted at addition

## Limitations

### What Phase 2 Cannot Do

1. **DOUBLE → INTEGER demotion**: Not safe (precision loss)
2. **Cross-subroutine promotion**: Phase 3 needed
3. **Conditional promotion**: IF-THEN-ELSE creates merge points
4. **Array element promotion**: Complex (need per-element tracking)

### Edge Cases

1. **Loss of precision**: INT() truncates, affects promotion
2. **Overflow**: INTEGER is 16-bit (-32768 to 32767), can overflow
3. **Type suffixes**: X% must stay INTEGER, cannot promote

## Phase 2 vs Phase 3

**Phase 2** (Promotion):
- Single version per variable
- Explicit promotions (casts)
- Intra-procedural only
- Focus: Keep variables INTEGER as long as possible

**Phase 3** (Specialization):
- Multiple versions of subroutines
- Call-site type matching
- Inter-procedural optimization
- Focus: Optimize across function boundaries

## Success Metrics

Phase 2 is successful if:
1. ✅ Detects 50%+ more INTEGER opportunities than Phase 1
2. ✅ All promotions are safe (no precision loss)
3. ✅ Real programs show measurable speedup
4. ✅ Memory usage decreases (more 2-byte vars)
5. ✅ No false positives (incorrect promotions)

## Next Steps

1. Implement `TypePromotion` dataclass
2. Add promotion detection to `_analyze_variable_type_bindings()`
3. Implement mixed-type expression analysis
4. Add promotion tracking and reporting
5. Test on real BASIC programs
6. Measure performance improvement

---

**Status**: Design phase
**Priority**: High (enables significant optimization)
**Complexity**: Medium (type inference is tricky)
**Dependency**: Phase 1 complete ✅
