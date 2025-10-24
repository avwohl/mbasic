# Type Re-binding Strategy: Variables Can Change Types

## Core Concept

Allow variables to **change types at compile time** by treating each assignment as potentially creating a new "version" of the variable with a different type.

## The Key Insight

In your example:
```basic
100 I=22.1                ' I is DOUBLE here
110 FOR I=0 TO 10         ' I is INTEGER here (new binding!)
120   J=J+I               ' J and I are both INTEGER (fast!)
130 NEXT I
```

The variable `I` changes from DOUBLE to INTEGER at line 110. This is **valid** because:
- Each assignment creates a new type binding
- The FOR loop doesn't use the previous value of I (overwrites it completely)
- We can compile line 120 as fast INTEGER math

## When Type Re-binding Works

### Case 1: Complete Overwrite (No Data Flow)

```basic
100 X = 10.5              ' X is DOUBLE
110 PRINT X               ' Print DOUBLE
120 X = 5                 ' X is now INTEGER (no dependency on previous X)
130 PRINT X               ' Print INTEGER
```

**Analysis**:
- Line 120 doesn't use the old value of X
- Old DOUBLE binding is dead
- New INTEGER binding created
- ✅ **Safe to re-bind**

**Generated Code**:
```c
double X_v1 = 10.5;       // First version: DOUBLE
print_double(X_v1);

int16_t X_v2 = 5;         // Second version: INTEGER
print_integer(X_v2);
```

### Case 2: FOR Loop (Special Case)

```basic
100 I = 22.1              ' I is DOUBLE
110 FOR I = 0 TO 10       ' I is INTEGER (FOR overwrites)
120   PRINT I
130 NEXT I
```

**Analysis**:
- FOR statement completely overwrites I
- Loop body uses only the INTEGER version
- ✅ **Safe to re-bind**

**Generated Code**:
```c
double I_v1 = 22.1;       // Before loop: DOUBLE

int16_t I_v2;             // In loop: INTEGER
for (I_v2 = 0; I_v2 <= 10; I_v2++) {
    print_integer(I_v2);
}
```

### Case 3: Sequential Reassignment

```basic
100 A=1 : B=2
110 GOSUB 1000            ' Calls with INTEGER A, B
120 A=1.1 : B=2.2         ' New bindings: DOUBLE A, B
130 GOSUB 1000            ' Calls with DOUBLE A, B
1000 C=A+B
1010 RETURN
```

**Analysis**:
- Line 100: A, B are INTEGER
- Line 110: Subroutine sees INTEGER A, B → C is INTEGER
- Line 120: A, B re-bound as DOUBLE (no dependency on old values)
- Line 130: Subroutine sees DOUBLE A, B → C is DOUBLE
- ⚠️ **Subroutine C must handle both types!**

**Generated Code (Version 1: Polymorphic Subroutine)**:
```c
// First call
int16_t A_v1 = 1;
int16_t B_v1 = 2;
int16_t C_v1 = A_v1 + B_v1;  // INTEGER + INTEGER

// Second call
double A_v2 = 1.1;
double B_v2 = 2.2;
double C_v2 = A_v2 + B_v2;   // DOUBLE + DOUBLE
```

**Generated Code (Version 2: Unified Subroutine)**:
```c
// Problem: Subroutine must work with both types!
// Solution: Use tagged union or generate multiple versions

typedef struct { uint8_t type; union { int16_t i; double d; } val; } Var;

Var A, B, C;

// First call
A.type = INT; A.val.i = 1;
B.type = INT; B.val.i = 2;
gosub_1000();  // C.type = INT, C.val.i = 3

// Second call
A.type = DOUBLE; A.val.d = 1.1;
B.type = DOUBLE; B.val.d = 2.2;
gosub_1000();  // C.type = DOUBLE, C.val.d = 3.3

void gosub_1000() {
    // Polymorphic addition
    if (A.type == INT && B.type == INT) {
        C.type = INT;
        C.val.i = A.val.i + B.val.i;
    } else {
        C.type = DOUBLE;
        C.val.d = to_double(A) + to_double(B);
    }
}
```

