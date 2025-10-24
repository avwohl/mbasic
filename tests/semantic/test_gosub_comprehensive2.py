#!/usr/bin/env python3
"""Comprehensive GOSUB analysis test with non-constant values"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from lexer import tokenize
from parser import Parser
from semantic_analyzer import SemanticAnalyzer

test_program = """
10 REM === Test CSE with GOSUB (non-constant values) ===
20 INPUT A, B
30 X = A + B

40 REM Call subroutine that doesn't modify A or B
50 GOSUB 1000
60 Y = A + B
70 PRINT "Y should be CSE with X (line 30, 60)"

80 REM Call subroutine that modifies B
90 GOSUB 2000
100 Z = A + B
110 PRINT "Z should NOT be CSE (B modified)"

120 REM Test nested GOSUB
130 INPUT C
140 D = C * 2
150 GOSUB 3000
160 E = C * 2
170 PRINT "E should NOT be CSE (C modified transitively)"

200 END

1000 REM Subroutine 1 - reads but doesn't modify A or B
1010 PRINT A + B
1020 RETURN

2000 REM Subroutine 2 - modifies B
2010 B = B + 1
2020 RETURN

3000 REM Subroutine 3 - calls subroutine 4 which modifies C
3010 GOSUB 4000
3020 RETURN

4000 REM Subroutine 4 - modifies C
4010 C = C * 2
4020 RETURN
"""

print("=" * 70)
print("COMPREHENSIVE GOSUB CSE TEST")
print("=" * 70)

print("\nParsing test program...")
tokens = tokenize(test_program)
parser = Parser(tokens)
program = parser.parse()

print("Performing semantic analysis...")
analyzer = SemanticAnalyzer()
success = analyzer.analyze(program)

# Show analysis results
print("\n" + "=" * 70)
print("RESULTS")
print("=" * 70)

print(f"\nConstant Folding: {len(analyzer.folded_expressions)}")
for line, expr, value in analyzer.folded_expressions:
    print(f"  Line {line}: {expr} → {value}")

print(f"\nCommon Subexpressions: {len(analyzer.common_subexpressions)}")
for cse in sorted(analyzer.common_subexpressions.values(), key=lambda x: x.first_line):
    print(f"  {cse.expression_desc}")
    print(f"    Lines: {cse.first_line}, {', '.join(map(str, cse.occurrences))}")

print(f"\nSubroutines Analyzed: {len(analyzer.subroutines)}")
for line_num, sub_info in sorted(analyzer.subroutines.items()):
    print(f"  Subroutine at line {line_num}:")
    if sub_info.variables_modified:
        print(f"    Modifies: {', '.join(sorted(sub_info.variables_modified))}")
    else:
        print(f"    Modifies: (none)")
    if sub_info.calls_other_subs:
        print(f"    Calls: {', '.join(map(str, sorted(sub_info.calls_other_subs)))}")

print("\n" + "=" * 70)
print("VALIDATION")
print("=" * 70)

# Validate expectations
errors = []

# Test 1: Y = A + B should be CSE with X = A + B
cse_a_b = None
for cse in analyzer.common_subexpressions.values():
    if '(a + b)' in cse.expression_desc.lower():
        cse_a_b = cse
        break

if cse_a_b:
    all_lines = [cse_a_b.first_line] + cse_a_b.occurrences
    if 30 in all_lines and 60 in all_lines:
        print("✓ Test 1 PASS: A + B is CSE at lines 30 and 60 (sub 1000 doesn't modify)")
    else:
        print(f"✗ Test 1 FAIL: A + B found at lines {all_lines}, expected 30 and 60")
        errors.append("Test 1")
else:
    print("✗ Test 1 FAIL: A + B not detected as CSE")
    errors.append("Test 1")

# Test 2: Z = A + B should NOT be CSE (B modified)
if cse_a_b:
    all_lines = [cse_a_b.first_line] + cse_a_b.occurrences
    if 100 not in all_lines:
        print("✓ Test 2 PASS: A + B is NOT CSE at line 100 (B modified by sub 2000)")
    else:
        print("✗ Test 2 FAIL: A + B should NOT be CSE at line 100")
        errors.append("Test 2")
else:
    # If no CSE found at all, that's also acceptable for test 2
    print("✓ Test 2 PASS: A + B is NOT CSE at line 100 (B modified by sub 2000)")

# Test 3: E = C * 2 should NOT be CSE with D = C * 2
cse_c = None
for cse in analyzer.common_subexpressions.values():
    if '(c * 2' in cse.expression_desc.lower():
        cse_c = cse
        break

if cse_c:
    all_lines = [cse_c.first_line] + cse_c.occurrences
    if 160 not in all_lines:
        print("✓ Test 3 PASS: C * 2 is NOT CSE at line 160 (C modified transitively)")
    else:
        print("✗ Test 3 FAIL: C * 2 should NOT be CSE at line 160")
        errors.append("Test 3")
else:
    print("✓ Test 3 PASS: C * 2 is NOT CSE at line 160 (C modified transitively)")

# Test 4: Transitive modification
sub_3000 = analyzer.subroutines.get(3000)
if sub_3000:
    all_modified = analyzer._get_all_modified_variables(3000)
    if 'C' in all_modified:
        print("✓ Test 4 PASS: Subroutine 3000 transitively modifies C (through 4000)")
    else:
        print(f"✗ Test 4 FAIL: Subroutine 3000 should transitively modify C. Modified: {all_modified}")
        errors.append("Test 4")
else:
    print("✗ Test 4 FAIL: Subroutine 3000 not analyzed")
    errors.append("Test 4")

if errors:
    print(f"\n✗ {len(errors)} test(s) failed: {', '.join(errors)}")
    sys.exit(1)
else:
    print("\n✓ All tests passed!")
