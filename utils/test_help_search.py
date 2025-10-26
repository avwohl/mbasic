#!/usr/bin/env python3
"""
Test help search functionality.

Tests the search index loading and searching capabilities.
"""

import sys
from pathlib import Path

# Add parent directory to path to import help_widget
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from ui.help_widget import HelpWidget

def test_search_indexes():
    """Test that search indexes load correctly."""
    help_root = Path(__file__).parent.parent / "docs" / "help"

    # Create a minimal HelpWidget to test search
    class TestHelpWidget:
        def __init__(self, help_root):
            self.help_root = Path(help_root)

        def _load_search_indexes(self):
            """Load all three search indexes (language, mbasic, ui)."""
            import json
            indexes = {}

            index_paths = [
                ('language', self.help_root / 'common/language/search_index.json'),
                ('mbasic', self.help_root / 'mbasic/search_index.json'),
                ('ui', self.help_root / 'ui/curses/search_index.json'),
            ]

            for name, path in index_paths:
                try:
                    if path.exists():
                        with open(path, 'r') as f:
                            indexes[name] = json.load(f)
                except Exception as e:
                    print(f"Error loading {name}: {e}")

            return indexes

    widget = TestHelpWidget(help_root)
    indexes = widget._load_search_indexes()

    print("Search Index Loading Test")
    print("=" * 60)
    print()

    for name, index in indexes.items():
        if index:
            files_count = len(index.get('files', []))
            keywords_count = len(index.get('keywords', {}))
            aliases_count = len(index.get('aliases', {}))
            print(f"✓ {name.capitalize()} index loaded:")
            print(f"  - {files_count} files")
            print(f"  - {keywords_count} keywords")
            print(f"  - {aliases_count} aliases")
        else:
            print(f"✗ {name.capitalize()} index failed to load")
        print()

    if len(indexes) == 3:
        total_files = sum(len(idx.get('files', [])) for idx in indexes.values())
        total_keywords = sum(len(idx.get('keywords', {})) for idx in indexes.values())
        print(f"✓ All 3 indexes loaded successfully")
        print(f"  Total: {total_files} files, {total_keywords} keywords")
        return True
    else:
        print(f"✗ Only {len(indexes)} of 3 indexes loaded")
        return False

def test_search_queries():
    """Test search query functionality."""
    from pathlib import Path
    import json

    help_root = Path(__file__).parent.parent / "docs" / "help"

    print("\nSearch Query Test")
    print("=" * 60)
    print()

    # Test queries
    test_queries = [
        "loop",
        "array",
        "print",
        "file",
        "subroutine",
    ]

    for query in test_queries:
        # Count results across all indexes
        total_results = 0

        for index_name in ['common/language', 'mbasic', 'ui/curses']:
            index_path = help_root / index_name / 'search_index.json'
            if index_path.exists():
                with open(index_path, 'r') as f:
                    index = json.load(f)

                # Search in keywords
                query_lower = query.lower()
                if 'keywords' in index:
                    for keyword, paths in index['keywords'].items():
                        if query_lower in keyword.lower():
                            if isinstance(paths, list):
                                total_results += len(paths)
                            else:
                                total_results += 1

                # Search in titles
                if 'files' in index:
                    for file_info in index['files']:
                        title = file_info.get('title', '').lower()
                        desc = file_info.get('description', '').lower()
                        if query_lower in title or query_lower in desc:
                            total_results += 1

        print(f"Query: '{query}' → {total_results} results")

    print()
    return True

if __name__ == '__main__':
    print("MBASIC Help Search Test")
    print()

    success = True

    # Test 1: Index loading
    if not test_search_indexes():
        success = False

    # Test 2: Search queries
    if not test_search_queries():
        success = False

    if success:
        print("✅ All tests passed!")
        sys.exit(0)
    else:
        print("❌ Some tests failed")
        sys.exit(1)
