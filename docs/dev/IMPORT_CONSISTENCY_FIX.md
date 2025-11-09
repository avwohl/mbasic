# Import Consistency Fix

## Problem
Parse errors occurred when loading BASIC programs, showing:
```
Parse error at line 10: None
Parse error at line 20: None
```

## Root Cause
**Module dual-import issue**: Python loaded `src/tokens.py` twice as separate modules:
- Once as `tokens` (via `from tokens import TokenType`)
- Once as `src.tokens` (via `from src.tokens import TokenType`)

This created two separate `TokenType` enum classes in memory. When the lexer created tokens with one TokenType and the parser tried to match them with the other, comparisons failed:

```python
token.type == TokenType.LINE_NUMBER  # False! Different objects
```

## Why It Happened
The `mbasic` script does `sys.path.insert(0, 'src')` which allows importing modules both ways:
- `from tokens import X` - loads as module 'tokens'
- `from src.tokens import X` - loads as module 'src.tokens'

Python's import system doesn't prevent this - it treats them as different modules.

## The Fix
Made all imports consistent - always use `from src.MODULE import`:

**Files fixed:**
- `src/lexer.py:9` - Changed `from tokens import` → `from src.tokens import`
- `src/lexer.py:10` - Changed `from simple_keyword_case import` → `from src.simple_keyword_case import`
- `src/semantic_analyzer.py:22` - Changed `from ast_nodes import` → `from src.ast_nodes import`
- `src/semantic_analyzer.py:23` - Already correct: `from src.tokens import`

## Python Import Best Practices

### The Problem: Dual Imports
```python
sys.path.insert(0, 'src')

# These load the SAME file as DIFFERENT modules:
from tokens import TokenType       # Creates 'tokens' module
from src.tokens import TokenType   # Creates 'src.tokens' module

# Result: Two separate TokenType classes!
```

### The Solution: Consistency
Always use the same import path throughout the codebase:

**Option 1: Absolute imports with prefix** (what we use)
```python
from src.tokens import TokenType
from src.ast_nodes import *
from src.parser import Parser
```

**Option 2: Relative imports** (alternative)
```python
# Within src/ files only:
from .tokens import TokenType
from .ast_nodes import *
```

### Detection
Python doesn't detect or prevent dual imports. You can check if it's happening:
```python
import sys
print('tokens' in sys.modules)      # True if imported as 'tokens'
print('src.tokens' in sys.modules)  # True if imported as 'src.tokens'
# Both True = dual import problem!
```

### Why Python Doesn't Prevent This
- It's a deliberate design choice
- Allows package aliasing and flexibility
- But requires discipline to avoid gotchas
- The responsibility is on the developer to be consistent

## Symptoms of Dual Import
- Enum/class comparisons fail mysteriously
- `isinstance()` checks fail
- Identity checks (`is`) fail
- Equality checks (`==`) fail for enums
- Everything "looks" correct when printed

## Verification
```bash
# Should work now:
venv/bin/python3 mbasic --ui cli test.bas

# All backends working:
venv/bin/python3 mbasic --list-backends
```

## Date Fixed
2025-11-09
