#!/usr/bin/env python3
"""
Test that keyword case settings are properly integrated with lexer.

Verifies that the keywords.case_style setting is respected when creating
lexers, and tests all three available policies: force_lower, force_upper, force_capitalize.
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
        settings_set('keywords.case_style', 'force_capitalize')
        manager = create_keyword_case_manager()
        self.assertEqual(manager.policy, 'force_capitalize')

        settings_set('keywords.case_style', 'force_upper')
        manager = create_keyword_case_manager()
        self.assertEqual(manager.policy, 'force_upper')

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

    def test_force_capitalize_policy(self):
        """Test that force_capitalize policy works."""
        settings_set('keywords.case_style', 'force_capitalize')

        code = '''10 Print "test"
20 PRINT "test"
30 print "test"'''

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
