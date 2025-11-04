#!/usr/bin/env python3
"""
Test that keyword case policies correctly affect display case.

Verifies that the lexer uses the policy-determined case from
KeywordCaseManager.register_keyword() return value, not the original typed case.

This is a regression test for a bug where keywords showed their original
typed case instead of the policy-determined case.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

import unittest
from src.settings import set as settings_set, get as settings_get
from src.lexer import tokenize


class TestKeywordCaseDisplayConsistency(unittest.TestCase):
    """Test that keyword display case follows policy."""

    def setUp(self):
        """Set up test fixtures."""
        # Save original setting
        self.original_policy = settings_get('keywords.case_style', 'force_lower')

    def tearDown(self):
        """Restore original setting."""
        settings_set('keywords.case_style', self.original_policy)

    def get_keyword_cases(self, code):
        """Helper to extract keyword display cases from tokenized code."""
        tokens = tokenize(code)
        return [getattr(t, 'original_case_keyword', None)
                for t in tokens
                if hasattr(t, 'original_case_keyword') and t.original_case_keyword]

    def test_force_lower_policy(self):
        """Test that force_lower converts all to lowercase."""
        settings_set('keywords.case_style', 'force_lower')

        code = '''10 Print "First"
20 PRINT "Second"
30 print "Third"'''

        cases = self.get_keyword_cases(code)
        self.assertEqual(cases, ['print', 'print', 'print'])

    def test_force_upper_policy(self):
        """Test that force_upper converts all to UPPERCASE."""
        settings_set('keywords.case_style', 'force_upper')

        code = '''10 Print "First"
20 PRINT "Second"
30 print "Third"'''

        cases = self.get_keyword_cases(code)
        self.assertEqual(cases, ['PRINT', 'PRINT', 'PRINT'])

    def test_force_capitalize_policy(self):
        """Test that force_capitalize converts all to Capitalized."""
        settings_set('keywords.case_style', 'force_capitalize')

        code = '''10 PRINT "First"
20 print "Second"
30 PrInT "Third"'''

        cases = self.get_keyword_cases(code)
        self.assertEqual(cases, ['Print', 'Print', 'Print'])

    def test_multiple_keywords_same_line(self):
        """Test that all keywords on same line follow policy."""
        settings_set('keywords.case_style', 'force_upper')

        code = '10 if x>0 then print "yes" else print "no"'

        cases = self.get_keyword_cases(code)
        # All keywords should be uppercase
        expected = ['IF', 'THEN', 'PRINT', 'ELSE', 'PRINT']
        self.assertEqual(cases, expected)

    def test_different_keywords_share_policy(self):
        """Test that different keywords all follow same policy."""
        settings_set('keywords.case_style', 'force_capitalize')

        code = '''10 FOR i=1 TO 10
20   PRINT i
30 NEXT i'''

        cases = self.get_keyword_cases(code)
        expected = ['For', 'To', 'Print', 'Next']
        self.assertEqual(cases, expected)

    def test_consistency_across_program(self):
        """Test that all occurrences of same keyword are consistent."""
        settings_set('keywords.case_style', 'force_capitalize')

        code = '''10 Print "1"
20 FOR I=1 TO 5
30   PRINT I
40 NEXT I
50 print "Done"'''

        cases = self.get_keyword_cases(code)
        print_cases = [c for c in cases if c.upper() == 'PRINT']

        # All PRINT occurrences should be same case (capitalized)
        self.assertEqual(len(set(print_cases)), 1, "All PRINT occurrences should have same case")
        self.assertEqual(print_cases[0], 'Print', "Should be capitalized")


def run_tests():
    """Run all tests."""
    suite = unittest.TestLoader().loadTestsFromTestCase(TestKeywordCaseDisplayConsistency)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(run_tests())
