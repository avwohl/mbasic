# Contributing to MBASIC 5.21 Interpreter

Thank you for your interest in contributing to the MBASIC 5.21 Interpreter project!

## Getting Started

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/yourusername/mbasic.git
   cd mbasic
   ```
3. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
4. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

## Development Workflow

### Running Tests

Run the parser tests:
```bash
cd tests
python3 test_parser_corpus.py
```

Run interpreter tests:
```bash
python3 mbasic.py basic/tests_with_results/test_operator_precedence.bas
```

### Code Style

- Follow PEP 8 style guidelines
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Keep functions focused and concise

### Making Changes

1. Create a new branch for your feature or bugfix:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes

3. Test your changes thoroughly:
   - Run existing tests
   - Test with multiple BASIC programs
   - Test both interactive and file execution modes

4. Commit your changes with a clear message:
   ```bash
   git add .
   git commit -m "Add feature: description of what you added"
   ```

5. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

6. Create a Pull Request on GitHub

## Areas for Contribution

### High Priority

- **More Tests**: Add test cases for edge cases and real-world programs
- **Bug Fixes**: Test existing features and report/fix bugs
- **Documentation**: Improve inline documentation and add more examples
- **Performance**: Optimize interpreter performance

### Medium Priority

- **Platform Testing**: Test on different operating systems (Windows, macOS, Linux)
- **Examples**: Add more example BASIC programs to the corpus
- **Debugging**: Add better error messages and debugging support
- **Compatibility**: Test with more vintage BASIC programs

### Low Priority

- **Extended Features**: Optional features beyond MBASIC 5.21 spec (with compatibility flag)
- **Tools**: Program analysis or conversion utilities

## Code Organization

```
mbasic/
├── mbasic.py              # Main entry point
├── src/
│   ├── lexer.py           # Tokenizer - converts text to tokens
│   ├── parser.py          # Parser - converts tokens to AST
│   ├── ast_nodes.py       # AST node definitions
│   ├── tokens.py          # Token type definitions
│   ├── runtime.py         # Runtime state (variables, arrays, etc.)
│   ├── interpreter.py     # Statement and expression execution
│   ├── basic_builtins.py  # Built-in functions (SIN, COS, etc.)
│   └── interactive.py     # Interactive REPL mode
├── basic/                 # Test programs
├── tests/                 # Test scripts
└── doc/                   # Documentation
```

## Testing Guidelines

- Test with programs from `basic/bas_tests1/`
- Test both interactive and file execution modes
- Test edge cases (empty input, very large numbers, etc.)
- Verify compatibility with MBASIC 5.21 behavior

## Documentation

When adding features:
- Update relevant documentation in `doc/`
- Update README.md if it affects user-facing functionality
- Add examples if applicable
- Document any breaking changes

## Questions?

Feel free to open an issue if you have questions or need clarification on anything.

## Code of Conduct

- Be respectful and constructive
- Focus on the code, not the person
- Help others learn and grow
- Keep discussions on-topic

Thank you for contributing!