## When Type Re-binding Fails (Gets Complex)

### Problem 1: Data Flow Between Types

```basic
100 X = 10                ' X is INTEGER
110 Y = X + 1             ' Y is INTEGER
120 X = 10.5              ' X is now DOUBLE - but what about Y?
130 Z = Y + X             ' INTEGER Y + DOUBLE X → ???
```

**Analysis**:
- Line 110: Y depends on INTEGER X
- Line 120: X re-bound as DOUBLE
- Line 130: Y is still INTEGER, X is now DOUBLE
- Mixed types in expression: INTEGER + DOUBLE → DOUBLE
- ✅ **Can handle this**: Promote Y to DOUBLE for line 130

**Generated Code**:
```c
int16_t X_v1 = 10;        // First version: INTEGER
int16_t Y = X_v1 + 1;     // Y is INTEGER (depends on X_v1)

double X_v2 = 10.5;       // Second version: DOUBLE
double Z = (double)Y + X_v2;  // Promote Y to DOUBLE for operation
```

### Problem 2: Branching Creates Multiple Versions

```basic
100 X = 10                ' X is INTEGER
110 IF A > 0 THEN X = 10.5 ' Maybe X is DOUBLE?
120 PRINT X               ' What type is X here?
```

**Analysis**:
- Line 100: X is INTEGER
- Line 110: X *might* be re-bound as DOUBLE (depends on condition)
- Line 120: X is INTEGER or DOUBLE depending on runtime path
- ⚠️ **Control flow merge problem**

**Solution 1: Conservative (Promote to DOUBLE)**
```c
double X = 10.0;          // Promote initial value to DOUBLE
if (A > 0) {
    X = 10.5;             // Both paths use DOUBLE
}
print_double(X);
```

**Solution 2: SSA Form (Track Versions)**
```c
int16_t X_v1 = 10;        // Version 1: INTEGER
double X_v2;              // Version 2: DOUBLE (if branch taken)
Var X_v3;                 // Version 3: Phi node (merge of v1 and v2)

if (A > 0) {
    X_v2 = 10.5;
    X_v3.type = DOUBLE;
    X_v3.val.d = X_v2;
} else {
    X_v3.type = INT;
    X_v3.val.i = X_v1;
}
print_var(X_v3);          // Polymorphic print
```

### Problem 3: Loops with Type Changes

```basic
100 X = 0                 ' X is INTEGER
110 FOR I = 1 TO 10
120   X = X + 0.1         ' X is DOUBLE (0.1 is DOUBLE)
130 NEXT I
140 PRINT X
```

**Analysis**:
- Line 100: X is INTEGER (0)
- Line 120: X = X + 0.1
  - Old X is INTEGER
  - 0.1 is DOUBLE
  - New X must be DOUBLE
- Loop creates dependency: new X depends on old X
- ⚠️ **Type changes mid-loop with data flow**

**Solution 1: Promote before loop**
```c
double X = 0.0;           // Promote to DOUBLE before loop
for (int16_t I = 1; I <= 10; I++) {
    X = X + 0.1;
}
print_double(X);
```

**Solution 2: Insert conversion**
```c
int16_t X_v1 = 0;         // Initial: INTEGER
double X_v2 = (double)X_v1;  // Promote before loop
for (int16_t I = 1; I <= 10; I++) {
    X_v2 = X_v2 + 0.1;
}
print_double(X_v2);
```

### Problem 4: Subroutines with Multiple Call Sites

```basic
100 A=1 : B=2             ' INTEGER
110 GOSUB 1000
120 A=1.1 : B=2.2         ' DOUBLE
130 GOSUB 1000
200 A=1.1# : B=2.2#       ' DOUBLE (explicit)
210 GOSUB 1000
1000 C=A+B                ' What type is C?
1010 D=C*2                ' What type is D?
1020 RETURN
```

**Analysis**:
- Subroutine called 3 times
- Call 1: A, B are INTEGER → C should be INTEGER
- Call 2: A, B are DOUBLE → C should be DOUBLE
- Call 3: A, B are DOUBLE → C should be DOUBLE
- Subroutine must be **polymorphic** or **specialized**

