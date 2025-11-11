#!/usr/bin/env python3
"""
Example: Compiling with custom memory configuration

This demonstrates how to customize stack, heap, and string pool sizes
when compiling BASIC programs.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.lexer import tokenize
from src.parser import Parser
from src.semantic_analyzer import SemanticAnalyzer
from src.codegen_backend import Z88dkCBackend

# Simple test program
basic_code = """
10 REM Test with custom memory settings
20 PRINT "Memory test"
30 F = FRE(0)
40 S = FRE("")
50 PRINT "Total:"; F; "String pool:"; S
60 END
"""

# Tokenize and parse
tokens = tokenize(basic_code)
parser = Parser(tokens)
program = parser.parse()

# Semantic analysis
analyzer = SemanticAnalyzer()
analyzer.analyze(program)

# Custom memory configuration
custom_config = {
    'stack_pointer': '0xFC00',      # 63K - for systems with more RAM
    'stack_size': 1024,              # 1KB stack (double the default)
    'heap_size': 4096,               # 4KB heap (double the default)
    'string_pool_size': 2048,        # 2KB string pool (double the default)
}

print("=== Compiling with custom memory config ===")
print(f"Stack pointer:    {custom_config['stack_pointer']} (63K)")
print(f"Stack size:       {custom_config['stack_size']} bytes")
print(f"Heap size:        {custom_config['heap_size']} bytes")
print(f"String pool size: {custom_config['string_pool_size']} bytes")
print()

# Generate code with custom config
backend = Z88dkCBackend(analyzer.symbols, config=custom_config)
c_code = backend.generate(program)

# Show the generated memory configuration
print("=== Generated C code (memory config) ===")
for line in c_code.split('\n'):
    if 'Memory configuration' in line:
        # Print next 10 lines
        idx = c_code.split('\n').index(line)
        for i in range(10):
            print(c_code.split('\n')[idx + i])
        break

# Save to file
with open('custom_mem.c', 'w') as f:
    f.write(c_code)

print("\n=== Saved to custom_mem.c ===")
print("\nTo compile:")
print("  z88dk.zcc +cpm custom_mem.c test_compile/mb25_string.c -Itest_compile -create-app -lm -o custom_mem")
