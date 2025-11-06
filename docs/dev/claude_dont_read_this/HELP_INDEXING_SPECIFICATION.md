# Help System Indexing Specification

**Status**: RECOMMENDED APPROACH - Use YAML front matter
**Date**: 2025-10-25

## Decision: YAML Front Matter

After analyzing all deployment targets (CLI, Curses, Tk, Web), **YAML front matter** is the best solution.

### Why YAML Front Matter?

✅ **Works everywhere**:
- MkDocs: Native support, uses metadata for SEO, search
- GitHub: Renders correctly (ignores front matter)
- Python parsers: Easy to extract with `python-frontmatter` package
- In-UI help: Can be hidden or displayed as needed

✅ **Industry standard**:
- Jekyll, Hugo, MkDocs all use it
- Well-documented, widely understood
- Mature tooling ecosystem

✅ **Structured and extensible**:
- Clear key-value pairs
- Easy to add new fields
- Type-safe (lists, strings, booleans)

✅ **Future-proof**:
- Supports versioning
- Can add custom fields
- Doesn't break if parser doesn't support it

## Front Matter Schema

### Required Fields (All Files)

```yaml
---
title: String        # Display title (may differ from filename)
type: String         # content type: statement|function|guide|reference
---
```

### Optional Fields (Contextual)

```yaml
---
# Categorization
category: String              # Primary category
subcategory: String           # Optional subcategory
tags: [String, ...]          # Free-form tags for search

# Search & Discovery
keywords: [String, ...]       # Search keywords (including synonyms)
aliases: [String, ...]        # Alternative names (?, PRINT#, etc.)
description: String           # One-line summary (for search results)

# Language-Specific (Tier 1)
syntax: String                # BASIC syntax (if simple one-liner)
returns: String               # Return type (for functions)
arguments: [String, ...]      # Argument list (for functions)
related: [String, ...]        # Related topics (filenames without .md)

# Implementation-Specific (Tier 2)
status: String                # implemented|partial|compatibility|not-implemented
since: String                 # Version when added (1.0, 2.0, etc.)
compatibility: String         # Notes about MBASIC 5.21 compatibility

# UI-Specific (Tier 3)
ui: String                    # cli|curses|tk|visual
shortcuts: [String, ...]      # Keyboard shortcuts
---
```

## Front Matter by Content Type

### Language Reference - Statements

**Example**: `docs/help/language/statements/print.md`

```yaml
---
title: PRINT
type: statement
category: input-output
keywords: [print, output, display, console, write, show, ?, question mark]
aliases: ["?"]
description: Output text and values to the screen
syntax: "PRINT [expression[;|,]...]"
related: [input, print-using, lprint, write]
---

# PRINT

## Syntax

```basic
PRINT [<list of expressions>]
```

...
```

### Language Reference - Functions

**Example**: `docs/help/language/functions/abs.md`

```yaml
---
title: ABS
type: function
category: mathematical
keywords: [abs, absolute, value, magnitude, math]
description: Returns the absolute value of a number
syntax: "ABS(X)"
returns: number
arguments: [number]
related: [sgn, int, fix]
---

# ABS

## Syntax

```basic
ABS(X)
```

...
```

### Language Reference - Functions (Not Implemented)

**Example**: `docs/help/language/functions/inp.md`

```yaml
---
title: INP
type: function
category: hardware
keywords: [inp, input, port, io, hardware]
description: Read byte from I/O port (not implemented)
syntax: "INP(port)"
returns: number
arguments: [port]
status: not-implemented
compatibility: Cannot access hardware ports from Python interpreter
related: [out, peek, poke]
---

# INP

## Implementation Note

⚠️ **Not Implemented**: This feature requires direct hardware I/O port access...
```

### MBASIC Implementation Docs

**Example**: `docs/help/mbasic/architecture.md`

```yaml
---
title: MBASIC Architecture
type: guide
category: implementation
keywords: [architecture, interpreter, compiler, semantic analyzer, optimization]
description: Overview of MBASIC's interpreter and compiler architecture
tags: [internals, design, performance]
related: [features, optimizations, compatibility]
---

# MBASIC Architecture: Interpreter and Compiler
...
```

### UI-Specific Docs

**Example**: `docs/help/ui/curses/keyboard-commands.md`

```yaml
---
title: Keyboard Commands
type: reference
category: ui-controls
ui: curses
keywords: [keyboard, shortcuts, commands, keys, ctrl, hotkeys]
description: Complete keyboard command reference for the Curses UI
tags: [ui, controls, navigation]
shortcuts: [Ctrl+H, Ctrl+R, Ctrl+A, Ctrl+S, Ctrl+L]
---

# Keyboard Commands
...
```

