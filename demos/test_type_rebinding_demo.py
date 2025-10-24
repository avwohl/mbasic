#!/usr/bin/env python3
"""
Demonstration of Type Rebinding Analysis on various BASIC programs
"""

import sys
sys.path.insert(0, 'src')

from lexer import Lexer
from parser import Parser
from semantic_analyzer import SemanticAnalyzer

def analyze_and_show_rebinding(source, title):
    """Analyze a program and show type rebinding results"""
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

        # Extract type rebinding section from report
        report = analyzer.get_report()
        lines = report.split('\n')
        in_section = False
        for line in lines:
            if 'Type Rebinding Analysis' in line:
                in_section = True
            if in_section:
                print(line)
                if line.startswith('Warnings') or line.startswith('Errors') or (line.startswith('====') and in_section):
                    break
    except Exception as e:
        print(f'Error: {e}')


# Example 1: Original motivating example
example1 = """100 I=22.1
110 FOR I=0 TO 10
120   J=J+I
130 NEXT I
"""

analyze_and_show_rebinding(example1, "Example 1: FOR loop re-binding DOUBLE → INTEGER")


# Example 2: Multiple FOR loops with same variable
example2 = """100 FOR N=1 TO 10
110   PRINT N
120 NEXT N
130 FOR N=1.0 TO 5.0
140   PRINT N
150 NEXT N
160 FOR N=1 TO 100
170   PRINT N
180 NEXT N
"""

analyze_and_show_rebinding(example2, "Example 2: Variable re-used in multiple loops")


# Example 3: Sequential independent assignments
example3 = """100 X = 10
110 PRINT X
120 X = 10.5
130 PRINT X
140 X = 20
150 PRINT X
"""

analyze_and_show_rebinding(example3, "Example 3: Sequential assignments with type changes")


# Example 4: Dependent assignment (cannot rebind)
example4 = """100 X = 10
110 X = X + 1
120 X = X * 2
"""

analyze_and_show_rebinding(example4, "Example 4: Dependent assignments (cannot rebind)")


# Example 5: Complex loop with INTEGER arithmetic
example5 = """100 DIM A(100)
110 SUM = 0
120 FOR I = 1 TO 100
130   A(I) = I * 2
140   SUM = SUM + A(I)
150 NEXT I
160 PRINT SUM
"""

analyze_and_show_rebinding(example5, "Example 5: Array initialization with INTEGER loop")


# Example 6: Mixed types
example6 = """100 COUNT = 0
110 TOTAL = 0.0
120 FOR I = 1 TO 10
130   COUNT = COUNT + 1
140   TOTAL = TOTAL + I * 0.5
150 NEXT I
"""

analyze_and_show_rebinding(example6, "Example 6: Mixed INTEGER and DOUBLE in loop")


print(f"\n{'='*70}")
print("Type Rebinding Analysis Complete")
print(f"{'='*70}\n")
