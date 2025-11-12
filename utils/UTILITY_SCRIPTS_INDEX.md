# Utility Scripts Index

**Purpose:** Quick reference for finding existing utility scripts before writing new ones.

## Script Categories

### Error Logging & Analysis

- **`view_error_logs.py`** - View and analyze web UI error logs from MySQL database
  - `python3 utils/view_error_logs.py` - Show recent errors
  - `python3 utils/view_error_logs.py --summary` - Show error statistics
  - `python3 utils/view_error_logs.py --unexpected` - Show only unexpected errors
  - `python3 utils/view_error_logs.py --session ID` - Filter by session
  - `python3 utils/view_error_logs.py --detail ID` - Show full error details
  - `python3 utils/view_error_logs.py --clear` - Clear old logs (>30 days)

### BASIC Code Fixing/Preprocessing

- **`fix_keyword_spacing.py`** - Fixes missing spaces after BASIC keywords
  - Handles: `FORI=1TO10` → `FOR I=1 TO 10`
  - Handles: `IFK9>T9` → `IF K9>T9`
  - Handles: `NEXTI` → `NEXT I`
  - Handles: `GOTO980` → `GOTO 980`
  - Use before importing old BASIC programs

- **`clean_post_end.py`** - Removes code after END statements
  - Cleans up unreachable code
  - MBASIC stops at END

- **`clean_pdf_artifacts.py`** - Removes PDF conversion artifacts from BASIC files
  - Fixes line wrapping issues
  - Removes page headers/footers

### Tokenization/Detokenization

- **`detokenizer.py`** - Convert tokenized BASIC to ASCII
  - Handles Microsoft BASIC tokenized format

- **`detokenize_all.py`** - Batch detokenize multiple files

- **`unsqueeze2.py`** - Unsqueeze compressed BASIC programs
  - Handles squeezed/compressed formats

- **`move_tokenized.py`** - Move tokenized files to separate directory

### Analysis Tools

- **`analyze_errors.py`** - Analyze parser/lexer errors across files
  - Categorizes error types
  - Identifies common issues

- **`analyze_end_statements.py`** - Find code after END statements
  - Identifies unreachable code

- **`analyze_token_usage.py`** - Analyze token usage in BASIC programs
  - Statistics on keyword usage

- **`categorize_files.py`** - Categorize BASIC files by type/dialect

- **`find_duplicates.py`** - Find duplicate BASIC programs
  - Identifies copies with different names

- **`find_microsoft_refs.py`** - Find Microsoft BASIC specific features

- **`find_gosub_limit.py`** - Test GOSUB stack depth limits

- **`extract_statements.py`** - Extract all statements from BASIC programs
  - For documentation generation

- **`extract_functions.py`** - Extract all functions from BASIC programs
  - For documentation generation

### Testing Tools

- **`run_tests_with_results.py`** - Run tests and capture results

- **`debug_test.py`** - Debug specific test cases

- **`show_parse_tree.py`** - Display parse tree for BASIC program
  - Visual debugging of parser

- **`tick_api_demo.py`** - Demo of tick-based execution API

- **`gen_compact_stack.py`** - Generate test for compact stack usage

- **`gen_deep_stack.py`** - Generate test for deep stack usage

### Compilation/Build Tools

- **`check_z88dk.py`** - Check if z88dk compiler is properly installed
  - Verifies z88dk.zcc is in PATH
  - Tests if compiler is accessible via /usr/bin/env
  - Provides installation suggestions if not found
  - Use before compiling BASIC to CP/M executables

- **`check_tnylpo.py`** - Check if tnylpo CP/M emulator is properly installed
  - Verifies tnylpo is in PATH
  - Tests if emulator is accessible via /usr/bin/env
  - Tests basic CP/M program execution
  - Provides build instructions if not found
  - Use before running compiled .COM files

- **`check_compiler_tools.py`** - Check entire compiler toolchain at once
  - Runs both check_z88dk.py and check_tnylpo.py
  - Shows summary of what's installed
  - Indicates if toolchain is ready for compilation/testing
  - Convenient single check for all requirements

### Documentation Tools

- **`check_docs_consistency.py`** - Analyze docs for inconsistencies using Claude API
  - Finds license conflicts, missing references, outdated info
  - Requires: `pip install anthropic` and ANTHROPIC_API_KEY env var
  - Generates report in `utils/docs_inconsistencies_report.md`
  - Cross-analyzes all findings to identify patterns
  - Groups issues by severity (high/medium/low)

- **`check_docs_consistency1.py`** - Limited scope documentation consistency checker
  - Scans only help, library, stylesheets, user directories
  - Finds documentation inconsistencies
  - Generates report in `utils/docs_inconsistencies_report1.md`

