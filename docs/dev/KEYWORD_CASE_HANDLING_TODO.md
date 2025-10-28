# Keyword Case Handling - TODO

⏳ **Status**: TODO

## Overview

Extend the case conflict handling system to support keywords (PRINT, FOR, IF, etc.) with separate configuration from variable case handling.

## Current State

- Variables have case conflict handling via `variables.case_conflict` setting
- Keywords are currently normalized to lowercase by the lexer
- No tracking or preservation of original keyword case

## Proposed Implementation

### New Setting: `keywords.case_style`

Add to `src/settings_definitions.py`:

```python
"keywords.case_style": SettingDefinition(
    key="keywords.case_style",
    type=SettingType.ENUM,
    default="force_lower",
    choices=["force_lower", "force_upper", "first_wins", "error", "preserve"],
    description="How to handle keyword case in source code",
    help_text="""Controls how keywords are displayed and validated.

- force_lower: Convert all keywords to lowercase (default, MBASIC 5.21 style)
- force_upper: Convert all keywords to UPPERCASE (classic BASIC style)
- first_wins: First occurrence sets case for that keyword throughout program
- error: Flag case inconsistencies as errors
- preserve: Keep each keyword exactly as typed (modern style)

Example with force_upper:
  10 print "hello"  -> 10 PRINT "hello"
  20 Print "world"  -> 20 PRINT "world"

Example with first_wins:
  10 Print "hello"  -> 10 Print "hello"
  20 PRINT "world"  -> 20 Print "world"  (uses first case)

Example with error:
  10 Print "hello"
  20 PRINT "world"  -> ERROR: Keyword case conflict!
""",
    scope=SettingScope.PROJECT,
)
```

### Policies Explained

1. **force_lower** (default)
   - All keywords normalized to lowercase
   - Matches MBASIC 5.21 behavior
   - `PRINT`, `Print`, `print` all become `print`

2. **force_upper**
   - All keywords normalized to uppercase
   - Classic BASIC style
   - `PRINT`, `Print`, `print` all become `PRINT`

3. **first_wins**
   - First occurrence of each keyword sets its case
   - Subsequent uses displayed with first case
   - `PRINT` first → all become `PRINT`, else `Print` first → all become `Print`

4. **error**
   - Raise error if same keyword appears with different cases
   - Forces consistency
   - Useful for teams with style guidelines

5. **preserve**
   - Keep each keyword exactly as typed
   - No normalization
   - Most flexible but can look inconsistent

### Implementation Steps

1. **Token Enhancement** (`src/tokens.py`)
   - Add `original_case_keyword` field to Token (similar to `original_case`)
   - Lexer stores original keyword case before normalization

2. **Lexer Changes** (`src/lexer.py`)
   - Store original keyword case in token
   - Keep current lowercase normalization in `token.value`
   - New: `token.original_case_keyword = "PRINT"` (for example)

3. **Runtime Tracking** (`src/runtime.py`)
   - Add `_keyword_case_map`: Dict[str, str]
     - Maps normalized keyword → canonical case
   - Add `_keyword_case_variants`: Dict[str, List[Tuple[str, int, int]]]
     - Tracks all case variants seen per keyword (for debugging/error messages)
   - Add `_check_keyword_case_conflict()` method
     - Similar to `_check_case_conflict()` but for keywords

4. **Parser Integration** (`src/parser.py`)
   - Parse-time case checking if `keywords.case_style == "error"`
   - Store canonical keyword case in AST nodes
   - New field: `keyword_case` on statement nodes?

5. **Serializer Updates** (`src/position_serializer.py`, `src/ui/ui_helpers.py`)
   - Output keywords using canonical case from runtime
   - Respect `keywords.case_style` setting

6. **Statement Node Enhancement** (`src/ast_nodes.py`)
   - Add `original_keyword_case` field to statement nodes
   - Example: `IfStatementNode.original_keyword_case = "If"` (if typed as `If`)

### Key Differences from Variable Case Handling

| Aspect | Variables | Keywords |
|--------|-----------|----------|
| Default Policy | `first_wins` | `force_lower` |
| Historical Basis | Modern enhancement | Follows MBASIC 5.21 |
| Scope | Per-variable tracking | Per-keyword-type tracking |
| Error Impact | Runtime error | Parse-time error (optional) |
| Common Use | Mixed case names | Consistent style |

### Testing Strategy

1. **Unit Tests** (`test_keyword_case_unit.py`)
   - Test each policy independently
   - Test case conflict detection
   - Test error reporting with line numbers

2. **Integration Tests** (`test_keyword_case_integration.py`)
   - Parse programs with mixed keyword cases
   - Verify serialization outputs correct case
   - Test interaction with settings system

3. **Edge Cases**
   - Keywords in strings (should not affect)
   - Keywords in comments (should not affect)
   - Reserved words used as variable names (shouldn't conflict)

### Example Programs

**Input with `force_lower`:**
```basic
10 PRINT "Hello"
20 Print "World"
30 print "!"
```

**Output:**
```basic
10 print "Hello"
20 print "World"
30 print "!"
```

**Input with `force_upper`:**
```basic
10 print "Hello"
20 Print "World"
30 PRINT "!"
```

**Output:**
```basic
10 PRINT "Hello"
20 PRINT "World"
30 PRINT "!"
```

**Input with `first_wins`:**
```basic
10 Print "Hello"
20 PRINT "World"
30 print "!"
```

**Output:**
```basic
10 Print "Hello"
20 Print "World"
30 Print "!"
```

**Input with `error`:**
```basic
10 Print "Hello"
20 PRINT "World"
```

**Error:**
```
Keyword case conflict at line 20: 'PRINT' vs 'Print' at line 10
```

## Implementation Complexity

**Estimated Effort:** Medium (4-6 hours)

**Complexity Factors:**
- Similar to variable case handling (proven pattern)
- Lexer already tracks token types
- Serializers already handle token output
- Main work: tracking and policy enforcement

## Benefits

1. **Style Consistency**: Enforce team/project coding standards
2. **Readability**: Choose case style that matches project conventions
3. **Historical Accuracy**: Option to match MBASIC 5.21 or classic BASIC styles
4. **Flexibility**: Developers can choose what works for them

## Risks

1. **Performance**: Minimal - case checking is fast
2. **Complexity**: Adds another setting to learn
3. **Migration**: Existing code may need case adjustments if changing policies

## Priority

**Low-Medium** - Nice to have feature, complements variable case handling

## Notes

- Variable case and keyword case are **independent** settings
- Keywords include: PRINT, IF, FOR, WHILE, GOSUB, RETURN, etc.
- Does not affect string literals or comments
- Default (`force_lower`) maintains backward compatibility

## Related Work

- Variable case conflict handling (v1.0.106-109) - ✅ COMPLETED
- Settings system (v1.0.104-105) - ✅ COMPLETED
- Position-aware serialization (v1.0.89) - ✅ COMPLETED
