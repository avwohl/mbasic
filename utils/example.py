#!/usr/bin/env python3
"""
Example usage of the MBASIC 5.21 lexer
"""
from lexer import tokenize

# Example MBASIC program
program = """10 REM Simple MBASIC program
20 PRINT "Hello, World!"
30 INPUT "What is your name"; NAME$
40 PRINT "Nice to meet you, "; NAME$
50 FOR I% = 1 TO 5
60 PRINT "Count: "; I%
70 NEXT I%
80 END
"""

print("MBASIC 5.21 Lexer Example")
print("=" * 60)
print("\nSource code:")
print("-" * 60)
print(program)
print("-" * 60)

# Tokenize the program
tokens = tokenize(program)

# Display tokens
print("\nTokens:")
print("-" * 60)
for token in tokens:
    if token.type.name != 'EOF':
        print(f"{token.line:3}:{token.column:<3} {token.type.name:20} {token.value!r}")

print("-" * 60)
print(f"\nTotal tokens: {len(tokens)}")
