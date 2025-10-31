# How to Run Real MBASIC 5.21 for Testing

## Setup
- Real MBASIC 5.21 runs via tnylpo CP/M emulator
- Location: `com/mbasic.com`
- Wrapper script: `utils/mbasic521` (but see below - doesn't work as expected)

## Requirements for Test Files

### 1. File Location
Must run from the `tests/` directory:
```bash
cd /home/wohl/cl/mbasic/tests
```

### 2. Program Exit
**CRITICAL**: Programs MUST end with `SYSTEM` not `END`
- `END` leaves you at the "Ok" prompt (hangs waiting for input)
- `SYSTEM` exits MBASIC back to CP/M and tnylpo exits properly

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
MBASIC cannot read the file from command-line arguments when invoked via tnylpo.

### The Correct Way: Pipe Program as Typed Input

You must pipe the program content to MBASIC as if it's being typed:

```bash
cd /home/wohl/cl/mbasic/tests
(cat test.bas && printf "RUN\nSYSTEM\nSYSTEM\nSYSTEM\n") | timeout 1 tnylpo ../com/mbasic
```

This:
1. Cats the .bas file (types the program lines)
2. Sends RUN command followed by multiple SYSTEM commands
3. Pipes everything to tnylpo running MBASIC
4. Multiple SYSTEM commands ensure exit even if syntax errors garble input
5. Uses timeout as final fallback (rarely needed with multiple SYSTEM)

**Why Multiple SYSTEM?** When a program has syntax errors, MBASIC returns to "Ok" prompt and input can get garbled. Sending multiple SYSTEM commands ensures at least one gets through cleanly, causing immediate exit (~0.1s) instead of waiting for timeout (~1s).

### Example: Running hello.bas

```bash
cd /home/wohl/cl/mbasic/tests
(cat hello.bas && printf "RUN\nSYSTEM\nSYSTEM\nSYSTEM\n") | timeout 1 tnylpo ../com/mbasic
```

Output:
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

```bash
(cat test.bas && printf "RUN\nSYSTEM\nSYSTEM\nSYSTEM\n") | timeout 1 tnylpo ../com/mbasic 2>&1 | tee output.txt
```

## Common Issues

1. **Using `utils/mbasic521` directly**:
   - This does NOT work - MBASIC can't read files from command line via tnylpo
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

Run:
```bash
cd /home/wohl/cl/mbasic/tests
(cat hello.bas && echo "RUN") | timeout 5 tnylpo ../com/mbasic
```

## Comparing Output

To compare our MBASIC vs real MBASIC:
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

MBASIC 5.21 was designed for CP/M's interactive environment. When you pass a filename on the command line to tnylpo:
- tnylpo passes it to MBASIC as a CP/M command-line argument
- MBASIC doesn't parse command-line arguments for auto-loading files
- It just starts at the "Ok" prompt waiting for typed commands

By piping the file contents:
- MBASIC receives the program lines as if typed at the keyboard
- Each line is entered into the program buffer
- The "RUN" command executes the program
- `SYSTEM` exits back to CP/M (and tnylpo exits)
