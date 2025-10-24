#!/usr/bin/env python3
"""Test constant folding and CSE with GOSUB"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from lexer import tokenize
from parser import Parser
from semantic_analyzer import SemanticAnalyzer

# Test various scenarios with GOSUB
test_program = """
10 REM === Test 1: Simple constant through GOSUB ===
20 N% = 10
30 GOSUB 1000
40 M% = N% * 2
50 PRINT M%

100 REM === Test 2: CSE before and after GOSUB ===
110 X = A + B
120 GOSUB 2000
130 Y = A + B

200 REM === Test 3: Subroutine modifies variable ===
210 C = 5
220 GOSUB 3000
230 D = C * 2

300 REM === Test 4: CSE within subroutine ===
310 GOSUB 4000
320 END

1000 REM Subroutine 1 - doesn't modify N%
1010 PRINT "In sub 1"
1020 RETURN

2000 REM Subroutine 2 - doesn't modify A or B
2010 PRINT "In sub 2"
2020 RETURN

3000 REM Subroutine 3 - modifies C
3010 C = C + 1
3020 RETURN

4000 REM Subroutine 4 - has CSE internally
4010 E = F * G
4020 H = F * G
4030 I = F * G
4040 RETURN
"""

print("=" * 70)
print("GOSUB ANALYSIS TEST")
print("=" * 70)

print("\nParsing test program...")
tokens = tokenize(test_program)
parser = Parser(tokens)
program = parser.parse()

print("Performing semantic analysis...")
analyzer = SemanticAnalyzer()
success = analyzer.analyze(program)

print(analyzer.get_report())

if success:
    print("\n" + "=" * 70)
    print("Analysis Summary:")
    print("=" * 70)
    print(f"Constant folding optimizations: {len(analyzer.folded_expressions)}")
    print(f"Common subexpressions found: {len(analyzer.common_subexpressions)}")

    if analyzer.folded_expressions:
        print("\nConstant Folding:")
        for line, expr, value in analyzer.folded_expressions:
            print(f"  Line {line}: {expr} → {value}")

    if analyzer.common_subexpressions:
        print("\nCSEs:")
        for cse in sorted(analyzer.common_subexpressions.values(), key=lambda x: x.first_line):
            print(f"  {cse.expression_desc}: lines {cse.first_line}, {', '.join(map(str, cse.occurrences))}")

    print("\n✓ Test completed!")
else:
    print("\n✗ Test failed!")
    sys.exit(1)
