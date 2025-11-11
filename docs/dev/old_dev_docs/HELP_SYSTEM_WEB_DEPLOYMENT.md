# Help System Web Deployment Considerations

## Overview

The three-tier help system is designed to work both in-UI (CLI, Curses, Tk) **and** on the web as static documentation. This document discusses what changes or additions are needed for web deployment.

## Current Design: Already Web-Compatible

The help system markdown files are **already web-ready**:

✅ **Standard Markdown**: All files use GitHub-flavored markdown
✅ **Relative Links**: Navigation uses relative paths (`.md` or `../`)
✅ **No Special Syntax**: No UI-specific markup or directives
✅ **Hierarchical Structure**: Logical directory organization
✅ **Index Files**: Each directory has `index.md` as entry point

## Web Deployment Options

### Option 1: GitHub Pages (Simplest)

**What it is**: GitHub automatically renders markdown as HTML

**Setup**:
```yaml
# .github/workflows/pages.yml (if using Actions)
# Or just enable Pages in repo settings → /docs folder
```

**Pros**:
- ✅ Zero configuration
- ✅ Automatic rendering
- ✅ GitHub handles hosting
- ✅ Works immediately

**Cons**:
- ⚠️ Basic styling only
- ⚠️ Limited customization
- ⚠️ No search functionality
- ⚠️ `.md` extensions in URLs

**Changes needed**: None! Works as-is.

### Option 2: MkDocs (Recommended)

**What it is**: Static site generator specifically for documentation

**Setup**:
```bash
pip install mkdocs mkdocs-material
```

**Configuration** (`mkdocs.yml` in repo root):
```yaml
site_name: MBASIC Documentation
site_url: https://avwohl.github.io/mbasic/
repo_url: https://github.com/avwohl/mbasic

theme:
  name: material
  palette:
    scheme: slate
  features:
    - navigation.tabs
    - navigation.sections
    - navigation.expand
    - search.suggest
    - search.highlight

nav:
  - Home: README.md
  - Getting Started: INSTALL.md

  - User Guide:
    - Overview: docs/help/mbasic/index.md
    - Getting Started: docs/help/mbasic/getting-started.md
    - Architecture: docs/help/mbasic/architecture.md
    - Features: docs/help/mbasic/features.md
    - Examples: docs/help/mbasic/examples/index.md

  - Language Reference:
    - Overview: docs/help/language/index.md
    - Statements: docs/help/language/statements/index.md
    - Functions: docs/help/language/functions/index.md
    - Operators: docs/help/language/operators.md
    - Appendices: docs/help/language/appendices/index.md

  - UI Guides:
    - CLI: docs/help/ui/cli/index.md
    - Curses: docs/help/ui/curses/index.md
    - Tkinter: docs/help/ui/tk/index.md

  - Developer:
    - Status: docs/dev/STATUS.md
    - Design: docs/design/future_compiler/README.md

plugins:
  - search
  - awesome-pages  # Auto-discover pages

markdown_extensions:
  - admonition
  - codehilite
  - toc:
      permalink: true
  - pymdownx.superfences
  - pymdownx.tabbed
  - pymdownx.tasklist
```

**Deployment**:
```bash
# Build
mkdocs build

# Deploy to GitHub Pages
mkdocs gh-deploy
```

**Pros**:
- ✅ Beautiful, professional styling
- ✅ Built-in search
- ✅ Navigation sidebar
- ✅ Responsive design
- ✅ Code syntax highlighting
- ✅ Clean URLs (no `.md` extensions)
- ✅ Automatic link resolution

**Cons**:
- ⚠️ Requires mkdocs.yml configuration
- ⚠️ Extra build step
- ⚠️ Dependency on Python package

**Changes needed**: Add `mkdocs.yml` configuration file

### Option 3: Docusaurus (Modern, Feature-Rich)

**What it is**: Facebook's documentation site generator (React-based)