## Minimal vs Complete Front Matter

### Minimal (Required Only)

For simple pages, just title and type:

```yaml
---
title: Hello World Example
type: guide
---
```

### Complete (All Fields)

For language reference (statements/functions):

```yaml
---
title: FOR-NEXT
type: statement
category: control-flow
subcategory: loops
keywords: [for, next, loop, iteration, counter]
description: Execute statements repeatedly with a loop counter
syntax: "FOR var = start TO end [STEP increment]"
related: [while-wend, goto, on-goto]
tags: [loops, control-flow, iteration]
---
```

## Implementation Plan

### Phase 1: Add Parser (Now)

**Install dependency**:
```bash
pip install python-frontmatter
```

**Add to `requirements.txt`**:
```
python-frontmatter>=1.0.0
```

**Create parser utility** (`utils/frontmatter_utils.py`):

```python
#!/usr/bin/env python3
"""
Utilities for parsing YAML front matter in markdown files.
"""

import frontmatter
from pathlib import Path
from typing import Dict, List, Optional

def parse_markdown_file(file_path: Path) -> Dict:
    """
    Parse markdown file with YAML front matter.

    Returns:
        {
            'metadata': dict,    # YAML front matter
            'content': str,      # Markdown content
            'path': Path         # File path
        }
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        post = frontmatter.load(f)

    return {
        'metadata': dict(post.metadata),
        'content': post.content,
        'path': file_path
    }

def build_search_index(help_root: Path) -> Dict:
    """
    Build search index from all markdown files with front matter.

    Returns:
        {
            'files': [
                {
                    'path': 'language/statements/print.md',
                    'title': 'PRINT',
                    'type': 'statement',
                    'keywords': [...],
                    ...
                }
            ],
            'keywords': {
                'print': ['language/statements/print.md', ...],
                ...
            },
            'aliases': {
                '?': 'language/statements/print.md',
                ...
            },
            'categories': {
                'input-output': ['language/statements/print.md', ...],
                ...
            }
        }
    """
    index = {
        'files': [],
        'keywords': {},
        'aliases': {},
        'categories': {},
        'by_type': {}
    }

    for md_file in help_root.rglob('*.md'):
        if md_file.name == 'index.md':
            continue  # Skip index files

        try:
            parsed = parse_markdown_file(md_file)
            metadata = parsed['metadata']

            if not metadata:
                continue  # No front matter

            rel_path = md_file.relative_to(help_root)
            rel_path_str = str(rel_path)

            # Add to files list
            file_entry = {
                'path': rel_path_str,
                'title': metadata.get('title', ''),
                'type': metadata.get('type', ''),
                'category': metadata.get('category', ''),
                'description': metadata.get('description', ''),
            }
            index['files'].append(file_entry)

            # Index keywords
            for keyword in metadata.get('keywords', []):
                keyword_lower = keyword.lower()
                if keyword_lower not in index['keywords']:
                    index['keywords'][keyword_lower] = []
                index['keywords'][keyword_lower].append(rel_path_str)

            # Index aliases
            for alias in metadata.get('aliases', []):
                index['aliases'][alias.upper()] = rel_path_str

            # Index by category
            category = metadata.get('category', '')
            if category:
                if category not in index['categories']:
                    index['categories'][category] = []
                index['categories'][category].append(rel_path_str)

            # Index by type
            doc_type = metadata.get('type', '')
            if doc_type:
                if doc_type not in index['by_type']:
                    index['by_type'][doc_type] = []
                index['by_type'][doc_type].append(rel_path_str)

        except Exception as e:
            print(f"Error parsing {md_file}: {e}")

    return index

def search_help(query: str, index: Dict) -> List[str]:
    """
    Search help index for query.

    Returns list of matching file paths.
    """
    query_lower = query.lower()
    results = set()

    # Exact alias match (highest priority)
    if query.upper() in index['aliases']:
        results.add(index['aliases'][query.upper()])

    # Keyword match
    for keyword, files in index['keywords'].items():
        if query_lower in keyword:
            results.update(files)

    # Title match
    for entry in index['files']:
        if query_lower in entry['title'].lower():
            results.add(entry['path'])

    # Description match
    for entry in index['files']:
        if query_lower in entry.get('description', '').lower():
            results.add(entry['path'])

    return list(results)

def get_related_topics(file_path: str, help_root: Path) -> List[Dict]:
    """
    Get related topics for a file based on its front matter.

    Returns list of related file metadata.
    """
    full_path = help_root / file_path
    parsed = parse_markdown_file(full_path)
    metadata = parsed['metadata']

    related_names = metadata.get('related', [])
    related_files = []

    for name in related_names:
        # Try to find file matching name
        # Could be in same directory or need to search
        parent_dir = full_path.parent

        # Try same directory first
        candidate = parent_dir / f"{name}.md"
        if candidate.exists():
            related_parsed = parse_markdown_file(candidate)
            related_files.append({
                'path': str(candidate.relative_to(help_root)),
                'title': related_parsed['metadata'].get('title', name),
                'description': related_parsed['metadata'].get('description', '')
            })

    return related_files
```

