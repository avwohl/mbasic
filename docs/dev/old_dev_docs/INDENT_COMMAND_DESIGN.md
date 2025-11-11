# INDENT Command Design

## Overview

A new command to automatically adjust line indentation based on lexical loop nesting.

## Syntax

```basic
INDENT                    - Indent entire program
INDENT start-end          - Indent line range
INDENT start-             - Indent from start to end of program
INDENT -end               - Indent from beginning to end line
```

## Examples

### Before INDENT:
```basic
10 FOR I = 1 TO 10
20 PRINT I
30 FOR J = 1 TO 5
40 PRINT I * J
50 NEXT J
60 NEXT I
70 PRINT "DONE"
```

### After INDENT:
```basic
10 FOR I = 1 TO 10
20   PRINT I
30   FOR J = 1 TO 5
40     PRINT I * J
50   NEXT J
60 NEXT I
70 PRINT "DONE"
```

## Nesting Rules

### Structures That Increase Indent

1. **FOR...NEXT**
   - `FOR` increases indent level
   - Lines between FOR and NEXT are indented
   - `NEXT` returns to FOR's indent level

2. **WHILE...WEND**
   - `WHILE` increases indent level
   - Lines between WHILE and WEND are indented
   - `WEND` returns to WHILE's indent level

3. **Multi-line IF...THEN**
   - `IF...THEN line_number` - No indentation (GOTO style)
   - `IF...THEN` with statements on next line - Increases indent
   - Problem: MBASIC doesn't have ENDIF, so how to detect end of IF block?
   - **Solution**: Don't indent IF blocks in MBASIC (too ambiguous)

### Structures That Don't Increase Indent

1. **GOSUB...RETURN**
   - Not lexical scope (can jump anywhere)
   - Subroutines stay at base indent level

2. **ON...GOTO/GOSUB**
   - Computed jumps, not loops
   - No indentation change

3. **Single-line statements**
   - `IF X THEN PRINT Y` - No indentation
   - Multiple statements separated by `:` - Same indent

## Algorithm

### Step 1: Calculate Nesting Levels

```python
def calculate_indent_levels(line_numbers):
    """Calculate indent level for each line based on nesting."""
    indent_levels = {}
    current_level = 0
    stack = []  # Track FOR/WHILE nesting

    for line_num in sorted(line_numbers):
        line_node = program.line_asts[line_num]

        # Check if this line closes a loop
        for stmt in line_node.statements:
            if isinstance(stmt, NextStatementNode):
                # NEXT closes FOR loop(s)
                if stack and stack[-1][0] == 'FOR':
                    current_level = stack[-1][1]  # Return to FOR level
                    stack.pop()
            elif isinstance(stmt, WendStatementNode):
                # WEND closes WHILE loop
                if stack and stack[-1][0] == 'WHILE':
                    current_level = stack[-1][1]  # Return to WHILE level
                    stack.pop()

        # Assign indent level to this line
        indent_levels[line_num] = current_level

        # Check if this line opens a loop
        for stmt in line_node.statements:
            if isinstance(stmt, ForStatementNode):
                stack.append(('FOR', current_level))
                current_level += 1
            elif isinstance(stmt, WhileStatementNode):
                stack.append(('WHILE', current_level))
                current_level += 1

    return indent_levels
```

### Step 2: Apply Indentation

```python
def apply_indentation(line_numbers, indent_levels, indent_size=2):
    """Apply calculated indent levels to program lines."""
    for line_num in line_numbers:
        line_node = program.line_asts[line_num]

        # Calculate spaces needed
        spaces = indent_size * indent_levels[line_num]

        # Update source_text to reflect new indentation
        # This preserves the indentation through serialization
        # (Implementation detail: modify source_text directly)

        # Re-serialize with new indentation
        serialized = serialize_line_with_indent(line_node, spaces)
        program.lines[line_num] = serialized
```

### Step 3: Handle Edge Cases

1. **Unmatched loops**
   - Extra NEXT without FOR - Warning, no indent change
   - Extra WEND without WHILE - Warning, no indent change
   - FOR without NEXT - Warning, continue with increased indent

2. **Multiple NEXT variables**
   - `NEXT I, J, K` closes 3 FOR loops
   - Pop 3 levels from stack

3. **NEXT without variable**
   - `NEXT` closes most recent FOR
   - Pop 1 level from stack

