# CLI Variable Inspection

Learn how to inspect and monitor variables while debugging BASIC programs in the CLI.

## Variable Inspection with PRINT

The CLI uses the PRINT statement for variable inspection during debugging:

```basic
PRINT A            ' Show single variable
PRINT A, B, C$     ' Show multiple variables
PRINT A; " = "; A  ' Show with label
```

**Example session:**
```
Ok
10 A = 5
20 B = 10
30 C$ = "Hello"
RUN
Ok
PRINT A
 5
Ok
PRINT A, B, C$
 5            10           Hello
Ok
```

## Checking Variables During Debugging

Add PRINT statements to your program to inspect variables:

```
Ok
10 FOR I = 1 TO 5
15   PRINT "Loop I="; I; "A="; A    ' Debug output
20   A = A + I
30 NEXT I
40 PRINT "Sum:"; A
RUN
Loop I= 1 A= 0
Loop I= 2 A= 1
Loop I= 3 A= 3
Loop I= 4 A= 6
Loop I= 5 A= 10
Sum: 15
Ok
PRINT I, A         ' Check final values after program ends
 6            15
```

## Variable Types

MBASIC has four variable types:

### Integer Variables
```basic
A% = 100
PRINT A%
 100
```

### Single-Precision (Float)
```basic
A! = 3.14159
PRINT A!
 3.14159
```

### Double-Precision
```basic
A# = 3.141592653589793
PRINT A#
 3.141592653589793
```

### String Variables
```basic
A$ = "Hello, World!"
PRINT A$
Hello, World!
```

## Arrays

Arrays require DIM and can be inspected element by element:

```basic
10 DIM ARR(5)
20 FOR I = 1 TO 5
30   ARR(I) = I * 10
40 NEXT I
RUN
Ok
PRINT ARR(1), ARR(2), ARR(3)
 10           20           30
```

## Variables Window (GUI UIs Only)

The CLI does not have a Variables Window feature. For visual variable inspection, use:
- **Curses UI** - Full-screen terminal with Variables Window ({{kbd:toggle_variables:curses}})
- **Tk UI** - Desktop GUI with Variables Window
- **Web UI** - Browser-based with Variables Window

## Tips for Variable Inspection

1. **Use meaningful names** - Makes debugging clearer
2. **PRINT with labels** - `PRINT "A="; A` shows what you're checking
3. **Add debug PRINT statements** - Insert PRINT in your program to trace execution
4. **Use TRON** - Enable line tracing to see execution flow
5. **Format output** - Use semicolons and commas for readability

## Example: Debugging with PRINT

```basic
Ok
10 FOR I = 1 TO 10
20   F = F + 1
25   PRINT "DEBUG: I="; I; "F="; F; "N="; N
30   N = N + F
40 NEXT I
50 PRINT "Result:"; N
RUN
DEBUG: I= 1 F= 1 N= 0
DEBUG: I= 2 F= 2 N= 1
DEBUG: I= 3 F= 3 N= 3
...
Result: 55
Ok
PRINT I, F, N         ' Check final values
 11           10           55
```

## Common Patterns

### Check Multiple Variables
```basic
PRINT "I="; I, "Sum="; S, "Avg="; A
```

### Check Array Elements
```basic
PRINT A(1), A(2), A(3)
```

### Check String Variables
```basic
PRINT "Name: "; N$; " Age: "; A%
```

## Best Practices

1. **PRINT after RUN** - Variables persist after program ends
2. **Use PRINT for quick checks** - Faster than running the whole program
3. **Label your output** - Makes it clear what you're inspecting
4. **Use TRON/TROFF** - See execution flow to understand variable changes
5. **Test in direct mode** - Try expressions before adding to program

## See Also

- [Debugging Guide](debugging.md) - CLI debugging techniques (TRON/TROFF, PRINT debugging)
- [CLI Index](index.md) - Full CLI command reference
- [Tk UI](../tk/index.md) - For advanced debugging with breakpoints
- [Curses UI](../curses/index.md) - For terminal-based advanced debugging
