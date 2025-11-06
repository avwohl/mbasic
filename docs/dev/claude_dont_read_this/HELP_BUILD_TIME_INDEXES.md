# Build-Time Help Index System

**Status**: ✅ IMPLEMENTED
**Date**: 2025-10-27

## Overview

The help system now uses **pre-built merged indexes** generated at build time, eliminating the need for runtime index merging and catching broken links before they reach users.

## Problem

Previously, the help system had reliability issues:

1. **Runtime merging**: Each UI loaded and merged three separate indexes (language, mbasic, ui-specific) at startup
2. **Late error detection**: Broken links only discovered when users clicked them
3. **Path confusion**: Links like `common/language/statements/def-fn.md` could be resolved incorrectly
4. **No validation**: No way to verify all help files and links were valid before deployment

## Solution

### Build-Time Index Generation

A build script (`utils/build_help_indexes.py`) now:

1. **Merges three-tier help structure** into single pre-built index per UI
2. **Validates all file paths** referenced in indexes actually exist
3. **Validates all markdown links** by extracting and checking targets
4. **Catches errors at build time** instead of at runtime

### Documentation Build Coordinator

A general documentation builder (`utils/build_docs.py`) coordinates:

1. Help index building (always)
2. Web documentation building (optional, requires mkdocs)
3. Future documentation tasks (API docs, etc.)

## Architecture

### Input: Three-Tier Help System

```
docs/help/
├── common/
│   └── language/           # Tier 1: BASIC language reference
│       ├── search_index.json
│       ├── statements/
│       └── functions/
├── mbasic/                # Tier 2: MBASIC-specific implementation
│   └── search_index.json
└── ui/
    ├── tk/                # Tier 3: UI-specific help
    │   └── search_index.json
    └── curses/
        └── search_index.json
```

### Output: Merged Indexes

```
docs/help/ui/
├── tk/
│   └── merged_index.json    # Pre-built, validated, ready to load
└── curses/
    └── merged_index.json    # Pre-built, validated, ready to load
```

### Merged Index Structure

```json
{
  "ui": "tk",
  "generated": "build_help_indexes.py",
  "files": [
    {
      "path": "common/language/statements/print.md",
      "title": "PRINT",
      "type": "statement",
      "tier": "language",
      "category": "input-output",
      "description": "Output text and values to the screen",
      "keywords": ["print", "output", "display"]
    },
    {
      "path": "mbasic/features.md",
      "title": "MBASIC Features",
      "type": "guide",
      "tier": "mbasic",
      "category": "implementation",
      "description": "Overview of MBASIC implementation features"
    },
    {
      "path": "ui/tk/keyboard-shortcuts.md",
      "title": "Keyboard Shortcuts",
      "type": "reference",
      "tier": "ui/tk",
      "description": "Tk UI keyboard command reference"
    }
  ]
}
```

## Build Process

### Running the Build

```bash
# Build everything (help indexes + web docs if available)
python3 utils/build_docs.py

# Build only help indexes
python3 utils/build_docs.py --help-only

# Validate without writing
python3 utils/build_docs.py --validate-only

# Build only web docs
python3 utils/build_docs.py --web-only
```

### What Gets Validated

1. **File existence**: All files referenced in search indexes must exist
2. **Index JSON**: All index files must be valid JSON
3. **Markdown links**: All internal links extracted and validated:
   - `[text](../path/file.md)` - relative links
   - `[text](common/language/...)` - absolute links (relative to help root)
   - Anchor fragments (`#section`) are stripped before validation
4. **Path resolution**: Links are resolved based on:
   - Current file location (for relative links)
   - Help root (for `common/` paths)

### Build Output

```
============================================================
Building help index for: tk
============================================================
  Language topics: 108
  MBASIC topics:   4
  UI topics:       1
  Total merged:    113
  ✓ Written: docs/help/ui/tk/merged_index.json

============================================================
Building help index for: curses
============================================================
  Language topics: 108
  MBASIC topics:   4
  UI topics:       7
  Total merged:    119
  ✓ Written: docs/help/ui/curses/merged_index.json

============================================================
VALIDATION SUMMARY
============================================================

✅ BUILD SUCCESSFUL
```

### Error Reporting

If validation fails:

```
❌ Errors (2):
  • Help file not found: docs/help/common/language/missing.md
  • Broken link in common/language/statements/resume.md:
    ../../appendices/error-codes.md -> docs/help/common/language/appendices/error-codes.md
```

## UI Changes

### Before: Runtime Index Merging

```python
def _load_search_indexes(self) -> Dict[str, Dict]:
    """Load all three search indexes (language, mbasic, ui)."""
    indexes = {}

    # Load three separate indexes
    index_paths = [
        ('language', self.help_root / 'common/language/search_index.json'),
        ('mbasic', self.help_root / 'mbasic/search_index.json'),
        ('ui', self.help_root / 'ui/tk/search_index.json'),
    ]

    for name, path in index_paths:
        if path.exists():
            with open(path, 'r') as f:
                indexes[name] = json.load(f)

    return indexes

def _search_indexes(self, query: str) -> List:
    results = []

    # Search across all three indexes
    for tier_name, index in self.search_indexes.items():
        # Add tier prefix to paths
        tier_prefix = {'language': 'common/language/', ...}.get(tier_name)

        # Search keywords, aliases, titles...
        for file_info in index['files']:
            results.append((tier_label, tier_prefix + path, title, desc))

    return results
```

### After: Pre-Built Index Loading

