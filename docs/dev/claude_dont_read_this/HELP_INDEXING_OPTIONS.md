# Help System Indexing Options

Discussion of options for adding search/indexing to the help system.

## Current State

The help system currently supports:
- ✅ Navigation via links (Tab, Enter)
- ✅ Back button (U)
- ✅ Table of contents (index.md files)
- ❌ No text search within help
- ❌ No keyword indexing

## Standard Markdown Approaches

### 1. HTML Comments (Invisible Metadata)

```markdown
<!-- keywords: print output display console -->
# PRINT

Prints text to the screen.
```

**Pros:**
- Invisible to users
- Standard markdown syntax
- Can be parsed by any markdown processor

**Cons:**
- Not standard across tools
- Would need custom parser

### 2. Front Matter (YAML/TOML)

```markdown
---
keywords: [print, output, display, console]
aliases: [PRINT, ?]
category: statements
---

# PRINT

Prints text to the screen.
```

**Pros:**
- Well-established convention (Jekyll, Hugo, etc.)
- Structured metadata
- Easy to parse

**Cons:**
- Not rendered by basic markdown renderers
- Requires YAML parser

### 3. Heading IDs (Anchors)

```markdown
# PRINT {#stmt-print}

## Syntax {#print-syntax}
```

**Pros:**
- Supports deep linking
- Standard in many markdown flavors

**Cons:**
- Only for navigation, not search keywords
- Currently not parsed by MarkdownRenderer

### 4. Definition Lists

```markdown
Keywords
: print, output, display, console

# PRINT
```

**Pros:**
- Visible to users
- Standard markdown extension

**Cons:**
- Takes up space
- Not semantic metadata

## Recommended Approach: Front Matter + Search Index

### Implementation Plan

**Phase 1: Add Front Matter to Help Files**

```markdown
---
title: PRINT
type: statement
category: input-output
keywords: [print, output, display, console, write, show, ?, question mark]
aliases: [?, PRINT #]
related: [INPUT, WRITE, LPRINT]
---

# PRINT

Prints text to the screen.
```

**Phase 2: Build Search Index**

Create `utils/build_help_index.py`:

```python
#!/usr/bin/env python3
"""
Build searchable index of help files.
"""

import yaml
from pathlib import Path
import json

def extract_front_matter(md_file):
    """Extract YAML front matter from markdown file."""
    with open(md_file) as f:
        content = f.read()

    if not content.startswith('---\n'):
        return None, content

    # Find end of front matter
    end = content.find('\n---\n', 4)
    if end == -1:
        return None, content

    front_matter = content[4:end]
    body = content[end+5:]

    return yaml.safe_load(front_matter), body

def build_index(help_root):
    """Build search index from all help files."""
    index = {
        'files': [],
        'keywords': {},  # keyword -> list of file paths
        'aliases': {},   # alias -> canonical file
    }

    for md_file in Path(help_root).rglob('*.md'):
        rel_path = md_file.relative_to(help_root)

        front_matter, body = extract_front_matter(md_file)
        if not front_matter:
            continue

        # Add file entry
        entry = {
            'path': str(rel_path),
            'title': front_matter.get('title', ''),
            'type': front_matter.get('type', ''),
            'category': front_matter.get('category', ''),
        }
        index['files'].append(entry)

        # Index keywords
        for keyword in front_matter.get('keywords', []):
            keyword_lower = keyword.lower()
            if keyword_lower not in index['keywords']:
                index['keywords'][keyword_lower] = []
            index['keywords'][keyword_lower].append(str(rel_path))

        # Index aliases
        for alias in front_matter.get('aliases', []):
            index['aliases'][alias.upper()] = str(rel_path)

    return index

# Save as JSON
index = build_index('docs/help')
with open('docs/help/search_index.json', 'w') as f:
    json.dump(index, f, indent=2)
```

**Phase 3: Add Search to Help Widget**

Modify `src/ui/help_widget.py`:

```python
class HelpWidget(urwid.WidgetWrap):
    def __init__(self, help_root: str, initial_topic: str):
        # Load search index
        index_file = Path(help_root) / 'search_index.json'
        if index_file.exists():
            with open(index_file) as f:
                self.search_index = json.load(f)
        else:
            self.search_index = None

    def keypress(self, size, key):
        if key == '/':  # Start search
            self.show_search_dialog()
            return None
        # ... rest of keypress handling

    def search(self, query):
        """Search help index for query."""
        if not self.search_index:
            return []

        query_lower = query.lower()
        results = set()

        # Exact alias match
        if query.upper() in self.search_index['aliases']:
            results.add(self.search_index['aliases'][query.upper()])

        # Keyword match
        for keyword, files in self.search_index['keywords'].items():
            if query_lower in keyword:
                results.update(files)

        # Title match
        for entry in self.search_index['files']:
            if query_lower in entry['title'].lower():
                results.add(entry['path'])

        return list(results)
```

## Simpler Alternative: grep-based Search

Without modifying help files, could add search via grep:

**Add to help widget:**
- Press `/` to search
- Enter search term
- Use grep to find matches across all help files
- Display list of matching files
- Navigate to selected file

**Implementation:**
```python
def search_help(self, query):
    """Search help files using grep."""
    import subprocess
    result = subprocess.run(
        ['grep', '-i', '-l', query, '-r', self.help_root, '--include=*.md'],
        capture_output=True,
        text=True
    )
    return result.stdout.strip().split('\n')
```

**Pros:**
- No modification to help files needed
- Simple implementation
- Works immediately

**Cons:**
- No keyword expansion
- No relevance ranking
- Full-text search only (may have false positives)

## Recommendation

For **immediate use**: Implement grep-based search
- Press `/` in help to search
- Simple and works with existing files
- Can be added to help_widget.py easily

For **future enhancement**: Add front matter + build index
- More control over search results
- Better UX with aliases and keywords
- Requires updating all help files (can be done incrementally)

## Example Front Matter for Common Files

### Function Example
```yaml
---
title: ABS
type: function
category: mathematical
keywords: [abs, absolute, value, magnitude]
returns: number
arguments: [number]
related: [SGN, INT, FIX]
---
```

### Statement Example
```yaml
---
title: PRINT
type: statement
category: input-output
keywords: [print, output, display, console, write, show, ?, question mark]
aliases: [?]
related: [INPUT, WRITE, PRINT#, LPRINT]
---
```

### Implementation Note Example
```yaml
---
title: PEEK
type: function
category: system
keywords: [peek, memory, read, address, compatibility]
status: compatibility
implementation: returns random value
related: [POKE, INP, RANDOMIZE]
---
```

## Next Steps

1. Decide on approach (grep vs front matter)
2. If grep: Add search to help_widget.py
3. If front matter:
   - Add front matter to existing help files
   - Create build_help_index.py script
   - Add search to help_widget.py
   - Update help navigation docs

## See Also

- `src/ui/help_widget.py` - Current help implementation
- `src/ui/markdown_renderer.py` - Markdown parsing
