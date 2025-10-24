# Integer Size Inference - 8/16/32-bit Optimization

## Overview

**Goal**: Automatically detect when variables can use smaller integer types (8-bit or 16-bit instead of 32-bit), enabling massive performance improvements on 8-bit CPUs like the Intel 8080.

**Performance Impact on 8080**:
- 8-bit operations: ~5-10 cycles
- 16-bit operations: ~10-20 cycles
- 32-bit operations: ~80-100 cycles (software routines)

**Speedup: 10-20x for 8-bit vs 32-bit!**

## Integer Size Ranges

### 8-bit INTEGER
- **Signed**: -128 to 127
- **Unsigned**: 0 to 255
- **Storage**: 1 byte
- **Registers**: A, B, C, D, E, H, L (8080)

### 16-bit INTEGER
- **Signed**: -32,768 to 32,767
- **Unsigned**: 0 to 65,535
- **Storage**: 2 bytes
- **Registers**: BC, DE, HL (8080 register pairs)

### 32-bit INTEGER
- **Signed**: -2,147,483,648 to 2,147,483,647
- **Unsigned**: 0 to 4,294,967,295
- **Storage**: 4 bytes
- **Registers**: Memory only (no 32-bit registers on 8080)

## When We Can Detect Sizes

### Pattern 1: FOR Loops with Constant Bounds

```basic
FOR I = 0 TO 10          ' I: 8-bit (0-10)
FOR I = 1 TO 100         ' I: 8-bit (1-100)
FOR I = 0 TO 255         ' I: 8-bit (0-255)
FOR I = 1 TO 1000        ' I: 16-bit (1-1000)
FOR I = 0 TO 10000       ' I: 16-bit (0-10000)
FOR I = -100 TO 100      ' I: 16-bit (-100-100, doesn't fit signed 8-bit)
FOR I = 0 TO N           ' I: 32-bit (N unknown, be conservative)
```

### Pattern 2: String Operations (ALWAYS 8-bit!)

**Key insight**: BASIC strings are limited to 255 characters maximum.

```basic
FOR I = 1 TO LEN(A$)           ' I: 8-bit (LEN returns 0-255)
C = ASC(A$)                    ' C: 8-bit (ASC returns 0-255)
P = INSTR(A$, "X")             ' P: 8-bit (INSTR returns 0-255)
B = PEEK(1000)                 ' B: 8-bit (PEEK returns 0-255)
```

### Pattern 3: Literal Constants

```basic
X = 42                   ' X: 8-bit (literal 42)
Y = 256                  ' Y: 16-bit (literal 256)
Z = 100000               ' Z: 32-bit (literal 100000)
N = -5                   ' N: 8-bit signed (-5)
```

### Pattern 4: Arithmetic Results

```basic
A = 10                   ' A: 8-bit
B = 20                   ' B: 8-bit
C = A + B                ' C: 8-bit (10+20=30, fits in 8-bit)

D = 200                  ' D: 8-bit
E = 100                  ' E: 8-bit
F = D + E                ' F: 16-bit (200+100=300, needs 16-bit)

G = 30000                ' G: 16-bit
H = 30000                ' H: 16-bit
I = G + H                ' I: 32-bit (60000, needs 32-bit)
```

## Built-in Functions Return Sizes

### Always 8-bit (0-255)

```python
INT8_FUNCTIONS = {
    'LEN',      # String length (0-255) - BASIC string limit
    'ASC',      # ASCII value (0-255)
    'PEEK',     # Memory byte (0-255)
    'INP',      # Input port byte (0-255)
    'INSTR',    # String position (0-255, or 0 if not found)
}
```

### Small range (often 8-bit)

```python
INT8_RANGE_FUNCTIONS = {
    'POS',      # Cursor position (0-79 typically, 80 columns)
    'CSRLIN',   # Cursor line (0-24 typically, 25 lines)
    'SGN',      # Sign: -1, 0, or 1
    'EOF',      # End of file: 0 or -1
}
```

### 16-bit functions

```python
INT16_FUNCTIONS = {
    'LOF',      # File length (can be > 255 but usually < 65536)
    'FRE',      # Free memory (16-bit address space)
    'VARPTR',   # Variable pointer (16-bit address)
    'CVI',      # Convert to integer (16-bit)
}
```

## Type System Extension

### New Enums

