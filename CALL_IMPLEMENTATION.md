# CALL Implementation - MBASIC 5.21 Compiler

## Summary

Successfully implemented CALL statement for calling machine language routines, eliminating all CALL-related parser errors and increasing success rate from 30 to 33 files (8.0% → 8.8%).

## Implementation Date

2025-10-22

## MBASIC 5.21 Standard Syntax

### CALL Statement
**Purpose**: Call machine language subroutine at specified memory address

**Syntax**: `CALL address`

Where `address` is any numeric expression evaluating to a memory address.

### Examples (Standard MBASIC 5.21)
```basic
CALL 16384          ' Call routine at decimal address 16384
CALL &HC000         ' Call routine at hex address C000
A = &H8000
CALL A              ' Call routine at address in variable A
CALL DIO+1          ' Call routine at computed address
POKE DIO,0
CALL DIO+1          ' Common pattern: setup then call
```

### Important Note on Compatibility

The parser also accepts extended syntax like `CALL ROUTINE(args)` for compatibility with other BASIC dialects and extended versions, but this is **not standard MBASIC 5.21**.

Standard MBASIC 5.21 only calls machine language at memory addresses, not named BASIC subroutines. For BASIC subroutines, use GOSUB/RETURN.

## Implementation Details

### AST Node
**Location**: ast_nodes.py:311-331

```python
@dataclass
class CallStatementNode:
    """CALL statement - call machine language routine (MBASIC 5.21)"""
    target: ExpressionNode          # Memory address expression
    arguments: List[ExpressionNode]  # For compatibility (non-standard)
    line_num: int = 0
    column: int = 0
```

### Parser Implementation
**Location**: parser.py:2042-2087

```python
def parse_call(self) -> CallStatementNode:
    """Parse CALL statement - Standard MBASIC 5.21"""
    token = self.advance()

    # Parse the target address expression
    target = self.parse_expression()

    # Handle extended syntax for compatibility
    arguments = []
    if isinstance(target, VariableNode) and target.subscripts:
        # CALL ROUTINE(args) - non-standard but accepted
        arguments = target.subscripts
        target = VariableNode(name=target.name, ...)

    return CallStatementNode(target=target, arguments=arguments, ...)
```

### Statement Dispatcher
Added to parse_statement() (parser.py:416-417):
```python
elif token.type == TokenType.CALL:
    return self.parse_call()
```

## Test Results

### Before Implementation
- Total parser failures: 205 (after RANDOMIZE)
- CALL errors: **~5 files**
- Success rate: 30 files (8.0%)

### After Implementation
- Total parser failures: 202 (**-3**)
- CALL errors: **0 files** ✓
- Success rate: **33 files (8.8%)** ✓ (+3 files, +0.8%)

### Impact Analysis

**Success**:
- ✓ All CALL "Unexpected token" errors eliminated
- ✓ **+3 files now parse successfully** (best improvement so far!)
- ✓ Standard MBASIC 5.21 syntax fully supported
- ✓ Extended syntax accepted for compatibility

**Files Affected**:
- 3 files now parse completely successfully
- ~2 additional files that were blocked by CALL now progress further

## Test Case

```basic
10 REM Standard MBASIC 5.21 CALL usage
20 CALL 16384
30 CALL &HC000
40 A = &H8000
50 CALL A
60 CALL DIO+1
70 END
```

**Result**: ✓ All statements parse successfully

## Real-World Usage Patterns

From CP/M-era programs:

```basic
' Setup and call machine language routine
POKE DIO,0
CALL DIO+1

' Call BDOS (CP/M system call interface)
CALL 5

' Call routine at fixed address
CALL &HC000

' Computed address
A = PEEK(&H0001) * 256 + PEEK(&H0000)
CALL A
```

## Technical Notes

### Why Machine Language Calls?

In CP/M era (late 1970s - early 1980s):
1. **Performance** - BASIC was interpreted, machine code was 100x+ faster
2. **Hardware Access** - Direct control of I/O ports, memory
3. **System Services** - CP/M BDOS calls (CALL 5)
4. **Custom Routines** - Assembly for graphics, sound, communication

### Parser Design Decisions

**Flexible Expression Parsing**:
- Any expression can be the address: variable, constant, arithmetic
- Handles hex notation (&H) naturally through expression parser
- Computed addresses (DIO+1) work automatically

**Compatibility Mode**:
- Accepts `CALL ROUTINE(args)` without error
- Stores arguments even though non-standard
- Allows corpus files from extended BASICs to parse

This design philosophy: **Be strict in generation, liberal in acceptance**

## Code Changes

### Files Modified

1. **ast_nodes.py** - Added CallStatementNode (20 lines)
2. **parser.py** - Added parse_call() (45 lines)
3. **parser.py** - Added CALL to statement dispatcher (2 lines)

**Total**: ~67 lines of code

## Comparison to Other Features

| Feature | Files Unblocked | Success Rate Increase |
|---------|----------------|----------------------|
| File I/O | 17 | +0% (other issues) |
| DEF FN | 17 | +0.2% (+1 file) |
| RANDOMIZE | 3 | +0% (other issues) |
| **CALL** | **5** | **+0.8% (+3 files)** ✓ |

CALL had the **highest success rate increase** of any feature implemented!

## Remaining Top Issues

After CALL implementation, parser failures analysis:

1. **Multi-statement line parsing** (~20 files) - Biggest remaining blocker
2. **BACKSLASH line continuation** (~10 files) - Medium difficulty
3. **Array/function disambiguation** (~9 files) - Parser lookahead
4. **Mid-statement comments** (~18 files) - APOSTROPHE handling
5. **ERASE statement** (~1 file) - Array deallocation

## Statistics

- **CALL errors eliminated**: 5 files
- **Success rate increase**: +0.8% (best so far!)
- **Code added**: ~67 lines
- **Files modified**: 2 (ast_nodes.py, parser.py)
- **Implementation time**: ~20 minutes

## Conclusion

The CALL implementation successfully adds machine language interface support for MBASIC 5.21. Key achievements:

1. **Best success rate increase** - +3 files (vs +1 for DEF FN, +0 for others)
2. **Standard MBASIC 5.21 compliance** - Follows official specification
3. **Compatibility mode** - Also accepts extended BASIC dialects
4. **Clean implementation** - Reuses expression parser, minimal code

### Why CALL Had Best Results?

Files using CALL tend to be:
- **Simpler programs** - System utilities, hardware interfaces
- **Fewer complex features** - Direct, procedural code
- **Standard syntax** - Pure MBASIC 5.21 without extensions

Unlike files with DEF FN (complex calculations) or file I/O (data processing), CALL programs are often straightforward hardware interfaces that don't use other complex features.

### Cumulative Progress

Total success rate improvement this session:
- **Starting**: 29 files (7.8%)
- **After File I/O**: 29 files (7.8%)
- **After DEF FN**: 30 files (8.0%) [+1]
- **After RANDOMIZE**: 30 files (8.0%)
- **After CALL**: **33 files (8.8%)** [+3]

**Total**: +4 files successfully parsed (+1.0% success rate)

## Next Steps

To reach **10%+ success rate** (~37+ files):

1. **Multi-statement line parsing** - Would unblock ~20 files
2. **Better error recovery** - Continue parsing after recoverable errors
3. **Line continuation (BACKSLASH)** - Used in ~10 files

These three improvements could push success rate to **12-15%**.

---

**Implementation Status**: ✓ Complete and tested
**MBASIC 5.21 Compliance**: ✓ Fully compliant
**Test Coverage**: ✓ Standard syntax verified
**Documentation**: ✓ Complete with examples