- **`check_docs_consistency2.py`** - Enhanced consistency checker for code AND documentation
  - Analyzes Python source files (.py) and JSON files (.json)
  - Scans src/, utils/, tests/ directories before docs/
  - Detects code vs comment conflicts (outdated comments, code bugs)
  - Interactive mode: asks for clarification when conflicts are unclear
  - Identifies documentation vs implementation mismatches
  - Generates comprehensive report in `utils/consistency_report2.md`
  - Requires: `pip install anthropic` and ANTHROPIC_API_KEY env var

- **`regenerate_see_also_sections.py`** - Auto-generate "See Also" sections in help docs
  - Reads category metadata from all function/statement docs
  - Generates cross-references based on categories
  - Removes "not yet documented" placeholders
  - Run after adding new functions/statements or changing categories
  - Ensures 100% documentation cross-referencing

- **`build_help_indexes.py`** - Build help system search indexes
  - Run after modifying docs/help/

- **`build_library_docs.py`** - Generate games library documentation
  - Reads docs/library/games.json metadata
  - Generates docs/library/games/index.md
  - Copies .bas files from source to docs/library/games/
  - Run before deploying documentation

- **`build_docs.py`** - Build documentation

- **`check_help_links.py`** - Verify help documentation links

- **`add_frontmatter.py`** - Add YAML frontmatter to markdown files

- **`enhance_metadata.py`** - Enhance metadata in documentation

- **`fix_function_formatting.py`** - Fix function documentation formatting

- **`frontmatter_utils.py`** - Utilities for YAML frontmatter

### File Format Conversion

- **`convert_eol_to_lf.py`** - Convert BASIC files to Unix LF line endings
  - Converts CRLF (\r\n) → LF (\n)
  - Converts CR (\r) → LF (\n)
  - Processes all .bas files in basic/ directory

- **`convert_docs_eol_to_lf.py`** - Convert docs/ files to Unix LF line endings
  - Converts .md, .txt, .bas, .json, .sh, .py, .pl, .css files
  - Skips .pdf (binary) and .mac (need CRLF for CP/M M80 assembler)

- **`convert_to_cpm.py`** - Convert files to CP/M format (CRLF + EOF marker)
  - Converts LF (\n) → CRLF (\r\n)
  - Adds CP/M EOF marker (\x1a)
  - Use for transferring files to CP/M emulators (tnylpo, etc.)
  - Usage: `python3 utils/convert_to_cpm.py input.bas [output.bas]`

### Duplicate/Cleanup

- **`remove_duplicates.py`** - Remove duplicate BASIC files
  - Use after find_duplicates.py

### Example Programs

- **`example.py`** - Example MBASIC program runner

- **`example_parser.py`** - Example of using the parser directly

## Usage Examples

### Fixing Old BASIC Programs
```bash
# Fix keywords running together
python3 utils/fix_keyword_spacing.py basic/program.bas

# Clean code after END
python3 utils/clean_post_end.py basic/program.bas

# Remove PDF artifacts
python3 utils/clean_pdf_artifacts.py basic/converted.bas
```

### Analyzing Programs
```bash
# Find parsing errors
python3 utils/analyze_errors.py basic/*.bas

# Show parse tree
python3 utils/show_parse_tree.py basic/program.bas

# Find duplicates
python3 utils/find_duplicates.py basic/
```

### Working with Tokenized Files
```bash
# Detokenize a file
python3 utils/detokenizer.py tokenized.bas > ascii.bas

# Batch detokenize
python3 utils/detokenize_all.py

# Unsqueeze compressed file
python3 utils/unsqueeze2.py squeezed.bas > normal.bas
```

## When to Use Which Script

**Before importing BASIC programs:**
1. `unsqueeze2.py` - If compressed
2. `detokenizer.py` - If tokenized
3. `fix_keyword_spacing.py` - If from old BASIC dialect
4. `clean_pdf_artifacts.py` - If converted from PDF
5. `clean_post_end.py` - To remove unreachable code

**When debugging parser issues:**
1. `analyze_errors.py` - Identify error patterns
2. `show_parse_tree.py` - Visualize parsing
3. `analyze_token_usage.py` - Check token patterns

**For documentation:**
1. `build_help_indexes.py` - After editing help files
2. `check_help_links.py` - Verify documentation

## Adding New Scripts

When creating new utility scripts:
1. Place in `utils/` directory
2. Add docstring explaining purpose
3. Update this index
4. Consider if existing script could be extended instead

## Notes

- Many scripts support `--dry-run` to preview changes
- Most scripts can process single files or directories
- Check script docstrings for specific options