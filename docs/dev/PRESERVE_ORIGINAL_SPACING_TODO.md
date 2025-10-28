# Preserve Original Spacing in AST Serialization

⏳ **Status:** TODO

**Priority:** HIGH - Critical for maintaining user's code formatting

## Problem

Currently, when serializing the AST back to source code, we use pretty printing which adds standardized spacing. This **loses the user's original formatting**.

**Example - Current behavior (WRONG):**
```basic
User types:    10 X=Y+3
Saved as:      10 X = Y + 3
```

The user's compact spacing is replaced with standardized spacing.

## Key Insight: Token Positions Available

**We already have the information we need!** The lexer captures character positions for each token:

```python
class Token:
    def __init__(self, type, value, line=None, column=None):
        self.type = type
        self.value = value
        self.line = line      # Line number in source
        self.column = column  # Character position in line
```

**This means we can reconstruct the exact original spacing!**

## Proposed Solution

### Use Token Positions to Preserve Spacing

Instead of pretty printing with fixed spacing rules, use the column positions from tokens to reconstruct the original spacing.

**Algorithm:**
1. For each token in the AST node, we know its original column position
2. When serializing, calculate spaces needed between tokens
3. Output exact spacing from original source

**Example:**
```python
# Original line: "10 X=Y+3"
# Token positions:
#   "10"  -> column 0
#   "X"   -> column 3
#   "="   -> column 4
#   "Y"   -> column 5
#   "+"   -> column 6
#   "3"   -> column 7

# Serialization:
output = ""
prev_end = 0

for token in tokens:
    spaces = token.column - prev_end
    output += " " * spaces + token.value
    prev_end = token.column + len(token.value)

# Result: "10 X=Y+3" ✅ Exact original!
```

## Current Architecture

### Lexer (Already Tracks Positions)

```python
# In lexer.py - already implemented!
def tokenize(self, text):
    column = 0
    for char in text:
        # Create token with position
        token = Token(type, value, line=self.line, column=column)
        column += len(value)
```

**Status:** ✅ Column tracking already exists in lexer

### Parser (Stores Tokens in AST)

```python
# In parser.py - tokens stored in AST nodes
class BinaryOpNode:
    def __init__(self, left, op, right):
        self.left = left
        self.op = op          # Token with position!
        self.right = right
```

**Status:** ✅ Tokens with positions already in AST

### Serializer (Currently Pretty Prints)

```python
# In ui_helpers.py - currently IGNORES positions
def serialize_binary_op(node):
    left = serialize_expression(node.left)
    right = serialize_expression(node.right)
    return f"{left} {node.op.value} {right}"  # ❌ Fixed spacing!
```

**Status:** ❌ Needs updating to use token positions

## Implementation Plan

### Phase 1: Update Serialization to Use Positions

**Modify `ui_helpers.py` serialization functions:**

```python
def serialize_with_spacing(node, tokens):
    """Serialize AST node preserving original spacing"""
    output = []
    prev_end_column = 0

    for token in tokens:
        # Calculate spaces from previous token
        if token.column > prev_end_column:
            spaces = token.column - prev_end_column
            output.append(" " * spaces)

        # Add token value
        output.append(token.value)
        prev_end_column = token.column + len(token.value)

    return "".join(output)
```

**Update each serialize function:**
- `serialize_statement()` - Use token positions
- `serialize_expression()` - Use token positions
- `serialize_binary_op()` - Use token positions
- `serialize_variable()` - Use token positions
- etc.

### Phase 2: Store Token Sequences in AST Nodes

**Problem:** AST nodes don't currently store the full sequence of tokens, only key tokens (like operator).

**Solution:** Add `tokens` list to AST nodes during parsing.

```python
class BinaryOpNode:
    def __init__(self, left, op, right, tokens=None):
        self.left = left
        self.op = op
        self.right = right
        self.tokens = tokens or []  # NEW: All tokens for this node

# During parsing:
def parse_binary_op():
    tokens_used = []  # Track all tokens consumed
    left = parse_term(tokens_used)
    op_token = self.current_token
    tokens_used.append(op_token)
    self.advance()
    right = parse_term(tokens_used)

    return BinaryOpNode(left, op_token, right, tokens=tokens_used)
```

### Phase 3: Handle Edge Cases

**Edge Case 1: Nested Expressions**
```basic
10 X = (Y + 3) * 2
```
Need to preserve spacing within and around parentheses.

**Edge Case 2: Multi-line Statements**
```basic
10 IF X > 5 THEN PRINT "YES": GOTO 100
```
Need to preserve spacing across multiple statement parts.

**Edge Case 3: Comments**
```basic
10 X = Y + 3 ' Add three
```
Need to preserve spacing before comment.

