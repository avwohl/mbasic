# MBASIC-2025: Modern MBASIC 5.21 Interpreter & Compilers

A complete implementation of Microsoft BASIC-80 5.21 (CP/M era) with an interactive interpreter and TWO compiler backends (Z80/8080 + JavaScript), written in Python.

> **About MBASIC:** MBASIC was a BASIC interpreter originally developed by Microsoft in the late 1970s. This is an independent, open-source reimplementation created for educational purposes and historical software preservation. See [MBASIC History](https://github.com/avwohl/mbasic/blob/main/docs/history/MBASIC_HISTORY.md) for more information.
>
> **📄 Want the full story?** See [MBASIC Project Overview](https://github.com/avwohl/mbasic/blob/main/docs/MBASIC_PROJECT_OVERVIEW.md) for a comprehensive feature showcase.

**Status:** Full MBASIC 5.21 implementation complete with 100% compatibility in interpreter and both compiler backends.

## 🎉 THREE Complete Implementations

### Interactive Interpreter (100% Complete)
- ✅ **100% Compatible**: All original MBASIC 5.21 programs run unchanged
- ✅ **Modern Extensions**: Optional debugging commands (BREAK, STEP, WATCH, STACK)
- ✅ **Multiple UIs**: CLI (classic), Curses, Tk (GUI), Web (browser)
- ✅ **Full REPL**: Interactive command mode with RUN, LIST, SAVE, LOAD, etc.

### Z80/8080 Compiler (100% Complete)
- ✅ **100% Feature Complete**: ALL compilable MBASIC 5.21 features implemented
- ✅ **Generates CP/M Executables**: Produces native .COM files for 8080 or Z80 CP/M systems
- ✅ **Efficient Runtime**: Optimized string handling with O(n log n) garbage collection
- ✅ **Hardware Access**: Full support for PEEK/POKE/INP/OUT/WAIT
- ✅ **Machine Language**: CALL/USR/VARPTR for assembly integration

### JavaScript Compiler (100% Complete)
- ✅ **100% Feature Complete**: All MBASIC 5.21 features except hardware access
- ✅ **Generates JavaScript**: Produces standalone .js files for Node.js and browsers
- ✅ **Cross-Platform**: Same code runs in browsers and Node.js
- ✅ **Full File I/O**: localStorage in browser, fs module in Node.js
- ✅ **Standalone HTML**: Optional HTML wrapper for browser deployment

See [Features and Implementation Status](https://github.com/avwohl/mbasic/blob/main/docs/user/FEATURES_AND_STATUS.md) for details, [Extensions](https://github.com/avwohl/mbasic/blob/main/docs/help/mbasic/extensions.md) for modern features, [Compilers](https://github.com/avwohl/mbasic/blob/main/docs/user/COMPILERS.md) for compiler information, and [PROJECT_STATUS.md](https://github.com/avwohl/mbasic/blob/main/docs/PROJECT_STATUS.md) for current project health and metrics.

## Installation

### From PyPI

```bash
# Minimal install - CLI backend only (zero dependencies)
pip install mbasic

# With all UI backends
pip install "mbasic[all]"
```

The other extras (`curses`, `tk`, `web`, `dev`) and the Tkinter notes are in the
[Installation Guide](https://github.com/avwohl/mbasic/blob/main/docs/user/INSTALL.md).

### From Source

**For end users** (interpreter only): See **[INSTALL.md](https://github.com/avwohl/mbasic/blob/main/docs/user/INSTALL.md)** for detailed installation instructions.

**For developers** (full development environment including compiler): See **[Linux Mint Developer Setup](https://github.com/avwohl/mbasic/blob/main/docs/dev/LINUX_MINT_DEVELOPER_SETUP.md)** for comprehensive system setup with all packages and tools.

## Quick Start

```bash
python3 mbasic myprogram.bas   # Run a BASIC program
python3 mbasic                 # Curses screen editor (default UI)
python3 mbasic --ui cli        # CLI mode (line-by-line REPL)
python3 mbasic --list-backends # Show which UI backends are available
```

The curses editor keys, the debugger keys, and a CLI session example are in
[Interactive Mode](https://github.com/avwohl/mbasic/blob/main/docs/user/INTERACTIVE_MODE.md).

To compile BASIC to JavaScript (no external dependencies):

```bash
mbasic --compile-js program.js program.bas
node program.js
```

The Z80/8080 compiler emits C and prefers the uc80 compiler and the cpmemu
emulator. The Z80/8080 compiler setup is in [Compilers](https://github.com/avwohl/mbasic/blob/main/docs/user/COMPILERS.md).

## Documentation

- [Features and Implementation Status](https://github.com/avwohl/mbasic/blob/main/docs/user/FEATURES_AND_STATUS.md) - Full feature list and implementation status
- [Interactive Mode](https://github.com/avwohl/mbasic/blob/main/docs/user/INTERACTIVE_MODE.md) - Curses screen editor and CLI REPL
- [Compilers](https://github.com/avwohl/mbasic/blob/main/docs/user/COMPILERS.md) - Z80/8080 and JavaScript compilers: requirements, usage, features
- [Example Programs](https://github.com/avwohl/mbasic/blob/main/docs/user/EXAMPLE_PROGRAMS.md) - Sample BASIC programs, including hardware access
- **[Curses Screen Editor](https://github.com/avwohl/mbasic/blob/main/docs/help/ui/curses/index.md)** - Full-screen terminal editor (default UI)
- **[Quick Reference](https://github.com/avwohl/mbasic/blob/main/docs/user/QUICK_REFERENCE.md)** - Command reference
- **[Installation Guide](https://github.com/avwohl/mbasic/blob/main/docs/user/INSTALL.md)** - Detailed installation instructions
- **[Compiler Status Summary](https://github.com/avwohl/mbasic/blob/main/docs/history/COMPILER_STATUS_SUMMARY.md)** - Complete feature list (100% complete!)
- **[Compiler Setup](https://github.com/avwohl/mbasic/blob/main/docs/dev/COMPILER_SETUP.md)** - z88dk installation and configuration
- **[CP/M Emulator Setup](https://github.com/avwohl/mbasic/blob/main/docs/dev/TNYLPO_SETUP.md)** - tnylpo installation for testing
- **[Linux Mint Developer Setup](https://github.com/avwohl/mbasic/blob/main/docs/dev/LINUX_MINT_DEVELOPER_SETUP.md)** - Complete system setup guide (all packages & tools)
- [Testing](https://github.com/avwohl/mbasic/blob/main/docs/dev/TESTING.md) - Running and writing tests (`python3 tests/run_regression.py`)
- [Project Structure](https://github.com/avwohl/mbasic/blob/main/docs/dev/PROJECT_STRUCTURE.md) - Source tree layout
- [Developer Documentation](https://github.com/avwohl/mbasic/blob/main/docs/dev/) - Parser, interpreter, and compiler architecture and implementation notes
- [Development History](https://github.com/avwohl/mbasic/blob/main/docs/history/DEVELOPMENT_HISTORY.md) - How the project was built, phase by phase
- [Credits and Disclaimers](https://github.com/avwohl/mbasic/blob/main/docs/CREDITS_AND_DISCLAIMERS.md) - Credit to Microsoft and disclaimers

See the **[docs/](https://github.com/avwohl/mbasic/blob/main/docs/)** directory for complete documentation.

## License

GPLv3 License - see [LICENSE](https://github.com/avwohl/mbasic/blob/main/LICENSE) file for details.

This project is an independent implementation created for educational and historical preservation purposes. It is not affiliated with, endorsed by, or supported by Microsoft Corporation. MBASIC and Microsoft BASIC are historical products of Microsoft Corporation.

## Related Projects

- [80un](https://github.com/avwohl/80un) - Unpacker for the CP/M archive and compression formats LBR, ARC, squeeze, crunch, and CrLZH.
- [cpmdroid](https://github.com/avwohl/cpmdroid) - Z80/CP/M emulator for Android phones and tablets. It emulates the RomWBW HBIOS interface and a VT100 terminal.
- [cpmemu](https://github.com/avwohl/cpmemu) - Z80/CP/M emulator for Linux and Windows, with Z80 and 8080 CPU cores. It translates the BDOS and BIOS calls of CP/M 2.2 programs to the host file system.
- [ioscpm](https://github.com/avwohl/ioscpm) - Z80/CP/M emulator for iOS and macOS. It emulates the RomWBW HBIOS interface and runs CP/M 2.2 and CP/M 3.
- [learn-ada-z80](https://github.com/avwohl/learn-ada-z80) - Collection of more than 90 Ada example programs for uada80, the Ada compiler for the Z80 processor and CP/M.
- [mbasic2025](https://github.com/avwohl/mbasic2025) - Reconstruction of the lost source code of MBASIC 5.21, the Microsoft BASIC-80 for CP/M. The MACRO-80 source code assembles to a binary that matches mbasic.com byte for byte.
- [mbasicc](https://github.com/avwohl/mbasicc) - C++17 interpreter for MBASIC 5.21, the Microsoft BASIC-80 for CP/M. It runs on Linux and macOS.
- [mbasicc_web](https://github.com/avwohl/mbasicc_web) - Web browser interpreter for MBASIC 5.21, the Microsoft BASIC-80 for CP/M. Emscripten compiles the mbasicc interpreter to WebAssembly.
- [mpm2](https://github.com/avwohl/mpm2) - Z80 emulator for MP/M II, the multi-user CP/M operating system. Users connect over SSH, and SFTP clients transfer files.
- [romwbw_emu](https://github.com/avwohl/romwbw_emu) - Hardware-level Z80/CP/M emulator for Linux and macOS. It emulates the RomWBW HBIOS interface and switches banks in 512 KB of ROM and 512 KB of RAM.
- [scelbal](https://github.com/avwohl/scelbal) - Floating-point BASIC interpreter for the 8080 processor and CP/M. A translator converts the original 8008 source code to 8080 source code.
- [uada80](https://github.com/avwohl/uada80) - Ada compiler for the Z80 processor and CP/M 2.2. It compiles a subset of Ada 2012 to CP/M .COM files.
- [uc80](https://github.com/avwohl/uc80) - C compiler for the Z80 processor and CP/M. It optimizes for small code size.
- [ucow](https://github.com/avwohl/ucow) - Cowgol compiler for the Z80 processor and CP/M. It runs on Linux in Python.
- [um80_and_friends](https://github.com/avwohl/um80_and_friends) - Linux toolchain that is compatible with Microsoft MACRO-80. It has an assembler, a linker, a librarian, and a disassembler.
- [upeepz80](https://github.com/avwohl/upeepz80) - Peephole optimizer for Z80 compilers that write lowercase Z80 assembly language. It shortens jumps to jr, builds djnz loops, and removes dead stores.
- [uplm80](https://github.com/avwohl/uplm80) - PL/M-80 compiler for the Z80 processor and CP/M. It writes Intel 8080 and Zilog Z80 assembly language.
- [z80cpmw](https://github.com/avwohl/z80cpmw) - Z80/CP/M emulator for Windows. It emulates the RomWBW HBIOS interface and boots CP/M from disk images.