**Setup**:
```bash
npx create-docusaurus@latest docs-site classic
```

**Pros**:
- ✅ Modern, fast UI
- ✅ Versioning support
- ✅ i18n support
- ✅ Advanced search (Algolia)
- ✅ React components in markdown

**Cons**:
- ⚠️ Node.js dependency
- ⚠️ More complex setup
- ⚠️ Different directory structure expected

**Changes needed**: Restructure for Docusaurus conventions

### Option 4: Jekyll (GitHub Pages Default)

**What it is**: Ruby-based static site generator, GitHub Pages' default

**Setup**:
```yaml
# _config.yml
title: MBASIC Documentation
theme: jekyll-theme-slate
```

**Pros**:
- ✅ Native GitHub Pages integration
- ✅ Many themes available
- ✅ Good GitHub integration

**Cons**:
- ⚠️ Ruby dependency for local builds
- ⚠️ Less modern than alternatives
- ⚠️ Slower build times

**Changes needed**: Add `_config.yml`

## Recommended Approach: MkDocs Material

**Why**: Best balance of features, ease of use, and professional appearance.

### Implementation Plan

#### 1. Add Configuration

Create `mkdocs.yml`:
```yaml
site_name: MBASIC 5.21 Documentation
site_description: MBASIC-80 Interpreter for Modern Systems
site_author: MBASIC Team
site_url: https://avwohl.github.io/mbasic/

repo_name: avwohl/mbasic
repo_url: https://github.com/avwohl/mbasic
edit_uri: edit/main/

theme:
  name: material
  palette:
    # Light mode
    - media: "(prefers-color-scheme: light)"
      scheme: default
      primary: indigo
      accent: indigo
      toggle:
        icon: material/brightness-7
        name: Switch to dark mode
    # Dark mode
    - media: "(prefers-color-scheme: dark)"
      scheme: slate
      primary: indigo
      accent: indigo
      toggle:
        icon: material/brightness-4
        name: Switch to light mode

  features:
    - navigation.tabs
    - navigation.sections
    - navigation.expand
    - navigation.top
    - search.suggest
    - search.highlight
    - content.code.copy
    - content.action.edit

nav:
  - Home: README.md
  - Install: INSTALL.md

  - User Guide:
    - Getting Started: docs/help/mbasic/getting-started.md
    - Architecture: docs/help/mbasic/architecture.md
    - Features: docs/help/mbasic/features.md
    - Compatibility: docs/help/mbasic/compatibility.md
    - Not Implemented: docs/help/mbasic/not-implemented.md
    - File Formats: docs/help/mbasic/file-formats.md
    - Examples: docs/help/mbasic/examples/index.md

  - Language Reference:
    - Overview: docs/help/language/index.md
    - Operators: docs/help/language/operators.md
    - Statements: docs/help/language/statements/index.md
    - Functions: docs/help/language/functions/index.md
    - Appendices:
      - Error Codes: docs/help/language/appendices/error-codes.md
      - ASCII Table: docs/help/language/appendices/ascii-codes.md
      - Math Functions: docs/help/language/appendices/math-functions.md

  - UI Guides:
    - CLI Interface: docs/help/ui/cli/index.md
    - Curses (Terminal): docs/help/ui/curses/index.md
    - Tkinter (GUI): docs/help/ui/tk/index.md

  - Developer Documentation:
    - Status: docs/dev/STATUS.md
    - Compiler Design: docs/design/future_compiler/README.md
    - Optimizations: docs/design/future_compiler/README_OPTIMIZATIONS.md

plugins:
  - search:
      lang: en
  - awesome-pages

markdown_extensions:
  - admonition
  - attr_list
  - codehilite:
      guess_lang: false
  - toc:
      permalink: true
  - pymdownx.arithmatex
  - pymdownx.betterem:
      smart_enable: all
  - pymdownx.caret
  - pymdownx.critic
  - pymdownx.details
  - pymdownx.emoji:
      emoji_index: !!python/name:materialx.emoji.twemoji
      emoji_generator: !!python/name:materialx.emoji.to_svg
  - pymdownx.highlight
  - pymdownx.inlinehilite
  - pymdownx.keys
  - pymdownx.magiclink
  - pymdownx.mark
  - pymdownx.smartsymbols
  - pymdownx.superfences
  - pymdownx.tabbed:
      alternate_style: true
  - pymdownx.tasklist:
      custom_checkbox: true
  - pymdownx.tilde
```

