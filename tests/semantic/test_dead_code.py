#!/usr/bin/env python3
"""Test dead code detection and reachability analysis"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from lexer import tokenize
from parser import Parser
from semantic_analyzer import SemanticAnalyzer

test_program = """
10 REM === Reachable code ===
20 PRINT "Starting program"
30 X = 10

40 REM === Dead code after GOTO ===
50 GOTO 100
60 PRINT "This is unreachable!"
70 X = X + 1

100 REM === Reachable via GOTO ===
110 PRINT "Reached via GOTO"
120 IF X > 5 THEN 200

130 REM === Dead code after END ===
140 END
150 PRINT "After END - unreachable!"
160 Y = 20

200 REM === Reachable via IF ===
210 PRINT "Conditional branch"
220 GOSUB 1000
230 GOTO 300

240 REM === Dead code - no path here ===
250 PRINT "Orphaned code"
260 Z = 30

300 REM === Reachable ===
310 PRINT "Continuing"
320 END

1000 REM === Subroutine (reachable via GOSUB) ===
1010 PRINT "In subroutine"
1020 RETURN

1100 REM === Dead subroutine - never called ===
1110 PRINT "Never called"
1120 RETURN
"""

print("=" * 70)
print("DEAD CODE DETECTION TEST")
print("=" * 70)

print("\nParsing test program...")
tokens = tokenize(test_program)
parser = Parser(tokens)
program = parser.parse()

print("Performing semantic analysis with reachability check...")
analyzer = SemanticAnalyzer()
success = analyzer.analyze(program)

print("\n" + "=" * 70)
print("REACHABILITY ANALYSIS")
print("=" * 70)

print(f"\nReachable lines: {len(analyzer.reachability.reachable_lines)}")
for line_num in sorted(analyzer.reachability.reachable_lines):
    print(f"  Line {line_num}")

print(f"\nUnreachable lines (dead code): {len(analyzer.reachability.unreachable_lines)}")
for line_num in sorted(analyzer.reachability.unreachable_lines):
    print(f"  Line {line_num} - DEAD CODE")

print(f"\nTerminating lines: {len(analyzer.reachability.terminating_lines)}")
for line_num in sorted(analyzer.reachability.terminating_lines):
    print(f"  Line {line_num} (END/STOP)")

print("\n" + "=" * 70)
print("WARNINGS")
print("=" * 70)

dead_code_warnings = [w for w in analyzer.warnings if 'Unreachable' in w or 'dead code' in w.lower()]
if dead_code_warnings:
    for warning in dead_code_warnings:
        print(f"  {warning}")
else:
    print("  No dead code warnings")

print("\n" + "=" * 70)
print("VALIDATION")
print("=" * 70)

errors = []

# Test 1: Lines after GOTO should be unreachable
if 60 in analyzer.reachability.unreachable_lines and 70 in analyzer.reachability.unreachable_lines:
    print("✓ Test 1 PASS: Code after GOTO is unreachable")
else:
    print(f"✗ Test 1 FAIL: Lines 60, 70 should be unreachable")
    errors.append("Test 1")

# Test 2: Line 100 should be reachable via GOTO
if 100 in analyzer.reachability.reachable_lines and 110 in analyzer.reachability.reachable_lines:
    print("✓ Test 2 PASS: GOTO target is reachable")
else:
    print("✗ Test 2 FAIL: Lines 100, 110 should be reachable via GOTO")
    errors.append("Test 2")

# Test 3: Code after END should be unreachable
if 150 in analyzer.reachability.unreachable_lines and 160 in analyzer.reachability.unreachable_lines:
    print("✓ Test 3 PASS: Code after END is unreachable")
else:
    print("✗ Test 3 FAIL: Lines 150, 160 should be unreachable after END")
    errors.append("Test 3")

# Test 4: Conditional branch target should be reachable
if 200 in analyzer.reachability.reachable_lines and 210 in analyzer.reachability.reachable_lines:
    print("✓ Test 4 PASS: IF-THEN target is reachable")
else:
    print("✗ Test 4 FAIL: Lines 200, 210 should be reachable via IF")
    errors.append("Test 4")

# Test 5: Orphaned code should be unreachable (skip REM-only line 240)
if 250 in analyzer.reachability.unreachable_lines and 260 in analyzer.reachability.unreachable_lines:
    print("✓ Test 5 PASS: Orphaned code detected as unreachable")
else:
    print("✗ Test 5 FAIL: Lines 250, 260 should be unreachable")
    errors.append("Test 5")

# Test 6: GOSUB target should be reachable
if 1000 in analyzer.reachability.reachable_lines and 1010 in analyzer.reachability.reachable_lines:
    print("✓ Test 6 PASS: GOSUB target is reachable")
else:
    print("✗ Test 6 FAIL: Subroutine at 1000 should be reachable")
    errors.append("Test 6")

# Test 7: Uncalled subroutine should be unreachable (skip REM-only line 1100)
if 1110 in analyzer.reachability.unreachable_lines and 1120 in analyzer.reachability.unreachable_lines:
    print("✓ Test 7 PASS: Uncalled subroutine detected as dead code")
else:
    print("✗ Test 7 FAIL: Lines 1110, 1120 should be unreachable")
    errors.append("Test 7")

# Test 8: Dead code warnings generated (excluding REM-only lines 240, 1100)
expected_dead_lines = {60, 70, 150, 160, 250, 260, 1110, 1120}
detected_dead = analyzer.reachability.unreachable_lines
if expected_dead_lines.issubset(detected_dead):
    print(f"✓ Test 8 PASS: All expected dead code detected ({len(detected_dead)} lines)")
else:
    missing = expected_dead_lines - detected_dead
    print(f"✗ Test 8 FAIL: Missing dead code detection: {missing}")
    errors.append("Test 8")

if errors:
    print(f"\n✗ {len(errors)} test(s) failed: {', '.join(errors)}")
    sys.exit(1)
else:
    print("\n✓ All tests passed!")
    print("\nDead code detection is working! The analyzer correctly identifies:")
    print("  • Code after GOTO/END/STOP")
    print("  • Orphaned code with no incoming control flow")
    print("  • Uncalled subroutines")
    print("  • Reachable code via GOTO/GOSUB/IF-THEN")