4. **Line range that splits loop**
   - `INDENT 25-35` where FOR is at 20 and NEXT is at 40
   - **Option A**: Refuse (error: "Cannot indent partial loop")
   - **Option B**: Indent anyway (user's responsibility)
   - **Recommendation**: Option B with warning

## Configuration

### Indent Size

Default: 2 spaces per level
Configurable via:
- Global setting: `OPTION INDENT 4`
- Per-command: `INDENT 10-100, 4`

### Maximum Indent Level

Cap at reasonable level (e.g., 10 levels = 20 spaces)
Prevents ridiculous indentation from deeply nested or unmatched loops

## Implementation Notes

### Preserve Source Text

The current AST serialization uses `source_text` to extract relative indentation.
INDENT command must update `source_text` field in LineNode to preserve new indentation.

```python
# After calculating new indentation
new_source = f"{line_num}{' ' * new_indent}{statement_text}"
line_node.source_text = new_source
```

### Integration with RENUM

INDENT and RENUM should work together:
```basic
RENUM 100, 10, 10      - Renumber lines
INDENT                 - Auto-format based on structure
```

RENUM preserves relative indentation (existing behavior)
INDENT creates new relative indentation (new behavior)

### UI Integration

All UIs should support INDENT command:
- CLI: `INDENT` command
- Tk: Edit menu → "Auto-Indent" or keyboard shortcut
- Web: Edit menu → "Auto-Indent" button
- Curses: Ctrl+I for auto-indent

## Test Cases

### Test 1: Simple FOR Loop
```basic
Before:
10 FOR I=1 TO 5
20 PRINT I
30 NEXT I

After (indent=2):
10 FOR I=1 TO 5
20   PRINT I
30 NEXT I
```

### Test 2: Nested FOR Loops
```basic
Before:
10 FOR I=1 TO 3
20 FOR J=1 TO 2
30 PRINT I*J
40 NEXT J
50 NEXT I

After (indent=2):
10 FOR I=1 TO 3
20   FOR J=1 TO 2
30     PRINT I*J
40   NEXT J
50 NEXT I
```

### Test 3: Multiple NEXT
```basic
Before:
10 FOR I=1 TO 3
20 FOR J=1 TO 2
30 PRINT I*J
40 NEXT J,I

After (indent=2):
10 FOR I=1 TO 3
20   FOR J=1 TO 2
30     PRINT I*J
40 NEXT J,I
```

### Test 4: WHILE Loop
```basic
Before:
10 I=1
20 WHILE I<=5
30 PRINT I
40 I=I+1
50 WEND

After (indent=2):
10 I=1
20 WHILE I<=5
30   PRINT I
40   I=I+1
50 WEND
```

### Test 5: Mixed Nesting
```basic
Before:
10 FOR I=1 TO 3
20 WHILE I<10
30 PRINT I
40 I=I+1
50 WEND
60 NEXT I

After (indent=2):
10 FOR I=1 TO 3
20   WHILE I<10
30     PRINT I
40     I=I+1
50   WEND
60 NEXT I
```

### Test 6: Multiple Statements Per Line
```basic
Before:
10 FOR I=1 TO 5 : PRINT I : NEXT I

After (indent=2):
10 FOR I=1 TO 5 : PRINT I : NEXT I
   (No change - single line with multiple statements)
```

### Test 7: Comments
```basic
Before:
10 FOR I=1 TO 5    ' Start loop
20 PRINT I    ' Print value
30 NEXT I    ' End loop

After (indent=2):
10 FOR I=1 TO 5    ' Start loop
20   PRINT I    ' Print value
30 NEXT I    ' End loop
```

### Test 8: Partial Range
```basic
Program:
10 X=0
20 FOR I=1 TO 5
30 PRINT I
40 NEXT I
50 PRINT "DONE"

Command: INDENT 30-40

Result:
10 X=0
20 FOR I=1 TO 5
30   PRINT I      <- Indented (inside FOR loop)
40 NEXT I         <- Base level (warning: partial loop)
50 PRINT "DONE"
```

## Open Questions

1. **Should GOSUB/RETURN indent subroutines?**
   - Pro: Visual separation of subroutines
   - Con: Not lexical scope, jumps can go anywhere
   - **Recommendation**: No, keep GOSUB at base level

2. **Should single-line IF...THEN...ELSE indent?**
   - `10 IF X THEN PRINT "YES" ELSE PRINT "NO"`
   - **Recommendation**: No, it's a single statement

3. **Should we support manual indent markers?**
   - Special comments like `' INDENT+` and `' INDENT-`
   - Allows user to control indentation manually
   - **Recommendation**: Not in initial version

4. **Should INDENT be undoable?**
   - Store previous indentation for UNDO?
   - **Recommendation**: Yes, if we implement general UNDO

5. **Should we warn about unmatched loops?**
   - FOR without NEXT
   - WHILE without WEND
   - NEXT without FOR
   - **Recommendation**: Yes, show warnings but continue

## Compatibility

### Real MBASIC 5.21

Real MBASIC 5.21 does not have an INDENT command.
This is a quality-of-life enhancement for modern usage.

Similar to:
- Auto-format in modern IDEs
- `gofmt` for Go
- `black` for Python
- `prettier` for JavaScript

### Other BASIC Variants

Some modern BASIC IDEs have auto-indent features, but no standard command.
Our INDENT command would be unique to this implementation.

## Implementation Phases

### Phase 1: Basic Implementation
- Support FOR...NEXT and WHILE...WEND
- Fixed indent size (2 spaces)
- Whole program only (`INDENT` with no args)

### Phase 2: Range Support
- Line range syntax: `INDENT start-end`
- Partial range warnings

### Phase 3: Configuration
- Configurable indent size
- Per-command indent size override

### Phase 4: Advanced Features
- Undo support
- UI integration (menu items, keyboard shortcuts)
- Preview mode (show what would change)

## Files to Modify

1. `src/interactive.py` - Add `cmd_indent()` command
2. `src/ui/ui_helpers.py` - Add `calculate_indent_levels()` and `apply_indentation()` helpers
3. `src/ui/tk_ui.py` - Add Edit menu → "Auto-Indent"
4. `src/ui/web_ui.py` - Add Edit menu → "Auto-Indent"
5. `src/ui/curses_ui.py` - Add Ctrl+I keyboard shortcut
6. `docs/help/common/commands/indent.md` - User documentation

## Related Work

Similar to the recent RENUM fix, this leverages AST serialization to modify
program structure while preserving correctness.

Key difference:
- RENUM modifies line numbers (structural change)
- INDENT modifies whitespace (cosmetic change)

Both rely on:
- AST as source of truth
- Serialization with formatting preservation
- source_text field for indentation tracking
