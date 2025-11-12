# MBASIC-2025 Documentation

Welcome to the complete documentation for MBASIC-2025, a Python implementation of MBASIC-80 for CP/M.

## What is MBASIC-2025?

MBASIC 5.21 is a classic BASIC dialect from the CP/M era (late 1970s - early 1980s). MBASIC-2025 provides 100% compatibility with MBASIC 5.21 programs while offering modern user interfaces and cross-platform support.

## Quick Links

<div class="grid cards" markdown>

-   :material-rocket-launch:{ .lg .middle } __Getting Started__

    ---

    Install MBASIC and write your first program in minutes

    [:octicons-arrow-right-24: Installation Guide](help/mbasic/getting-started.md)

-   :material-book-open-variant:{ .lg .middle } __Language Reference__

    ---

    Complete BASIC-80 language documentation with all 63 statements and 40 functions

    [:octicons-arrow-right-24: Language Reference](help/common/language/index.md)

-   :material-monitor:{ .lg .middle } __User Interfaces__

    ---

    Choose your interface: Curses (terminal), CLI (command-line), Tkinter (GUI), or Web (browser)

    [:octicons-arrow-right-24: UI Guides](help/ui/index.md)

-   :material-cog:{ .lg .middle } __Implementation Details__

    ---

    Learn about the interpreter architecture, features, and compatibility

    [:octicons-arrow-right-24: MBASIC Docs](help/mbasic/index.md)

-   :material-cogs:{ .lg .middle } __Compiler__

    ---

    Compile BASIC to native CP/M executables - 100% feature complete!

    [:octicons-arrow-right-24: Compiler Guide](help/common/compiler/index.md)

-   :material-gamepad-variant:{ .lg .middle } __Games Library__

    ---

    Browse 113 classic BASIC games from the CP/M era - ready to run!

    [:octicons-arrow-right-24: Games Library](library/games/index.md)

-   :fontawesome-brands-github:{ .lg .middle } __Source Code__

    ---

    View the source, report issues, and contribute on GitHub

    [:octicons-arrow-right-24: GitHub Repository](https://github.com/avwohl/mbasic)

</div>

## Key Features

- ✅ **Two Complete Implementations** - Interactive interpreter AND native code compiler
- ✅ **100% MBASIC 5.21 Compatibility** - Run authentic MBASIC programs unchanged
- ✅ **Generates CP/M Executables** - Compile to native .COM files for 8080 or Z80 processors
- ✅ **Multiple User Interfaces** - CLI, Curses terminal, Tkinter GUI, or Web browser
- ✅ **Cross-Platform** - Linux, macOS, Windows
- ✅ **Zero Dependencies** - Pure Python, no external libraries required for interpreter
- ✅ **Hardware Access** - Full PEEK/POKE/INP/OUT support in compiled code
- ✅ **Complete Documentation** - Comprehensive help for every feature

## Documentation Structure

This documentation is organized into four tiers:

### 1. User Interfaces (📘)

Interface-specific documentation for each UI:

- **[Curses UI](help/ui/curses/index.md)** - Full-screen terminal interface
- **[CLI](help/ui/cli/index.md)** - Classic command-line REPL
- **[Tkinter GUI](help/ui/tk/index.md)** - Graphical interface
- **[Web IDE](help/ui/web/index.md)** - Browser-based interface

### 2. MBASIC Interpreter (📗)

Implementation-specific documentation:

- **[Getting Started](help/mbasic/getting-started.md)** - Installation and first steps
- **[Features](help/mbasic/features.md)** - What's implemented
- **[Compatibility](help/mbasic/compatibility.md)** - Differences from CP/M MBASIC
- **[Architecture](help/mbasic/architecture.md)** - How it works

### 3. MBASIC Compiler (🔧)

Native code compiler documentation:

- **[Compiler Guide](help/common/compiler/index.md)** - Getting started with the compiler
- **[Setup Instructions](https://github.com/avwohl/mbasic/blob/main/docs/dev/COMPILER_SETUP.md)** - Installing z88dk and tools
- **[Feature Status](https://github.com/avwohl/mbasic/blob/main/docs/dev/COMPILER_STATUS_SUMMARY.md)** - 100% complete feature list
- **[CP/M Emulator](https://github.com/avwohl/mbasic/blob/main/docs/dev/TNYLPO_SETUP.md)** - Testing compiled programs

### 4. BASIC-80 Language (📕)

Complete language reference:

- **[Statements](help/common/language/statements/index.md)** - All 63 BASIC-80 statements
- **[Functions](help/common/language/functions/index.md)** - All 40 built-in functions
- **[Operators](help/common/language/operators.md)** - Arithmetic, logical, relational
- **[Appendices](help/common/language/appendices/error-codes.md)** - Error codes, ASCII table

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/avwohl/mbasic.git
cd mbasic

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install optional dependencies
pip install -r requirements.txt
```

### Your First Program

Start the Curses UI:

```bash
mbasic
```

Type your program:

```basic
10 PRINT "Hello, World!"
20 END
```

Press **Ctrl+R** to run!

## Example Programs

### Classic "Hello, World!"

```basic
10 PRINT "Hello, World!"
20 END
```

### FOR Loop

```basic
10 FOR I = 1 TO 10
20   PRINT I; "squared is"; I * I
30 NEXT I
40 END
```

### User Input

```basic
10 INPUT "What is your name"; N$
20 PRINT "Hello, "; N$; "!"
30 END
```

### File I/O

```basic
10 OPEN "O", #1, "output.txt"
20 PRINT #1, "This is a test"
30 CLOSE #1
40 PRINT "File written!"
50 END
```

## Platform Support

- **Linux** - Ubuntu, Debian, Fedora, Arch
- **macOS** - 10.14+
- **Windows** - 10, 11, WSL
- **Python** - 3.8+ (3.10+ recommended)

## Contributing

MBASIC is open source! Contributions are welcome:

- Report issues on [GitHub](https://github.com/avwohl/mbasic/issues)
- Submit pull requests
- Improve documentation
- Share example programs

## License

See the project repository for license information.

---

**Ready to get started?** Head to the [Installation Guide](help/mbasic/getting-started.md) or browse the [Language Reference](help/common/language/index.md)!
