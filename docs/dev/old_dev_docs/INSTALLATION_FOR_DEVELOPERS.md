# Developer Installation Guide

> **⚠️ NOTE:** This is an older, basic setup guide. For comprehensive Linux Mint/Ubuntu/Debian developer setup including compiler tools, web server, and all system packages, see **[../LINUX_MINT_DEVELOPER_SETUP.md](../LINUX_MINT_DEVELOPER_SETUP.md)**.

Complete setup instructions for developing MBASIC on a clean Linux system.

## System Requirements

- **OS**: Linux (Ubuntu/Debian recommended), macOS, or Windows with WSL
- **Python**: 3.8 or later (3.9+ recommended)
- **Git**: Any recent version
- **Disk Space**: ~50MB for repository and dependencies

## Quick Start

```bash
# Clone repository
git clone https://github.com/avwohl/mbasic.git
cd mbasic

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Test installation
python3 mbasic
```

## Detailed Installation

### 1. Install System Dependencies

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv git
```

**macOS (with Homebrew):**
```bash
brew install python3 git
```

**Arch Linux:**
```bash
sudo pacman -S python python-pip git
```

### 2. Clone Repository

```bash
git clone https://github.com/avwohl/mbasic.git
cd mbasic
```

### 3. Set Up Virtual Environment (Recommended)

Using a virtual environment isolates dependencies:

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # Linux/macOS
# OR
venv\Scripts\activate  # Windows
```

**Note**: You'll need to activate the virtual environment each time you work on the project.

### 4. Install Python Dependencies

**Core dependencies** (required):
```bash
pip install -r requirements.txt
```

This installs:
- `urwid>=2.0.0` - Curses UI (optional but recommended)
- `pexpect>=4.8.0` - Automated testing (optional)
- `python-frontmatter>=1.0.0` - Help system indexing

**Web deployment tools** (optional):
```bash
pip install mkdocs mkdocs-material mkdocs-awesome-pages-plugin
```

### 5. Verify Installation

**Test the interpreter:**
```bash
python3 mbasic
```

You should see:
```
MBASIC 5.21

Ok
```

Type `PRINT "Hello"` and press Enter. You should see `Hello` printed.

**Test the curses UI:**
```bash
python3 mbasic --ui curses
```

Press `Ctrl+Q` to exit.

**Run tests:**
```bash
# Test parser on all BASIC programs
python3 utils/test_all_programs.py

# Test curses UI
python3 utils/test_curses_comprehensive.py
```

## Dependency Reference

### Core Dependencies

**None!** The interpreter uses only Python standard library.

### Optional Dependencies

#### UI Backends

**urwid** (Curses UI - Terminal-based IDE):
```bash
pip install urwid>=2.0.0
```

Used by: `python3 mbasic --ui curses`

#### Testing

**pexpect** (Automated UI testing):
```bash
pip install pexpect>=4.8.0
```

Used by: Test scripts in `utils/test_curses_*.py`

#### Help System

**python-frontmatter** (YAML front matter parsing):
```bash
pip install python-frontmatter>=1.0.0
```

Used by:
- `utils/frontmatter_utils.py` - Build search indexes
- `utils/add_frontmatter.py` - Add metadata to help files
- Help system search functionality

#### Web Deployment

**MkDocs** (Static site generator):
```bash
pip install mkdocs>=1.5.0
```

**MkDocs Material** (Theme):
```bash
pip install mkdocs-material>=9.0.0
```

**Awesome Pages Plugin** (Auto-discovery):
```bash
pip install mkdocs-awesome-pages-plugin>=2.8.0
```

Used by:
```bash
mkdocs serve   # Local preview at http://127.0.0.1:8000
mkdocs build   # Build static site to site/
mkdocs gh-deploy  # Deploy to GitHub Pages
```

## Development Workflow

### Daily Workflow

```bash
# Activate virtual environment
source venv/bin/activate

# Make changes to code...

# Test changes
python3 mbasic test_program.bas

# Run tests
python3 utils/test_curses_comprehensive.py

# Commit when done
git add .
git commit -m "Description of changes"
git push
```

