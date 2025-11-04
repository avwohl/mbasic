#!/usr/bin/env python3
"""Test check_docs_consistency2.py with just two files"""

import os
import sys
from pathlib import Path

# Make sure ANTHROPIC_API_KEY is set
if not os.getenv("ANTHROPIC_API_KEY"):
    print("Error: ANTHROPIC_API_KEY not set")
    sys.exit(1)

# Import the analyzer
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.check_docs_consistency2 import EnhancedConsistencyAnalyzer

print("Testing with src/interactive.py and src/case_string_handler.py")
print("="*60)

analyzer = EnhancedConsistencyAnalyzer()

# Read just these two files
test_files = {
    'src/interactive.py': (Path(__file__).parent.parent / 'src' / 'interactive.py').read_text(),
    'src/case_string_handler.py': (Path(__file__).parent.parent / 'src' / 'case_string_handler.py').read_text()
}

print(f"\nLoaded {len(test_files)} files")

# Extract code context
for filepath, content in test_files.items():
    if filepath.endswith('.py'):
        analyzer._extract_code_context(filepath, content)

# Analyze code/comment conflicts
conflicts = analyzer.analyze_code_comment_conflicts(test_files)

print(f"\n{'='*60}")
print(f"RESULTS: Found {len(conflicts)} conflicts")
print(f"{'='*60}\n")

for i, conflict in enumerate(conflicts, 1):
    print(f"Conflict {i}:")
    print(f"  File: {conflict.get('file')}")
    print(f"  Type: {conflict.get('type')}")
    print(f"  Line: {conflict.get('line')}")
    print(f"  Explanation: {conflict.get('explanation')}")
    print()