**Solution 1: Polymorphic (Slow)**
```c
Var A, B, C, D;  // Tagged unions

void gosub_1000() {
    // Runtime type dispatch
    if (A.type == INT && B.type == INT) {
        C.type = INT;
        C.val.i = A.val.i + B.val.i;
        D.type = INT;
        D.val.i = C.val.i * 2;
    } else {
        C.type = DOUBLE;
        C.val.d = to_double(A) + to_double(B);
        D.type = DOUBLE;
        D.val.d = C.val.d * 2.0;
    }
}
```

**Solution 2: Specialization (Fast but Code Size)**
```c
// Generate two versions of the subroutine

void gosub_1000_int(int16_t A, int16_t B, int16_t* C, int16_t* D) {
    *C = A + B;
    *D = *C * 2;
}

void gosub_1000_double(double A, double B, double* C, double* D) {
    *C = A + B;
    *D = *C * 2.0;
}

// Call sites
int16_t A_v1 = 1, B_v1 = 2, C_v1, D_v1;
gosub_1000_int(A_v1, B_v1, &C_v1, &D_v1);

double A_v2 = 1.1, B_v2 = 2.2, C_v2, D_v2;
gosub_1000_double(A_v2, B_v2, &C_v2, &D_v2);

double A_v3 = 1.1, B_v3 = 2.2, C_v3, D_v3;
gosub_1000_double(A_v3, B_v3, &C_v3, &D_v3);
```

## Complexity Analysis

### Simple Cases (Low Complexity)

These are worth optimizing:

```basic
' Pattern 1: Temporary in loop
100 FOR I = 1 TO 100
110   X = I * 2         ' X is INTEGER (I is INTEGER)
120   PRINT X
130 NEXT I
```
**Benefit**: Fast INTEGER arithmetic
**Cost**: None (simple)

```basic
' Pattern 2: Sequential phases
100 X = 10              ' X is INTEGER
110 PRINT X
120 X = 10.5            ' X is DOUBLE (new binding)
130 PRINT X
```
**Benefit**: INTEGER for first phase, DOUBLE for second
**Cost**: Low (no control flow, no data dependency)

```basic
' Pattern 3: FOR loop re-uses variable
100 I = 22.1            ' I is DOUBLE
110 PRINT SIN(I)
120 FOR I = 0 TO 10     ' I is INTEGER (new binding)
130   J = J + I         ' Fast INTEGER math
140 NEXT I
```
**Benefit**: Fast INTEGER loop despite earlier DOUBLE use
**Cost**: Low (FOR overwrites completely)

### Complex Cases (High Complexity)

These are probably not worth it:

```basic
' Anti-pattern 1: Type oscillation
100 FOR I = 1 TO 100
110   X = I             ' X is INTEGER
120   PRINT X
130   X = X / 2.0       ' X is DOUBLE (depends on old X!)
140   PRINT X
150 NEXT I
```
**Problem**: X changes type every iteration with data dependency
**Cost**: Need conversion every iteration, or just use DOUBLE throughout

```basic
' Anti-pattern 2: Branching with type changes
100 X = 10              ' X is INTEGER
110 IF A > 0 THEN X = 10.5
120 IF B > 0 THEN X = X + 1    ' What type is X?
130 PRINT X
```
**Problem**: Multiple merge points, complex control flow
**Cost**: Need SSA analysis + phi nodes or tagged unions

```basic
' Anti-pattern 3: Recursive subroutines
1000 IF N = 0 THEN RETURN
1010 N = N / 2.0        ' N changes to DOUBLE
1020 GOSUB 1000         ' Recursive call
1030 RETURN
```
**Problem**: Recursive call with type change
**Cost**: Very complex (need stack of typed versions)

## Proposed Strategy: Selective Re-binding

### Tier 1: Always Allow Re-binding For

1. **FOR loop variables** (overwrite, no dependency)
```basic
I = 22.1
FOR I = 0 TO 10      ' ✅ Re-bind as INTEGER
  ...
NEXT I
```

