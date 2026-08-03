# How to Run Real MBASIC 5.21 for Testing

## Setup
- Real MBASIC 5.21 is a CP/M `.COM` binary, so it needs a CP/M emulator to run:
  - **cpmemu** (preferred) - https://github.com/avwohl/cpmemu
  - **tnylpo** (alternate) - the emulator this procedure was originally worked out and
    verified against
- Location: `com/mbasic.com`
- Wrapper script: `utils/mbasic521` (but see below - doesn't work as expected)

### Emulator note - read this before changing any command below

This procedure is fragile and was hard-won. **Every `tnylpo` command in this file is
left exactly as it was originally verified and still works.** Do not "modernise" them.

cpmemu is a verified drop-in replacement for tnylpo here: same piping, same `SYSTEM`
handling, same `com/mbasic.com` binary. Only the program name on the command line
changes, so each example below is shown both ways.

- Preferred: `... | timeout 5 cpmemu ../com/mbasic`
- Alternate: `... | timeout 1 tnylpo ../com/mbasic`

Two cpmemu-specific details:

1. cpmemu writes its own diagnostics - `CPU mode: Z80`, `Loaded NNNNN bytes from ...`,
   and `Program exit via JMP 0` - to **stderr**, not stdout. Add `2>/dev/null` when you
   want MBASIC's output on its own. `2>&1` folds that chatter into your capture, where it
   turns up later as spurious diff lines.
2. cpmemu exits by itself as soon as MBASIC executes `SYSTEM`, so `timeout` is only a
   backstop. The `SYSTEM` requirement below is unchanged and still mandatory.

Which emulator to prefer, and why:
[../docs/dev/TOOLCHAIN_POLICY.md](../docs/dev/TOOLCHAIN_POLICY.md)

### Path note

The commands below say `cd /home/wohl/cl/mbasic/tests`, which is where the checkout used
to live. The checkout is now at `/home/wohl/src/mbasic`, so `cd` to
`/home/wohl/src/mbasic/tests`. Everything after the `cd` is unchanged and correct - the
only thing that matters is that you are in the repo's `tests/` directory so that
`../com/mbasic` resolves.

## Requirements for Test Files

### 1. File Location
Must run from the `tests/` directory:
```bash
cd /home/wohl/cl/mbasic/tests
```

### 2. Program Exit
**CRITICAL**: Programs MUST end with `SYSTEM` not `END`
- `END` leaves you at the "Ok" prompt (hangs waiting for input)
- `SYSTEM` exits MBASIC back to CP/M and the emulator - cpmemu or tnylpo - exits properly

Example:
```basic
10 PRINT "Hello"
20 SYSTEM
```

### 3. Line Length Limits
MBASIC 5.21 has a line buffer limit. Keep lines short:
- Comments: Keep under ~50 characters
- Code lines: Keep reasonable length
- Error: "Line buffer overflow in XX" means line XX is too long

## Running Tests - THE WORKING METHOD

**IMPORTANT**: The `utils/mbasic521` wrapper script does NOT work for passing programs via command line.
MBASIC cannot read the file from command-line arguments when invoked via an emulator -
this is an MBASIC limitation, so it is true under cpmemu and tnylpo alike.

### The Correct Way: Pipe Program as Typed Input

You must pipe the program content to MBASIC as if it's being typed.

With cpmemu (preferred):

```bash
cd /home/wohl/cl/mbasic/tests
(cat test.bas && printf "RUN\nSYSTEM\nSYSTEM\nSYSTEM\n") | timeout 5 cpmemu ../com/mbasic 2>/dev/null
```

With tnylpo (alternate) - the original, unchanged form:

```bash
cd /home/wohl/cl/mbasic/tests
(cat test.bas && printf "RUN\nSYSTEM\nSYSTEM\nSYSTEM\n") | timeout 1 tnylpo ../com/mbasic
```

This:
1. Cats the .bas file (types the program lines)
2. Sends RUN command followed by multiple SYSTEM commands
3. Pipes everything to the emulator (cpmemu or tnylpo) running MBASIC
4. Multiple SYSTEM commands ensure exit even if syntax errors garble input
5. Uses timeout as final fallback (rarely needed with multiple SYSTEM)

**Why Multiple SYSTEM?** When a program has syntax errors, MBASIC returns to "Ok" prompt and input can get garbled. Sending multiple SYSTEM commands ensures at least one gets through cleanly, causing immediate exit (~0.1s) instead of waiting for timeout (~1s).

### Example: Running hello.bas

With cpmemu (preferred):

```bash
cd /home/wohl/cl/mbasic/tests
(cat hello.bas && printf "RUN\nSYSTEM\nSYSTEM\nSYSTEM\n") | timeout 5 cpmemu ../com/mbasic 2>/dev/null
```

With tnylpo (alternate):

```bash
cd /home/wohl/cl/mbasic/tests
(cat hello.bas && printf "RUN\nSYSTEM\nSYSTEM\nSYSTEM\n") | timeout 1 tnylpo ../com/mbasic
```

Output. The banner and program output are the same under either emulator, but the
free-memory figure is not: the capture below is from tnylpo, and cpmemu reports
`39218 Bytes free` because it leaves a slightly different amount of TPA. Expect that one
line to differ when diffing across emulators.
```
BASIC-80 Rev. 5.21
[CP/M Version]
Copyright 1977-1981 (C) by Microsoft
Created: 28-Jul-81
39719 Bytes free
Ok
10 PRINT "Hello from MBASIC!"
20 SYSTEM
RUN
Hello from MBASIC!
```

### Capturing Output to File

With cpmemu, discard stderr so its startup/exit chatter stays out of the capture:

```bash
(cat test.bas && printf "RUN\nSYSTEM\nSYSTEM\nSYSTEM\n") | timeout 5 cpmemu ../com/mbasic 2>/dev/null | tee output.txt
```

With tnylpo (alternate):

```bash
(cat test.bas && printf "RUN\nSYSTEM\nSYSTEM\nSYSTEM\n") | timeout 1 tnylpo ../com/mbasic 2>&1 | tee output.txt
```

## Common Issues

1. **Using `utils/mbasic521` directly**:
   - This does NOT work - MBASIC can't read files from the command line under an
     emulator, cpmemu or tnylpo alike
   - Must pipe program as typed input (see above)

2. **Hangs after running**:
   - Program needs `SYSTEM` at end, not `END`
   - Use `timeout` command to prevent infinite hangs

3. **"Line buffer overflow"**:
   - Shorten the line mentioned in error
   - Break long lines into multiple statements
   - Keep comments under ~50 characters

4. **No output or hangs at "Ok" prompt**:
   - Check program ends with `SYSTEM`, not `END`
   - Make sure you're piping `echo "RUN"` after the program

## Example Working Test

File: `tests/hello.bas`
```basic
10 PRINT "Hello from MBASIC 5.21"
20 PRINT "Math test: 2+2 ="; 2+2
30 SYSTEM
```

Run, with cpmemu (preferred):
```bash
cd /home/wohl/cl/mbasic/tests
(cat hello.bas && echo "RUN") | timeout 5 cpmemu ../com/mbasic 2>/dev/null
```

Run, with tnylpo (alternate):
```bash
cd /home/wohl/cl/mbasic/tests
(cat hello.bas && echo "RUN") | timeout 5 tnylpo ../com/mbasic
```

## Comparing Output

To compare our MBASIC vs real MBASIC, with cpmemu (preferred):
```bash
cd /home/wohl/cl/mbasic/tests

# Run on our implementation
python3 ../mbasic mytest.bas > /tmp/our_output.txt 2>&1

# Run on real MBASIC (multiple SYSTEM for instant exit on errors)
# 2>/dev/null keeps cpmemu's own startup/exit lines out of the diff
(cat mytest.bas && printf "RUN\nSYSTEM\nSYSTEM\nSYSTEM\n") | timeout 5 cpmemu ../com/mbasic > /tmp/real_output.txt 2>/dev/null

# Compare
diff /tmp/our_output.txt /tmp/real_output.txt
```

The same comparison with tnylpo (alternate):
```bash
cd /home/wohl/cl/mbasic/tests

# Run on our implementation
python3 ../mbasic mytest.bas > /tmp/our_output.txt 2>&1

# Run on real MBASIC (multiple SYSTEM for instant exit on errors)
(cat mytest.bas && printf "RUN\nSYSTEM\nSYSTEM\nSYSTEM\n") | timeout 1 tnylpo ../com/mbasic > /tmp/real_output.txt 2>&1

# Compare
diff /tmp/our_output.txt /tmp/real_output.txt
```

## Why This Method Works

MBASIC 5.21 was designed for CP/M's interactive environment. When you pass a filename on the command line to the emulator - cpmemu or tnylpo:
- The emulator passes it to MBASIC as a CP/M command-line argument
- MBASIC doesn't parse command-line arguments for auto-loading files
- It just starts at the "Ok" prompt waiting for typed commands

By piping the file contents:
- MBASIC receives the program lines as if typed at the keyboard
- Each line is entered into the program buffer
- The "RUN" command executes the program
- `SYSTEM` exits back to CP/M, and the emulator exits with it (cpmemu prints
  `Program exit via JMP 0` on stderr as it goes; tnylpo just exits)
