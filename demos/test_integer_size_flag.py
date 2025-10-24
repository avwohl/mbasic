#!/usr/bin/env python3
"""
Test Integer Size Inference Flag

Demonstrates that the enable_integer_size_inference flag correctly controls
whether integer size analysis is performed.
"""

import sys
sys.path.insert(0, 'src')

from lexer import Lexer
from parser import Parser
from semantic_analyzer import SemanticAnalyzer


def test_flag(source, enable_flag, title):
    """Test integer size inference flag"""
    print(f"\n{'='*70}")
    print(f"{title}")
    print(f"enable_integer_size_inference = {enable_flag}")
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
        analyzer.analyze(program, enable_integer_size_inference=enable_flag)

        # Check if integer size analysis was performed
        report = analyzer.get_report()
        lines = report.split('\n')

        # Look for integer size section
        found_section = False
        in_section = False
        for line in lines:
            if 'Integer Size Inference' in line:
                found_section = True
                in_section = True
            if in_section:
                print(line)
                if line.startswith('Warnings') or line.startswith('Errors') or (line.startswith('====') and 'Integer' not in line):
                    break

        if not found_section:
            print("Integer Size Inference (8/16/32-bit optimization):")
            print("  Analysis disabled or no optimizable sizes detected")
            print(f"  Ranges found: {len(analyzer.integer_ranges)}")

        # Verify flag behavior
        print(f"\nVerification:")
        print(f"  Flag setting: {enable_flag}")
        print(f"  Ranges detected: {len(analyzer.integer_ranges)}")
        if enable_flag:
            print(f"  Expected: Should detect integer sizes")
            if len(analyzer.integer_ranges) > 0:
                print(f"  ✓ PASS: Detected {len(analyzer.integer_ranges)} sizes")
            else:
                print(f"  ✗ FAIL: Expected to find sizes but found none")
        else:
            print(f"  Expected: Should NOT detect integer sizes")
            if len(analyzer.integer_ranges) == 0:
                print(f"  ✓ PASS: No sizes detected (as expected)")
            else:
                print(f"  ✗ FAIL: Found {len(analyzer.integer_ranges)} sizes (should be 0)")

    except Exception as e:
        print(f'Error: {e}')
        import traceback
        traceback.print_exc()


# =================================================================
# Test program with obvious integer size optimization opportunities
# =================================================================
test_program = """100 FOR I = 1 TO 10
110   PRINT I
120 NEXT I
130 A$ = "HELLO"
140 FOR J = 1 TO LEN(A$)
150   C = ASC(MID$(A$, J, 1))
160   PRINT CHR$(C)
170 NEXT J
"""

# Test 1: Flag enabled (default) - should detect integer sizes
test_flag(test_program, True, "Test 1: Flag ENABLED (Default)")

# Test 2: Flag disabled - should NOT detect integer sizes
test_flag(test_program, False, "Test 2: Flag DISABLED")


print(f"\n{'='*70}")
print("INTEGER SIZE FLAG TESTS COMPLETE")
print(f"{'='*70}")
print("\nSummary:")
print("  enable_integer_size_inference=True  → Analyze sizes (10-20x faster!)")
print("  enable_integer_size_inference=False → Use 32-bit for all (smaller code)")
print("\nTrade-off:")
print("  Enabled:  Fast execution, larger code (all size variants needed)")
print("  Disabled: Slower execution, smaller code (one 32-bit version)")
print(f"{'='*70}\n")