**Edge Case 4: String Literals**
```basic
10 PRINT "Hello   World"
```
Spaces inside strings must be preserved (already handled by token value).

### Phase 4: Fallback for Generated Code

**Problem:** When code is generated (not parsed from source), there are no token positions.

**Examples:**
- RENUM generates new line numbers
- User types new line without parsing first
- Code synthesized by commands

**Solution:** Provide fallback to pretty printing when positions unavailable.

```python
def serialize_node(node):
    if node.has_token_positions():
        return serialize_with_spacing(node)
    else:
        return serialize_pretty_print(node)  # Fallback
```

### Phase 5: Handle RENUM Special Cases

**Critical:** RENUM changes line numbers in TWO places:

1. **Line number at start of line:** `10 X=Y` → `100 X=Y`
2. **Line number references in statements:**
   - `GOTO 10` → `GOTO 100`
   - `GOSUB 10` → `GOSUB 100`
   - `IF ERL = 10 THEN` → `IF ERL = 100 THEN`
   - `ON X GOTO 10, 20, 30` → `ON X GOTO 100, 200, 300`
   - `RESTORE 10` → `RESTORE 100`
   - `RESUME 10` → `RESUME 100`

**The Problem:**
When line number length changes, it affects column positions of ALL subsequent tokens on that line.

**Example 1: Line number at start**
```basic
Original:     10 X = Y + 3
Positions:    ^  ^ ^ ^ ^ ^
              0  3 5 7 9 11

After RENUM:  1000 X = Y + 3
              ^    ?
              0    Should be at 5, but stored position is 3!
```

**Example 2: GOTO target**
```basic
Original:     20 GOTO 10
Positions:       ^    ^
                 3    8

After RENUM:  200 GOTO 100
              ^   ?    ?
              0   Should be 4, but stored is 3
                       Should be 9, but stored is 8
                       And worse: "100" is 3 chars, not "10" (2 chars)
```

**Solutions:**

**Option A: Invalidate positions (RECOMMENDED for Phase 1)**
- Mark all RENUMed lines as "no positions"
- Fall back to pretty printing
- Simple, reliable, acceptable UX

```python
def renum_program(program, start, step):
    for line in program.lines.values():
        line.invalidate_positions()  # Force pretty printing
        # ... do renumbering ...
```

**Option B: Adjust all positions**
- Calculate delta for line number change
- Walk AST and adjust all token positions
- Complex, error-prone, but preserves spacing

```python
def adjust_positions_after_renum(line, old_line_num, new_line_num):
    old_len = len(str(old_line_num))
    new_len = len(str(new_line_num))
    delta = new_len - old_len

    # Adjust all tokens in line
    for token in line.all_tokens():
        if token.column > old_len:
            token.column += delta

    # Find and adjust all line number references
    for node in line.find_all_nodes(LineNumberNode):
        if node.value == old_line_num:
            node.value = new_line_num
            # Adjust position of this line number reference
            old_ref_len = len(str(old_line_num))
            new_ref_len = len(str(new_line_num))
            ref_delta = new_ref_len - old_ref_len
            # Adjust all subsequent tokens on this line
            # ... complex logic ...
```

**Recommendation:** Do Option B (adjust all positions). We're already 57,000 lines deep into a Python implementation of a 30-year-dead language with a fancy modern UI - why half-ass the spacing preservation? Do it right!

**Implementation approach for Option B:**

```python
def renum_line_and_adjust_positions(line_node, old_num, new_num, line_num_map):
    """
    Renumber a line and adjust all token positions to preserve spacing.

    Args:
        line_node: The AST node for the line
        old_num: Old line number
        new_num: New line number
        line_num_map: Dict mapping old line numbers to new ones
    """
    changes = []  # Track all position changes

    # Step 1: Adjust line number at start
    old_len = len(str(old_num))
    new_len = len(str(new_num))
    line_delta = new_len - old_len

    if line_delta != 0:
        # Shift all tokens after line number
        for token in line_node.all_tokens():
            if token.column >= old_len:
                token.column += line_delta
                changes.append(f"Line {new_num}: shifted token '{token.value}' by {line_delta}")

    # Step 2: Find and update all line number references
    for ref_node in line_node.find_all_line_number_refs():
        old_target = ref_node.line_number
        new_target = line_num_map.get(old_target, old_target)

        if old_target != new_target:
            # Update the line number value
            old_target_len = len(str(old_target))
            new_target_len = len(str(new_target))
            ref_delta = new_target_len - old_target_len

            if ref_delta != 0:
                # Find token for this line number reference
                ref_token = ref_node.token

                # Shift all tokens AFTER this reference
                for token in line_node.all_tokens():
                    if token.column > ref_token.column + old_target_len:
                        token.column += ref_delta
                        changes.append(f"Line {new_num}: shifted token '{token.value}' by {ref_delta} after target update")

                # Update the reference value and token
                ref_node.line_number = new_target
                ref_token.value = str(new_target)

    return changes

def renum_program_preserve_spacing(program, start, step):
    """
    Renumber entire program while preserving spacing.
    """
    # Build mapping of old -> new line numbers
    old_line_nums = sorted(program.lines.keys())
    line_num_map = {}
    new_num = start

    for old_num in old_line_nums:
        line_num_map[old_num] = new_num
        new_num += step

    # Process lines in order (important for cascading changes)
    all_changes = []
    for old_num in old_line_nums:
        line_node = program.lines[old_num]
        new_num = line_num_map[old_num]

        changes = renum_line_and_adjust_positions(line_node, old_num, new_num, line_num_map)
        all_changes.extend(changes)

        # Update the line number in the program
        if old_num != new_num:
            del program.lines[old_num]
            program.lines[new_num] = line_node
            line_node.line_number = new_num

    return all_changes  # Return for debugging/logging
```