2. **Simple sequential assignments** (no dependency, no control flow)
```basic
X = 10               ' INTEGER
PRINT X
X = 10.5             ' ✅ Re-bind as DOUBLE
PRINT X
```

3. **Dead assignments** (value never used)
```basic
X = 10.5             ' DOUBLE (but never used)
X = 5                ' ✅ Re-bind as INTEGER
PRINT X
```

### Tier 2: Analyze Cost/Benefit

If re-binding requires:
- ✅ **Simple promotion**: INTEGER → DOUBLE (worth it)
- ✅ **No subroutine specialization**: All call sites have same types (worth it)
- ✅ **No control flow merges**: Straight-line code (worth it)
- ❌ **Tagged unions**: Runtime type dispatch (maybe not worth it)
- ❌ **Multiple subroutine versions**: Code size explosion (probably not worth it)
- ❌ **Complex SSA**: Phi nodes, multiple versions (too complex)

### Tier 3: Fallback to Unified Type

When complexity is too high:
- Analyze all assignments to variable
- Pick the "widest" type (INTEGER < SINGLE < DOUBLE)
- Use that type throughout
- Error if even that doesn't work

## Implementation Algorithm

```python
class TypeRebindingAnalyzer:
    def __init__(self):
        # Map: (var_name, line_number) -> type
        self.variable_versions: Dict[Tuple[str, int], str] = {}

        # Map: var_name -> list of (line, type, depends_on_previous)
        self.assignments: Dict[str, List[Tuple[int, str, bool]]] = {}

    def analyze_variable_types(self, var_name: str) -> str:
        """
        Determine if variable can have multiple types or needs unified type.
        Returns: "REBINDABLE" or "UNIFIED(type)"
        """

        # Get all assignments
        assignments = self.assignments.get(var_name, [])

        if not assignments:
            raise CompilationError(f"Variable {var_name} has no assignments")

        # Check if all assignments are same type
        types = [t for _, t, _ in assignments]
        if all(t == types[0] for t in types):
            return f"UNIFIED({types[0]})"  # All same type, no rebinding needed

        # Check for re-binding patterns
        can_rebind = True

        for i, (line, typ, depends) in enumerate(assignments):
            # If assignment depends on previous value, check type change
            if depends and i > 0:
                prev_type = assignments[i-1][1]
                if typ != prev_type:
                    # Type changes with data dependency
                    can_rebind = False
                    break

        if can_rebind:
            # Check for control flow complexity
            if self.has_complex_control_flow(var_name):
                can_rebind = False

            # Check for subroutine polymorphism
            if self.requires_subroutine_specialization(var_name):
                # Estimate code size cost
                num_versions = len(set(types))
                if num_versions > 2:  # More than 2 versions = too much code
                    can_rebind = False

        if can_rebind:
            return "REBINDABLE"
        else:
            # Fall back to unified type (widest type wins)
            unified_type = self.get_widest_type(types)
            return f"UNIFIED({unified_type})"

    def get_widest_type(self, types: List[str]) -> str:
        """Get the widest type from a list (INTEGER < SINGLE < DOUBLE)"""
        if "DOUBLE" in types:
            return "DOUBLE"
        if "SINGLE" in types:
            return "SINGLE"
        if "INTEGER" in types:
            return "INTEGER"
        return "DOUBLE"  # Default

    def has_complex_control_flow(self, var_name: str) -> bool:
        """Check if variable has complex control flow (branches, merges)"""
        # Simplified check
        assignments = self.assignments[var_name]

        # If assignments are in different control flow regions, it's complex
        for line, _, _ in assignments:
            if self.is_in_conditional_block(line):
                return True

        return False

    def requires_subroutine_specialization(self, var_name: str) -> bool:
        """Check if variable requires multiple subroutine versions"""
        # Check if variable is used in subroutines
        # Check if subroutine is called with different types
        # This is simplified - real implementation would track call sites
        return False  # Placeholder
```

## Cost/Benefit Decision Tree

