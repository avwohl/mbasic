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
- `README.md` - Main project documentation (root)
- Other docs in root directory

## Code Style
- Python 3 with type hints where appropriate
- Use pathlib for file operations when possible
- Include docstrings for functions
- Add comments explaining complex logic

## Testing
- Test files should be in `basic/bas_tests/`
- Use MBASIC 5.21 syntax only
- Test both successful parsing and error cases
