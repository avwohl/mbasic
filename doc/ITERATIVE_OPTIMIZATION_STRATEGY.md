# Iterative Optimization Strategy

## The Problem

Many optimizations enable other optimizations, creating cascading improvement opportunities:

**Example 1: Constant Folding → Dead Code Elimination**
```basic
100 DEBUG = 0
110 IF DEBUG THEN PRINT "Debug info"
```
- Pass 1: Constant propagation detects `DEBUG = 0`
- Pass 1: Boolean simplification sees `IF 0 THEN` → always false
- **Pass 2**: Dead code elimination can now remove line 110!

**Example 2: Forward Substitution → CSE**
```basic
100 X = A + B
110 Y = A + B
120 Z = X + 1
```
- Pass 1: Forward substitution inlines `X` into line 120: `Z = (A+B) + 1`
- Pass 1: CSE detects `A+B` appears twice (lines 110, 120)
- **Pass 2**: After CSE creates temp, more substitution opportunities

**Example 3: Type Rebinding → Strength Reduction**
```basic
100 FOR I = 1 TO 100
110   X = I * 8
120 NEXT I
```
- Pass 1: Type rebinding detects I is INTEGER
- **Pass 2**: Strength reduction can now use INTEGER shift: `X = I << 3`

## Current Single-Pass Design

The current implementation runs 15 passes in fixed order:

1. Collect symbols
2. Analyze subroutines
3. Validate statements
4. Loop-invariant expressions
5. Validate line references
6. Reachability analysis
7. Forward substitution
8. Live variable analysis
9. String constant pooling
10. Function purity
11. Array bounds checking
12. Alias analysis
13. Available expressions
14. String concatenation in loops
15. Type rebinding

**Problem**: Each pass runs exactly once, missing cascading opportunities.

## Optimization Dependencies

### Graph of Dependencies

```
Constant Folding ────┬──> Dead Code Elimination
                     │
Constant Propagation ┴──> Boolean Simplification ──> Dead Code Elimination
                                                  │
Type Rebinding ──────────────────────────────────┴──> Strength Reduction
                                                  │
Forward Substitution ────┬───────────────────────┴──> CSE
                         │
Copy Propagation ────────┴──> Forward Substitution

Live Variables ──────────────> Dead Code Elimination

Reachability ────────────────> Dead Code Elimination
```

### Specific Cascades

#### Cascade 1: Constant → Boolean → Dead Code
1. **Constant Folding**: `X = 5 + 3` → `X = 8`
2. **Constant Propagation**: `IF X > 10` → `IF 8 > 10`
3. **Boolean Simplification**: `IF 8 > 10` → `IF 0`
4. **Dead Code Elimination**: Remove unreachable THEN block

#### Cascade 2: Substitution → CSE → Substitution
1. **Forward Substitution**: Replace simple variables
2. **CSE**: Find common subexpressions (including substituted ones)
3. **Forward Substitution**: Substitute CSE temps

#### Cascade 3: Type → Arithmetic → Loop
1. **Type Rebinding**: Detect INTEGER loop variable
2. **Strength Reduction**: Use INTEGER shifts instead of multiply
3. **Loop Unrolling**: Smaller INTEGER operations make unrolling profitable

#### Cascade 4: Reachability → Live → Dead
1. **Reachability**: Mark unreachable code
2. **Live Variables**: Variables in unreachable code are dead
3. **Dead Code Elimination**: Remove dead assignments

## Proposed Solution: Iterative Fixed-Point

Run optimizations until no more changes occur (fixed point reached):

```python
def analyze(self, program: ProgramNode) -> bool:
    """
    Analyze with iterative optimization until fixed point.
    """
    # Always run first (structure analysis)
    self._collect_symbols(program)
    self._analyze_subroutines(program)
    self._analyze_statements(program)
    self._validate_line_references(program)

    # Iterative optimization loop
    MAX_ITERATIONS = 10  # Safety limit
    iteration = 0

    while iteration < MAX_ITERATIONS:
        iteration += 1
        changes_made = False

        # Track state before optimization round
        state_before = self._get_optimization_state()

        # Run optimizations that can cascade
        self._analyze_loop_invariants()
        self._analyze_reachability(program)
        self._analyze_forward_substitution(program)
        self._analyze_live_variables(program)
        self._analyze_available_expressions(program)
        self._analyze_variable_type_bindings(program)

        # Check if anything changed
        state_after = self._get_optimization_state()
        changes_made = (state_before != state_after)

        if not changes_made:
            break  # Fixed point reached

    # Run final analyses (reporting only, no cascades)
    self._analyze_string_constants(program)
    self._analyze_function_purity(program)
    self._analyze_array_bounds(program)
    self._analyze_aliases(program)
    self._analyze_string_concat_in_loops(program)

    return len(self.errors) == 0
```

