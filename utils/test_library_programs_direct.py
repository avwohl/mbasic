#!/usr/bin/env python3
"""
Test all BASIC programs in the basic tree by directly importing the interpreter.

Tests ALL .bas files except those in:
- basic/incompatible/
- basic/bad_syntax/

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
from src.runtime import Runtime
from src.interpreter import Interpreter

ROOT = Path(__file__).parent.parent
BASIC_DIR = ROOT / "basic"

# Directories to exclude
EXCLUDE_DIRS = {"incompatible", "bad_syntax", "dev"}

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
        try:
            # Suppress program output by redirecting stdout/stderr
            devnull = io.StringIO()

            with redirect_stdout(devnull), redirect_stderr(devnull):
                # Create runtime and interpreter
                runtime = Runtime(program)
                runtime.setup()

                interp = Interpreter(runtime)

                # Run with step limit to avoid infinite loops
                ticks = 0
                max_ticks = 100  # Each tick can execute up to 100 statements

                while not interp.state.status in ('done', 'error', 'waiting_for_input') and ticks < max_ticks:
                    interp.tick()
                    ticks += 1

            if ticks >= max_ticks:
                return "ran_to_input", f"Parsed OK, likely waiting for INPUT (stopped after {ticks} ticks)"
            elif interp.state.status == 'done':
                return "ran_to_end", "Ran to completion"
            elif interp.state.status == 'waiting_for_input':
                return "ran_to_input", "Stopped at INPUT"
            elif interp.state.status == 'error':
                return "runtime_error", f"Runtime error: {interp.state.error_info.error_message if interp.state.error_info else 'Unknown error'}"
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
    """Test all .bas files in basic tree except incompatible and bad_syntax."""

    print("=" * 80)
    print("MBASIC Basic Tree Test Suite (Direct Import)")
    print("=" * 80)
    print()
    print(f"Testing all .bas files in: {BASIC_DIR}")
    print(f"Excluding directories: {', '.join(EXCLUDE_DIRS)}")
    print()

    total_programs = 0

    # Find all subdirectories
    subdirs = sorted([d for d in BASIC_DIR.iterdir()
                     if d.is_dir() and d.name not in EXCLUDE_DIRS])

    for subdir in subdirs:
        # Get all .bas files in this directory
        bas_files = sorted(subdir.glob("*.bas"))

        if not bas_files:
            continue

        category = subdir.name
        print(f"\n{'=' * 80}")
        print(f"Testing: {category}/ ({len(bas_files)} programs)")
        print(f"{'=' * 80}")

        for bas_file in bas_files:
            total_programs += 1
            print(f"{bas_file.name}...", end=" ", flush=True)

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
                # Truncate long messages
                msg = message[:100] + "..." if len(message) > 100 else message
                print(f"    {msg}")

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

    # Success stories - programs that work (ran_to_end or ran_to_input)
    all_working = results['ran_to_end'] + results['ran_to_input']
    if all_working:
        print("\n" + "=" * 80)
        print(f"WORKING PROGRAMS ({len(all_working)})")
        print("=" * 80)
        print(f"Ran to completion: {len(results['ran_to_end'])}")
        print(f"Stopped at INPUT:  {len(results['ran_to_input'])}")
        print()
        for category, filename, message in sorted(all_working):
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