```
Variable X has multiple type assignments?
│
├─ NO → Use single inferred type
│
└─ YES → Can we re-bind?
    │
    ├─ All assignments independent (no data flow)?
    │  └─ YES → ✅ RE-BIND (cheap: just use different versions)
    │
    ├─ FOR loop overwrite?
    │  └─ YES → ✅ RE-BIND (cheap: FOR creates new scope)
    │
    ├─ Simple promotion needed (INT → DOUBLE)?
    │  └─ YES → ✅ RE-BIND with promotion (cheap: single cast)
    │
    ├─ Complex control flow (branches, merges)?
    │  └─ YES → ❌ UNIFY to widest type (too complex)
    │
    ├─ Subroutine with >2 different call types?
    │  └─ YES → ❌ UNIFY to widest type (code size explosion)
    │
    └─ Default → ❌ UNIFY to widest type (safety)
```

## Recommended Implementation

### Phase 1: Basic Re-binding (Easy Wins)

Support only these patterns:
1. FOR loop variable re-binding
2. Sequential independent assignments (no control flow)
3. Dead assignment elimination

**Example**:
```basic
' Pattern 1: FOR loop
I = 22.1
FOR I = 0 TO 10
  PRINT I
NEXT I

' Pattern 2: Sequential
X = 10
PRINT X
X = 10.5
PRINT X
```

**Cost**: Low complexity, big performance win for loops

### Phase 2: Promotion Analysis (Medium Complexity)

Allow re-binding with simple promotion:
```basic
X = 10               ' INTEGER
Y = X + 1            ' INTEGER
X = 10.5             ' DOUBLE (promote)
Z = Y + X            ' Promote Y to DOUBLE for operation
```

**Cost**: Medium complexity, handles common mixed-type cases

### Phase 3: Subroutine Analysis (Optional)

Detect if subroutine needs specialization:
- Count unique type combinations at call sites
- If ≤ 2 combinations and simple subroutine: specialize
- Otherwise: use unified type

**Cost**: High complexity, may not be worth it

## Comparison with Previous Strategy

| Aspect | Error on Ambiguity | **Type Re-binding** |
|--------|-------------------|---------------------|
| **Correctness** | ⭐⭐⭐⭐⭐ (never wrong) | ⭐⭐⭐⭐⭐ (never wrong) |
| **Performance** | ⭐⭐⭐⭐ (good) | ⭐⭐⭐⭐⭐ (better - more INTEGER) |
| **Ease of Use** | ⭐⭐⭐ (requires annotations) | ⭐⭐⭐⭐ (fewer annotations needed) |
| **Implementation** | ⭐⭐⭐⭐ (simple) | ⭐⭐ (complex) |
| **Code Size** | ⭐⭐⭐⭐⭐ (small) | ⭐⭐⭐ (possibly larger with specialization) |

## Recommendation

**Start with Phase 1** (basic re-binding for FOR loops and sequential assignments):
- Low implementation complexity
- Big performance win for common patterns
- No code size penalty
- Still error on truly ambiguous cases

**Example behavior**:
```basic
' This works (Phase 1)
I = 22.1
FOR I = 0 TO 10      ' ✅ I is INTEGER in loop (fast!)
  J = J + I
NEXT I

' This works (Phase 1)
X = 10               ' ✅ X is INTEGER
PRINT X
X = 10.5             ' ✅ X is DOUBLE (new binding)
PRINT X

' This errors (too complex for Phase 1)
100 A=1 : B=2
110 GOSUB 1000
120 A=1.1 : B=2.2
130 GOSUB 1000
1000 C=A+B           ' ❌ ERROR: Subroutine called with different types
                     '    Use DEFDBL or add C# suffix

' Fix: Add DEFDBL
10 DEFDBL A-Z        ' ✅ All variables are DOUBLE
100 A=1 : B=2
110 GOSUB 1000
120 A=1.1 : B=2.2
130 GOSUB 1000
1000 C=A+B           ' ✅ Works (all DOUBLE)
```

This gives us the best of both worlds:
- Fast INTEGER loops (your original example works!)
- Simple implementation (just track variable versions for easy cases)
- Clear errors for complex cases (subroutines, control flow)
- Escape hatch (--defdbl-default flag)

What do you think? Should we proceed with Phase 1 implementation?
