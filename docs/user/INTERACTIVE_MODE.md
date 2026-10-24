# Interactive Mode: Curses Screen Editor and CLI

## Start interactive mode (Curses Screen Editor)

```bash
python3 mbasic
```

The **curses screen editor** (default) provides a full-screen terminal interface:
- Visual line editor with auto-numbering
- Status indicators for breakpoints and errors
- **Automatic syntax checking** (marks parse errors with '?')
- Calculator-style line number editing
- Automatic line sorting
- Split-screen output window
- Optimized paste performance (instant display)
- Smart line number parsing (preserves pasted line numbers)
- Edge-to-edge display (clean copy/paste without borders)

**Features:**
- `Ctrl+R` - Run program
- `Ctrl+S` - Save program
- `Ctrl+O` - Open program
- `Ctrl+B` - Toggle breakpoint on current line
- `Ctrl+D` - Delete current line
- `Ctrl+E` - Renumber all lines (RENUM)
- `Ctrl+H` - Help
- `Tab` - Switch between editor and output
- Arrow keys, Page Up/Down for navigation
- Auto-numbering with smart collision avoidance
- Fast paste operations with automatic formatting

**Debugger:**
- `Ctrl+G` - Continue execution (from breakpoint)
- `Ctrl+T` - Step (execute one line)
- `Ctrl+X` - Stop execution

See **[Curses Editor Documentation](../help/ui/curses/index.md)** for complete guide.

## CLI Mode (Line-by-line REPL)

```bash
python3 mbasic --ui cli
```

Then enter your program:

```basic
MBASIC 5.21 Interpreter
Ready

10 PRINT "Hello, World!"
20 FOR I = 1 TO 10
30 PRINT I
40 NEXT I
50 END
RUN
LIST
SAVE "hello.bas"
```

Opening a file at startup loads it for editing; it does not automatically run it:

```powershell
# Windows PowerShell, from the source checkout
py .\mbasic .\myprogram.bas --ui cli
```

The CLI displays `Loaded from ...`, a hint to type `RUN`, and the `MBASIC> `
command prompt. Enter `RUN` to execute or `LIST` to inspect the loaded program.
For an installed package, use `mbasic myprogram.bas --ui cli`. On Linux/macOS,
use `python3 mbasic myprogram.bas --ui cli` from a checkout.

Both `10 PRINT "hello"` and `10PRINT "hello"` are accepted by LOAD and MERGE.
Load diagnostics name the file, physical file line, and BASIC line number (when
present), followed by the parser's reason. An empty file reports that no numbered
program lines were found. If some lines are valid, they are loaded and the rejected
lines are reported; inspect those diagnostics before running a partially loaded
program. A missing file is reported separately from invalid source.
