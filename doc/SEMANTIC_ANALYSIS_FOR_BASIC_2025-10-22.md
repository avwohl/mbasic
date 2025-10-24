# Semantic Analysis for MBASIC 5.21

**Date**: 2025-10-22
**Question**: "Is there really a phase between parser and code generator? If so what does it do?"

---

## Short Answer

For MBASIC 5.21, you're **mostly right** - there's minimal traditional semantic analysis needed. However, there ARE some semantic checks and transformations that should happen between parsing and execution/codegen:

---

## What Traditional Semantic Analysis Does

In modern languages with scoping, types, declarations:

1. **Symbol table management** - Track variable declarations, scopes
2. **Type checking** - Verify type compatibility
3. **Scope resolution** - Resolve variable/function names
4. **Error detection** - Catch semantic errors (undeclared vars, type mismatches)

---

## Why BASIC Needs Less

You're correct that BASIC is simpler:

### ❌ No scope analysis needed
- All variables are global (no scoping)
- No need to track scope chains or closures

### ❌ No declaration checking needed
- Variables don't need to be declared (implicit declaration on first use)
- No "undeclared variable" errors

### ❌ Minimal type checking needed
- Types are dynamic (determined by suffix: $, %, !, #)
- Type coercion happens at runtime
- Parser already handles type suffixes

---

## What MBASIC *DOES* Need Between Parser and Execution

However, there ARE important semantic tasks for MBASIC:

### 1. Line Number Resolution ✓ NEEDED

**Issue**: GOTO/GOSUB use line numbers, but the AST has LineNodes

**Solution**: Build a line number table
```python
line_table = {
    10: line_node_1,
    20: line_node_2,
    30: line_node_3,
    ...
}
```

**Why needed**:
- `GOTO 50` needs to find which LineNode has line number 50
- `ON X GOTO 10,20,30` needs to resolve multiple line numbers
- `RESTORE 100` needs to find the DATA statement at line 100

### 2. DATA Statement Indexing ✓ NEEDED

**Issue**: READ statements need to know where DATA is

**Solution**: Build a DATA table
```python
data_items = [
    (10, "value1"),
    (10, "value2"),
    (20, 100),
    (20, 200),
    ...
]
data_pointer = 0  # Current READ position
```

**Why needed**:
- `READ A, B, C` needs to fetch from DATA statements
- `RESTORE` resets data pointer
- `RESTORE 100` sets pointer to DATA at line 100

### 3. DEF FN Function Table ✓ NEEDED

**Issue**: Function calls need to find function definitions

**Solution**: Build function definition table
```python
user_functions = {
    'FN.SQUARE': DefFnNode(...),
    'FN.CALC': DefFnNode(...),
}
```

**Why needed**:
- Parser sees `DEF FN.SQUARE(X) = X * X`
- Later code calls `Y = FN.SQUARE(5)`
- Need to find the definition and evaluate it

### 4. FOR Loop Stack Management ✓ NEEDED

**Issue**: NEXT needs to match with FOR

**Solution**: Track active FOR loops
```python
for_stack = [
    {'var': 'I', 'end': 10, 'step': 1, 'return_line': 50},
    {'var': 'J', 'end': 5, 'step': 1, 'return_line': 40},
]
```

**Why needed**:
- `FOR I = 1 TO 10` pushes loop info
- `NEXT I` pops and checks
- `NEXT` without variable pops innermost loop

### 5. GOSUB Return Stack ✓ NEEDED

**Issue**: RETURN needs to know where to go back to

**Solution**: Track GOSUB calls
```python
gosub_stack = [
    (calling_line=30, next_statement=1),
    (calling_line=50, next_statement=2),
]
```

**Why needed**:
- `GOSUB 1000` pushes return address
- `RETURN` pops and jumps back

### 6. ON ERROR Handler ⚠️ OPTIONAL

**Issue**: Error handling needs to track handler location

**Solution**: Track error handler
```python
error_handler_line = None  # Set by ON ERROR GOTO
error_occurred = False
```

### 7. Array Dimension Tracking ⚠️ OPTIONAL

**Issue**: Array access needs dimension info

**Solution**: Track array dimensions
```python
arrays = {
    'A': {'dims': [10], 'data': [...]},
    'B': {'dims': [5, 5], 'data': [...]},
}
```

**Why needed**:
- `DIM A(10)` creates array
- `A(5) = 100` needs bounds checking
- Can be done at runtime, but pre-indexing helps

---

## Proposed Architecture

### For INTERPRETER (runtime execution)

```
┌─────────┐    ┌────────┐    ┌──────────────────┐    ┌─────────────┐
│ Lexer   │ -> │ Parser │ -> │ Runtime Setup    │ -> │ Interpreter │
└─────────┘    └────────┘    └──────────────────┘    └─────────────┘
                                     │
                                     v
                              ┌──────────────┐
                              │ - Line table │
                              │ - DATA index │
                              │ - DEF FN map │
                              └──────────────┘
```

**Runtime Setup Phase**:
1. Build line number table (GOTO/GOSUB targets)
2. Index DATA statements (for READ)
3. Extract DEF FN definitions
4. Validate line number references exist

**Interpreter Phase**:
- Execute statements directly from AST
- Maintain runtime state (variables, stacks, etc.)
- Use line table for jumps
- Use DATA index for READ

### For COMPILER (ahead-of-time compilation)

```
┌─────────┐    ┌────────┐    ┌──────────────────┐    ┌─────────────┐
│ Lexer   │ -> │ Parser │ -> │ Semantic Analysis│ -> │ Code Gen    │
└─────────┘    └────────┘    └──────────────────┘    └─────────────┘
                                     │
                                     v
                              ┌──────────────┐
                              │ - Line table │
                              │ - DATA index │
                              │ - DEF FN map │
                              │ - Optimizations│
                              └──────────────┘
```

**Semantic Analysis Phase** (for compiler):
1. Build line number table
2. Index DATA statements
3. Extract DEF FN definitions
4. **Validate all GOTO/GOSUB targets exist**
5. **Validate all variables follow naming rules**
6. **Detect unreachable code** (optional optimization)
7. **Constant folding** (optional optimization)

**Code Generation Phase**:
- Translate AST to target language (Python, C, JavaScript, etc.)
- Use line table to generate labels
- Generate DATA initialization
- Inline or generate functions for DEF FN

---

## Minimal vs Full Semantic Analysis

### Minimal (sufficient for interpreter)
✓ Build line table
✓ Index DATA statements
✓ Extract DEF FN definitions

**Total**: ~100 lines of code

### Full (better for compiler)
✓ Everything from minimal, plus:
✓ Validate all GOTO/GOSUB targets exist (catch errors early)
✓ Validate variable names don't start with keywords
✓ Check FOR/NEXT pairing
✓ Detect infinite loops (optional)
✓ Constant folding (optional)
✓ Dead code elimination (optional)

**Total**: ~300-500 lines of code

---

## Recommendation

### For Interpreter (Phase 1)

**Use minimal semantic analysis**:

```python
class RuntimeSetup:
    """Prepare AST for execution"""

    def __init__(self, ast):
        self.ast = ast
        self.line_table = {}      # line_num -> LineNode
        self.data_items = []       # List of data values
        self.user_functions = {}   # fn_name -> DefFnNode

    def setup(self):
        """Single pass to prepare for execution"""
        for line in self.ast.lines:
            # Build line table
            self.line_table[line.line_number] = line

            # Process statements
            for stmt in line.statements:
                if isinstance(stmt, DataStatementNode):
                    self.data_items.extend(stmt.values)
                elif isinstance(stmt, DefFnStatementNode):
                    self.user_functions[stmt.name] = stmt

        return self
```

**That's it!** No complex semantic analysis needed for interpreter.

### For Compiler (Phase 2)

**Add validation**:

```python
class SemanticAnalyzer:
    """Validate and optimize AST before code generation"""

    def __init__(self, ast):
        self.ast = ast
        self.line_table = {}
        self.data_items = []
        self.user_functions = {}
        self.errors = []

    def analyze(self):
        """Multi-pass analysis"""
        self._build_tables()      # Pass 1: Build tables
        self._validate_jumps()    # Pass 2: Check GOTOs exist
        self._validate_loops()    # Pass 3: Check FOR/NEXT
        self._optimize()          # Pass 4: Optimizations

        if self.errors:
            raise SemanticError(self.errors)

        return self

    def _validate_jumps(self):
        """Ensure all GOTO/GOSUB targets exist"""
        for line in self.ast.lines:
            for stmt in line.statements:
                if isinstance(stmt, GotoStatementNode):
                    if stmt.line_number not in self.line_table:
                        self.errors.append(
                            f"Line {line.line_number}: "
                            f"GOTO to undefined line {stmt.line_number}"
                        )
```

---

## Conclusion

### Answer to Your Question

**For MBASIC interpreter**: You need a **lightweight setup phase** (not traditional "semantic analysis"):
- Build line number table (essential for GOTO/GOSUB)
- Index DATA statements (essential for READ)
- Extract DEF FN definitions (essential for function calls)

**For MBASIC compiler**: You want **semantic analysis** that adds:
- Validation (catch errors before code generation)
- Optimization (constant folding, dead code elimination)

### Implementation Order

1. **Interpreter** (Phase 1):
   - Start with minimal setup (~100 lines)
   - Get basic execution working
   - No complex analysis needed

2. **Compiler** (Phase 2):
   - Add validation (~200 lines)
   - Ensure correctness
   - Add optimizations as needed

### You're Right

You're correct that BASIC doesn't need traditional semantic analysis for:
- ❌ Scope resolution (no scoping)
- ❌ Type checking (dynamic types)
- ❌ Declaration checking (implicit variables)

But it DOES need:
- ✓ Line number resolution (for jumps)
- ✓ DATA indexing (for READ)
- ✓ Function definitions (for DEF FN)

Call it "runtime setup" for interpreter, "semantic analysis" for compiler - either way, it's a thin layer between parser and execution/codegen.
