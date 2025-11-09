#!/usr/bin/env python3
"""
Test script for compiler backend.

This script tests the complete compilation pipeline:
1. Parse BASIC source
2. Semantic analysis
3. Code generation
4. Compilation with z88dk
5. Execution with tnylpo
"""

import sys
import os
import subprocess

# Add parent directory to path to import mbasic modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.lexer import tokenize
from src.parser import Parser
from src.semantic_analyzer import SemanticAnalyzer


def main():
    if len(sys.argv) < 2:
        print("Usage: test_compile.py <program.bas> [output_name]")
        sys.exit(1)

    basic_file = sys.argv[1]
    output_name = sys.argv[2] if len(sys.argv) > 2 else 'test'

    # Read BASIC program
    print(f"Reading {basic_file}...")
    try:
        with open(basic_file, 'r') as f:
            source = f.read()
    except IOError as e:
        print(f"Error reading file: {e}")
        sys.exit(1)

    # Tokenize
    print("Tokenizing...")
    try:
        tokens = tokenize(source)
    except Exception as e:
        print(f"Tokenization error: {e}")
        sys.exit(1)

    # Parse
    print("Parsing...")
    try:
        parser = Parser(tokens)
        program = parser.parse()
    except Exception as e:
        print(f"Parse error: {e}")
        sys.exit(1)

    # Semantic analysis
    print("Analyzing...")
    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(program)

    if not success:
        print("\nSemantic analysis failed:")
        print(analyzer.get_report())
        sys.exit(1)

    print("Semantic analysis passed!")

    # Compile
    print("\n" + "=" * 70)
    success = analyzer.compile(program, backend_name='z88dk', output_file=output_name)

    if not success:
        print("\nCompilation failed:")
        for error in analyzer.errors:
            print(f"  {error}")
        sys.exit(1)

    # Show warnings
    if analyzer.warnings:
        print("\nWarnings:")
        for warning in analyzer.warnings:
            print(f"  {warning}")

    # Run with tnylpo
    com_file = output_name.lower() + '.com'
    if os.path.exists(com_file):
        print("\n" + "=" * 70)
        print(f"Running {com_file} with tnylpo...")
        print("=" * 70)
        try:
            subprocess.run(['tnylpo', com_file], check=True)
        except subprocess.CalledProcessError as e:
            print(f"\nExecution failed: {e}")
            sys.exit(1)
        except FileNotFoundError:
            print("\ntnylpo not found - install tnylpo to test execution")
    else:
        print(f"\nWarning: {com_file} not found")

    print("\n" + "=" * 70)
    print("Test complete!")


if __name__ == '__main__':
    main()