### Phase 2: Build Index on Startup (In-UI)

**Update `src/ui/help_widget.py`**:

```python
import json
from pathlib import Path
from utils.frontmatter_utils import build_search_index, search_help

class HelpWidget(urwid.WidgetWrap):
    def __init__(self, ui_docs: str, mbasic_docs: str, language_docs: str,
                 initial_topic: str):
        self.contexts = {
            'ui': Path(ui_docs),
            'mbasic': Path(mbasic_docs),
            'language': Path(language_docs)
        }

        # Build search indexes
        self.indexes = {}
        for context, path in self.contexts.items():
            print(f"Building search index for {context}...")
            self.indexes[context] = build_search_index(path)

        # Combined index
        self.combined_index = self._combine_indexes()

        # ... rest of init

    def search(self, query: str) -> List[str]:
        """Search all contexts for query."""
        return search_help(query, self.combined_index)

    def keypress(self, size, key):
        if key == '/':  # Start search
            self.show_search_dialog()
            return None
        # ... rest of keypress handling
```

### Phase 3: Update MkDocs Configuration

**Add to `mkdocs.yml`**:

```yaml
plugins:
  - search:
      lang: en
      indexing: 'full'  # Index all content
  - tags:  # Enable tag plugin
      tags_file: tags.md

# Enable front matter metadata
markdown_extensions:
  - meta  # YAML front matter support
```

MkDocs automatically:
- Extracts front matter
- Uses `title` for page titles
- Uses `description` for meta description (SEO)
- Uses `keywords` for search indexing
- Ignores unknown fields

### Phase 4: Add Front Matter to Existing Files

**Create migration script** (`utils/add_frontmatter.py`):

```python
#!/usr/bin/env python3
"""
Add YAML front matter to existing help files.
"""

import frontmatter
import re
from pathlib import Path
from typing import Dict, Optional

def infer_metadata_from_file(file_path: Path, content: str) -> Dict:
    """
    Infer front matter metadata from file location and content.
    """
    metadata = {}

    # Get title from first heading
    match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    if match:
        metadata['title'] = match.group(1).strip()

    # Infer type from directory structure
    parts = file_path.parts
    if 'statements' in parts:
        metadata['type'] = 'statement'
    elif 'functions' in parts:
        metadata['type'] = 'function'
    elif 'appendices' in parts:
        metadata['type'] = 'reference'
    elif 'ui' in parts:
        metadata['type'] = 'guide'
    elif 'mbasic' in parts:
        metadata['type'] = 'guide'

    # Infer category from directory
    if 'language' in parts:
        if 'statements' in parts:
            # Could categorize by examining content
            # For now, mark as needing manual categorization
            metadata['category'] = 'NEEDS_CATEGORIZATION'
        elif 'functions' in parts:
            metadata['category'] = 'NEEDS_CATEGORIZATION'

    return metadata

def add_frontmatter_to_file(file_path: Path, metadata: Dict,
                            dry_run: bool = True) -> None:
    """
    Add front matter to a markdown file if it doesn't have it.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        post = frontmatter.load(f)

    # If already has front matter, skip
    if post.metadata:
        print(f"✓ {file_path} - already has front matter")
        return

    # Infer metadata from content
    inferred = infer_metadata_from_file(file_path, post.content)

    # Merge with provided metadata
    final_metadata = {**inferred, **metadata}

    # Create new post with front matter
    post.metadata = final_metadata

    if dry_run:
        print(f"Would add to {file_path}:")
        print(f"  {final_metadata}")
    else:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(frontmatter.dumps(post))
        print(f"✓ Added front matter to {file_path}")

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='Add YAML front matter to help files'
    )
    parser.add_argument('path', type=Path, help='Path to help directory')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be done without doing it')

    args = parser.parse_args()

    for md_file in args.path.rglob('*.md'):
        add_frontmatter_to_file(md_file, {}, dry_run=args.dry_run)

if __name__ == '__main__':
    main()
```

**Usage**:
```bash
# Dry run - show what would be done
python3 utils/add_frontmatter.py docs/help/language --dry-run

# Actually add front matter
python3 utils/add_frontmatter.py docs/help/language
```