**Key insight:** Process each line independently, tracking cumulative position adjustments:
1. Adjust for line number length change at start
2. Find each line number reference (GOTO, GOSUB, etc.)
3. For each reference that changes length, shift all subsequent tokens

This preserves the user's exact spacing even through RENUM!

**All statements that reference line numbers:**
- `GOTO line`
- `GOSUB line`
- `THEN line` (in IF statement)
- `ELSE line` (in IF statement)
- `ON expr GOTO line1, line2, ...`
- `ON expr GOSUB line1, line2, ...`
- `RESTORE line`
- `RESUME line`
- `ERL = line` (in expressions comparing error line)
- `DELETE line` or `DELETE line1-line2`
- `LIST line` or `LIST line1-line2`

All of these need position adjustment if we do Option B.

## Benefits

### 1. Preserves User Intent
User's spacing choices reflect their style and intentions:
- Compact: `X=Y+3` (user prefers tight)
- Spacious: `X = Y + 3` (user prefers readable)
- Mixed: `X=Y + 3` (user's preference)

### 2. No Surprising Changes
When user saves/loads/renumbers, their code looks the same (except line numbers).

### 3. Respects Coding Style
Different users have different preferences. Don't force a standard.

### 4. Related to Case Preservation
Both preserve user's original input:
- Case-preserving variables: `TargetAngle` not `targetangle`
- Spacing preservation: `X=Y+3` not `X = Y + 3`

Same philosophy: **Maintain fidelity to source code**

## Comparison with Pretty Printing

### Current (Pretty Print) Approach

**Pros:**
- Consistent formatting
- Easy to implement
- No need to track positions

**Cons:**
- Loses user's formatting ❌
- Surprising changes to code ❌
- Forces one style on everyone ❌

### Proposed (Position-Based) Approach

**Pros:**
- Preserves user's formatting ✅
- No surprising changes ✅
- Respects user's style ✅
- Information already available ✅

**Cons:**
- Slightly more complex
- Need fallback for generated code
- Need to store token sequences

**Verdict:** Position-based is clearly superior for user experience.

## Related TODOs

### PRETTY_PRINTER_SPACING_TODO.md

The pretty printer spacing TODO becomes **optional** if we preserve spacing:
- Spacing options only needed for **generated code** (fallback)
- User's code automatically uses their spacing
- Still useful for: RENUM, NEW, auto-generated lines

**Update:** Pretty printer becomes fallback, not primary serialization method.

### TYPE_SUFFIX_SERIALIZATION (Completed v1.0.85)

Similar problem and solution:
- **Problem:** Serialization added type suffixes user didn't type
- **Solution:** Track explicit vs inferred suffixes, only output explicit
- **Same principle:** Preserve what user actually typed

### CASE_PRESERVING_VARIABLES_TODO.md

Same philosophy:
- Preserve case user typed: `TargetAngle` not `targetangle`
- Preserve spacing user typed: `X=Y+3` not `X = Y + 3`

**Common theme:** Maintain fidelity to source code

## Testing Plan

### Test Cases

**Test 1: Compact spacing**
```basic
Input:  10 X=Y+3
Output: 10 X=Y+3  ✅ Preserved
```

**Test 2: Spacious spacing**
```basic
Input:  10 X = Y + 3
Output: 10 X = Y + 3  ✅ Preserved
```

**Test 3: Mixed spacing**
```basic
Input:  10 X=Y + 3*Z
Output: 10 X=Y + 3*Z  ✅ Preserved
```

**Test 4: Parentheses**
```basic
Input:  10 X=(Y+3)*2
Output: 10 X=(Y+3)*2  ✅ Preserved
```

**Test 5: Multiple statements**
```basic
Input:  10 X=1:Y=2:PRINT X,Y
Output: 10 X=1:Y=2:PRINT X,Y  ✅ Preserved
```

**Test 6: String literals**
```basic
Input:  10 PRINT "Hello   World"
Output: 10 PRINT "Hello   World"  ✅ Preserved
```

**Test 7: Comments**
```basic
Input:  10 X=Y+3 ' Calculate
Output: 10 X=Y+3 ' Calculate  ✅ Preserved
```

**Test 8: Generated code (fallback)**
```basic
RENUM: 10 X=Y+3
Output: 10 X = Y + 3  ✅ Pretty printed (no positions)
```

**Test 9: Round-trip**
```basic
Load → Parse → Serialize → Parse → Serialize
Result: Should match original after first serialize
```

### Integration Tests

1. **Save/Load cycle:** Load program, save it, compare
2. **RENUM:** Renumber, check spacing preserved (except line numbers)
3. **Edit and refresh:** Edit line, refresh, check spacing
4. **Copy/paste:** Copy lines, paste, check spacing
5. **Variable window:** Check case and spacing consistency

## Implementation Files

### Files to Modify

- **`src/ui/ui_helpers.py`** - Update serialization functions
  - Add `serialize_with_spacing()` function
  - Update all `serialize_*()` functions
  - Add fallback to pretty printing

- **`src/ast_nodes.py`** - Store token sequences
  - Add `tokens` field to AST node classes
  - Preserve tokens during AST construction

- **`src/parser.py`** - Track tokens during parsing
  - Collect tokens as they're consumed
  - Store in AST nodes

### Files to Create

- **`tests/test_spacing_preservation.py`** - Test suite for spacing

### Files to Update (Related)

- **`docs/dev/PRETTY_PRINTER_SPACING_TODO.md`** - Mark as fallback only
  - Pretty printer used for generated code
  - Not primary serialization method

## Migration Strategy

### Step 1: Verify Token Positions Exist
- Audit lexer to ensure all tokens have positions
- Add positions to any tokens that don't have them
- Test that positions are accurate

### Step 2: Add Token Storage to AST
- Add `tokens` field to AST node classes
- Update parser to store tokens
- Don't use positions yet (verify storage works)

### Step 3: Implement Position-Based Serialization
- Create `serialize_with_spacing()` function
- Test with simple expressions
- Compare with original source

### Step 4: Add Fallback
- Detect when positions unavailable
- Fall back to pretty printing
- Test both paths

### Step 5: Roll Out to All Statements
- Update all statement types
- Update all expression types
- Test edge cases

### Step 6: Integration Testing
- Test save/load cycles
- Test RENUM
- Test all UIs (CLI, curses, TK)

## Performance Considerations

**Position-based serialization is actually FASTER than pretty printing:**

- Pretty printing: Traverse AST, apply spacing rules
- Position-based: Traverse tokens, insert spaces from positions

**Estimated impact:** Negligible to positive (simpler logic)

## Success Criteria

- ✅ User's spacing preserved in save/load cycle
- ✅ Spacing preserved through RENUM (except line numbers)
- ✅ No surprising formatting changes
- ✅ Fallback works for generated code
- ✅ All tests pass
- ✅ Performance not degraded

## Historical Context

### Classic BASIC Interpreters

**Microsoft BASIC (MBASIC, GW-BASIC, etc.):**
- Actually preserved spacing in line buffer!
- Stored lines as tokenized form + original text
- When LISTing, used original text (with spacing)
- Only re-formatted on RENUM or auto-number

**Modern Interpreters:**
- Often use AST + pretty printer
- Loses spacing information
- Users complain about reformatting

**Our approach:** Combine best of both:
- Modern AST architecture
- Classic spacing preservation

## Notes

- This is the RIGHT way to do it - preserve user's input
- We already have the information (token positions)
- Small implementation effort for big UX improvement
- Aligns with case preservation and type suffix preservation
- Users will appreciate their code staying the way they wrote it

## Priority Justification

**HIGH Priority** because:
1. User experience impact is significant
2. Data already available (token positions)
3. Implementation is straightforward
4. Related to recently completed type suffix fix
5. Part of "maintain fidelity to source" theme

Should be implemented after:
- Type suffix serialization fix ✅ (completed v1.0.85)

Should be implemented before:
- Settings system (doesn't depend on settings)
- Case-preserving variables (similar philosophy, should do together)

## Implementation Notes

When implementing, be careful with:
1. **Tab characters:** How are column positions counted?
2. **Multi-byte characters:** UTF-8 handling in column positions
3. **Line continuations:** If we ever support them
4. **Implicit line numbers:** Auto-numbered lines don't have positions

Test thoroughly with:
- Different spacing styles
- Edge cases (empty statements, etc.)
- Round-trip save/load
- RENUM operation
