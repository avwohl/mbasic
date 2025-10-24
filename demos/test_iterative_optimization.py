#!/usr/bin/env python3
"""
Test and demonstrate iterative optimization with cascading effects.

Shows how optimizations enable each other through multiple iterations:
- Constant folding → Boolean simplification → Dead code elimination
- Forward substitution → CSE → More substitution opportunities
- Type rebinding → Strength reduction → Better loop optimization
"""

import sys
sys.path.insert(0, 'src')

from lexer import Lexer
from parser import Parser
from semantic_analyzer import SemanticAnalyzer


def test_program(source, title, max_iterations=5):
    """Test a program and show iteration results"""
    print(f"\n{'='*70}")
    print(f"{title}")
    print(f"{'='*70}")
    print("\nProgram:")
    print(source)
    print()

    try:
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        program = parser.parse()

        analyzer = SemanticAnalyzer()
        analyzer.analyze(program, max_iterations=max_iterations)

        # Show iteration statistics
        report = analyzer.get_report()
        lines = report.split('\n')

        # Extract and show iteration info
        for line in lines:
            if 'Optimization Iterations:' in line or 'Converged' in line or 'limit reached' in line:
                print(line)

        print()

        # Show key optimizations found
        if analyzer.reachability.unreachable_lines:
            print(f"Dead Code: {len(analyzer.reachability.unreachable_lines)} unreachable line(s)")
        if analyzer.forward_substitutions:
            print(f"Forward Substitution: {len(analyzer.forward_substitutions)} opportunity(s)")
        if analyzer.common_subexpressions:
            print(f"CSE: {len(analyzer.common_subexpressions)} common subexpression(s)")
        if analyzer.type_bindings:
            print(f"Type Rebinding: {len(analyzer.type_bindings)} binding(s)")
        if analyzer.strength_reductions:
            print(f"Strength Reduction: {len(analyzer.strength_reductions)} opportunity(s)")
        if analyzer.dead_writes:
            print(f"Dead Writes: {len(analyzer.dead_writes)} dead write(s)")

    except Exception as e:
        print(f'Error: {e}')
        import traceback
        traceback.print_exc()


# ============================================================================
# Example 1: Constant Folding → Boolean Simplification → Dead Code
# ============================================================================
example1 = """100 DEBUG = 0
110 N = 100
120 IF DEBUG THEN PRINT "Debug mode enabled"
130 IF DEBUG THEN GOTO 200
140 FOR I = 1 TO N
150   PRINT I
160 NEXT I
170 END
200 PRINT "Debug section"
"""

test_program(example1, "Example 1: Constant → Boolean → Dead Code Cascade")


# ============================================================================
# Example 2: Forward Substitution → CSE → More Substitution
# ============================================================================
example2 = """100 X = A + B
110 Y = A + B
120 Z = X + 1
130 W = Y + 1
"""

test_program(example2, "Example 2: Forward Substitution → CSE Cascade")


# ============================================================================
# Example 3: Type Rebinding → Strength Reduction
# ============================================================================
example3 = """100 FOR I = 1 TO 100
110   X = I * 8
120   Y = I * 16
130   Z = I * 2
140 NEXT I
"""

test_program(example3, "Example 3: Type Rebinding → Strength Reduction")


# ============================================================================
# Example 4: Complex Cascade (multiple iterations)
# ============================================================================
example4 = """100 OPTIMIZE = 1
110 VERBOSE = 0
120 N = 100
130 IF VERBOSE THEN PRINT "Starting"
140 FOR I = 1 TO N
150   IF OPTIMIZE THEN X = I * 2 ELSE X = I * I
160   IF VERBOSE THEN PRINT X
170 NEXT I
180 IF VERBOSE THEN PRINT "Done"
"""

test_program(example4, "Example 4: Complex Multi-Iteration Cascade")


# ============================================================================
# Example 5: Deep cascade (should converge in 2-3 iterations)
# ============================================================================
example5 = """100 N = 100
110 DEBUG = 0
120 FAST = 1
130 IF DEBUG THEN PRINT "Debug"
140 FOR I = 1 TO N
150   IF DEBUG THEN PRINT I
160   IF FAST THEN X = I * 4 ELSE X = I * I
170 NEXT I
180 IF DEBUG THEN GOTO 200
190 END
200 PRINT "Debug end"
"""

test_program(example5, "Example 5: Deep Cascading (Tests Convergence)")


# ============================================================================
# Example 6: Minimal changes (should converge in 1 iteration)
# ============================================================================
example6 = """100 FOR I = 1 TO 10
110   PRINT I
120 NEXT I
"""

test_program(example6, "Example 6: No Cascading (Converges Immediately)")


# ============================================================================
# Example 7: Live variable → Dead write cascade
# ============================================================================
example7 = """100 X = 10
110 Y = 20
120 X = 30
130 PRINT X
"""

test_program(example7, "Example 7: Dead Write Detection After Optimization")


# ============================================================================
# Summary
# ============================================================================
print(f"\n{'='*70}")
print("ITERATIVE OPTIMIZATION TEST COMPLETE")
print(f"{'='*70}")
print("\nKey Observations:")
print("1. Most programs converge in 2-3 iterations")
print("2. Simple programs converge in 1 iteration")
print("3. Complex cascades may need 3-5 iterations")
print("4. Fixed-point detection prevents wasted iterations")
print(f"{'='*70}\n")