```python
class IntegerSize(Enum):
    """Size of integer variable"""
    INT8 = 1    # 8-bit: -128 to 127 (signed) or 0 to 255 (unsigned)
    INT16 = 2   # 16-bit: -32768 to 32767 (signed) or 0 to 65535 (unsigned)
    INT32 = 3   # 32-bit: full range

class VarType(Enum):
    """Variable types with integer size information"""
    INTEGER = 1      # Generic integer (size determined separately)
    SINGLE = 2
    DOUBLE = 3
    STRING = 4
```

### Range Tracking

```python
@dataclass
class IntegerRangeInfo:
    """Range information for an integer variable"""
    variable: str
    integer_size: IntegerSize     # Determined size
    min_value: Optional[int]       # Minimum possible value
    max_value: Optional[int]       # Maximum possible value
    is_constant: bool              # Always same value?
    constant_value: Optional[int]  # If constant, what value?
    reason: str                    # Why this size was chosen
    line: int                      # Where determined
```

## Size Inference Algorithm

### Step 1: Literal Detection

```python
def _infer_size_from_literal(self, value: int) -> IntegerSize:
    """Determine size needed for a literal value"""
    if -128 <= value <= 127:
        return IntegerSize.INT8  # Fits in signed 8-bit
    elif 0 <= value <= 255:
        return IntegerSize.INT8  # Fits in unsigned 8-bit
    elif -32768 <= value <= 32767:
        return IntegerSize.INT16  # Fits in signed 16-bit
    elif 0 <= value <= 65535:
        return IntegerSize.INT16  # Fits in unsigned 16-bit
    else:
        return IntegerSize.INT32  # Needs 32-bit
```

### Step 2: FOR Loop Analysis

```python
def _analyze_for_loop_size(self, stmt: ForStatementNode) -> IntegerSize:
    """Determine optimal size for FOR loop counter"""

    # Try to evaluate loop bounds as constants
    start_val = self.evaluator.evaluate(stmt.start)
    end_val = self.evaluator.evaluate(stmt.end)
    step_val = self.evaluator.evaluate(stmt.step) if stmt.step else 1

    if start_val is not None and end_val is not None:
        # Determine range
        if step_val > 0:
            min_val = start_val
            max_val = end_val
        else:
            min_val = end_val
            max_val = start_val

        # Choose smallest size that fits
        if 0 <= min_val <= 255 and 0 <= max_val <= 255:
            return IntegerSize.INT8
        elif -128 <= min_val <= 127 and -128 <= max_val <= 127:
            return IntegerSize.INT8
        elif -32768 <= min_val <= 32767 and -32768 <= max_val <= 32767:
            return IntegerSize.INT16

    # Unknown bounds - be conservative
    return IntegerSize.INT32
```

### Step 3: Function Return Size

```python
def _infer_size_from_function(self, func_name: str) -> IntegerSize:
    """Determine size of function return value"""

    func_upper = func_name.upper()

    # String functions return 8-bit
    if func_upper in {'LEN', 'ASC', 'PEEK', 'INP', 'INSTR'}:
        return IntegerSize.INT8

    # Small-range functions
    if func_upper in {'POS', 'CSRLIN', 'SGN', 'EOF'}:
        return IntegerSize.INT8

    # 16-bit functions
    if func_upper in {'LOF', 'FRE', 'VARPTR', 'CVI'}:
        return IntegerSize.INT16

    # Unknown - be conservative
    return IntegerSize.INT32
```

### Step 4: Arithmetic Size Propagation

```python
def _infer_size_from_binary_op(self, left_size: IntegerSize, right_size: IntegerSize,
                                 op: str) -> IntegerSize:
    """Determine result size of binary operation"""

    # Multiplication can overflow
    if op == '*':
        if left_size == IntegerSize.INT8 and right_size == IntegerSize.INT8:
            return IntegerSize.INT16  # 8-bit * 8-bit can be 16-bit (255*255=65025)
        elif left_size == IntegerSize.INT16 or right_size == IntegerSize.INT16:
            return IntegerSize.INT32  # 16-bit * 16-bit can overflow

    # Addition can overflow
    if op == '+':
        if left_size == IntegerSize.INT8 and right_size == IntegerSize.INT8:
            return IntegerSize.INT16  # 8-bit + 8-bit can be 9-bit (255+255=510)
        elif left_size == IntegerSize.INT16 or right_size == IntegerSize.INT16:
            return IntegerSize.INT32  # 16-bit + 16-bit can overflow

    # Subtraction similar to addition
    if op == '-':
        if left_size == IntegerSize.INT8 and right_size == IntegerSize.INT8:
            return IntegerSize.INT16  # Can go negative or overflow
        elif left_size == IntegerSize.INT16 or right_size == IntegerSize.INT16:
            return IntegerSize.INT32

    # Division makes result smaller
    if op in ('/', '\\', 'MOD'):
        return max(left_size, right_size)  # Result fits in larger operand

    # Default: use larger size
    return max(left_size, right_size)
```

