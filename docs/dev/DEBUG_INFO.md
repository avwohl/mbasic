# Debug information for compiled programs (-g)

`mbasic --compile-c -g` builds a CP/M program together with a file `prog.dbg`. The file maps each address of the program to a line of the BASIC file. The debugger `udb80` reads the file. It sets breakpoints on BASIC lines, steps by BASIC line, and shows the BASIC text. The design is in [debugger_plan.md](https://github.com/avwohl/cpmemu/blob/main/docs/debugger_plan.md) of cpmemu (decision D8). The marker format is in `docs/debug_info.md` of um80_and_friends.

## Use

```
mbasic prog.bas -g --compile-c prog
udb80 prog.dbg --run 'cpmemu prog.com'
```

The option `-g` (long form `--debug-info`) works with the uc80 toolchain only. With `--toolchain z88dk` or `--cpu 8080`, mbasic prints a note and builds without debug information. z88dk does not read the debug markers of uc80.

With `-g`, mbasic runs the three tools of the uc80 toolchain with debug options:

```
uc80 ... -g
um80 --debug-info ...
ul80 --debug-info ...
```

`ul80` writes `prog.dbg` beside `prog.com`.

## The program does not change

The `.com` file is the same, byte for byte, with and without `-g`. A `#line` directive and a debug marker write no code. The tests compare the two `.com` files.

## What mbasic writes

mbasic writes the directive `#line N "prog.bas"` before each line of the C text that comes from a BASIC line. The file name is the name that you gave on the command line. The number `N` is the physical line of the BASIC file, and not the BASIC line number. A debugger lists the file by physical line, so `list` and `break prog.bas:N` need that number.

Example: the BASIC line `40 A = A + I` is on line 4 of the file. Use the command `break prog.bas:4`. The `list` command shows `4  40 A = A + I`.

A `#line` directive sets the line of the next C line only. The C text of one BASIC line has more than one line, so mbasic writes the directive before each of them. A line inside a comment gets no directive.

After the last BASIC line, mbasic writes `#line K "prog.c"`. The C text that follows (the end of `main`, the dispatcher for `GOSUB`) then maps to the C file and not to the BASIC file.

The backend writes no directive in the z88dk dialect, and none without `-g`.

## Two levels of line

The compiled program comes from two source files: the BASIC file and the C file. uc80 maps through `#line`, so each marker `;#line F L` names the BASIC file and the BASIC line. The C line is not in the marker. The marker field `outer=G:M` is for the C position. uc80 does not write the field yet, so `prog.dbg` has no C position for the BASIC lines.

The runtime (`mb25_string.c`) is C code and has no `#line` for BASIC. Its rows name its own file. `step` goes into a runtime routine such as `mb25_fadd`.

## Limits

- A BASIC line that has only `REM` makes no code, so it has no row. A `break` on such a line uses the next line that has code.
- Every statement of a multi-statement line maps to the line. The debugger cannot tell the statements apart.
- The `FOR` line has code in more than one place: the start value, and the test at the top of the loop. A breakpoint on the line has one location for each place, and `step` stops twice on the line.
- `prog.dbg` has no variables. Phase 8 of the plan adds variables.
- The `bt` command shows `_main` as the routine of all BASIC code. A `GOSUB` is a jump in the C text, so the shadow stack of cpmemu has no frame for it. A breakpoint inside a subroutine shows only `_main` and the start-up code (measured).
- The path in `#line` is the path from the command line. Give `udb80` the option `-d DIR` when you run the debugger in another directory.
