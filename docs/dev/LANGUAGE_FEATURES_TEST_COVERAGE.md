# MBASIC Language Features Test Coverage

**Generated:** 2025-10-29
**Purpose:** Map .bas test files to language features to identify testing gaps

## Summary Statistics

- **Total .bas test files:** 84 files in tests/ directory
- **Total Python test files:** 133 files (50+ in tests/, others in subdirectories)
- **Test categories:** Parser, Lexer, Interpreter, Semantic, UI, Integration

---

## Language Feature Coverage Matrix

### Core Language Statements

| Feature | Statement | Test Files | Coverage | Notes |
|---------|-----------|------------|----------|-------|
| **Variables** | LET, implicit assignment | test_let.bas, test_implicit_let.bas | ✅ Good | |
| **Output** | PRINT | test_print_only.bas, printsep.bas | ✅ Good | |
| **Output Formatting** | PRINT USING | test_print_using.sh, prtusing.bas | ✅ Good | |
| **Input** | INPUT, LINE INPUT | test_input.bas, testinp.bas | ✅ Good | |
| **Arrays** | DIM, array access | test_simple_array.bas, test_array_*.bas | ✅ Good | |
| **OPTION BASE** | OPTION BASE 0/1 | test_optbase*.bas (5 files) | ✅ Excellent | Multiple edge cases |
| **Loops - FOR** | FOR/NEXT | test_for_*.bas, multiple files | ✅ Good | |
| **Loops - WHILE** | WHILE/WEND | test_while_*.bas | ✅ Good | |
| **Subroutines** | GOSUB/RETURN | test_gosub_return.py, gosubmax.bas | ✅ Good | Stack limits tested |
| **Branching** | GOTO | test_goto_into_while.bas | ⚠️ Partial | Edge cases |
| **Conditionals** | IF/THEN/ELSE | Multiple indirect tests | ⚠️ Partial | No dedicated tests |
| **Error Handling** | ON ERROR GOTO | test_err_var.bas, test_resume*.bas | ✅ Good | |
| **RESUME** | RESUME, RESUME NEXT | test_resume.bas, test_resume2.bas, test_resume3.bas | ✅ Excellent | |
| **Functions** | DEF FN | test_def_fn_*.bas (5 files) | ✅ Excellent | Various syntaxes |
| **Program Control** | END, STOP, SYSTEM | test_end_*.py | ✅ Good | |
| **Program Control** | CONT | test_continue*.sh | ✅ Good | |
| **Line Management** | DELETE, RENUM | regression tests | ✅ Good | |
| **Data Statements** | DATA, READ, RESTORE | ❌ Missing | No tests found | **GAP** |
| **ON GOTO/GOSUB** | ON x GOTO/GOSUB | ❌ Missing | No dedicated tests | **GAP** |
| **String Functions** | LEN, MID$, LEFT$, RIGHT$ | teststr.bas | ⚠️ Partial | Limited coverage |
| **Math Functions** | SIN, COS, TAN, etc. | mathtest.bas, mathcomp.bas | ⚠️ Partial | |
| **Type Conversion** | STR$, VAL, INT, etc. | type_suffix_test.bas | ⚠️ Partial | |
| **File I/O** | OPEN, CLOSE, PRINT#, INPUT# | testfile*.bas, testeof*.bas | ⚠️ Partial | |
| **Random Access** | FIELD, GET, PUT | test_field_var.bas | ⚠️ Minimal | |
| **CHAIN** | CHAIN, COMMON | test_chain_case_preservation.py | ⚠️ Partial | |

### Advanced Features

| Feature | Description | Test Files | Coverage | Notes |
|---------|-------------|------------|----------|-------|
| **Multi-statement lines** | : separator | Multiple files use it | ✅ Good | Well tested |
| **Recursion** | Recursive GOSUB | recurse.bas, test_recurse.bas | ✅ Good | |
| **Stack limits** | GOSUB depth | gosubmax.bas, stacktst.bas | ✅ Good | stk*.bas files |
| **Circle algorithms** | Graphics simulation | circ*.bas (6 files) | ✅ Good | Algorithm testing |
| **Case handling** | Upper/lower case | test_case_*.py | ✅ Excellent | Multiple tests |
| **Breakpoints** | Debug features | test_breakpoint*.* | ✅ Excellent | Many test files |
| **Variable tracking** | Debug features | test_variable_tracking.* | ✅ Good | |
| **Input sanitization** | Clean input | test_input_sanitization.py | ✅ Good | |
| **Parser robustness** | Syntax errors | test_parser*.py | ✅ Good | |

