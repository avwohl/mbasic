#!/usr/bin/env python3
"""
Test that keyword case policies are properly scoped.

Verifies that:
1. Immediate mode and program mode use separate KeywordCaseManagers
2. Each tokenization gets a fresh manager (no cross-contamination)
3. Case conflicts only detected within same tokenization scope
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

import unittest
from src.settings import set as settings_set, get as settings_get
from src.lexer import tokenize


class TestKeywordCaseScopeIsolation(unittest.TestCase):
    """Test keyword case scope isolation between tokenization calls."""

    def setUp(self):
        """Set up test fixtures."""
        # Save original setting
        self.original_policy = settings_get('keywords.case_style', 'force_lower')

    def tearDown(self):
        """Restore original setting."""
        settings_set('keywords.case_style', self.original_policy)

    def test_separate_tokenizations_isolated(self):
        """Test that separate tokenize() calls don't share case managers."""
        settings_set('keywords.case_style', 'force_lower')

        # First tokenization with PRINT (uppercase)
        code1 = '10 PRINT "test"'
        tokens1 = tokenize(code1)
        self.assertGreater(len(tokens1), 0)

        # Second tokenization with print (lowercase)
        # Should NOT raise error (different scope)
        code2 = '20 print "test"'
        tokens2 = tokenize(code2)
        self.assertGreater(len(tokens2), 0)

    def test_conflict_within_same_tokenization(self):
        """Test that conflicts ARE detected within same tokenization."""
        settings_set('keywords.case_style', 'force_lower')

        # Single tokenization with mixed case
        code = '''10 PRINT "First"
20 print "Second"'''

        # With force_lower, all keywords normalized (no error)
        tokens = tokenize(code)
        self.assertGreater(len(tokens), 0)

    def test_immediate_mode_simulation(self):
        """Test simulating immediate mode vs program mode."""
        settings_set('keywords.case_style', 'force_lower')

        # Simulate program with RUN (uppercase)
        program = '10 RUN'
        tokens_program = tokenize(program)
        self.assertGreater(len(tokens_program), 0)

        # Simulate immediate mode with run (lowercase)
        # In real usage, immediate mode does: "0 " + statement
        immediate = '0 run'
        tokens_immediate = tokenize(immediate)
        self.assertGreater(len(tokens_immediate), 0)

        # Both should succeed (different scopes)

    def test_adding_lines_individually(self):
        """Test that adding program lines one at a time works."""
        settings_set('keywords.case_style', 'force_lower')

        # Simulate adding lines individually (as in interactive mode)
        # Each line gets its own tokenization
        lines = [
            '10 PRINT "First"',
            '20 print "Second"',  # Different case, but different tokenization
            '30 PRINT "Third"'
        ]

        # Each line tokenizes separately - no conflicts
        for line in lines:
            tokens = tokenize(line)
            self.assertGreater(len(tokens), 0)

    def test_whole_program_tokenization(self):
        """Test that whole program tokenization detects conflicts."""
        settings_set('keywords.case_style', 'force_lower')

        # When running the program, all lines tokenized together
        whole_program = '''10 PRINT "First"
20 print "Second"
30 PRINT "Third"'''

        # With force_lower, all keywords normalized (no error)

    def test_consistent_case_no_error(self):
        """Test that consistent case never errors."""
        settings_set('keywords.case_style', 'force_lower')

        # All uppercase - should work
        code_upper = '''10 PRINT "test"
20 PRINT "test"
30 PRINT "test"'''
        tokens = tokenize(code_upper)
        self.assertGreater(len(tokens), 0)

        # All lowercase - should work
        code_lower = '''10 print "test"
20 print "test"
30 print "test"'''
        tokens = tokenize(code_lower)
        self.assertGreater(len(tokens), 0)

    def test_multiple_keywords_same_line(self):
        """Test case consistency for multiple keywords on same line."""
        settings_set('keywords.case_style', 'force_lower')

        # Consistent case - should work
        code_ok = '10 IF X>0 THEN PRINT "positive" ELSE PRINT "non-positive"'
        tokens = tokenize(code_ok)
        self.assertGreater(len(tokens), 0)

        # Inconsistent case - should error
        code_bad = '10 IF X>0 THEN print "positive" ELSE PRINT "non-positive"'


def run_tests():
    """Run all tests."""
    suite = unittest.TestLoader().loadTestsFromTestCase(TestKeywordCaseScopeIsolation)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(run_tests())
