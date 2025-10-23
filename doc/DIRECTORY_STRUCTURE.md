# MBASIC 5.21 Compiler - Directory Structure

## Overview
This document describes the organization of the MBASIC 5.21 compiler project.

## Directory Structure

```
mbasic/
├── basic/              # BASIC source files and test corpus
│   ├── bas_tests1/     # Main test corpus (215 MBASIC 5.21 files) ⭐
│   ├── bad_not521/     # Non-MBASIC 5.21 dialect files (20 files)
│   ├── interpreter_vs_compiler.bas  # Example file
│   └── old/            # Archived/unused test directories
│       ├── bas/            # General BASIC files (209 files)
│       ├── bas_other/      # Other BASIC files (114 files)
│       ├── bas_out/        # Detokenized output files (50 files)
│       ├── bas_tests1_other/ # Additional test files (138 files)
│       └── bas_tok/        # Tokenized BASIC files (50 files)
│
├── src/                # Compiler source code ⭐
│   ├── lexer.py        # Lexical analyzer
│   ├── parser.py       # Parser
│   ├── ast_nodes.py    # AST node definitions
│   └── tokens.py       # Token definitions
│
├── utils/              # Utility scripts
│   ├── analyze_errors.py    # Error pattern analysis
│   ├── move_tokenized.py    # File organization
│   ├── detokenize_all.py    # Batch detokenization
│   ├── example.py           # Example usage
│   ├── example_parser.py    # Parser examples
│   └── debug_test.py        # Debug utilities
│
├── tests/              # Test scripts and results
│   ├── test_*.py            # Test scripts
│   └── test_*.txt           # Test output files
│
├── doc/                # Documentation (*.md files)
│   ├── SESSION_*.md         # Session summaries
│   ├── *_FIX.md             # Implementation notes
│   ├── *_IMPLEMENTATION.md  # Feature documentation
│   └── README.md            # Main documentation
│
├── bin/                # Binary/executable files
└── com/                # CP/M .COM files

```

## Key Files

### Core Compiler (src/)
- **src/lexer.py** - Tokenizes BASIC source code
- **src/parser.py** - Parses tokens into Abstract Syntax Tree
- **src/ast_nodes.py** - Defines AST node structures
- **src/tokens.py** - Token type definitions and keyword mappings

### Utilities (utils/)
- **utils/analyze_errors.py** - Analyzes parser error patterns
- **utils/move_tokenized.py** - Organizes tokenized BASIC files
- **utils/detokenize_all.py** - Batch detokenizes BASIC files
- **utils/example.py** - Example lexer usage
- **utils/example_parser.py** - Example parser usage

### Test Suite
- **tests/test_all_bas_detailed.py** - Comprehensive test runner
- **tests/test_bas_files.py** - Basic file testing
- **tests/test_lexer.py** - Lexer unit tests
- **tests/test_parser.py** - Parser unit tests

### Documentation
- **doc/README.md** - Main project documentation
- **doc/FAILURE_CATEGORIZATION.md** - Analysis of remaining parse failures
- **doc/SESSION_*.md** - Session summaries with progress tracking
- **doc/*_IMPLEMENTATION.md** - Feature implementation notes

## Test Corpus

### basic/bas_tests1/ (215 files)
Clean MBASIC 5.21 test corpus. Files verified to be MBASIC 5.21 dialect.

**Current Status**: 104/215 files (48.4%) parsing successfully

### basic/bas_not51/ (20 files)
Programs identified as non-MBASIC 5.21 dialects:
- Atari BASIC (TRAP, SETCOLOR, GRAPHICS)
- Applesoft BASIC (VTAB, HTAB)
- Kaypro BASIC (WINDOW, WSELECT)
- Files with C-style escape sequences (\t, \n, \a)

## Running Tests

All test scripts should be run from the project root directory:

```bash
# Comprehensive test
python3 tests/test_all_bas_detailed.py

# Basic file test
python3 tests/test_bas_files.py

# Unit tests
python3 tests/test_lexer.py
python3 tests/test_parser.py
```

## Development Workflow

1. Edit compiler source files in `src/` directory
2. Run comprehensive tests: `python3 tests/test_all_bas_detailed.py`
3. Document changes in `doc/` directory
4. Commit with descriptive message

## Import Structure

All test and utility scripts use:
```python
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))
```

This adds the `src/` directory to the Python path, allowing imports like:
```python
from lexer import tokenize, LexerError
from parser import parse, ParseError
from ast_nodes import *
from tokens import TokenType
```

## Notes

- Compiler source code is in `src/` directory
- Utility scripts are in `utils/` directory
- Test scripts are in `tests/` directory
- All scripts automatically configure Python path to find compiler modules
- Documentation is in `doc/` directory

## Directory Details

### Active Directories

#### basic/bas_tests1/ (215 files) ⭐ ACTIVE
The primary test corpus for MBASIC 5.21 parser development.

**Status**: 104/215 files (48.4%) parsing successfully

**Contents**: Clean MBASIC 5.21 programs verified to be the correct dialect. This is the ONLY directory used for parser testing.

**Usage**: Referenced by `tests/test_all_bas_detailed.py`

#### basic/bad_not521/ (20 files)
Programs identified and moved out of the test corpus because they use non-MBASIC 5.21 features.

**Contents**:
- Atari BASIC: TRAP, SETCOLOR, GRAPHICS, PLOT statements
- Applesoft BASIC: VTAB, HTAB statements
- Kaypro BASIC: WINDOW, WSELECT statements
- Programs with C-style escape sequences: \t, \n, \a

**Purpose**: Reference for what was filtered out; helps avoid false positive test results

### Archived Directories (basic/old/)

These directories are no longer actively used for testing but are kept for reference.

#### basic/old/bas/ (209 files)
General collection of BASIC files. Likely duplicates or subset of bas_tests1.

#### basic/old/bas_other/ (114 files)
Another collection of BASIC files, purpose unclear.

#### basic/old/bas_out/ (50 files)
ASCII text files - output from detokenization process. These are detokenized versions of files from bas_tok/.

#### basic/old/bas_tok/ (50 files)
Binary tokenized BASIC files. These are the tokenized (binary) format of BASIC programs.

#### basic/old/bas_tests1_other/ (138 files)
Additional test files not in the main test corpus.

### Cleanup Recommendations

The old/ directories can likely be deleted if:
1. bas_tests1/ contains all needed test files (✓ confirmed - 215 files)
2. No unique programs exist in old/ that aren't in bas_tests1/
3. Tokenization/detokenization functionality is tested elsewhere

**Note**: Before deletion, verify no unique test cases exist in old/ directories.
