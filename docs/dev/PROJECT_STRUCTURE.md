# Project Structure

```
mbasic/
├── mbasic                 # Main entry point (interpreter)
├── src/
│   ├── lexer.py              # Tokenizer (shared by interpreter & compilers)
│   ├── parser.py             # Parser - generates AST (shared)
│   ├── ast_nodes.py          # AST node definitions (shared)
│   ├── tokens.py             # Token types (shared)
│   ├── semantic_analyzer.py  # Type checking and analysis (compilers)
│   ├── codegen_backend.py    # Code generation to C (Z80/8080 compiler)
│   ├── codegen_js_backend.py # Code generation to JavaScript (JS compiler)
│   ├── runtime.py            # Runtime state management (interpreter)
│   ├── interpreter.py        # Main interpreter
│   ├── basic_builtins.py     # Built-in functions (interpreter)
│   ├── interactive.py        # Interactive REPL
│   └── ui/                   # UI backends (cli, curses, tk, web)
├── test_compile/
│   ├── test_compile.py       # Compiler test script
│   ├── mb25_string.h/.c      # String runtime library for compiled code
│   └── test_*.bas            # Compiler test programs
├── basic/
│   ├── dev/                  # Development and test programs
│   │   ├── bas_tests/            # BASIC test programs
│   │   ├── tests_with_results/   # Self-checking BASIC tests
│   │   └── bad_syntax/           # Programs with parse errors
│   ├── games/                # Game programs
│   ├── utilities/            # Utility programs
│   └── ...                   # Other categorized programs
├── tests/
│   ├── regression/           # Automated regression tests
│   ├── manual/               # Manual verification tests
│   └── run_regression.py     # Test runner
├── docs/
│   ├── user/                 # User documentation
│   ├── dev/                  # Developer documentation (includes compiler docs)
│   └── help/                 # In-UI help system content
└── utils/                    # Development utilities
```
