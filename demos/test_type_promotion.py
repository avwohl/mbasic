#!/usr/bin/env python3
"""
Test Type Promotion Analysis (Phase 2)

Demonstrates detection of INTEGER → DOUBLE promotions in mixed-type expressions.
"""

import sys
sys.path.insert(0, 'src')

from lexer import Lexer
from parser import Parser
from semantic_analyzer import SemanticAnalyzer


def test_promotion(source, title):
    """Test type promotion detection"""
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
        analyzer.analyze(program)

        # Extract promotion section from report
        report = analyzer.get_report()
        lines = report.split('\n')

        # Show type bindings
        in_bindings = False
        for line in lines:
            if 'Type Rebinding Analysis' in line:
                in_bindings = True
            if in_bindings:
                print(line)
                if 'Type Promotion Analysis' in line:
                    break

        # Show type promotions
        in_promotions = False
        for line in lines:
            if 'Type Promotion Analysis' in line:
                in_promotions = True
            if in_promotions:
                print(line)
                if line.startswith('Warnings') or line.startswith('Errors') or (line.startswith('====') and in_promotions and 'Type Promotion' not in line):
                    break

        if not analyzer.type_promotions:
            print("Type Promotion Analysis (Phase 2):")
            print("  No promotions detected")

    except Exception as e:
        print(f'Error: {e}')
        import traceback
        traceback.print_exc()


# =================================================================
# Example 1: Simple promotion (INTEGER + DOUBLE literal)
# =================================================================
example1 = """100 X = 10
110 Y = X + 0.5
"""

test_promotion(example1, "Example 1: Simple INTEGER → DOUBLE Promotion")


# =================================================================
# Example 2: No promotion needed (all INTEGER)
# =================================================================
example2 = """100 X = 10
110 Y = X + 5
"""

test_promotion(example2, "Example 2: No Promotion (All INTEGER)")


# =================================================================
# Example 3: Multiple promotions
# =================================================================
example3 = """100 X = 10
110 Y = X + 1
120 Z = Y + 0.5
"""

test_promotion(example3, "Example 3: Multiple Promotions")


# =================================================================
# Example 4: Loop with promotion
# =================================================================
example4 = """100 FOR I = 1 TO 10
110   X = I * 2
120   Y = X + 0.5
130 NEXT I
"""

test_promotion(example4, "Example 4: Promotion in Loop")


# =================================================================
# Example 5: Explicit type suffix
# =================================================================
example5 = """100 X% = 10
110 Y = X% + 0.5
"""

test_promotion(example5, "Example 5: Explicit INTEGER Suffix with Promotion")


# =================================================================
# Example 6: Mixed operators
# =================================================================
example6 = """100 A = 10
110 B = 20
120 C = A + B
130 D = C * 1.5
"""

test_promotion(example6, "Example 6: INTEGER Arithmetic then Promotion")


# =================================================================
# Example 7: No promotion (DOUBLE from start)
# =================================================================
example7 = """100 X = 10.0
110 Y = X + 0.5
"""

test_promotion(example7, "Example 7: No Promotion (Already DOUBLE)")


# =================================================================
# Example 8: Complex expression with promotions
# =================================================================
example8 = """100 A% = 10
110 B% = 20
120 C = A% + B%
130 D = (C * 2) + 3.14
"""

test_promotion(example8, "Example 8: Complex Expression with Promotion")


print(f"\n{'='*70}")
print("TYPE PROMOTION ANALYSIS TESTS COMPLETE")
print(f"{'='*70}\n")
