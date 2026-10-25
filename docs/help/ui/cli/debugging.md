# CLI Debugging

The CLI backend provides basic debugging through direct mode commands and program tracing.

## Debugging Limitations

**The CLI does not support advanced debugging features like:**
- Breakpoints (BREAK command)
- Single-stepping (STEP command)
- Call stack viewing (STACK command)

**For full debugging support, use:**
- **Tk GUI** - Visual debugger with breakpoints, stepping, variable watching
- **Curses UI** - Terminal-based debugger with similar features

## Available Debugging Techniques

### 1. Direct Mode Testing

Test expressions and statements immediately without running the full program:

```
Ok
PRINT 2 + 2
 4
Ok
LET A = 10
Ok
PRINT A * 3
 30
Ok
```

### 2. PRINT Statement Debugging

Add PRINT statements to your program to trace execution and inspect variables:

```basic
10 LET A = 0
20 FOR I = 1 TO 10
25 PRINT "Loop:"; I; "A ="; A    ' Debug output
30   A = A + I
40 NEXT I
50 PRINT "Final sum:"; A
```

### 3. Program Tracing with TRON/TROFF

Enable execution tracing to see which lines are executed:

```
Ok
10 PRINT "START"
20 FOR I = 1 TO 3
30   PRINT I
40 NEXT I
50 END
Ok
TRON
Tracing ON
Ok
RUN
[10]START
[20][30] 1
[40][30] 2
[40][30] 3
[40][50]
Ok
TROFF
Tracing OFF
```

**How it works:**
- `TRON` - Turn tracing on
- `TROFF` - Turn tracing off
- Each `[line_number]` shows which line executed
- Helps identify control flow and which paths are taken

### 4. Incremental Testing

Run partial programs by adding temporary END statements:

```basic
10 PRINT "Phase 1"
20 LET A = 10
30 PRINT "A ="; A
35 END              ' Temporary - stop here to test phase 1
40 PRINT "Phase 2"
50 LET B = A * 2
60 PRINT "B ="; B
```

Test each section, then move the END statement down as you verify each part works.

### 5. Error Line Inspection

When an error occurs, BASIC shows the line number:

```
Ok
10 LET A = 10
20 PRINT B * 2
Ok
RUN
?Undefined variable B in 20
Ok
LIST 20
20 PRINT B * 2
```

Use `LIST line_number` to examine the problematic line.

### 6. Variable Inspection After Execution

After a program runs (or errors), variables remain accessible in direct mode:

```
Ok
10 FOR I = 1 TO 5
20   A = A + I
30 NEXT I
Ok
RUN
Ok
PRINT I, A
 6             15
```

This lets you inspect the final state after execution.

## Debugging Workflow

**Typical debugging process in CLI:**

1. **Write and test small sections**
   ```
   10 LET A = 5
   20 PRINT A
   RUN
   ```

2. **Add tracing for complex sections**
   ```
   TRON
   RUN
   TROFF
   ```

3. **Use PRINT statements liberally**
   ```
   25 PRINT "DEBUG: I="; I; "A="; A
   ```

4. **Test in direct mode**
   ```
   PRINT function_expression
   LET X = test_value
   ```

5. **Inspect after errors**
   ```
   ?Error in 45
   LIST 40-50
   PRINT relevant_variables
   ```

## Comparison with Other UIs

| Feature | CLI | Tk/Curses |
|---------|-----|-----------|
| Breakpoints | ❌ No | ✅ Yes |
| Single-step | ❌ No | ✅ Yes |
| Variable watch | ❌ No | ✅ Yes |
| Call stack | ❌ No | ✅ Yes |
| TRON/TROFF | ✅ Yes | ✅ Yes |
| PRINT debugging | ✅ Yes | ✅ Yes |
| Direct mode | ✅ Yes | ✅ Yes |

## Tips

1. **Use TRON for loops** - See exactly how many times and which path the loop takes
2. **PRINT with labels** - `PRINT "Here:"; X` makes output clear
3. **Test expressions in direct mode** - Verify calculations before adding to program
4. **Keep programs simple** - CLI debugging is manual, so shorter programs are easier
5. **Switch to Tk/Curses for complex debugging** - When PRINT statements aren't enough

## When to Use Other UIs

**Switch to Tk or Curses UI if you need to:**
- Set breakpoints at specific lines
- Step through code line by line
- Watch variable values in real-time
- View the call stack during execution
- Debug complex nested loops or subroutines

**Launch other UIs:**
```bash
mbasic --ui tk yourprogram.bas      # Graphical debugger
mbasic --ui curses yourprogram.bas  # Terminal-based debugger
```

## See Also

- [CLI Index](index.md) - Full CLI command reference
- [Variables](variables.md) - Inspecting and testing variables
- [Tk UI](../tk/index.md) - Full visual debugger
- [Curses UI](../curses/index.md) - Terminal-based debugger