### Working with Help System

```bash
# Build help search index
python3 utils/frontmatter_utils.py docs/help/language

# Search help
python3 utils/frontmatter_utils.py docs/help/language --search print

# Add front matter to help files
python3 utils/add_frontmatter.py docs/help/language/statements --dry-run
python3 utils/add_frontmatter.py docs/help/language/statements
```

### Web Documentation

```bash
# Preview documentation website locally
mkdocs serve
# Visit http://127.0.0.1:8000

# Build static site
mkdocs build

# Deploy to GitHub Pages
mkdocs gh-deploy
```

## Troubleshooting

### "No module named 'urwid'"

Install urwid:
```bash
pip install urwid
```

### "No module named 'frontmatter'"

Install python-frontmatter:
```bash
pip install python-frontmatter
```

### Permission denied when running scripts

Make scripts executable:
```bash
chmod +x utils/*.py
```

### Virtual environment not activating

**Linux/macOS:**
```bash
source venv/bin/activate
```

**Windows:**
```bash
venv\Scripts\activate
```

Or use `python3 -m venv venv` to recreate it.

### Tests failing

Make sure you're in the project root directory and have activated the virtual environment:
```bash
cd /path/to/mbasic
source venv/bin/activate
python3 utils/test_curses_comprehensive.py
```

## Additional Tools

### CP/M Emulator (Optional)

To test against real MBASIC 5.21:

**Install tnylpo:**
```bash
# Ubuntu/Debian
sudo apt-get install tnylpo

# Or build from source
git clone https://gitlab.com/gbrault/tnylpo.git
cd tnylpo
make
sudo make install
```

**Usage:**
```bash
cd tests/
(cat test.bas && echo "RUN") | timeout 10 tnylpo ../com/mbasic
```

See `tests/HOW_TO_RUN_REAL_MBASIC.md` for details.

## IDE Setup

### VS Code

Recommended extensions:
- Python (Microsoft)
- BASIC (language support)
- Markdown All in One
- YAML

### PyCharm

Works out of the box. Set interpreter to the virtual environment.

### Vim/Neovim

Add to `.vimrc` or `init.vim`:
```vim
" Python support
autocmd FileType python setlocal expandtab shiftwidth=4 softtabstop=4

" BASIC syntax
autocmd BufRead,BufNewFile *.bas set filetype=basic
```

## Directory Structure

```
mbasic/
├── .claude/           # Claude AI project instructions
├── basic/             # BASIC test programs
├── com/               # CP/M executables (MBASIC 5.21)
├── docs/              # All documentation
│   ├── dev/          # Development documentation
│   ├── help/         # In-UI help system
│   ├── user/         # User guides
│   └── design/       # Architecture and design
├── in/                # Input files for testing
├── src/               # Source code
│   ├── ui/           # UI backends
│   └── ...           # Core interpreter modules
├── tests/             # Test files
├── utils/             # Utility scripts
├── mbasic          # Main interpreter
├── requirements.txt   # Python dependencies
└── README.md          # Project README
```

## Getting Help

- **Documentation**: `docs/` directory
- **Help System**: Press Ctrl+A in curses UI
- **Issues**: https://github.com/avwohl/mbasic/issues
- **Development Guide**: `docs/dev/STATUS.md`

## Next Steps

After installation:

1. **Read the docs**: Start with `README.md` and `docs/dev/STATUS.md`
2. **Try the UIs**: Test CLI and curses interfaces
3. **Run BASIC programs**: Try examples in `basic/` directory
4. **Read help system design**: See `docs/dev/HELP_SYSTEM_REORGANIZATION.md`
5. **Run tests**: Verify everything works

## Summary

**Minimum setup (interpreter only):**
```bash
git clone https://github.com/avwohl/mbasic.git
cd mbasic
python3 mbasic
```

**Full development setup:**
```bash
git clone https://github.com/avwohl/mbasic.git
cd mbasic
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install mkdocs mkdocs-material mkdocs-awesome-pages-plugin
python3 utils/test_curses_comprehensive.py
```

You're ready to develop!