## Optimization State Tracking

To detect when a fixed point is reached, track:

```python
def _get_optimization_state(self) -> tuple:
    """
    Capture current optimization state for comparison.
    Returns a hashable tuple of optimization results.
    """
    return (
        # CSE state
        len(self.common_subexpressions),
        tuple(sorted(self.common_subexpressions.keys())),

        # Forward substitution state
        len(self.forward_substitutions),

        # Copy propagation state
        len(self.copy_propagations),

        # Strength reduction state
        len(self.strength_reductions),

        # Dead code state
        len(self.reachability.unreachable_lines),
        len(self.dead_writes),

        # Type rebinding state
        len(self.type_bindings),
        tuple(sorted(self.can_rebind_variable.items())),

        # Available expressions state
        len(self.available_expr_analysis),

        # Constant folding state
        len(self.folded_expressions),
    )
```

## Safety Mechanisms

### 1. Iteration Limit
```python
MAX_ITERATIONS = 10  # Prevent infinite loops
```

**Rationale**: Most programs should converge in 2-3 iterations. 10 is generous safety margin.

### 2. Progress Detection
```python
if not changes_made and iteration > 1:
    # No changes in this iteration
    break
```

**Rationale**: Stop as soon as fixed point reached.

### 3. Iteration Warning
```python
if iteration >= MAX_ITERATIONS:
    self.warnings.append(
        f"Optimization iteration limit reached ({MAX_ITERATIONS}). "
        f"Some optimizations may have been missed."
    )
```

