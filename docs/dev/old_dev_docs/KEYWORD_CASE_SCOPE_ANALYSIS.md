# Keyword Case Scope Analysis

**Date:** 2025-10-28
**Version:** 1.0.153
**Status:** ✅ Implementation Correct

## User Concern

User raised a valid question about keyword case conflict scope:
> "look into how immediate mode works vs the program. what happens if the user says run in lower case but in the program it is Run. conflicts and case token setting should be limited to inside the program. variables share case immediate mode and program but keywords do not."

## Analysis Summary

**Conclusion: The implementation is already correct!**

Keyword case managers are properly scoped:
- Each tokenization creates a fresh `KeywordCaseManager`
- Immediate mode and program mode DO NOT share keyword case state
- Variables correctly share scope (runtime state)
- Keywords correctly do NOT share scope (syntax state)

## How Tokenization Works

### 1. Program Mode (Running Whole Program)

**Location:** `src/ui/tk_ui.py:743`
```python
keyword_mgr = create_keyword_case_manager()
lexer = Lexer(program_text, keyword_case_manager=keyword_mgr)
tokens = lexer.tokenize()
```

- Creates NEW KeywordCaseManager
- Tokenizes entire program at once
- Case conflicts detected WITHIN the program
- Scope: **All lines in the program**

### 2. Immediate Mode (No Line Number)

**Location:** `src/immediate_executor.py:208`
```python
tokens = list(tokenize(program_text))
```

Which calls `src/lexer.py:504`:
```python
def tokenize(source: str) -> List[Token]:
    keyword_mgr = create_keyword_case_manager()
    lexer = Lexer(source, keyword_case_manager=keyword_mgr)
    return lexer.tokenize()
```

- Creates NEW KeywordCaseManager
- Tokenizes single immediate command
- Scope: **Only that immediate command**

### 3. Adding Program Line from Immediate (Has Line Number)

**Location:** `src/editing/manager.py:360`
```python
tokens = list(tokenize(line_text))
parser = Parser(tokens, self.def_type_map, source=line_text)
line_node = parser.parse_line()
```

- Creates NEW KeywordCaseManager
- Tokenizes single program line
- Scope: **Only that one line**

## Scope Boundaries

```
┌─────────────────────────────────────────┐
│  Program Mode (RUN command)             │
│  ┌───────────────────────────────────┐  │
│  │ Single Tokenization               │  │
│  │ KeywordCaseManager #1             │  │
│  │                                   │  │
│  │ 10 PRINT "First"    ← same scope │  │
│  │ 20 print "Second"   ← CONFLICT!  │  │
│  │ 30 PRINT "Third"    ← same scope │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│  Immediate Mode                         │
│  ┌───────────────────────────────────┐  │
│  │ Tokenization #2                   │  │
│  │ KeywordCaseManager #2             │  │
│  │                                   │  │
│  │ run ← different scope, NO conflict│  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│  Adding Line from Immediate             │
│  ┌───────────────────────────────────┐  │
│  │ Tokenization #3                   │  │
│  │ KeywordCaseManager #3             │  │
│  │                                   │  │
│  │ 40 print "Fourth" ← different scope│ │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

## Test Results

Created comprehensive test suite: `tests/regression/lexer/test_keyword_case_scope_isolation.py`

**All 7 tests pass:**
```bash
$ python3 tests/regression/lexer/test_keyword_case_scope_isolation.py
test_adding_lines_individually ... ok
test_conflict_within_same_tokenization ... ok
test_consistent_case_no_error ... ok
test_immediate_mode_simulation ... ok
test_multiple_keywords_same_line ... ok
test_separate_tokenizations_isolated ... ok
test_whole_program_tokenization ... ok

Ran 7 tests in 0.001s
OK
```

## Examples

### ✅ CORRECT: Immediate vs Program (Different Scopes)

```basic
Program contains:
10 RUN

Immediate mode:
> run

Result: No error (different scopes)
```

### ✅ CORRECT: Conflict Within Program (Same Scope)

```basic
10 PRINT "test"
20 print "test"

Result: ERROR - Case conflict: 'print' at line 2:4 vs 'PRINT' at line 1:4
```

### ✅ CORRECT: Adding Lines Individually (Different Scopes)

```basic
Immediate mode (adding lines):
> 10 PRINT "test"  ← Tokenization #1
> 20 print "test"  ← Tokenization #2 (different scope!)
> 30 PRINT "test"  ← Tokenization #3

Result: No errors (each line is separate scope)

But when you RUN the program:
→ ERROR - Case conflict (now in same scope!)
```

## Why This Design is Correct

### Variables Share Scope (Runtime State)
```basic
Immediate mode:
> X = 100

Program:
10 PRINT X  ← Sees X=100 from immediate mode

✓ CORRECT: Variables share runtime state
```

### Keywords Don't Share Scope (Syntax State)
```basic
Immediate mode:
> print "hello"  ← Uses lowercase PRINT

Program:
10 PRINT "world"  ← Uses uppercase PRINT

✓ CORRECT: Keywords don't share syntax state
→ No conflict (different tokenizations)
```

## Implementation Details

**Key function:** `create_keyword_case_manager()` in `src/lexer.py:10`
```python
def create_keyword_case_manager() -> KeywordCaseManager:
    """Create a KeywordCaseManager configured from settings."""
    try:
        from src.settings import get
        policy = get("keywords.case_style", "force_lower")
        return KeywordCaseManager(policy=policy)
    except Exception:
        return KeywordCaseManager(policy="force_lower")
```

**Called from:**
1. `tokenize()` function - Used by immediate mode and line editing
2. `Lexer()` constructor - Used when running whole program
3. Each call creates a **fresh** manager with **empty** case table

**Result:** Each tokenization is isolated!

## Potential Confusion

The user's concern likely comes from thinking about MBASIC's traditional behavior:
- In classic MBASIC, the entire session might share keyword case state
- Modern implementation uses stateless tokenization
- Each parse/tokenize is independent

## Edge Cases Handled

### 1. Multiple Keywords Same Line
```basic
10 IF X>0 THEN print "yes" ELSE PRINT "no"
                    ^                  ^
                lowercase          uppercase
                → ERROR (same line, same tokenization)
```

### 2. Line-by-Line Entry vs Batch
```basic
# Entering lines one at a time:
> 10 PRINT "test"  ← OK (tokenization #1)
> 20 print "test"  ← OK (tokenization #2)

# Running program:
> RUN              ← ERROR (tokenization #3 includes both lines)
```

### 3. Program Edit During Execution
```basic
Program running with PRINT (uppercase)

Immediate mode during pause:
> 100 print "debug"  ← OK (separate tokenization)

Continue program:
→ Still OK (edit doesn't affect running program's tokens)
```

## Related Tests

- `tests/regression/lexer/test_keyword_case_settings_integration.py` - Settings integration
- `tests/regression/lexer/test_keyword_case_policies.py` - Policy behavior
- `tests/regression/lexer/test_keyword_case_scope_isolation.py` - **Scope isolation (NEW)**

## Conclusion

**No changes needed!** The implementation is already correct:

✅ Immediate mode uses separate KeywordCaseManager
✅ Program mode uses separate KeywordCaseManager
✅ Each tokenization is isolated
✅ Case conflicts only detected within same scope
✅ Variables correctly share state (runtime)
✅ Keywords correctly don't share state (syntax)

The design properly distinguishes between:
- **Runtime state** (variables, program counter) → Shared
- **Syntax state** (keyword case tracking) → Not shared

User's concern was valid to raise, but the implementation handles it correctly!
