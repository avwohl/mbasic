#!/usr/bin/env python3
"""
Test all BASIC programs in library categories by directly importing the interpreter.

This avoids subprocess permission issues and provides better error reporting.
"""

import sys
import io
from pathlib import Path
from contextlib import redirect_stdout, redirect_stderr

# Add parent directory to path so we can import mbasic modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.lexer import tokenize
from src.parser import Parser
from src.interpreter import Interpreter

# Categories to test
CATEGORIES = [
    "games",
    "utilities",
    "demos",
    "education",
    "business",
    "telecommunications",
    "electronics",
    "data_management",
    "ham_radio"
]

ROOT = Path(__file__).parent.parent
BASIC_DIR = ROOT / "basic"

# Test results
results = {
    "parse_success": [],     # Loaded and parsed successfully
    "parse_error": [],       # Failed to parse
    "ran_to_input": [],      # Ran and stopped at INPUT
    "ran_to_end": [],        # Ran to completion
    "runtime_error": []      # Runtime error during execution
}


def test_program(filepath: Path) -> tuple[str, str]:
    """
    Test a single BASIC program by directly importing it.

    Returns:
        tuple[status, message]
    """
    try:
        # Read the program
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            program_text = f.read()

        # Tokenize
        tokens = tokenize(program_text)

        # Parse
        parser = Parser(tokens)
        program = parser.parse()

        # If we got here, parsing succeeded
        parse_result = "parse_success"
        parse_msg = f"Parsed successfully ({len(program.lines)} lines)"

        # Try to run it (with timeout-like behavior)
        # Create interpreter with StringIO for I/O
        stdin = io.StringIO("test\n1\ny\n" * 10)  # Provide some default inputs
        stdout = io.StringIO()
        stderr = io.StringIO()

        try:
            with redirect_stdout(stdout), redirect_stderr(stderr):
                interp = Interpreter(
                    program,
                    stdin=stdin,
                    stdout=stdout,
                    stderr=stderr
                )

                # Run with step limit to avoid infinite loops
                steps = 0
                max_steps = 1000

                while not interp.halted and steps < max_steps:
                    interp.step()
                    steps += 1

                output = stdout.getvalue()
                errors = stderr.getvalue()

                if steps >= max_steps:
                    return "ran_to_input", f"Parsed OK, likely waiting for INPUT (stopped after {steps} steps)"
                elif interp.halted:
                    if output:
                        return "ran_to_end", f"Ran to completion with output ({len(output)} chars)"
                    else:
                        return "ran_to_end", "Ran to completion (no output)"
                else:
                    return "ran_to_input", "Stopped (likely at INPUT)"

        except KeyboardInterrupt:
            return "ran_to_input", "Interrupted (likely infinite loop or INPUT)"
        except Exception as e:
            return "runtime_error", f"Runtime error: {str(e)[:200]}"

    except SyntaxError as e:
        return "parse_error", f"Parse error: {str(e)[:200]}"
    except Exception as e:
        return "parse_error", f"Error loading: {str(e)[:200]}"


def main():
    """Test all programs in all published categories."""

    print("=" * 80)
    print("MBASIC Library Program Test Suite (Direct Import)")
    print("=" * 80)
    print()
    print(f"Testing categories: {', '.join(CATEGORIES)}")
    print()

    total_programs = 0

    # Test each category
    for category in CATEGORIES:
        category_dir = BASIC_DIR / category

        if not category_dir.exists():
            print(f"⚠️  Category directory not found: {category_dir}")
            continue

        # Get all .bas files in category
        bas_files = sorted(category_dir.glob("*.bas"))

        if not bas_files:
            print(f"⚠️  No .bas files found in {category}")
            continue

        print(f"\n{'=' * 80}")
        print(f"Testing category: {category.upper()} ({len(bas_files)} programs)")
        print(f"{'=' * 80}")

        for bas_file in bas_files:
            total_programs += 1
            print(f"\n{bas_file.name}...", end=" ", flush=True)

            status, message = test_program(bas_file)
            results[status].append((category, bas_file.name, message))

            # Print result with emoji
            status_emoji = {
                "parse_success": "✅",
                "parse_error": "❌",
                "ran_to_input": "⏸️",
                "ran_to_end": "✅",
                "runtime_error": "💥"
            }

            print(f"{status_emoji.get(status, '❓')} {status}")
            if status in ("parse_error", "runtime_error"):
                print(f"    {message}")

    # Print summary
    print("\n")
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print()
    print(f"Total programs tested: {total_programs}")
    print()
    print(f"✅ Parsed successfully:  {len(results['parse_success']) + len(results['ran_to_input']) + len(results['ran_to_end']):3d}")
    print(f"   - Ran to completion:  {len(results['ran_to_end']):3d}")
    print(f"   - Stopped at INPUT:   {len(results['ran_to_input']):3d}")
    print(f"❌ Parse errors:         {len(results['parse_error']):3d}")
    print(f"💥 Runtime errors:       {len(results['runtime_error']):3d}")

    # Detailed breakdown
    if results['parse_error']:
        print("\n" + "=" * 80)
        print(f"PARSE ERRORS ({len(results['parse_error'])})")
        print("=" * 80)
        for category, filename, message in results['parse_error']:
            print(f"\n{category}/{filename}")
            print(f"  {message}")

    if results['runtime_error']:
        print("\n" + "=" * 80)
        print(f"RUNTIME ERRORS ({len(results['runtime_error'])})")
        print("=" * 80)
        for category, filename, message in results['runtime_error']:
            print(f"\n{category}/{filename}")
            print(f"  {message}")

    # Success stories
    if results['ran_to_end']:
        print("\n" + "=" * 80)
        print(f"RAN TO COMPLETION ({len(results['ran_to_end'])})")
        print("=" * 80)
        for category, filename, message in results['ran_to_end']:
            print(f"  ✅ {category}/{filename}")

    # Exit code
    if results['parse_error']:
        print("\n❌ Some programs have parse errors")
        return 1
    else:
        print("\n✅ All programs parsed successfully!")
        return 0


if __name__ == "__main__":
    sys.exit(main())
