# Notes for Claude

## Workflow
- Always commit and push changes when you stop to talk to me
- Track all installed dependencies and update documentation

## Developer Setup

### System Requirements
- Python 3.8 or later (3.9+ recommended)
- Git
- pip

### Python Dependencies

Install all dependencies:
```bash
pip install -r requirements.txt
```

**Required dependencies:**
- None (uses Python standard library only)

**Optional UI dependencies:**
- `urwid>=2.0.0` - For curses backend (full-screen terminal UI)

**Development/testing dependencies:**
- `pexpect>=4.8.0` - For automated UI testing

**Help system dependencies:**
- `python-frontmatter>=1.0.0` - For YAML front matter parsing in help files

**Web deployment (optional):**
- `mkdocs>=1.5.0` - Static site generator for documentation
- `mkdocs-material>=9.0.0` - Material theme for MkDocs
- `mkdocs-awesome-pages-plugin>=2.8.0` - Auto-discover pages plugin

Install web deployment tools:
```bash
pip install mkdocs mkdocs-material mkdocs-awesome-pages-plugin
```

### Installation from Clean Linux

```bash
# Clone repository
git clone https://github.com/avwohl/mbasic.git
cd mbasic

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Test installation
python3 mbasic.py

# Optional: Install web deployment tools
pip install mkdocs mkdocs-material mkdocs-awesome-pages-plugin
```

See `docs/dev/INSTALLATION_FOR_DEVELOPERS.md` for complete setup guide.

# MBASIC Project Rules

## File Organization Rules

### Utility Scripts
**ALWAYS put utility scripts in `utils/` directory**
- Python scripts for analysis, testing, debugging, etc.
- Examples: categorize_files.py, find_duplicates.py, analyze_errors.py
- Never create utility scripts in the root directory

### BASIC Program Organization
- `basic/` - Working BASIC programs that parse correctly with MBASIC 5.21
- `basic/bad_syntax/` - Programs with syntax errors or non-MBASIC 5.21 features
- `basic/bas_tests/` - Test programs and test files
- `basic/tests_with_results/` - Test files with expected results

### Source Code
- `mbasic.py` - Main interpreter (root directory)
- Core implementation files in root (parser.py, lexer.py, etc.)

### Input Files
- `in/` - Input files for testing and unsqueezing

### Documentation
**NEVER create documentation files in the root directory!**
All documentation belongs in the `docs/` directory:

- `README.md` - Main project README (root, only exception)
- `docs/` - **ALL documentation goes here**
  - `docs/dev/` - Current development notes and implementation guides
    - Use for: feature implementations, fixes, current status, work-in-progress
    - Examples: `*_IMPLEMENTATION.md`, `*_FIX.md`, `STATUS.md`
  - `docs/help/` - In-UI help system documentation
    - `docs/help/common/` - General help shared across all UIs (language, statements)
    - `docs/help/ui/{backend}/` - UI-specific help (cli, curses, tk, visual)
  - `docs/user/` - External user-facing documentation
    - Use for: quick references, installation guides, tutorials
  - `docs/history/` - Historical/archived development documentation
    - Use for: session logs, completed milestones (move from dev/ when done)
  - `docs/design/` - Architecture and design documents
  - `docs/external/` - External references (PDFs, specifications)

**When creating new documentation:**
- Development notes → `docs/dev/`
- Help content → `docs/help/common/` or `docs/help/ui/{backend}/`
- User guides → `docs/user/`
- Completed sessions → `docs/history/`

## Code Style
- Python 3 with type hints where appropriate
- Use pathlib for file operations when possible
- Include docstrings for functions
- Add comments explaining complex logic

## UI/UX Rules
- **NO FUNCTION KEYS** - User cannot use F1-F12 keys
- Use Ctrl+letter combinations instead (Ctrl+G, Ctrl+T, etc.)
- All keyboard shortcuts must be Ctrl, Alt, or plain keys
- Document all keyboard shortcuts clearly

## Testing

### Testing with Python Implementation
- Test files should be in `basic/bas_tests/`
- Use MBASIC 5.21 syntax only
- Test both successful parsing and error cases
- Run with: `python3 mbasic.py <program.bas>`

### Testing with Real MBASIC 5.21

**IMPORTANT:** To verify behavior against authentic MBASIC 5.21, use the tnylpo CP/M emulator.

**Location:** Real MBASIC 5.21 is at `com/mbasic.com`

**How to run:**
```bash
cd tests/
(cat test.bas && echo "RUN") | timeout 10 tnylpo ../com/mbasic
```

**Critical requirements:**
1. **Must run from `tests/` directory**
2. **Programs must end with `SYSTEM` not `END`**
   - `END` hangs at "Ok" prompt waiting for input
   - `SYSTEM` exits MBASIC cleanly
3. **Keep lines short** (MBASIC has line buffer limits)

**Example test file:**
```basic
10 PRINT "Hello"
20 FOR I = 1 TO 3
30   PRINT I
40 NEXT I
50 SYSTEM
```

**Comparing outputs:**
```bash
cd tests/

# Our implementation
python3 ../mbasic.py test.bas > /tmp/our.txt 2>&1

# Real MBASIC 5.21
(cat test.bas && echo "RUN") | timeout 10 tnylpo ../com/mbasic > /tmp/real.txt 2>&1

# Compare
diff /tmp/our.txt /tmp/real.txt
```

**Full details:** See `tests/HOW_TO_RUN_REAL_MBASIC.md`

### Testing the Curses UI

**IMPORTANT:** The curses UI cannot be tested manually in headless environments. Use the automated testing framework.

**Quick test (recommended):**
```bash
python3 utils/test_curses_comprehensive.py
```

**What it tests:**
- UI creation and initialization
- Input handlers (Ctrl+H, Ctrl+L, Ctrl+N, Ctrl+R, etc.)
- Program parsing from editor
- Program execution with tick-based interpreter
- Process lifecycle (startup/shutdown)

**Exit codes:**
- `0` - All tests passed
- `1` - One or more tests failed (details in output)

**When to use:**
- Before committing changes to curses UI
- After modifying interpreter tick-based execution
- When debugging curses UI issues
- To verify UI works without manual testing

**Available test scripts:**
- `utils/test_curses_comprehensive.py` - Full test suite (use this)
- `utils/test_curses_pexpect.py` - Integration testing only
- `utils/test_curses_pyte.py` - Terminal emulator (experimental)
- `utils/test_curses_urwid_sim.py` - Direct simulation testing

**Full documentation:** See `docs/dev/CURSES_UI_TESTING.md`

**Common errors caught:**
- `loop.draw_screen()` called before loop running
- Missing interpreter initialization
- Input handler exceptions
- Tick execution errors