```python
def _load_search_indexes(self) -> Dict:
    """Load pre-built merged search index for this UI."""
    merged_index_path = self.help_root / 'ui/tk/merged_index.json'

    if merged_index_path.exists():
        with open(merged_index_path, 'r') as f:
            return json.load(f)

    return {'files': []}

def _search_indexes(self, query: str) -> List:
    results = []
    query_lower = query.lower()

    # Merged index has everything pre-built
    for file_info in self.search_indexes['files']:
        # Check if query matches (paths already have tier prefixes)
        if (query_lower in file_info.get('title', '').lower() or
            query_lower in file_info.get('description', '').lower() or
            any(query_lower in kw for kw in file_info.get('keywords', []))):

            # Path is already correct (no prefix needed)
            # Tier is already labeled
            results.append((tier_label, path, title, desc))

    return results
```

### Benefits

1. **Simpler code**: No runtime merging logic
2. **Faster startup**: Load one file instead of three
3. **Correct paths**: Paths are pre-validated and correct
4. **Better search**: Can search all fields (keywords, type, category)

## Integration with CI/CD

### When to Build

Build help indexes:

1. **Before commits**: When help content changes
2. **In CI pipeline**: Validate on pull requests
3. **Before releases**: Ensure no broken links ship

### Git Workflow

```bash
# After editing help files
python3 utils/build_docs.py

# Check for errors
echo $?  # Should be 0

# Commit both content and indexes
git add docs/help/
git commit -m "Update help content and rebuild indexes"
```

### GitHub Actions Example

```yaml
name: Validate Help System

on: [pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Validate help indexes
        run: python3 utils/build_docs.py --validate-only
```

## Maintenance

### Adding New Help Files

1. Create markdown file with YAML front matter
2. Add to appropriate tier's `search_index.json`
3. Run `python3 utils/build_docs.py`
4. Verify build succeeds
5. Commit both the file and updated merged indexes

### Fixing Broken Links

When the build reports broken links:

1. Check the reported path
2. Fix the link in the source markdown
3. Run `python3 utils/build_docs.py`
4. Verify error is gone
5. Commit the fix

### Adding New UI

To add help support for a new UI:

1. Create `docs/help/ui/newui/` directory
2. Create `docs/help/ui/newui/search_index.json`
3. Add UI to `build_help_indexes.py`:
   ```python
   uis = ['tk', 'curses', 'newui']  # Add here
   ```
4. Update UI code to load `ui/newui/merged_index.json`

## Implementation Files

### Core Build Scripts

- **`utils/build_help_indexes.py`** (312 lines)
  - Merges three-tier indexes
  - Validates file existence
  - Validates all markdown links
  - Generates merged indexes per UI

- **`utils/build_docs.py`** (218 lines)
  - Coordinates all documentation builds
  - Runs help index builder
  - Optionally runs mkdocs for web
  - Provides unified interface

### UI Updates

- **`src/ui/tk_help_browser.py`**
  - `_load_search_indexes()`: Now loads merged index
  - `_search_indexes()`: Simplified search logic
  - Removed `_find_file_info()` (no longer needed)

- **`src/ui/help_widget.py`** (Curses)
  - `_load_search_indexes()`: Now loads merged index
  - `_search_indexes()`: Simplified search logic
  - Removed `_find_file_info()` (no longer needed)

## Statistics

### Index Sizes

- **Tk UI**: 113 indexed topics
  - 108 language topics
  - 4 MBASIC topics
  - 1 UI-specific topic

- **Curses UI**: 119 indexed topics
  - 108 language topics
  - 4 MBASIC topics
  - 7 UI-specific topics

### Validation Coverage

- ✅ All 113 Tk index paths validated
- ✅ All 119 Curses index paths validated
- ✅ All internal markdown links validated
- ✅ Anchor fragments handled correctly

## Future Enhancements

### Possible Improvements

1. **Incremental builds**: Only rebuild indexes if source files changed
2. **Link verification**: Check external URLs (optional)
3. **Content validation**: Verify front matter completeness
4. **Search optimization**: Pre-compute search rankings
5. **Alias support**: Build alias map at build time
6. **Related topics**: Pre-compute related topic lists

### Web UI Integration

When Web UI gets help support:

1. Add `docs/help/ui/web/search_index.json`
2. Add 'web' to build script's UI list
3. Web UI loads `ui/web/merged_index.json`
4. Same validation and reliability benefits

## Testing

### Automated Tests

```bash
# Test index structure and search functionality
python3 -c "
import json
from pathlib import Path

# Load merged index
with open('docs/help/ui/curses/merged_index.json') as f:
    index = json.load(f)

print(f'Loaded {len(index[\"files\"])} topics')

# Test search would work
query = 'print'
matches = [f for f in index['files']
           if query in f.get('title', '').lower()]
print(f'Search \"{query}\": {len(matches)} results')
"
```

### Manual Testing

1. Run MBASIC with Curses UI
2. Press `/` to search
3. Type "print" - should see results
4. Press Enter to navigate to help topic
5. Verify topic loads correctly
6. Test links within topics work

## See Also

- [HELP_INDEXING_SPECIFICATION.md](HELP_INDEXING_SPECIFICATION.md) - Front matter schema
- [HELP_SYSTEM_REORGANIZATION.md](HELP_SYSTEM_REORGANIZATION.md) - Three-tier structure
- [HELP_SYSTEM_WEB_DEPLOYMENT.md](HELP_SYSTEM_WEB_DEPLOYMENT.md) - Web documentation