**Rationale**: Alert user if limit hit (shouldn't happen normally).

## Categorizing Optimizations

### Category A: Structural (Run Once First)
These establish program structure, don't cascade:
- ✅ Collect symbols
- ✅ Analyze subroutines
- ✅ Validate statements
- ✅ Validate line references

### Category B: Iterative (Run Until Fixed Point)
These can cascade and enable each other:
- 🔄 Constant folding & propagation
- 🔄 Boolean simplification
- 🔄 Loop-invariant detection
- 🔄 Reachability analysis
- 🔄 Forward substitution
- 🔄 Copy propagation
- 🔄 Live variable analysis
- 🔄 CSE (Common Subexpression Elimination)
- 🔄 Available expressions
- 🔄 Type rebinding
- 🔄 Strength reduction
- 🔄 Dead code elimination

### Category C: Final Report (Run Once Last)
These are reporting/warnings, don't cascade:
- ✅ String constant pooling
- ✅ Function purity analysis
- ✅ Array bounds checking
- ✅ Alias analysis
- ✅ String concatenation in loops
- ✅ Uninitialized variables

## Expected Iteration Counts

### Typical Programs: 2-3 iterations

**Iteration 1**: Initial optimizations
- Constant folding
- Type inference
- Basic CSE

**Iteration 2**: Cascading effects
- Dead code from constants
- More CSE after substitution
- Type-based optimizations

**Iteration 3**: Cleanup (usually no changes)
- Fixed point verification

### Complex Programs: 4-5 iterations

Programs with nested loops, many constants, complex control flow.

**Example**:
```basic
100 N = 100
110 DEBUG = 0
120 FOR I = 1 TO N
130   IF DEBUG THEN PRINT I
140   X = I * I
150 NEXT I
```

**Iteration 1**:
- Constant: N = 100, DEBUG = 0
- Type: I is INTEGER
- Loop bounds: 1 TO 100 (can unroll? no)

**Iteration 2**:
- Dead code: Line 130 (DEBUG = 0)
- Strength reduction: I * I (INTEGER multiply)
- Reachability updated

**Iteration 3**:
- No changes (fixed point)

## Performance Impact

### Benefits
- ✅ More optimization opportunities discovered
- ✅ Better code quality
- ✅ Finds deep optimization chains

### Costs
- ⚠️ Longer compilation time (2-5x)
- ⚠️ More memory (storing state snapshots)

### Mitigation
```python
# Quick mode: single pass (fast, less optimal)
analyzer.analyze(program, iterative=False)

# Standard mode: iterative (slower, more optimal)
analyzer.analyze(program, iterative=True, max_iterations=10)

# Aggressive mode: more iterations
analyzer.analyze(program, iterative=True, max_iterations=20)
```

## Implementation Plan

### Phase 1: Add Iteration Infrastructure
```python
def _get_optimization_state(self) -> tuple:
    """Capture state for comparison"""

def analyze(self, program: ProgramNode, iterative: bool = True,
            max_iterations: int = 10) -> bool:
    """Main analysis with optional iteration"""
```

### Phase 2: Categorize Existing Analyses
- Mark structural analyses (run once first)
- Mark iterative analyses (run in loop)
- Mark final analyses (run once last)

### Phase 3: Add Iteration Loop
```python
while iteration < max_iterations:
    state_before = self._get_optimization_state()

    # Run iterative analyses
    ...

    state_after = self._get_optimization_state()
    if state_before == state_after:
        break
```

### Phase 4: Add Reporting
```python
# Add to report
lines.append(f"\nOptimization Iterations: {iteration}")
if iteration >= max_iterations:
    lines.append(f"  ⚠️  Iteration limit reached")
else:
    lines.append(f"  ✓ Converged to fixed point")
```

## Example: Cascading Optimization

**Original Program**:
```basic
100 N = 100
110 DEBUG = 0
120 FOR I = 1 TO N
130   IF DEBUG THEN PRINT "I="; I
140   X = I * 2
150 NEXT I
160 PRINT X
```

**Iteration 1 Results**:
- Constant propagation: N=100, DEBUG=0
- Forward substitution: Line 120 becomes `FOR I = 1 TO 100`
- Type rebinding: I is INTEGER
- CSE: None yet

**Iteration 2 Results** (using results from Iteration 1):
- Boolean simplification: `IF 0 THEN` → always false
- Dead code: Line 130 unreachable
- Forward substitution: More opportunities after dead code removal
- Strength reduction: I * 2 → I << 1 (because I is INTEGER)

**Iteration 3 Results**:
- No changes detected
- Fixed point reached
- Stop iteration

**Final Optimized**:
```basic
100 N = 100
110 DEBUG = 0
120 FOR I = 1 TO 100
140   X = I << 1        ' Strength reduction applied
150 NEXT I
160 PRINT X
' Line 130 removed (dead code)
```

## Comparison: Single Pass vs Iterative

| Metric | Single Pass | Iterative (2-3 iter) | Iterative (5+ iter) |
|--------|-------------|----------------------|---------------------|
| Compile Time | 1x | 2-3x | 5-10x |
| Optimization Quality | Good | Excellent | Excellent+ |
| Cascading Optimizations | No | Yes | Yes |
| Memory Usage | Low | Medium | Medium |
| Code Size Reduction | ~10% | ~15-20% | ~20-25% |
| Runtime Speed | Fast | Faster | Faster |

## Recommendation

**Implement iterative optimization with:**
- Default: `max_iterations=5` (good balance)
- Quick mode: `iterative=False` (for fast development)
- Aggressive mode: `max_iterations=10` (for production)

**Expected results:**
- 80% of programs: converge in 2-3 iterations
- 15% of programs: converge in 4-5 iterations
- 5% of programs: hit limit (need investigation)

**Benefits far outweigh costs** for a compiler where compilation time is not critical compared to runtime performance.

---

**Next Steps:**
1. Implement `_get_optimization_state()` method
2. Add iteration loop to `analyze()`
3. Categorize all 27 optimizations
4. Add iteration reporting
5. Test on corpus to measure convergence
6. Benchmark compilation time impact

**Related Documents:**
- `doc/OPTIMIZATION_STATUS.md` - All 27 optimizations
- `doc/TYPE_REBINDING_STRATEGY.md` - Type cascades
