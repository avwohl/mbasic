# MBASIC Developer Guide Index

Welcome to the MBASIC developer documentation! This index organizes all developer resources by topic.

## Getting Started

- **[Installation for Developers](INSTALLATION_FOR_DEVELOPERS.md)** - How to set up your development environment
- **[Testing Guide](TESTING_GUIDE.md)** - Types of tests and how to run them
- **[Package Dependencies](PACKAGE_DEPENDENCIES.md)** - What packages are used and why

## Architecture & Design

- **[Architecture Overview](../help/mbasic/architecture.md)** - High-level system design
- **[Features](../help/mbasic/features.md)** - Implemented language features
- **[STATUS](STATUS.md)** - Current implementation status

## Development by Component

### Core Interpreter
- **[Parser](../history/PARSER_SUMMARY.md)** - How the parser works
- **[Lexer](../history/TOKEN_LIST_VERIFICATION_2025-10-22.md)** - Tokenization
- **[AST](AST_SERIALIZATION.md)** - Abstract Syntax Tree structure

### User Interfaces
- **[UI Development Guide](UI_DEVELOPMENT_GUIDE.md)** - Developing for each UI backend
  - CLI Development
  - Curses (Terminal) Development
  - TK (Desktop) Development
  - Web (NiceGUI) Development
- **[UI Feature Parity Tracking](UI_FEATURE_PARITY_TRACKING.md)** - What features each UI supports

### File I/O
- **File Operations** - See help/common/language/statements/ for file I/O documentation

### Help System
- **[Help System](HELP_MIGRATION_PLAN.md)** - Documentation and help infrastructure

## Testing

- **[Testing Guide](TESTING_GUIDE.md)** - Comprehensive testing documentation
  - Test types (unit, integration, language, UI, regression)
  - How to run tests
  - How to write tests
  - Test coverage

## Tools & Utilities

- **Utility Scripts Index** - See `utils/UTILITY_SCRIPTS_INDEX.md` in the repository
- **[Debug Mode](DEBUG_MODE.md)** - Using MBASIC_DEBUG for troubleshooting

## Current Work

- **Work in Progress** - Check for WORK_IN_PROGRESS.md if present

## Package Installation & Distribution

- **[Package Dependencies](PACKAGE_DEPENDENCIES.md)** - Understanding what gets installed
- **[Installation Testing TODO](INSTALLATION_TESTING_TODO.md)** - Testing on clean systems

## Historical Documentation

See `docs/history/` for:
- Completed feature implementations
- Design decisions
- Bug fixes
- Session summaries
- Timeline of changes

---

**Note:** This is a living document. As the project evolves, new documentation will be added and organized here.

**Last Updated:** 2025-10-30