### Phase 5: Manual Categorization Template

Create categorization guide for manual review:

**`docs/dev/HELP_CATEGORIZATION_GUIDE.md`**:

```markdown
# Help File Categorization Guide

## Statements Categories

- **input-output**: INPUT, PRINT, WRITE, LPRINT
- **control-flow**: IF, FOR, WHILE, GOTO, GOSUB, ON GOTO
- **file-io**: OPEN, CLOSE, FIELD, GET, PUT, INPUT#, PRINT#
- **file-management**: LOAD, SAVE, MERGE, KILL, NAME, RUN
- **data**: DATA, READ, RESTORE
- **arrays**: DIM, ERASE, OPTION BASE
- **variables**: LET, SWAP, DEFINT/SNG/DBL/STR
- **functions**: DEF FN
- **error-handling**: ON ERROR, ERROR, RESUME, ERR/ERL
- **strings**: MID$ (statement form)
- **hardware**: POKE, OUT, CALL, WAIT
- **program-control**: CHAIN, CLEAR, COMMON, CONT, END, NEW, STOP
- **editing**: AUTO, DELETE, EDIT, LIST, LLIST, RENUM
- **system**: NULL, RANDOMIZE, REM, TRON/TROFF, WIDTH

## Functions Categories

- **mathematical**: ABS, ATN, COS, EXP, FIX, INT, LOG, RND, SGN, SIN, SQR, TAN
- **string**: ASC, CHR$, HEX$, INSTR, LEFT$, LEN, MID$, RIGHT$, SPACE$, SPC, STR$, STRING$, VAL
- **type-conversion**: CDBL, CINT, CVD/CVI/CVS, MKD$/MKI$/MKS$
- **file-io**: EOF, INPUT$, LOC, LPOS, LOF, POS
- **system**: FRE, INKEY$, INP, USR, VARPTR, PEEK
```

## File Naming Convention

Filenames should match the BASIC keyword (lowercase, hyphens for spaces):

- `print.md` - PRINT statement
- `for-next.md` - FOR-NEXT loop
- `left_dollar.md` - LEFT$ function
- `mkd_dollar.md` - MKD$ function
- `print-using.md` - PRINT USING statement

## Migration Checklist

- [ ] Install `python-frontmatter` package
- [ ] Add to `requirements.txt`
- [ ] Create `utils/frontmatter_utils.py`
- [ ] Create `utils/add_frontmatter.py`
- [ ] Run dry-run on language/statements
- [ ] Manually categorize statements
- [ ] Add front matter to statements
- [ ] Run dry-run on language/functions
- [ ] Manually categorize functions
- [ ] Add front matter to functions
- [ ] Add front matter to mbasic/ docs (manual)
- [ ] Add front matter to ui/ docs (manual)
- [ ] Update HelpWidget to use search index
- [ ] Update mkdocs.yml to enable metadata
- [ ] Test search in-UI
- [ ] Test search on web
- [ ] Document front matter schema

## Benefits of This Approach

### For In-UI Help

✅ **Fast search**: Pre-built index, instant results
✅ **Alias support**: Type `?` finds PRINT
✅ **Keyword search**: Type "loop" finds FOR, WHILE, etc.
✅ **Category browsing**: Show all "file-io" statements
✅ **Related topics**: Automatic "See Also" links

### For Web (MkDocs)

✅ **SEO**: Meta descriptions, keywords
✅ **Search**: Full-text + keyword search
✅ **Navigation**: Auto-generated sidebar
✅ **Tags**: Automatic tag index
✅ **Clean URLs**: Uses title metadata

### For Maintenance

✅ **Structured**: Clear schema, validation possible
✅ **Extensible**: Add new fields anytime
✅ **Searchable**: Find all files of type X
✅ **Auditable**: Scripts can validate completeness

## Next Steps

1. **Review this specification** - Get feedback
2. **Install dependencies** - python-frontmatter
3. **Create utilities** - frontmatter_utils.py, add_frontmatter.py
4. **Pilot on 5 files** - Test the approach
5. **Categorize statements** - Manual review
6. **Add front matter** - Run migration script
7. **Update HelpWidget** - Implement search
8. **Test and iterate** - Refine as needed

## See Also

- [HELP_INDEXING_OPTIONS.md](HELP_INDEXING_OPTIONS.md) - Original analysis
- [HELP_SYSTEM_WEB_DEPLOYMENT.md](HELP_SYSTEM_WEB_DEPLOYMENT.md) - Web deployment
- [HELP_SYSTEM_REORGANIZATION.md](HELP_SYSTEM_REORGANIZATION.md) - Three-tier structure