---

## Test File Categories

### 1. Unit Tests (Python)
- **Parser tests:** test_parser.py, test_parser_corpus.py
- **Lexer tests:** test_lexer.py
- **Semantic analysis:** semantic/test_*.py (30+ files)
- **Optimizer tests:** Various semantic tests

### 2. Integration Tests (BASIC)
- **Algorithm tests:** circ*.bas (circle drawing)
- **Math tests:** mathtest.bas, mathcomp.bas
- **Stack tests:** stk*.bas, stacktst.bas
- **I/O tests:** test*.bas, print*.bas

### 3. UI Tests
- **Breakpoint UI:** test_breakpoint_*.py
- **Curses UI:** test_curses_*.bas
- **Help system:** test_help_*.sh

### 4. Edge Cases
- **GOTO into structures:** test_goto_into_while.bas
- **Mixed loops:** test_for_while_mix.bas, test_while_for_mix.bas
- **Error recovery:** test_resume*.bas
- **Case conflicts:** test_case_conflict_*.py

---

## Testing Gaps Identified

### Critical Gaps (Core Features)
1. **DATA/READ/RESTORE** - No test files found
2. **ON GOTO/ON GOSUB** - No dedicated tests
3. **IF/THEN/ELSE** - No dedicated test file (only indirect)
4. **SELECT CASE** - Not implemented/tested

### Moderate Gaps (Important Features)
1. **String manipulation** - Limited function coverage
2. **Math functions** - Basic tests only
3. **File I/O** - Minimal coverage
4. **Graphics statements** - No PSET, LINE, CIRCLE tests
5. **Sound statements** - No BEEP, SOUND tests

### Minor Gaps (Nice to Have)
1. **SWAP statement** - Not tested
2. **RANDOMIZE** - Limited testing
3. **PEEK/POKE** - Not applicable but not tested
4. **Time/Date functions** - Not tested

---

## Recommendations

### Immediate Priority
Create test files for:
1. `test_data_read.bas` - Test DATA, READ, RESTORE
2. `test_on_goto.bas` - Test ON x GOTO/GOSUB
3. `test_if_then_else.bas` - Comprehensive IF testing
4. `test_string_functions.bas` - All string functions

### Medium Priority
1. Expand math function tests
2. Add comprehensive file I/O tests
3. Create string manipulation test suite
4. Test all built-in functions systematically

### Low Priority
1. Graphics command stubs (even if not implemented)
2. Sound command stubs
3. Memory command stubs (PEEK/POKE)

---

## Test Organization Recommendations

### Current Structure (Good)
```
tests/
├── regression/     # Regression tests by component
├── semantic/       # Optimizer and analysis tests
├── debug/          # Debug feature tests
├── manual/         # Manual test procedures
└── *.bas          # Integration test programs
```

### Suggested Additions
```
tests/
├── language/       # Language feature tests
│   ├── statements/ # Each statement type
│   ├── functions/  # Built-in functions
│   └── operators/  # Operator tests
└── coverage/       # Coverage reports
```

---

## Coverage Metrics

### Well-Tested Features (>80% coverage)
- Variables and assignment
- Basic I/O (PRINT, INPUT)
- FOR/NEXT loops
- GOSUB/RETURN
- Error handling
- Breakpoints and debugging
- OPTION BASE

### Moderately Tested (40-80% coverage)
- WHILE loops
- File I/O
- String operations
- Math operations
- GOTO statements

### Poorly Tested (<40% coverage)
- DATA/READ/RESTORE
- ON GOTO/GOSUB
- Advanced string functions
- Graphics commands
- Sound commands

---

## Next Steps

1. **Create missing test files** for critical gaps
2. **Run coverage analysis** with actual metrics
3. **Update this document** as tests are added
4. **Create test automation** to run all .bas files
5. **Generate coverage reports** automatically

---

**Note:** This analysis is based on file names and brief content inspection. Actual coverage may vary based on test implementation details.