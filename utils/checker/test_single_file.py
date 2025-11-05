#!/usr/bin/env python3
"""
Test check_docs_consistency2.py on a single file to verify the fix.
"""

import os
import sys
from pathlib import Path

# Import the checker module
sys.path.insert(0, str(Path(__file__).parent))
from check_docs_consistency2 import EnhancedConsistencyAnalyzer

def test_single_file():
    """Test the analyzer on src/interactive.py specifically."""

    # Check for API key
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("Error: ANTHROPIC_API_KEY environment variable not set")
        return False

    try:
        analyzer = EnhancedConsistencyAnalyzer()

        # Read just the interactive.py file
        file_path = analyzer.project_root / "src" / "interactive.py"
        if not file_path.exists():
            print(f"Error: {file_path} does not exist")
            return False

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        print(f"Testing with {file_path}")
        print(f"File size: {len(content)} characters")
        print("-" * 60)

        # Test the analysis
        source_files = {"src/interactive.py": content}
        conflicts = analyzer.analyze_code_comment_conflicts(source_files)

        print("-" * 60)
        if conflicts:
            print(f"Found {len(conflicts)} conflicts:")
            for conflict in conflicts:
                print(f"  - Line {conflict.get('line', '?')}: {conflict.get('explanation', 'No explanation')[:80]}...")
        else:
            print("No conflicts found (or all responses were successfully parsed)")

        return True

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_single_file()
    if success:
        print("\n✅ Test completed successfully!")
    else:
        print("\n❌ Test failed!")
        sys.exit(1)