#### 2. Add Build Script

Create `build_docs.sh`:
```bash
#!/bin/bash
# Build documentation for web deployment

echo "Building MBASIC documentation..."

# Install MkDocs if needed
if ! command -v mkdocs &> /dev/null; then
    echo "Installing MkDocs..."
    pip install mkdocs mkdocs-material mkdocs-awesome-pages-plugin
fi

# Build the site
mkdocs build

echo "Documentation built to site/"
echo "To preview: mkdocs serve"
echo "To deploy: mkdocs gh-deploy"
```

#### 3. Add GitHub Actions Workflow

Create `.github/workflows/docs.yml`:
```yaml
name: Deploy Documentation

on:
  push:
    branches:
      - main
    paths:
      - 'docs/**'
      - 'mkdocs.yml'
      - 'README.md'
      - 'INSTALL.md'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.x'

      - name: Install dependencies
        run: |
          pip install mkdocs mkdocs-material mkdocs-awesome-pages-plugin

      - name: Build and deploy
        run: |
          mkdocs gh-deploy --force
```

#### 4. Update .gitignore

Add to `.gitignore`:
```
# MkDocs
site/
```

## Changes to Help Files

### Minimal Changes Needed

The good news: **very few changes needed!**

#### 1. Link Syntax (Optional Enhancement)

**Current** (works in-UI and on web):
```markdown
See [PRINT statement](../../language/statements/print.md)
```

**Enhanced for web** (also works in-UI):
```markdown
See [PRINT statement](../../language/statements/print.md)
<!-- MkDocs will convert to: /language/statements/print/ -->
```

**No changes required** - MkDocs handles `.md` links automatically.

#### 2. Add Metadata (Optional)

Add front matter for better web presentation:

```markdown
---
title: PRINT Statement
description: Output text and values to the screen
keywords: [print, output, display, console]
---

# PRINT

Prints text to the screen.
...
```

**Note**: Front matter is optional and doesn't affect in-UI rendering.

#### 3. Cross-Tier Links

**Current**:
```markdown
See [MBASIC Features](../../mbasic/features.md)
```

**Enhanced with explicit context** (future):
```markdown
See [MBASIC Features](mbasic:features.md)
```

**For web**: Would need preprocessor to convert `context:path` to relative paths.

**Recommendation**: Keep using relative paths for now (works everywhere).

## Navigation Structure

### In-UI Navigation
```
Curses UI Index
├── 📘 Curses UI Guide
│   ├── Getting Started
│   └── Keyboard Commands
├── 📗 MBASIC Interpreter
│   ├── Getting Started
│   └── Features
└── 📕 Language Reference
    ├── Statements
    └── Functions
```

### Web Navigation (MkDocs)
```
MBASIC Documentation
├── Home
├── Install
├── User Guide
│   ├── Getting Started
│   ├── Architecture
│   ├── Features
│   └── Examples
├── Language Reference
│   ├── Statements (63)
│   ├── Functions (40)
│   └── Appendices
├── UI Guides
│   ├── CLI Interface
│   ├── Curses (Terminal)
│   └── Tkinter (GUI)
└── Developer Documentation
```

**Key difference**: Web adds top-level "User Guide" grouping for MBASIC implementation docs.

## Search Functionality

### In-UI Search

**Current**: None (manual navigation only)

**Proposed** (from HELP_INDEXING_OPTIONS.md):
- grep-based search (immediate)
- YAML front matter + index (future)

