# Variable Management (CLI)

The CLI provides several ways to inspect and modify variables during program execution and debugging.

## Viewing Variables

### WATCH Command (New Feature)

The WATCH command provides comprehensive variable inspection:

```
WATCH              ' List all variables
WATCH A            ' Show specific variable
WATCH A, B, C$     ' Show multiple variables
```

**Output format:**
```
Ready
WATCH
Variables:
  A = 42 (Integer)
  B$ = "Hello" (String)
  ARR() = Array[10] (Integer Array)
  X! = 3.14159 (Single Precision)
```

### PRINT Command

Traditional variable inspection:

```
PRINT A           ' Show variable value
PRINT A; B; C     ' Multiple variables
PRINT "A ="; A    ' With label
? A               ' Shorthand for PRINT
```

### Immediate Mode

View variables after program execution:

```
RUN
Program ended
Ready
PRINT A           ' Variable persists after RUN
42
Ready
```

## Modifying Variables

### Immediate Mode Assignment

Variables can only be modified in immediate mode (not during execution):

```
Ready
A = 100           ' Set integer variable
B$ = "New text"   ' Set string variable
C! = 3.14         ' Set single precision
D# = 1.23456789   ' Set double precision
```

### Array Elements

```
DIM ARR(10)       ' Dimension array first
ARR(5) = 42       ' Set element
PRINT ARR(5)      ' View element
```

### String Operations

```
S$ = "Hello"      ' Set string
S$ = S$ + " World"  ' Concatenation
MID$(S$, 1, 5) = "Goodbye"  ' Modify substring (if supported)
```

## Variable Types

### Type Indicators

CLI follows MBASIC conventions:

| Suffix | Type | Range | Example |
|--------|------|-------|---------|
| (none) | Integer | -32768 to 32767 | `A = 42` |
| `%` | Integer | -32768 to 32767 | `A% = 42` |
| `!` | Single | ±1.7E-38 to ±1.7E+38 | `X! = 3.14` |
| `#` | Double | ±2.2E-308 to ±1.8E+308 | `Y# = 3.14159265` |
| `$` | String | 0-255 characters | `N$ = "Name"` |

### Type Declaration

```
DEFINT A-H        ' A through H are integers
DEFSNG I-N        ' I through N are single
DEFDBL O-S        ' O through S are double
DEFSTR T-Z        ' T through Z are strings
```

## Debugging with Variables

### During Breakpoints

When stopped at a breakpoint:

```
[Break at line 100]
Ready
WATCH             ' See all variables
A = 50            ' Modify variable
CONT              ' Continue with new value
```

### Monitoring Changes

Track variable values during stepping:

```
STEP
[Line 20] A = A + 1
Ready
WATCH A
A = 11
Ready
STEP
[Line 30] B = A * 2
Ready
WATCH A, B
A = 11
B = 22
```

### Common Debugging Pattern

```
10 FOR I = 1 TO 10
20   A = A + I
30   PRINT I, A
40 NEXT I
```

Debug session:
```
BREAK 20          ' Set breakpoint in loop
RUN
[Break at line 20]
WATCH I, A        ' Check loop variables
STEP              ' Execute one line
WATCH A           ' See updated value
CONT              ' Continue to next iteration
```

## Variable Scope

### Global Variables

All variables are global in MBASIC:

```
100 A = 10        ' Set in main program
200 GOSUB 300     ' Call subroutine
210 PRINT A       ' A is now 20
220 END
300 A = 20        ' Modified in subroutine
310 RETURN
```

### Variable Persistence

Variables persist between program runs:

```
RUN
Ready
PRINT A           ' Still has value from last run
NEW               ' Clears program AND variables
PRINT A           ' Now undefined (0)
```

### Clearing Variables

```
CLEAR             ' Clear all variables
NEW               ' Clear program and variables
RUN               ' Variables persist after RUN
SYSTEM            ' Exit (clears everything)
```

## Arrays

### Viewing Arrays

Arrays require element-by-element inspection:

```
DIM ARR(5)
FOR I = 1 TO 5: ARR(I) = I * 10: NEXT
WATCH ARR         ' Shows array info
PRINT ARR(1)      ' View specific element
FOR I = 1 TO 5: PRINT ARR(I): NEXT  ' View all
```

### Multi-dimensional Arrays

```
DIM MATRIX(3, 3)
MATRIX(1, 1) = 100
PRINT MATRIX(1, 1)
```

## Limitations

### Cannot Modify During Execution

Unlike GUI UIs, CLI cannot modify variables during program execution:

```
[Break at line 100]
Ready
A = 50            ' This works
CONT              ' Continue with new value

[Running]         ' Cannot modify while running
```

### No Variable Filtering

WATCH shows all variables; no filtering options:
- No search/filter
- No type filtering
- No sorting options

### No Visual Inspector

CLI lacks visual variable inspector found in GUI UIs:
- No tree view for arrays
- No type coloring
- No inline editing

## Best Practices

1. **Use meaningful names** - Makes WATCH output clearer
2. **Initialize variables** - Avoid undefined behavior
3. **Check types** - Use appropriate suffixes
4. **WATCH frequently** - During debugging
5. **Document variables** - Use REM statements

## Examples

### Example 1: Debugging Calculation

```
10 INPUT "Enter number"; N
20 F = 1
30 FOR I = 1 TO N
40   F = F * I
50 NEXT I
60 PRINT N; "factorial is"; F
```

Debug:
```
BREAK 40
RUN
Enter number? 5
[Break at line 40]
WATCH I, F, N
STEP
WATCH F          ' See factorial building
CONT
```

### Example 2: String Manipulation

```
10 INPUT "Your name"; N$
20 L = LEN(N$)
30 PRINT "Hello, "; N$
40 PRINT "Your name has"; L; "letters"
```

Check variables:
```
RUN
Your name? Alice
Hello, Alice
Your name has 5 letters
Ready
WATCH
Variables:
  N$ = "Alice" (String)
  L = 5 (Integer)
```

### Example 3: Array Processing

```
10 DIM SCORES(5)
20 FOR I = 1 TO 5
30   INPUT "Score"; SCORES(I)
40 NEXT I
50 REM Calculate average
60 SUM = 0
70 FOR I = 1 TO 5
80   SUM = SUM + SCORES(I)
90 NEXT I
100 AVG = SUM / 5
110 PRINT "Average:"; AVG
```

## Tips

1. **WATCH after RUN** - Variables persist
2. **Use PRINT for quick checks** - Faster than WATCH
3. **Modify before CONT** - Change values at breakpoints
4. **Check array bounds** - Prevent errors
5. **Clear when testing** - Use CLEAR between tests

## See Also

- [Debugging Commands](debugging.md) - WATCH, STACK, BREAK
- [CLI Commands](index.md) - Basic CLI operations
- [Language Variables](../../common/language/variables.md) - Variable types