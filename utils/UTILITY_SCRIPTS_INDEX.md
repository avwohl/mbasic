# Utility Scripts Index

**Purpose:** Quick reference for finding existing utility scripts before writing new ones.

## Script Categories

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

### Documentation Tools

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