### Web Search

**MkDocs**: Built-in full-text search
- Automatic indexing
- Instant client-side search
- Search suggestions
- Keyboard shortcuts

**Example**:
```
User types "/print" → Finds:
- PRINT statement
- PRINT USING statement
- PRINT# statement
- LPRINT statement
```

## Required Changes Summary

### Immediate (for basic web deployment)

1. ✅ **No changes to help files** - markdown works as-is
2. 🆕 **Add mkdocs.yml** - configuration file
3. 🆕 **Add .github/workflows/docs.yml** - auto-deployment
4. 🆕 **Update .gitignore** - ignore `site/` directory

### Optional Enhancements

1. ⭐ **Add front matter** - metadata for better SEO
2. ⭐ **Add images/diagrams** - visual aids (already have some)
3. ⭐ **Add landing page** - custom index.md for web
4. ⭐ **Add navigation footer** - "Next/Previous" links

### Future Improvements

1. 🔮 **Algolia search** - advanced search with typo tolerance
2. 🔮 **Versioning** - docs for different MBASIC versions
3. 🔮 **i18n support** - multilingual documentation
4. 🔮 **Interactive examples** - embedded BASIC interpreter (WebAssembly?)

## Directory Structure Impact

### Current Three-Tier Structure
```
docs/help/
├── language/       # Tier 1: Language Reference
├── mbasic/         # Tier 2: MBASIC Implementation
└── ui/             # Tier 3: UI-Specific
```

**For web**: This structure is **perfect**!

Each tier becomes a top-level navigation section.

### Additional Web-Specific Content

Create `docs/web/` for web-only content:
```
docs/web/
├── index.md        # Landing page (not in-UI)
├── about.md        # Project info
├── contributing.md # Contribution guide
└── changelog.md    # Release history
```

**Why separate**: Content that doesn't make sense in-UI help browser.

## Testing Web Deployment

### Local Preview
```bash
# Install MkDocs
pip install mkdocs mkdocs-material

# Serve locally
mkdocs serve

# View at http://127.0.0.1:8000
```

### Build Check
```bash
# Build to site/ directory
mkdocs build

# Check for broken links
mkdocs build --strict
```

### Deploy to GitHub Pages
```bash
# Deploy (pushes to gh-pages branch)
mkdocs gh-deploy

# View at https://avwohl.github.io/mbasic/
```

## Benefits of Web + In-UI Strategy

### Shared Content
✅ Write once, use everywhere
✅ Single source of truth
✅ Same markdown files for both

### Better Discovery
✅ Search engines index web docs
✅ Easy to share links
✅ Accessible without installing

### Enhanced Experience
✅ Web: Search, navigation, mobile-friendly
✅ In-UI: Context-sensitive, offline, integrated

### Maintenance
✅ One set of files to maintain
✅ Automatic deployment on push
✅ Version control via git

## Recommendations

### Immediate Action

1. **Add MkDocs configuration** - Enable web deployment now
2. **Enable GitHub Pages** - Free hosting
3. **Add auto-deploy workflow** - Automatic updates

### Content Organization

1. **Keep three-tier structure** - Perfect for both web and in-UI
2. **Use relative links** - Works everywhere
3. **Add optional front matter** - Better web SEO, doesn't hurt in-UI

### Future Enhancements

1. **Add search to in-UI help** - Match web experience
2. **Add interactive examples** - Web-based BASIC playground
3. **Add video tutorials** - Web-only content
4. **Add API documentation** - For developers extending MBASIC

## Conclusion

**Good news**: The three-tier help system design is **already web-compatible**!

**Required changes**: Minimal (just add MkDocs config)

**Benefits**:
- Professional documentation website
- Full-text search
- Mobile-friendly
- Automatic deployment
- Same content as in-UI help

**No breaking changes to existing structure or files needed.**

The help system works equally well embedded in applications and deployed on the web.
