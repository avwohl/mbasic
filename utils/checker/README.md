# Documentation Consistency Checker

Tools for analyzing consistency between code and documentation in the MBASIC project.

## Files

### check_docs_consistency3.py (Latest)
The primary consistency checker that analyzes both source code and documentation.

**Features:**
- Analyzes Python source files (.py) for code vs comment conflicts
- Checks JSON configuration files (.json)
- Scans documentation files (.md) from docs/help, docs/library, docs/stylesheets, docs/user
- Auto-generates versioned output filenames (docs_inconsistencies_report-v{N}.md)
- Saves reports to `../../docs/history/`

**Usage:**
```bash
cd utils/checker
python3 check_docs_consistency3.py
```

**Requirements:**
- ANTHROPIC_API_KEY environment variable must be set
- `pip install anthropic`

**Runtime:** Over 1 hour (due to comprehensive analysis)

**Output:** `../../docs/history/docs_inconsistencies_report-v{N}.md`

### get_next_report_filename.py
Utility module for determining the next available version number for report files.

**Features:**
- Scans `../../docs/history/` for existing report files
- Parses version numbers from filenames matching pattern: `docs_inconsistencies_report-v[0-9]*.md`
- Ignores zero-sized files (incomplete runs)
- Returns next available version number

**Usage:**
```python
from get_next_report_filename import get_next_report_filename
filename = get_next_report_filename()  # Returns: "docs_inconsistencies_report-v11.md"
```

**Test:**
```bash
python3 get_next_report_filename.py
```

### test_filename_picker.py
Test jig for validating the filename picker functionality.

**Usage:**
```bash
python3 test_filename_picker.py
```

**Tests:**
1. Getting next report filename
2. Validating filename format
3. Checking if output file already exists
4. Listing existing report files

### json_extractor.py
Helper module for robust JSON parsing from Claude API responses.

Handles various JSON formats including:
- Pure JSON arrays
- JSON wrapped in markdown code blocks
- Mixed text and JSON responses

### check_docs_consistency2.py (Previous version)
Original version that outputs to hardcoded `consistency_report2.md` filename.

**Note:** Version 3 supersedes this with auto-versioned filenames.

## Report Output

Reports are saved to `../../docs/history/docs_inconsistencies_report-v{N}.md` with sections:

1. **Code vs Comment Conflicts**
   - Code bugs (comment appears correct)
   - Outdated comments (code appears correct)
   - Unclear cases needing investigation

2. **General Inconsistencies**
   - High severity issues
   - Medium severity issues
   - Low severity issues

Each issue includes:
- Affected files
- Description and details
- Severity level
- Suggested fixes

## Version History

- **v3** (check_docs_consistency3.py): Auto-versioned output filenames
- **v2** (check_docs_consistency2.py): Enhanced with code/comment conflict analysis
- **v1** (check_docs_consistency.py): Initial documentation-only checker
