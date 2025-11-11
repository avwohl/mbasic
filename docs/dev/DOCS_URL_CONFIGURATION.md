# Documentation URL Configuration

## Overview

MBASIC UIs can access help documentation from multiple sources:
- **Production**: GitHub Pages (https://avwohl.github.io/mbasic/help/) - default
- **Local Development**: Local docs server or file access

## Configuration

### Default Behavior

By default, all UIs use the GitHub Pages documentation:
- **URL**: `https://avwohl.github.io/mbasic/help/`
- **No setup required**: Works out of the box for end users

### Local Development Override

For local documentation development, set the `MBASIC_DOCS_URL` environment variable:

```bash
# Use local MkDocs server
export MBASIC_DOCS_URL="http://localhost:8000/help/"
python3 mbasic --ui web

# Use different port
export MBASIC_DOCS_URL="http://localhost:8001/help/"
python3 mbasic --ui tk
```

### Starting Local Documentation Server

```bash
# Start MkDocs development server
cd /home/wohl/cl/mbasic
mkdocs serve

# Or specify port
mkdocs serve --dev-addr localhost:8001
```

The server runs at `http://localhost:8000/` by default, with help docs at `/help/`.

## Implementation

### Centralized Configuration

All documentation URLs are managed in `src/docs_config.py`:

```python
from src.docs_config import get_docs_url, DOCS_BASE_URL

# Get URL for specific topic
url = get_docs_url("common/statements/print", ui_type="cli")

# Get base URL
base = DOCS_BASE_URL  # Uses env var or GitHub Pages default
```

### UI-Specific Behavior

**Web-based UIs** (web, help browser):
- Use `get_docs_url()` to fetch documentation from URL
- Automatically use GitHub Pages or `MBASIC_DOCS_URL` override

**Local UIs** (curses, tk):
- Use `get_local_docs_path()` to read markdown files directly from `docs/help/`
- Faster and works offline
- Still use web URLs for "Open in Browser" features

## Files Modified

### Core Configuration
- `src/docs_config.py` - NEW: Centralized configuration module

### Updated for GitHub Pages
- `src/ui/web_help_launcher.py` - Now uses `docs_config.py`
- `src/ui/web/nicegui_backend.py` - Updated help and library URLs

### Unchanged (Use Local Files)
- `src/ui/help_widget.py` - Curses UI reads local markdown
- `src/ui/tk_help_browser.py` - Tk UI reads local markdown

## Testing

### Test GitHub Pages (Default)
```bash
# Should open https://avwohl.github.io/mbasic/help/
python3 mbasic --ui web
# Click Help > Help Topics
```

### Test Local Override
```bash
# Terminal 1: Start local docs server
mkdocs serve

# Terminal 2: Run MBASIC with override
export MBASIC_DOCS_URL="http://localhost:8000/help/"
python3 mbasic --ui web
# Click Help > Help Topics - should open localhost
```

### Test Offline (Local Files)
```bash
# Curses and Tk UIs work offline with local docs
python3 mbasic --ui curses
# Press Ctrl+H for help - reads docs/help/ files directly
```

## Benefits

1. **End Users**: Documentation works out-of-the-box via GitHub Pages
2. **Developers**: Can test documentation changes locally before publishing
3. **Offline**: Curses and Tk UIs work without internet
4. **Consistency**: Single configuration point for all UIs

## Environment Variables Summary

| Variable | Purpose | Default |
|----------|---------|---------|
| `MBASIC_DOCS_URL` | Override documentation base URL | `https://avwohl.github.io/mbasic/help/` |

## Related Files

- `src/docs_config.py` - Configuration module
- `mkdocs.yml` - User documentation build configuration
- `mkdocs-dev.yml` - Developer documentation build configuration
- `.github/workflows/docs.yml` - GitHub Pages deployment workflow
