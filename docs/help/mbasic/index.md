---
title: MBASIC Interpreter Documentation
type: guide
category: mbasic
keywords:
- mbasic
- interpreter
- implementation
- documentation
- index
description: Main index for MBASIC interpreter documentation
---

# MBASIC Interpreter Documentation

Documentation for the MBASIC 5.21 interpreter implementation.

## Getting Started

- **[Getting Started Guide](getting-started.md)** - Installation, first steps, and quick start
- **[Features](features.md)** - Complete list of interpreter capabilities
- **[Compatibility Guide](compatibility.md)** - MBASIC 5.21 compatibility and differences

## Implementation Details

- **[Architecture](architecture.md)** - Interpreter design, compiler backend, and optimizations
- **[String Allocation and Garbage Collection](implementation/string-allocation-and-garbage-collection.md)** - How CP/M MBASIC managed string memory

## For Developers

Looking to understand or modify the MBASIC interpreter?

- **Design Documents:** `docs/dev/` - Implementation notes and design decisions
- **Project Rules:** `.claude/CLAUDE.md` - Development guidelines
- **Installation Guide:** `docs/dev/INSTALLATION_FOR_DEVELOPERS.md` - Developer setup

## Quick Links

### By Topic

**Installation & Setup**
- [Getting Started](getting-started.md) → Installation instructions
- [Compatibility](compatibility.md) → What works, what doesn't

**Using MBASIC**
- [Features](features.md) → What you can do
- [UI Guides](../ui/curses/index.md) → How to use the interface

**Language Reference**
- [Statements](../common/language/statements/index.md) → BASIC-80 statements
- [Functions](../common/language/functions/index.md) → Built-in functions
- [Operators](../common/language/operators.md) → Arithmetic, logical, relational

**Advanced Topics**
- [Architecture](architecture.md) → How it works
- [File I/O](../common/language/statements/open.md) → Working with files
- [Error Handling](../common/language/statements/on-error-goto.md) → ON ERROR GOTO/RESUME

## About This Implementation

This is a complete Python implementation of MBASIC-80 (MBASIC) version 5.21 for CP/M.

**Key Features:**
- 100% MBASIC 5.21 language compatibility
- Choice of user interfaces (CLI, Curses, Tkinter)
- Advanced semantic analyzer with 18 optimizations
- Cross-platform (Linux, macOS, Windows)
- Zero dependencies for core functionality

**Version Information:**
- **Target compatibility:** MBASIC 5.21 for CP/M
- **Implementation language:** Python 3.8+
- **License:** See project repository

## Documentation Structure

This documentation is organized in three tiers:

1. **📗 MBASIC Implementation** (this section)
   - How to install and use the interpreter
   - What features are supported
   - Compatibility information

2. **📕 BASIC-80 Language Reference** ([Language Docs](../common/language/index.md))
   - Language syntax and semantics
   - Statements and functions
   - Common to all MBASIC interpreters

3. **📘 UI-Specific Guides**
   - Interface-specific help
   - Keyboard shortcuts
   - UI features and workflows

## Contributing

This is an open-source project. For contributing:
- Report issues on GitHub
- Follow coding guidelines in `.claude/CLAUDE.md`
- See developer documentation in `docs/dev/`

## See Also

- **[BASIC-80 Language Reference](../common/language/index.md)** - The BASIC language itself
- **[Curses UI Guide](../ui/curses/index.md)** - Full-screen terminal interface
- **[CLI Guide](../ui/cli/index.md)** - Classic command-line interface
- **[Tk GUI Guide](../ui/tk/index.md)** - Graphical interface
