# Semantic Analyzer Tests

This directory contains tests for the semantic analyzer's advanced optimization features.

## Test Categories

### Constant Folding
- **test_constant_folding.py** - Basic constant folding tests
- **test_constant_folding_comprehensive.py** - Comprehensive constant folding with runtime constants

### Common Subexpression Elimination (CSE)
- **test_cse.py** - Basic CSE detection
- **test_cse_functions.py** - CSE with function calls
- **test_cse_functions2.py** - Advanced function CSE tests
- **test_cse_if.py** - CSE across IF statements
- **test_cse_if_comprehensive.py** - Comprehensive IF/CSE tests

### GOSUB Subroutine Analysis
- **test_gosub_analysis.py** - Basic subroutine analysis
- **test_gosub_comprehensive.py** - Comprehensive GOSUB with constants
- **test_gosub_comprehensive2.py** - GOSUB with non-constant values (4 tests)

### Loop Analysis
- **test_loop_analysis.py** - FOR loop analysis with iteration counts
- **test_while_loops.py** - WHILE loop detection and analysis
- **test_if_goto_loops.py** - IF-GOTO backward jump loop detection
- **test_loop_invariants.py** - Loop-invariant expression detection (4 tests)

### Array Flattening
- **test_array_flattening.py** - Multi-dimensional array flattening (4 tests)
- **test_array_flattening_benefits.py** - Demonstration of optimization benefits

### Dead Code Detection
- **test_dead_code.py** - Reachability analysis and dead code detection (8 tests)

### Comprehensive Tests
- **test_optimization_report.py** - Full optimization report generation
- **test_comprehensive_analysis.py** - All features together

## Running Tests

From the project root directory:

```bash
# Run individual test
python3 tests/semantic/test_loop_invariants.py

# Run all tests
for test in tests/semantic/test_*.py; do
    echo "Running $test..."
    python3 "$test" || echo "FAILED: $test"
done
```

## Features Tested

1. **Constant Folding** - Compile-time evaluation of constant expressions
2. **Runtime Constants** - Tracking variable values through program flow
3. **CSE Detection** - Finding repeated subexpressions
4. **Smart CSE Invalidation** - Invalidating CSE across GOSUB based on actual modifications
5. **Loop Analysis**:
   - FOR loop iteration counts
   - WHILE loop structure
   - IF-GOTO backward jump loops
6. **Loop-Invariant Code Motion** - Identifying expressions that can be hoisted
7. **Loop Unrolling Candidates** - Small loops with constant bounds
8. **Subroutine Side-Effect Analysis** - Tracking variable modifications through GOSUB calls
9. **Transitive Modifications** - Tracking modifications through nested GOSUB calls
10. **Array Flattening** - Multi-dimensional arrays transformed to 1D:
    - Automatic stride calculation
    - OPTION BASE 0/1 support
    - Index calculations become CSE candidates
    - Enables better code generation
11. **Dead Code Detection** - Reachability analysis and elimination:
    - Control flow graph analysis
    - Detects code after GOTO/END/STOP/RETURN
    - Identifies orphaned code
    - Finds uncalled subroutines
    - Generates warnings for unreachable code

## Expected Results

All tests should pass with `✓ All tests passed!` or `✓ Analysis completed successfully!`
