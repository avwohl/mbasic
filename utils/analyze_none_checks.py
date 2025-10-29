#!/usr/bin/env python3
"""Analyze and categorize None checks in the codebase."""

import re
import sys
from pathlib import Path
from collections import defaultdict

def analyze_none_checks(src_dir='src'):
    """Analyze all None checks and categorize them."""

    categories = {
        'optional_params': [],  # Function params with defaults
        'error_handler': [],    # Error handler checks
        'control_flow': [],     # next_line, npc, etc.
        'interpreter_state': [], # Interpreter/runtime state
        'token_checks': [],     # Parser/lexer token checks
        'file_ops': [],         # File number/operations
        'line_lookups': [],     # Line not found
        'debugger': [],         # Debugger-specific
        'loop_state': [],       # FOR/WHILE loops
        'other': []
    }

    # Patterns to categorize
    patterns = {
        'optional_params': r'if \w+ is None:\s*\w+ = ',
        'error_handler': r'error_handler is',
        'control_flow': r'(next_line|npc|next_stmt_index) is',
        'interpreter_state': r'(current_line|current_stmt_index|runtime\.\w+) is',
        'token_checks': r'token is',
        'file_ops': r'file_number is',
        'line_lookups': r'line is None',
        'debugger': r'debugger',
        'loop_state': r'(loop_info|wend_pos) is'
    }

    src_path = Path(src_dir)
    total_checks = 0

    for py_file in src_path.rglob('*.py'):
        with open(py_file, 'r') as f:
            try:
                lines = f.readlines()
            except:
                continue

        for i, line in enumerate(lines, 1):
            if ' is None' in line or ' is not None' in line:
                total_checks += 1
                location = f"{py_file}:{i}"

                # Categorize
                categorized = False
                for category, pattern in patterns.items():
                    if re.search(pattern, line, re.IGNORECASE):
                        categories[category].append((location, line.strip()))
                        categorized = True
                        break

                if not categorized:
                    categories['other'].append((location, line.strip()))

    # Print report
    print("=" * 80)
    print("NONE CHECK ANALYSIS REPORT")
    print("=" * 80)
    print(f"\nTotal None checks: {total_checks}")
    print("\nBreakdown by category:")
    print("-" * 80)

    for category, items in sorted(categories.items(), key=lambda x: len(x[1]), reverse=True):
        if items:
            print(f"\n{category.upper()}: {len(items)} occurrences")
            print("-" * 40)
            for location, line in items[:10]:  # Show first 10
                print(f"  {location}")
                print(f"    {line[:70]}")
            if len(items) > 10:
                print(f"  ... and {len(items) - 10} more")

    # Summary recommendations
    print("\n" + "=" * 80)
    print("RECOMMENDATIONS")
    print("=" * 80)

    if categories['control_flow']:
        print(f"\n✓ Control Flow ({len(categories['control_flow'])}): Add has_pending_jump(), is_sequential_execution()")

    if categories['error_handler']:
        print(f"\n✓ Error Handler ({len(categories['error_handler'])}): Add has_error_handler()")

    if categories['interpreter_state']:
        print(f"\n✓ Interpreter State ({len(categories['interpreter_state'])}): Add has_active_program(), is_program_running()")

    if categories['loop_state']:
        print(f"\n✓ Loop State ({len(categories['loop_state'])}): Add has_active_loop(), find_loop() returning sentinel")

    if categories['optional_params']:
        print(f"\n○ Optional Params ({len(categories['optional_params'])}): OK - Keep as-is with type hints")

    print("\n" + "=" * 80)

if __name__ == '__main__':
    analyze_none_checks()
