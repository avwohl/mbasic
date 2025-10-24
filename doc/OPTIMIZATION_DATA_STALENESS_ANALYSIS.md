# Optimization Data Staleness Analysis

## The Critical Question

**When we run optimizations iteratively, does each optimization's data need to be cleared/recalculated, or can it be incrementally updated?**

This is crucial because:
- ❌ **Always clearing**: Simple but wasteful (O(n) passes × O(m) analyses)
- ✅ **Incremental update**: Fast but complex (need invalidation logic)
- ⚠️ **Hybrid**: Clear some, update others (need careful categorization)

## Analysis of Each Optimization's Data

### Category 1: STRUCTURAL (Never Stale)

These analyze the program structure and don't depend on other optimizations:

#### 1. Symbol Table (`self.symbols`)
```python
self.symbols.variables: Dict[str, VariableInfo]
self.symbols.functions: Dict[str, FunctionInfo]
self.symbols.line_numbers: Set[int]
```
- **Depends on**: AST only
- **Invalidated by**: Nothing (structure doesn't change)
- **Action**: ✅ **Keep** - Never stale

#### 2. Subroutine Analysis (`self.subroutines`)
```python
self.subroutines: Dict[int, SubroutineInfo]
self.gosub_targets: Set[int]
```
- **Depends on**: GOSUB/RETURN statements
- **Invalidated by**: Nothing (control flow structure fixed)
- **Action**: ✅ **Keep** - Never stale

#### 3. Loop Analysis (`self.loops`)
```python
self.loops: Dict[int, LoopAnalysis]
```
- **Depends on**: FOR/WHILE statements
- **Invalidated by**: Nothing (loop structure fixed)
- **Action**: ✅ **Keep** - Mostly never stale
- ⚠️ **Exception**: `iteration_count` might benefit from constants

### Category 2: INCREMENTAL (Can Be Updated)

These accumulate results and can be updated incrementally:

#### 4. Constant Folding (`self.folded_expressions`)
```python
self.folded_expressions: List[Tuple[int, str, Any]]
```
- **Depends on**: Expression evaluation
- **Invalidated by**: New constant propagation
- **Action**: ✅ **Append only** - Add new folded expressions
- **Problem**: May re-fold same expression
- **Solution**: Track folded expressions, skip if already done

#### 5. Common Subexpression Elimination (`self.common_subexpressions`)
```python
self.common_subexpressions: Dict[str, CommonSubexpression]
self.available_expressions: Dict[str, Any]
```
- **Depends on**: Expression hashing
- **Invalidated by**: Forward substitution, dead code elimination
- **Action**: ⚠️ **MUST CLEAR** - Expression structure changes
- **Reason**: After substitution, expressions are different

**Example**:
```basic
100 X = A + B
110 Y = A + B
120 Z = X + 1
```
After forward substitution of X:
```basic
100 X = A + B
110 Y = A + B
120 Z = (A + B) + 1    ' NEW subexpression!
```
CSE data is now incomplete - must recompute.

#### 6. Reachability Analysis (`self.reachability`)
```python
self.reachability.unreachable_lines: Set[int]
self.reachability.dead_code_lines: Set[int]
```
- **Depends on**: Control flow, constant conditions
- **Invalidated by**: Boolean simplification, constant folding
- **Action**: ⚠️ **MUST RECALCULATE** - Reachability changes
- **Example**: `IF 0 THEN` makes THEN block unreachable

#### 7. Forward Substitution (`self.forward_substitutions`)
```python
self.forward_substitutions: List[ForwardSubstitution]
self.variable_assignments: Dict[str, Tuple[int, Any, str]]
self.variable_usage_count: Dict[str, int]
```
- **Depends on**: Variable assignments and usage counts
- **Invalidated by**: Dead code elimination, CSE
- **Action**: ⚠️ **MUST RECALCULATE** - Usage counts change
- **Example**: After dead code removal, usage count decreases

#### 8. Live Variable Analysis (`self.live_var_info`, `self.dead_writes`)
```python
self.live_var_info: Dict[int, LiveVariableInfo]
self.dead_writes: List[DeadWrite]
```
- **Depends on**: Variable usage, reachability
- **Invalidated by**: Forward substitution, dead code elimination
- **Action**: ⚠️ **MUST RECALCULATE** - Liveness changes
- **Example**: After substitution, variables may become dead

#### 9. Type Rebinding (`self.type_bindings`)
```python
self.type_bindings: List[TypeBinding]
self.variable_type_versions: Dict[str, List[TypeBinding]]
self.can_rebind_variable: Dict[str, bool]
```
- **Depends on**: Expression types, variable assignments
- **Invalidated by**: Constant folding, forward substitution
- **Action**: ⚠️ **MUST RECALCULATE** - Expression types change
- **Example**: `X = 10.0` after folding might become `X = 10` (INTEGER!)

### Category 3: REPORTING ONLY (Stale OK)

These are for warnings/reports only, don't affect other optimizations:

#### 10. String Constant Pooling (`self.string_pool`)
```python
self.string_pool: Dict[str, StringConstantPool]
```
- **Depends on**: String literals
- **Invalidated by**: Nothing (reporting only)
- **Action**: ✅ **Keep** - Recalculate once at end

#### 11. Function Purity (`self.builtin_function_calls`)
```python
self.builtin_function_calls: Dict[str, List[int]]
self.impure_function_calls: List[Tuple[int, str, str]]
```
- **Depends on**: Function call analysis
- **Invalidated by**: Dead code (calls removed)
- **Action**: ✅ **Recalculate once at end** - Reporting only

#### 12. Array Bounds (`self.array_bounds_violations`)
```python
self.array_bounds_violations: List[ArrayBoundsViolation]
```
- **Depends on**: Constant array indices
- **Invalidated by**: Constant folding (more violations detected)
- **Action**: ✅ **Recalculate once at end** - Reporting only

#### 13. String Concatenation in Loops (`self.string_concat_in_loops`)
```python
self.string_concat_in_loops: List[StringConcatInLoop]
```
- **Depends on**: Loop analysis
- **Invalidated by**: Dead code in loops
- **Action**: ✅ **Recalculate once at end** - Reporting only

## Staleness Classification

### 🟢 NEVER STALE (Keep Forever)
```python
✅ self.symbols
✅ self.subroutines
✅ self.gosub_targets
✅ self.loops  # Structure only
✅ self.array_base
✅ self.flags
```

### 🟡 INCREMENTAL (Can Update)
```python
✅ self.folded_expressions  # Append only, deduplicate
⚠️ self.evaluator.runtime_constants  # Update per iteration
```

### 🔴 MUST RECALCULATE (Clear Each Iteration)
```python
❌ self.common_subexpressions
❌ self.available_expressions
❌ self.reachability
❌ self.forward_substitutions
❌ self.variable_assignments
❌ self.variable_usage_count
❌ self.live_var_info
❌ self.dead_writes
❌ self.type_bindings
❌ self.variable_type_versions
❌ self.can_rebind_variable
❌ self.strength_reductions
❌ self.expression_reassociations
❌ self.copy_propagations
❌ self.active_copies
❌ self.branch_optimizations
❌ self.uninitialized_warnings
❌ self.initialized_variables
❌ self.induction_variables
❌ self.active_ivs
❌ self.range_info
❌ self.active_ranges
❌ self.available_expr_analysis
```

### 🔵 RECALCULATE ONCE AT END (Reporting)
```python
🔄 self.string_pool
🔄 self.builtin_function_calls
🔄 self.impure_function_calls
🔄 self.array_bounds_violations
🔄 self.alias_info
🔄 self.string_concat_in_loops
```

## Implications for Iteration

### Simple Approach: Clear Everything Red
```python
def _clear_iterative_state(self):
    """Clear all optimization state that can become stale"""
    # CSE
    self.common_subexpressions.clear()
    self.available_expressions.clear()
    self.cse_counter = 0

    # Reachability
    self.reachability = ReachabilityInfo()

    # Forward substitution
    self.forward_substitutions.clear()
    self.variable_assignments.clear()
    self.variable_usage_count.clear()
    self.variable_usage_lines.clear()

    # Live variables
    self.live_var_info.clear()
    self.dead_writes.clear()

    # Type rebinding
    self.type_bindings.clear()
    self.variable_type_versions.clear()
    self.can_rebind_variable.clear()

    # Other optimizations
    self.strength_reductions.clear()
    self.expression_reassociations.clear()
    self.copy_propagations.clear()
    self.active_copies.clear()
    self.branch_optimizations.clear()
    self.uninitialized_warnings.clear()
    self.initialized_variables.clear()
    self.induction_variables.clear()
    self.active_ivs.clear()
    self.range_info.clear()
    self.active_ranges.clear()
    self.available_expr_analysis.clear()

    # Reset constant evaluator to initial state
    self.evaluator.runtime_constants.clear()
```

### Iteration Loop
```python
def analyze(self, program: ProgramNode, max_iterations: int = 5) -> bool:
    # Run once: structural analysis
    self._collect_symbols(program)
    self._analyze_subroutines(program)
    self._analyze_statements(program)
    self._validate_line_references(program)

    # Iterative optimization
    for iteration in range(max_iterations):
        # Clear stale data
        self._clear_iterative_state()

        # Run analyses that can cascade
        self._analyze_loop_invariants()
        self._analyze_reachability(program)
        self._analyze_forward_substitution(program)
        self._analyze_live_variables(program)
        self._analyze_available_expressions(program)
        self._analyze_variable_type_bindings(program)

        # Check for convergence
        if not self._has_changes_this_iteration():
            break

    # Run once at end: reporting
    self._analyze_string_constants(program)
    self._analyze_function_purity(program)
    self._analyze_array_bounds(program)
    self._analyze_aliases(program)
    self._analyze_string_concat_in_loops(program)

    return len(self.errors) == 0
```

## The Challenge: Detecting Convergence

**Problem**: How do we know if changes were made without comparing full state?

### Option 1: Count Changes
```python
# Track changes in each optimization
class OptimizationMetrics:
    def __init__(self):
        self.cse_found = 0
        self.dead_writes = 0
        self.unreachable_lines = 0
        self.substitutions = 0
        self.type_rebindings = 0

# After each iteration, compare counts
```

### Option 2: Hash State (Expensive)
```python
def _get_optimization_hash(self) -> int:
    return hash((
        tuple(self.common_subexpressions.keys()),
        tuple(self.reachability.unreachable_lines),
        len(self.forward_substitutions),
        # ...
    ))
```

### Option 3: Change Flags
```python
# Each analysis sets a flag if it makes changes
self._made_changes = False

def _analyze_forward_substitution(self, program):
    before_count = len(self.forward_substitutions)
    # ... do analysis ...
    if len(self.forward_substitutions) > before_count:
        self._made_changes = True
```

## Recommended Approach

### 1. Clear Red Data Each Iteration
All optimization state that can be affected by other optimizations gets cleared.

### 2. Keep Green Data Forever
Structural information never changes.

### 3. Recalculate Blue Data Once At End
Reporting data can wait until all optimizations done.

### 4. Use Simple Change Detection
```python
def _count_optimizations(self) -> int:
    """Count total optimizations found"""
    return (
        len(self.common_subexpressions) +
        len(self.reachability.unreachable_lines) +
        len(self.forward_substitutions) +
        len(self.dead_writes) +
        len(self.type_bindings) +
        len(self.strength_reductions)
        # etc.
    )

# In iteration loop:
count_before = self._count_optimizations()
# ... run analyses ...
count_after = self._count_optimizations()
if count_after == count_before:
    break  # No new optimizations found
```

## Example: What Gets Cleared

**Program**:
```basic
100 X = 10
110 Y = X + 1
120 Z = X + 1
```

**Iteration 1**:
- CSE finds: `X + 1` appears twice
- Forward substitution: none (X used multiple times)
- Type rebinding: X is INTEGER

**Between Iteration 1 and 2**:
- ✅ Keep: `self.symbols` (variables X, Y, Z)
- ❌ Clear: `self.common_subexpressions` (will recalculate)
- ❌ Clear: `self.type_bindings` (will recalculate with CSE results)
- ❌ Clear: `self.variable_usage_count` (will recount)

**Iteration 2**:
- CSE finds: `X + 1` still appears twice (same result)
- Forward substitution: Maybe substitute CSE temp
- Type rebinding: X is INTEGER (same result)
- **No new optimizations**: CONVERGED!

## Performance Impact

### Cost of Clearing
- **Memory**: Negligible (just clearing lists/dicts)
- **Time**: O(n) where n = number of optimization results
- **Typical**: < 1ms per iteration

### Cost of Recalculating
- **Time**: O(AST size × analyses)
- **Typical**: 10-50ms per iteration (for medium programs)

### Total Iteration Cost
- **Single pass**: 50ms
- **3 iterations**: 150ms (3x slower)
- **5 iterations**: 250ms (5x slower)

**For a compiler, this is acceptable** - we care more about output quality than compile speed.

## Conclusion

**Yes, most data must be cleared between iterations.**

The only safe data to keep:
- 🟢 Structural information (symbols, subroutines, loops)
- 🟢 Incremental data (folded expressions with deduplication)

Everything else depends on other optimizations and must be recalculated to ensure correctness.

**Recommended implementation**:
1. Add `_clear_iterative_state()` method
2. Clear all red/orange data each iteration
3. Use simple count-based convergence detection
4. Iterate until counts stabilize (typically 2-3 iterations)

---

**Next**: Implement `_clear_iterative_state()` and iteration loop
