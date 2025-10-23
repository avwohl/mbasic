# Utility Scripts

This directory contains utility scripts for developing and testing the MBASIC interpreter.

## Analysis Tools

### `analyze_end_statements.py`
Analyzes END statement usage across all BASIC test files.
- Scans all `.bas` files in the `basic/` directory
- Reports which files have END statements and which don't
- Helps identify programs that may run indefinitely

### `analyze_errors.py`
Analyzes error messages and patterns in BASIC programs.
- Parses BASIC files and collects error information
- Groups errors by type
- Useful for debugging parser and interpreter issues

### `analyze_token_usage.py`
Analyzes token usage statistics across the BASIC corpus.
- Counts usage of each token type in test files
- Generates statistics about language feature usage
- Helps identify most/least common BASIC features

## File Organization Tools

### `categorize_files.py`
Categorizes BASIC files based on parsing success and file characteristics.
- Tests each file to see if it parses correctly
- Identifies test files (filenames containing 'test')
- Moves files to appropriate subdirectories:
  - `basic/` - Working programs
  - `basic/bas_tests/` - Test files
  - `basic/bad_syntax/` - Files with syntax errors
- Interactive mode: asks for confirmation before moving files

### `find_duplicates.py`
Finds duplicate BASIC files by content hash.
- Calculates MD5 hash of each file
- Groups files with identical content
- Reports both exact duplicates and case variants
- Shows file distribution statistics

### `remove_duplicates.py`
Removes duplicate BASIC files intelligently.
- Uses priority scoring to keep the best version:
  - Prefers files in `basic/` root (score: +100)
  - Deprioritizes files in `basic/bas_tests/` (score: -100)
  - Deprioritizes files in `basic/bad_syntax/` (score: -50)
  - Prefers lowercase filenames (score: +10)
- Dry-run mode by default (use `--execute` to actually remove files)
- Reports which files are kept and removed

### `move_tokenized.py`
Moves tokenized BASIC files to appropriate directory.
- Identifies BASIC files with tokenized format
- Organizes files based on their format

## Detokenization Tools

### `detokenizer.py`
Detokenizes MBASIC binary format files.
- Converts tokenized BASIC files to ASCII text
- Supports MBASIC 5.21 token format
- Can be used as a library or standalone tool

### `detokenize_all.py`
Batch detokenizes all files in a directory.
- Processes multiple tokenized files at once
- Uses `detokenizer.py` for the conversion
- Outputs detokenized files with `.bas` extension

## Compression Tools

### `unsqueeze2.py`
Decompresses CP/M "squeezed" files (.BQS format).
- Implements Huffman decompression algorithm
- Handles DLE (Data Link Escape) run-length encoding
- Processes `.bqs` files from the CP/M era
- Note: A C version in `usq2/` directory is more reliable

## Testing Tools

### `run_tests_with_results.py`
Runs BASIC test files that have expected output.
- Located in `basic/tests_with_results/`
- Compares actual output with expected results
- Reports PASS/FAIL for each test
- Useful for regression testing

## Debugging Tools

### `debug_test.py`
Interactive debugging tool for testing BASIC programs.
- Allows step-by-step execution
- Shows variable values and program state
- Useful for troubleshooting interpreter issues

### `show_parse_tree.py`
Displays the abstract syntax tree (AST) for BASIC programs.
- Parses a BASIC file and shows its AST structure
- Helps understand how the parser interprets code
- Useful for debugging parser issues

### `clean_post_end.py`
Cleans code that appears after END statements.
- Removes unreachable code after END
- Helps identify potential issues in BASIC programs
- Can clean files in-place or report findings

## Example Files

### `example.py`
Simple example demonstrating basic interpreter usage.
- Shows how to load and run a BASIC program
- Demonstrates the interpreter API
- Good starting point for understanding the codebase

### `example_parser.py`
Example demonstrating parser usage.
- Shows how to parse BASIC code into an AST
- Demonstrates the parser API
- Useful for understanding the parsing pipeline

## Usage Examples

### Find and remove duplicates:
```bash
# Find duplicates (no changes made)
python3 utils/find_duplicates.py

# Remove duplicates (dry-run)
python3 utils/remove_duplicates.py

# Remove duplicates (actually delete files)
python3 utils/remove_duplicates.py --execute
```

### Categorize files:
```bash
# Analyze and organize BASIC files
python3 utils/categorize_files.py
```

### Analyze code:
```bash
# Check which files have END statements
python3 utils/analyze_end_statements.py

# Show token usage statistics
python3 utils/analyze_token_usage.py

# Show parse tree for a file
python3 utils/show_parse_tree.py myprogram.bas
```

### Test programs:
```bash
# Run self-checking tests
python3 utils/run_tests_with_results.py
```

## Notes

- Most scripts operate on files in the `basic/` directory
- Scripts follow the convention of not modifying files unless explicitly confirmed or with `--execute` flag
- Error handling is included to prevent data loss
- All scripts can be run from the project root directory
