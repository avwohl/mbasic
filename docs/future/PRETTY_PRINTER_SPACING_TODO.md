# Pretty Printer Spacing Options

⏳ **Status:** TODO

## Problem

The AST serialization code currently adds spaces after every token, making code very spaced out:

**Current output after renumber:**
```basic
10 x = x + 1
20 FOR i = 1 TO 10
30   PRINT i
40 NEXT i
```

This adds spaces everywhere:
- Around operators: `x = x + 1` (space before and after `=`, `+`)
- After keywords: `FOR `, `TO `, `NEXT `
- After commas in arrays: `DIM A( 10 , 20 )`

Some users prefer compact code:
```basic
10 x=x+1
20 FOR i=1 TO 10
30  PRINT i
40 NEXT i
```

Or semi-compact:
```basic
10 x = x+1
20 FOR i = 1 TO 10
30  PRINT i
40 NEXT i
```

## Affected Code

### Serialization Functions (src/ui/ui_helpers.py)

The serialization functions add spaces liberally:

**serialize_expression()** - Lines ~200-400
- Binary operators: `f"{left} {op} {right}"` → always adds spaces
- Function calls: `f"{name}({args})"` → no space before paren (correct)
- Array access: `f"{name}({subs})"` → no space before paren (correct)

**serialize_statement()** - Lines ~900-1150
- Assignment: `f"{var} = {expr}"` → spaces around `=`
- PRINT: `f"PRINT {items}"` → space after PRINT
- FOR: `f"FOR {var} = {start} TO {end}"` → spaces everywhere
- IF: `f"IF {cond} THEN {then_part}"` → spaces after keywords

### Root Cause

The serialization code uses f-strings with hardcoded spaces:
```python
return f"{left} {op} {right}"  # Always adds spaces
```

Should be configurable based on user preference.

## Proposed Solution

### 1. Add Spacing Configuration

Create a `PrettyPrintConfig` class:

```python
@dataclass
class PrettyPrintConfig:
    """Configuration for code pretty-printing"""
    # Spacing around operators
    space_around_assignment = True      # x = 1 vs x=1
    space_around_arithmetic = True      # x + 1 vs x+1
    space_around_comparison = True      # x > 5 vs x>5
    space_around_logical = True         # A AND B vs A AND B (always need space)

    # Spacing after keywords
    space_after_keyword = True          # PRINT x vs PRINTx (always need space)

    # Spacing in lists
    space_after_comma = True            # DIM A(10, 20) vs DIM A(10,20)

    # Spacing in subscripts
    space_in_subscripts = False         # A(10) vs A( 10 )

    # Preset modes
    @classmethod
    def compact(cls):
        """Minimal spacing"""
        return cls(
            space_around_assignment=False,
            space_around_arithmetic=False,
            space_around_comparison=False,
            space_around_logical=True,  # Required for keywords
            space_after_keyword=True,   # Required
            space_after_comma=False,
            space_in_subscripts=False
        )

    @classmethod
    def normal(cls):
        """Balanced spacing (default)"""
        return cls()

    @classmethod
    def spacious(cls):
        """Maximum spacing"""
        return cls(
            space_in_subscripts=True
        )
```

### 2. Update Serialization Functions

Modify serialize functions to accept config:

```python
def serialize_expression(expr, config=None):
    if config is None:
        config = PrettyPrintConfig.normal()

    if expr_type == 'BinaryOpNode':
        left = serialize_expression(expr.left, config)
        right = serialize_expression(expr.right, config)
        op = token_to_operator(expr.operator)

        # Determine spacing based on operator type and config
        if expr.operator in ARITHMETIC_OPS:
            if config.space_around_arithmetic:
                return f"{left} {op} {right}"
            else:
                return f"{left}{op}{right}"
        elif expr.operator in COMPARISON_OPS:
            if config.space_around_comparison:
                return f"{left} {op} {right}"
            else:
                return f"{left}{op}{right}"
        # etc.
```

### 3. Add UI Configuration

**TK UI:**
- Add to Edit menu: "Preferences" → "Code Formatting"
- Dialog with checkboxes for spacing options
- Radio buttons for presets (Compact / Normal / Spacious)
- Save preferences to config file

**Command-line option:**
```bash
python mbasic --format=compact program.bas
python mbasic --format=normal program.bas
python mbasic --format=spacious program.bas
```

### 4. Apply to RENUM Command

When renumbering, use the configured spacing:

```python
def cmd_renum(self, args):
    # ... existing code ...

    # Get user's spacing preference
    config = self.get_pretty_print_config()

    # Serialize with config
    for line_num, line_node in self.program.lines.items():
        source = serialize_line(line_node, config)
        # ...
```

## Implementation Plan

### Phase 1: Core Config (HIGH priority)
1. Create `PrettyPrintConfig` class in `src/formatting.py`
2. Add config parameter to serialize functions
3. Set default to current behavior (normal spacing)

### Phase 2: Basic Presets (MEDIUM priority)
4. Implement compact/normal/spacious presets
5. Add command-line option `--format`
6. Test with renumber command

### Phase 3: UI Integration (LOW priority)
7. Add preferences dialog to TK UI
8. Save preferences to `~/.mbasic_config.json`
9. Load preferences on startup

## Testing

Test with various programs:

```basic
10 x=x+1
20 y$="hello"
30 DIM A(10,20)
40 FOR i=1 TO 10
50   FOR j=1 TO 20
60     A(i,j)=i*j
70   NEXT j
80 NEXT i
90 IF x>5 AND y<10 THEN PRINT "yes" ELSE PRINT "no"
```

Verify each preset produces correct output:

**Compact:**
```basic
10 x=x+1
20 y$="hello"
30 DIM A(10,20)
40 FOR i=1 TO 10
```

**Normal (current):**
```basic
10 x = x + 1
20 y$ = "hello"
30 DIM A(10, 20)
40 FOR i = 1 TO 10
```

**Spacious:**
```basic
10 x = x + 1
20 y$ = "hello"
30 DIM A( 10, 20 )
40 FOR i = 1 TO 10
```

## Notes

- ALWAYS need space after keywords (PRINT, FOR, IF, etc.) - no option for this
- ALWAYS need space around logical operators (AND, OR, NOT) - they're keywords
- Be careful with negative numbers: `x=-1` could be confused with `x-=1`
- Consider keeping space around `=` even in compact mode for readability

## Priority

**MEDIUM** - Not urgent, but affects code readability and user experience. Should be implemented after critical bugs are fixed.

## Related Files

- `src/ui/ui_helpers.py` - serialize_expression(), serialize_statement()
- `src/interactive.py` - _serialize_line() (calls ui_helpers)
- `src/ui/tk_ui.py` - Would add preferences dialog
- `docs/user/` - Would add documentation for formatting options
