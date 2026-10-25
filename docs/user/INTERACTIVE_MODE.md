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
Ok

10 PRINT "Hello, World!"
20 FOR I = 1 TO 10
30 PRINT I
40 NEXT I
50 END
RUN
LIST
SAVE "hello.bas"
```

Opening a file at startup loads the file for editing. The CLI does not run the program automatically.

```powershell
# Windows PowerShell, from the source checkout
py .\mbasic .\myprogram.bas --ui cli
```

On a terminal, the CLI shows `Loaded from ...` and a hint to type `RUN`. The CLI then shows the `MBASIC> ` command prompt. Enter `RUN` to run the program. Enter `LIST` to view the program.

When input or output is not a terminal, the CLI shows no prompt and no hint. Piped and batch runs then produce only the program output.

For an installed package, use `mbasic myprogram.bas --ui cli`. On Linux and macOS, use `python3 mbasic myprogram.bas --ui cli` from a checkout.

LOAD and MERGE accept both `10 PRINT "hello"` and `10PRINT "hello"`. A file line that holds only a line number deletes that program line, as when you type the number at the prompt. No error occurs if the line does not exist.

Each load message names the file, the file line, and the BASIC line number (when the line has one). The message then gives the reason for the error. A file with no numbered lines gives the message "No numbered program lines found". The loader reports each line without a line number and continues with the next line.

As in MBASIC, the loader keeps a line that has a syntax error and prints no message. The error occurs when the program reaches the bad statement: the message is `Syntax error in 20`, and the CLI then opens the `EDIT` command on line 20. `LIST` shows the line as you typed it. A numeric constant that is too big (such as `1E39`) gives the message `Overflow`, and the line stays in the program. A line with an `&H` or `&O` constant that does not fit in 16 bits gives the message `Overflow`, and the loader stops at this line. The same rules apply to a line that you type.

Real MBASIC stops the load at the first line without a line number. The loader ignores a CP/M end-of-file mark (^Z) and all text after the mark.

Read these messages before you run a partly loaded program.

A missing file gets a separate message.
