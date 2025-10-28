#!/usr/bin/env python3
"""
Test that keyword case settings are properly integrated with lexer.

Verifies that the keywords.case_style setting is respected when creating
lexers, and that the 'error' policy properly raises ValueError on conflicts.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

import unittest
from src.settings import set as settings_set, get as settings_get
from src.lexer import Lexer, create_keyword_case_manager, tokenize


class TestKeywordCaseSettingsIntegration(unittest.TestCase):
    """Test keyword case settings integration with lexer."""

    def setUp(self):
        """Set up test fixtures."""
        # Save original setting
        self.original_policy = settings_get('keywords.case_style', 'force_lower')

    def tearDown(self):
        """Restore original setting."""
        settings_set('keywords.case_style', self.original_policy)

    def test_create_keyword_case_manager_respects_settings(self):
        """Test that create_keyword_case_manager() reads from settings."""
        settings_set('keywords.case_style', 'error')
        manager = create_keyword_case_manager()
        self.assertEqual(manager.policy, 'error')

        settings_set('keywords.case_style', 'force_upper')
        manager = create_keyword_case_manager()
        self.assertEqual(manager.policy, 'force_upper')

    def test_error_policy_raises_on_conflict(self):
        """Test that error policy raises ValueError on case conflict."""
        settings_set('keywords.case_style', 'error')

        code = '''10 PRINT "First"
20 print "Second"
30 PRINT "Third"'''

        with self.assertRaises(ValueError) as cm:
            tokenize(code)

        error_msg = str(cm.exception)
        self.assertIn('Case conflict', error_msg)
        self.assertIn('print', error_msg.lower())
        self.assertIn('line', error_msg.lower())

    def test_error_policy_no_conflict(self):
        """Test that error policy succeeds when no conflicts."""
        settings_set('keywords.case_style', 'error')

        code = '''10 PRINT "First"
20 PRINT "Second"
30 PRINT "Third"'''

        # Should not raise
        tokens = tokenize(code)
        self.assertGreater(len(tokens), 0)

    def test_force_lower_policy(self):
        """Test that force_lower policy works."""
        settings_set('keywords.case_style', 'force_lower')

        code = '''10 PRINT "test"
20 print "test"
30 Print "test"'''

        # Should not raise
        tokens = tokenize(code)
        self.assertGreater(len(tokens), 0)

    def test_force_upper_policy(self):
        """Test that force_upper policy works."""
        settings_set('keywords.case_style', 'force_upper')

        code = '''10 PRINT "test"
20 print "test"
30 Print "test"'''

        # Should not raise
        tokens = tokenize(code)
        self.assertGreater(len(tokens), 0)

    def test_first_wins_policy(self):
        """Test that first_wins policy works."""
        settings_set('keywords.case_style', 'first_wins')

        code = '''10 Print "test"
20 PRINT "test"
30 print "test"'''

        # Should not raise
        tokens = tokenize(code)
        self.assertGreater(len(tokens), 0)

    def test_preserve_policy(self):
        """Test that preserve policy works."""
        settings_set('keywords.case_style', 'preserve')

        code = '''10 PRINT "test"
20 print "test"
30 Print "test"'''

        # Should not raise
        tokens = tokenize(code)
        self.assertGreater(len(tokens), 0)


def run_tests():
    """Run all tests."""
    suite = unittest.TestLoader().loadTestsFromTestCase(TestKeywordCaseSettingsIntegration)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(run_tests())
