#!/usr/bin/env python3
"""
Unit tests for help system search ranking and fuzzy matching.

Tests search improvements without requiring GUI.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

import unittest
from unittest.mock import Mock, MagicMock


class TestHelpSearchRanking(unittest.TestCase):
    """Test help search ranking functionality."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a mock TkHelpBrowser instance
        from src.ui.tk_help_browser import TkHelpBrowser

        # Mock the parent and other dependencies
        self.mock_parent = Mock()
        self.help_root = Path(__file__).parent.parent.parent.parent / 'docs' / 'help'

        # We can't instantiate TkHelpBrowser in headless env, so test methods directly
        # Create instance with mocked tk components
        self.browser = Mock()
        self.browser._fuzzy_match = TkHelpBrowser._fuzzy_match.__get__(self.browser)
        self.browser._search_indexes = TkHelpBrowser._search_indexes.__get__(self.browser)

    def test_fuzzy_match_exact(self):
        """Test fuzzy matching with exact match."""
        # Exact match should return True
        result = self.browser._fuzzy_match("print", "print statement")
        self.assertTrue(result)

    def test_fuzzy_match_typo(self):
        """Test fuzzy matching with single character typo."""
        # "prnt" should match "print" (1 deletion)
        result = self.browser._fuzzy_match("prnt", "print statement")
        self.assertTrue(result)

        # "inpt" should match "input" (1 deletion)
        result = self.browser._fuzzy_match("inpt", "input data")
        self.assertTrue(result)

    def test_fuzzy_match_swap(self):
        """Test fuzzy matching with swapped characters."""
        # "pirnt" should match "print" (2 operations: swap counts as 2)
        result = self.browser._fuzzy_match("pirnt", "print")
        self.assertTrue(result)

    def test_fuzzy_match_too_short(self):
        """Test that short queries don't use fuzzy matching."""
        # Queries < 4 chars should not fuzzy match
        result = self.browser._fuzzy_match("for", "form")
        self.assertFalse(result)  # Exact substring match still works though

    def test_fuzzy_match_too_distant(self):
        """Test that very different strings don't match."""
        # More than 2 edits should not match
        result = self.browser._fuzzy_match("test", "basic")
        self.assertFalse(result)

    def test_search_ranking_mock(self):
        """Test search result ranking logic."""
        # Create mock search index
        self.browser.search_indexes = {
            'files': [
                {
                    'title': 'PRINT',
                    'description': 'Print to screen',
                    'type': 'statement',
                    'category': 'output',
                    'keywords': ['output', 'display'],
                    'tier': 'language',
                    'path': 'common/language/statements/print.md'
                },
                {
                    'title': 'LPRINT',
                    'description': 'Print to printer',
                    'type': 'statement',
                    'category': 'output',
                    'keywords': ['printer', 'output'],
                    'tier': 'language',
                    'path': 'common/language/statements/lprint.md'
                },
                {
                    'title': 'String Functions',
                    'description': 'Functions to print and format strings',
                    'type': 'reference',
                    'category': 'functions',
                    'keywords': ['strings', 'format'],
                    'tier': 'language',
                    'path': 'common/language/functions/string.md'
                }
            ]
        }

        # Search for "print"
        results = self.browser._search_indexes("print")

        # Should return all 3 results
        self.assertEqual(len(results), 3)

        # First result should be PRINT (exact title match)
        self.assertEqual(results[0][2], 'PRINT')  # (tier, path, title, desc)

        # Second should be LPRINT (title contains "print")
        self.assertEqual(results[1][2], 'LPRINT')

        # Third should be String Functions (description contains "print")
        self.assertEqual(results[2][2], 'String Functions')

    def test_search_fuzzy_fallback(self):
        """Test that fuzzy matching works when no exact matches."""
        # Create mock search index
        self.browser.search_indexes = {
            'files': [
                {
                    'title': 'PRINT',
                    'description': 'Output to screen',
                    'type': 'statement',
                    'category': 'output',
                    'keywords': ['output'],
                    'tier': 'language',
                    'path': 'common/language/statements/print.md'
                }
            ]
        }

        # Search for "prnt" (typo)
        results = self.browser._search_indexes("prnt")

        # Should find PRINT via fuzzy matching
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][2], 'PRINT')


def run_tests():
    """Run all tests."""
    suite = unittest.TestLoader().loadTestsFromTestCase(TestHelpSearchRanking)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(run_tests())
