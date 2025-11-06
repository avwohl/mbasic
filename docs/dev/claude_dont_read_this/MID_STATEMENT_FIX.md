# MID$ Statement Support Implementation

**Date**: 2025-10-22
**Context**: Session continuation - fixing parse errors in MBASIC 5.21 compiler

## Problem

MID$ can be used in two ways in MBASIC:
1. **As a function** (in expressions): `A$ = MID$(B$, 3, 5)`
2. **As a statement** (for substring assignment): `MID$(A$, 3, 5) = "HELLO"`

The parser only supported MID$ as a function. When encountering MID$ statement usage, it failed with:
```
Parse error: Expected : or newline, got MID
```

### Affected Files
- `bmodem.bas` - Parse error at line 20
- `bmodem1.bas` - Parse error at line 25
- `tanks.bas` - Parse error at line 31

### Example from tanks.bas
```basic
310 MID$(P$(TY(T)),TX(T),1)=" "
```

This assigns a single space character to position TX(T) in string P$(TY(T)).

## Solution

### 1. Created MidAssignmentStatementNode (ast_nodes.py)

Added new AST node to represent MID$ assignments:

```python
@dataclass
class MidAssignmentStatementNode:
    """MID$ statement - assign to substring of string variable

    Syntax:
        MID$(string_var, start, length) = value

    Example:
        MID$(A$, 3, 5) = "HELLO"
        MID$(P$(I), J, 1) = " "
    """
    string_var: 'ExpressionNode'  # String variable (can be array element)
    start: 'ExpressionNode'  # Starting position (1-based)
    length: 'ExpressionNode'  # Number of characters to replace
    value: 'ExpressionNode'  # Value to assign
    line_num: int = 0
    column: int = 0
```

### 2. Added Statement Detection Logic (parser.py)

The challenge: MID$ can be both a function and a statement. We need lookahead to distinguish:
- **MID$ statement**: `MID$(var, start, len) = value`
- **MID$ function**: `A$ = MID$(B$, 1, 5)`

Added detection in `parse_statement()` around line 437:

```python
# MID$ statement (substring assignment)
# Detect MID$ used as statement: MID$(var, start, len) = value
elif token.type == TokenType.MID:
    # Look ahead to distinguish MID$ statement from MID$ function
    # MID$ statement has pattern: MID$ ( ... ) =
    # MID$ is tokenized as single MID token ($ is part of the keyword)
    # We need to peek past the parentheses to see if there's an =
    saved_pos = self.position
    try:
        self.advance()  # Skip MID
        # MID$ is a single token, no need to check for DOLLAR separately
        if self.match(TokenType.LPAREN):
            # Try to find matching RPAREN followed by EQUAL
            paren_depth = 1
            self.advance()  # Skip opening (
            while not self.at_end_of_line() and paren_depth > 0:
                if self.match(TokenType.LPAREN):
                    paren_depth += 1
                elif self.match(TokenType.RPAREN):
                    paren_depth -= 1
                self.advance()
            # Now check if next token is EQUAL
            if self.match(TokenType.EQUAL):
                # This is MID$ statement!
                self.position = saved_pos  # Restore position
                return self.parse_mid_assignment()
    except:
        pass
    # Not a MID$ statement, restore and fall through to error
    self.position = saved_pos
    # If we get here, MID$ is being used in an unsupported way
    raise ParseError(f"MID$ must be used as function or assignment statement", token)
```

**Key Implementation Details:**
- MID$ is lexed as a single MID token (the $ is part of the keyword name)
- Lookahead scans through nested parentheses to find the matching closing paren
- Checks if EQUAL follows the closing paren
- If yes: it's a statement, call parse_mid_assignment()
- If no: raise error (MID$ in expression context will be handled elsewhere)

### 3. Implemented parse_mid_assignment() (parser.py)

Added around line 1666:

```python
def parse_mid_assignment(self) -> MidAssignmentStatementNode:
    """Parse MID$ assignment statement

    Syntax:
        MID$(string_var, start, length) = value

    Example:
        MID$(A$, 3, 5) = "HELLO"
        MID$(P$(I), J, 1) = " "

    Note: MID$ is tokenized as a single MID token
    """
    token = self.current()  # MID token
    self.advance()  # Skip MID (which includes the $)

    # Expect opening parenthesis
    self.expect(TokenType.LPAREN)

    # Parse string variable (can be array element)
    string_var = self.parse_expression()

    # Expect comma
    self.expect(TokenType.COMMA)

    # Parse start position
    start = self.parse_expression()

    # Expect comma
    self.expect(TokenType.COMMA)

    # Parse length
    length = self.parse_expression()

    # Expect closing parenthesis
    self.expect(TokenType.RPAREN)

    # Expect equals sign
    self.expect(TokenType.EQUAL)

    # Parse value expression
    value = self.parse_expression()

    return MidAssignmentStatementNode(
        string_var=string_var,
        start=start,
        length=length,
        value=value,
        line_num=token.line,
        column=token.column
    )
```

## Testing

### Isolated Test
```python
source = '310 MID$(P$(TY(T)),TX(T),1)=" "'
# Result: SUCCESS - MidAssignmentStatementNode created
```

### Comprehensive Test Results

**Before Implementation:**
- Error: "or newline, got MID" affecting 3 files
- bmodem.bas: Failed on MID$ at line 20
- bmodem1.bas: Failed on MID$ at line 25
- tanks.bas: Failed on MID$ at line 31

**After Implementation:**
- MID$ errors completely eliminated (0 files)
- All 3 files now progress past MID$ statements
- Files fail on subsequent errors (expected behavior):
  - bmodem.bas: Now fails on "Expected EQUAL, got IDENTIFIER" at line 20
  - bmodem1.bas: Now fails on "Expected EQUAL, got IDENTIFIER" at line 25
  - tanks.bas: Now fails on "DEF function name must start with FN" at line 37

**Overall Results:**
- Still 76 files parsing successfully (32.3%)
- MID$ statement errors: 3 → 0 (100% reduction)
- Files progress further through parsing before hitting other unrelated errors

## Technical Notes

### Why This Matters

MID$ statement is a powerful feature in MBASIC for in-place string modification:
- Efficient: modifies string without creating new string objects
- Common in CP/M era code for screen manipulation and text processing
- Used in communications software (bmodem), games (tanks), and utilities

### Parsing Challenge

The dual nature of MID$ (function vs statement) requires careful lookahead:
1. Cannot immediately parse as expression (would fail on `=` after `)`)
2. Cannot immediately parse as statement (might be function call)
3. Must scan ahead to determine context without consuming tokens
4. Must properly track parenthesis nesting (expressions can have complex nesting)

### Alternative Approaches Considered

1. **Context-free parsing**: Would require major refactor of expression parsing
2. **Two-pass statement parsing**: Would be inefficient
3. **Lookahead with restoration**: ✓ Chosen - minimal impact, clear logic

## Files Modified

1. **ast_nodes.py**: Added MidAssignmentStatementNode (lines 215-231)
2. **parser.py**:
   - Added MID$ detection logic in parse_statement() (lines 435-466)
   - Added parse_mid_assignment() implementation (lines 1666-1711)

## Code References

- MID$ detection: parser.py:437-466
- MID$ parsing: parser.py:1666-1711
- AST node definition: ast_nodes.py:215-231

## Impact

- **Error reduction**: Eliminated all 3 MID$ statement errors
- **Files impacted**: bmodem.bas, bmodem1.bas, tanks.bas now parse further
- **Code quality**: Clean separation between MID$ function and statement contexts
- **Maintainability**: Well-documented lookahead pattern for future dual-context keywords
