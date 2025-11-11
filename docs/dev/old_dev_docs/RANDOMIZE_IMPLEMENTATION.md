# RANDOMIZE Implementation - MBASIC 5.21 Compiler

## Summary

Successfully implemented RANDOMIZE statement and fixed RND function handling, eliminating all RANDOMIZE-related parser errors.

## Implementation Date

2025-10-22

## Features Implemented

### 1. RANDOMIZE Statement
**Syntax**:
- `RANDOMIZE` - Use timer as seed
- `RANDOMIZE seed` - Use specific seed value
- `RANDOMIZE(seed)` - With parentheses (less common)

**Examples**:
```basic
10 RANDOMIZE              ' Use timer
20 RANDOMIZE X            ' Use variable
30 RANDOMIZE(123)         ' With parentheses
40 RANDOMIZE VAL(TIME$)   ' Expression as seed
```

### 2. RND Function Enhancement
**Fixed**: RND can now be called without parentheses

**Syntax**:
- `RND` - Returns random number in [0, 1)
- `RND(n)` - With argument for sequence control

**Behavior** (MBASIC standard):
- `RND` or `RND(1)` - Returns next random number
- `RND(n)` where n > 0 - Same sequence each time
- `RND(n)` where n < 0 - Reseeds with n
- `RND(0)` - Repeats last random number

## Implementation Details

### AST Node
**Location**: ast_nodes.py:247-257

```python
@dataclass
class RandomizeStatementNode:
    """RANDOMIZE statement - initialize random number generator"""
    seed: Optional[ExpressionNode]  # Seed value (None = use timer)
    line_num: int = 0
    column: int = 0
```

### Parser Implementation

**Statement Parser** (parser.py:1026-1048):
```python
def parse_randomize(self) -> RandomizeStatementNode:
    """Parse RANDOMIZE statement"""
    token = self.advance()

    seed = None
    # Check if there's a seed value
    if not self.at_end_of_line() and not self.match(TokenType.COLON):
        seed = self.parse_expression()

    return RandomizeStatementNode(
        seed=seed,
        line_num=token.line,
        column=token.column
    )
```

**RND Function Fix** (parser.py:751-787):
```python
def parse_builtin_function(self) -> FunctionCallNode:
    func_token = self.advance()
    func_name = func_token.type.name

    # RND can be called without parentheses
    if func_token.type == TokenType.RND and not self.match(TokenType.LPAREN):
        return FunctionCallNode(
            name=func_name,
            arguments=[],
            line_num=func_token.line,
            column=func_token.column
        )

    # Regular function with arguments
    self.expect(TokenType.LPAREN)
    # ... parse arguments
```

### Statement Dispatcher
Added to parse_statement() (parser.py:404-405):
```python
elif token.type == TokenType.RANDOMIZE:
    return self.parse_randomize()
```

## Test Results

### Before Implementation
- Total parser failures: 205 (after DEF FN)
- RANDOMIZE errors: **~3 files**
- Success rate: 30 files (8.0%)

### After Implementation
- Total parser failures: 205 (no change - files have other errors)
- RANDOMIZE errors: **0 files** ✓
- Success rate: 30 files (8.0%) (unchanged - files blocked by other issues)

### Impact Analysis

**Success**:
- ✓ All RANDOMIZE "Unexpected token" errors eliminated
- ✓ RND function now works without parentheses
- ✓ Files with RANDOMIZE now progress to next parsing issue

**Files Affected**:
The ~3 files that were failing with RANDOMIZE errors now fail with different parse errors:
- `rock.bas` - Now fails with multi-statement line issue
- `cpm-pert.bas` - Now fails with multi-statement line issue

This is positive progress - RANDOMIZE is no longer a blocker.

## Test Case

```basic
10 RANDOMIZE
20 RANDOMIZE X
30 RANDOMIZE(VAL(TIME$))
40 RANDOMIZE 123
50 Y = RND
60 Z = RND(1)
70 END
```

**Result**: ✓ All statements parse successfully

## Real-World Examples

From corpus files:
```basic
RANDOMIZE(NNN)                          ' With parentheses
RANDOMIZE X                             ' With variable
RANDOMIZE RS                            ' With expression
RANDOMIZE(VAL(RIGHT$(TIME$,1)))        ' Complex seed
RANDOMIZE                               ' No seed (timer)
RANDOMIZE P                             ' Simple variable
```

## Code Changes

### Files Modified

1. **ast_nodes.py** - Added RandomizeStatementNode (11 lines)
2. **parser.py** - Added parse_randomize() (23 lines)
3. **parser.py** - Fixed parse_builtin_function() for RND (15 lines)
4. **parser.py** - Added RANDOMIZE to statement dispatcher (2 lines)

**Total**: ~51 lines of code

## Technical Notes

### Why RND Without Parentheses?

In MBASIC, RND is a special built-in function that:
1. Has default behavior when called without arguments
2. Can optionally take an argument for sequence control
3. Is frequently used as `X = RND` in loops

This is common in early BASIC dialects where brevity was valued (CP/M systems had limited memory and slow terminals).

### Parser Design

The implementation handles three cases gracefully:
1. `RANDOMIZE` alone - seed is None
2. `RANDOMIZE expr` - seed is expression
3. `RANDOMIZE(expr)` - seed is expression in parentheses

The expression parser handles the parentheses case automatically, so the RANDOMIZE parser doesn't need special logic for it.

## Remaining Top Issues

After RANDOMIZE implementation:

1. **Multi-statement line parsing** (~20 files) - Biggest blocker
2. **BACKSLASH line continuation** (~10 files) - Medium difficulty
3. **Array/function disambiguation** (~9 files) - Parser lookahead issue
4. **CALL statement** (~5 files) - Assembly interface
5. **ERASE statement** (~1 file) - Array deallocation

## Statistics

- **Statements eliminated**: RANDOMIZE errors (3 files)
- **Success rate change**: 0% (files have other issues)
- **Code added**: ~51 lines
- **Files modified**: 2 (ast_nodes.py, parser.py)
- **Implementation time**: ~15 minutes

## Conclusion

The RANDOMIZE implementation is complete and working correctly. While it didn't increase the overall success rate, it:

1. **Eliminated a blocker** for ~3 files
2. **Fixed RND function** to work without parentheses (benefits many files)
3. **Added essential BASIC feature** for games and simulations
4. **Enabled progress** on files that were stuck on RANDOMIZE

The success rate remaining at 8.0% is expected - files using RANDOMIZE typically have other complex syntax issues. The key achievement is removing RANDOMIZE as a blocker.

## Next Steps

To significantly improve success rate, the focus should shift to:

1. **Multi-statement line parsing** - Would have biggest impact (~20 files)
2. **Better error recovery** - Allow parsing to continue after minor errors
3. **Line continuation (BACKSLASH)** - Used in ~10 files

These three features would likely push success rate to 10-12%.