## Conservative Rules

**Safety first**: When uncertain, use larger size.

1. **Unknown bounds**: Use INT32
2. **User input**: Use INT32 (can't predict)
3. **Function arguments**: Use INT32 unless function signature known
4. **Cross-statement dependencies**: Track carefully or use INT32

## Common Optimization Patterns

### Pattern 1: String Processing Loop

```basic
100 INPUT A$
110 FOR I = 1 TO LEN(A$)
120   C = ASC(MID$(A$, I, 1))
130   IF C >= 65 AND C <= 90 THEN PRINT CHR$(C)
140 NEXT I
```

**Optimization**:
- `LEN(A$)`: Returns INT8 (0-255)
- `I`: INT8 (1 to LEN, max 255)
- `ASC(...)`: Returns INT8 (0-255)
- `C`: INT8 (0-255)
- `65`, `90`: INT8 literals
- `CHR$(C)`: Takes INT8 argument

**Result**: All variables are 8-bit! **10-20x speedup on 8080!**

### Pattern 2: Character Frequency Counter

```basic
100 DIM FREQ(255)
110 FOR I = 0 TO 255
120   FREQ(I) = 0
130 NEXT I
140 INPUT A$
150 FOR I = 1 TO LEN(A$)
160   C = ASC(MID$(A$, I, 1))
170   FREQ(C) = FREQ(C) + 1
180 NEXT I
```

**Optimization**:
- First loop `I`: INT8 (0-255)
- Second loop `I`: INT8 (1-LEN, max 255)
- `C`: INT8 (0-255)
- Array index `FREQ(C)`: INT8 (0-255)

**Result**: All counters and indices are 8-bit!

### Pattern 3: Small Counter Loops

```basic
100 FOR I = 1 TO 10
110   FOR J = 1 TO 10
120     PRINT I * J;
130   NEXT J
140 NEXT I
```

**Optimization**:
- `I`: INT8 (1-10)
- `J`: INT8 (1-10)
- `I * J`: INT8 (result max 100, fits in 8-bit)

## 8080 Assembly Examples

### 8-bit Loop

```basic
FOR I = 1 TO 100
  X = X + I
NEXT I
```

**Generated (8-bit):**
```asm
    MVI A, 1         ; I = 1 (A register, 8-bit) - 7 cycles
LOOP:
    MOV B, A         ; Save I - 5 cycles
    LDA X            ; Load X - 13 cycles
    ADD B            ; X + I (8-bit add!) - 4 cycles
    STA X            ; Store X - 13 cycles
    INR A            ; I++ (8-bit increment!) - 5 cycles
    CPI 101          ; Compare I with 101 - 7 cycles
    JC LOOP          ; Jump if < 101 - 10 cycles
    ; Total per iteration: ~64 cycles
```

**Generated (32-bit):**
```asm
    LXI H, I_ADDR    ; Point to I
    MVI M, 1         ; I = 1 (32-bit in memory: 01 00 00 00)
    INX H
    MVI M, 0
    INX H
    MVI M, 0
    INX H
    MVI M, 0         ; ~40 cycles
LOOP:
    LXI H, I_ADDR
    CALL LOAD32      ; Load 32-bit I into registers - ~60 cycles
    PUSH H
    PUSH D
    LXI H, X_ADDR
    CALL LOAD32      ; Load X - ~60 cycles
    POP D
    POP H
    CALL ADD32       ; 32-bit addition - ~120 cycles
    LXI H, X_ADDR
    CALL STORE32     ; Store X - ~60 cycles
    LXI H, I_ADDR
    CALL INC32       ; Increment 32-bit - ~80 cycles
    LXI D, 101       ; Load 101 into DE (32-bit: 00 00 00 65)
    CALL CMP32       ; 32-bit compare - ~100 cycles
    JC LOOP
    ; Total per iteration: ~480+ cycles
```

**Speedup: ~7.5x faster with 8-bit!**

### String Processing

```basic
FOR I = 1 TO LEN(A$)
  C = ASC(MID$(A$, I, 1))
  ' Process C
NEXT I
```

**Generated (8-bit):**
```asm
    ; Get string length
    LXI H, A_STR     ; Point to A$
    MOV A, M         ; Length byte (8-bit!) - first byte of string
    STA MAXLEN

    MVI A, 1         ; I = 1 (8-bit!)
LOOP:
    STA CURRENT_I
    ; Call MID$ and ASC (optimized for 8-bit index)
    LDA CURRENT_I
    CALL MID_ASC_8   ; Specialized 8-bit version - ~50 cycles
    ; A now contains character code (8-bit)
    ; ... process C ...

    LDA CURRENT_I
    INR A            ; I++ (8-bit increment!) - 5 cycles
    MOV B, A
    LDA MAXLEN
    CMP B            ; Compare (8-bit!) - 4 cycles
    JNC LOOP
    ; Per iteration: ~80-100 cycles
```

**vs 32-bit:** Would need ~400-500 cycles per iteration!

## Overflow Warnings

When a variable might overflow, emit warnings:

```python
if current_size == IntegerSize.INT8:
    if max_possible_value > 255:
        self.warnings.append(
            f"Line {line}: Variable {var_name} may overflow 8-bit range "
            f"(max value {max_possible_value}). Consider using 16-bit."
        )
```

Examples:
```basic
100 FOR I = 250 TO 260        ' Warning: I may overflow 8-bit (max 260)
110 X = 200 + 100             ' Warning: Result 300 needs 16-bit
```

## Testing Strategy

### Test Cases

1. **FOR loop bounds**:
   - `FOR I = 0 TO 10` → INT8
   - `FOR I = 0 TO 255` → INT8
   - `FOR I = 0 TO 256` → INT16
   - `FOR I = -100 TO 100` → INT16 (doesn't fit signed 8-bit)

2. **String operations**:
   - `FOR I = 1 TO LEN(A$)` → INT8
   - `C = ASC(A$)` → INT8
   - `P = INSTR(A$, "X")` → INT8

3. **Arithmetic**:
   - `X = 10 + 20` → INT8 (30)
   - `X = 200 + 100` → INT16 (300)
   - `X = 100 * 100` → INT16 (10000)

4. **Edge cases**:
   - `FOR I = 254 TO 260` → INT16 (crosses boundary)
   - `X = 127 + 1` → INT16 (128, overflow signed 8-bit)

## Implementation Plan

### Phase 1: Infrastructure
1. Add `IntegerSize` enum
2. Add `IntegerRangeInfo` dataclass
3. Update `_count_optimizations()` to include integer size analysis

### Phase 2: Detection
1. Implement literal size detection
2. Implement FOR loop size analysis
3. Implement function return size detection
4. Implement arithmetic size propagation

### Phase 3: Integration
1. Integrate into `analyze()` method
2. Add to iterative optimization loop
3. Add reporting in `get_report()`

### Phase 4: Testing
1. Create comprehensive test suite
2. Test on real BASIC programs
3. Validate overflow warnings

## Benefits

### Performance (8080)
- **8-bit loops**: 10-20x faster than 32-bit
- **String processing**: 10-15x faster
- **Small counters**: 5-10x faster

### Memory
- **8-bit**: 1 byte per variable
- **16-bit**: 2 bytes per variable
- **32-bit**: 4 bytes per variable
- **Savings**: 3 bytes per variable (8-bit vs 32-bit)

For a program with 50 integer variables, 40 of which can be 8-bit:
- **Before**: 200 bytes (50 × 4)
- **After**: 90 bytes (40 × 1 + 10 × 4)
- **Savings**: 110 bytes (55%)

### Register Allocation (8080)
- **8-bit**: Can use A, B, C, D, E registers
- **16-bit**: Can use BC, DE, HL register pairs
- **32-bit**: Must use memory

More variables in registers = faster code!

## Success Metrics

1. ✅ Detect 90%+ of string loop counters as 8-bit
2. ✅ Detect 80%+ of small FOR loops as 8-bit
3. ✅ Detect 70%+ of literals as 8-bit or 16-bit
4. ✅ Zero false positives (overflow bugs)
5. ✅ Measurable speedup on real programs (5-10x)

## Related Documents

- `doc/TYPE_REBINDING_STRATEGY.md` - Variable type changes
- `doc/TYPE_REBINDING_PHASE2_DESIGN.md` - Type promotion
- `doc/ITERATIVE_OPTIMIZATION_STRATEGY.md` - Optimization framework
- `doc/OPTIMIZATION_STATUS.md` - All optimizations

---

**Status**: Design complete, ready for implementation
**Priority**: HIGH (massive performance impact on 8080)
**Complexity**: Medium (range tracking is tricky)
**Dependencies**: Type rebinding analysis (Phase 1)
