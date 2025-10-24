# Interpreter and Compiler Architecture Plan

**Date**: 2025-10-22
**Goal**: Create separate interpreter and compiler, both using same lexer/parser

---

## Current State

We have:
- ✓ **Lexer** (`src/lexer.py`) - Tokenizes BASIC source
- ✓ **Parser** (`src/parser.py`) - Produces AST
- ✓ **AST Nodes** (`src/ast_nodes.py`) - All statement/expression types
- ✓ **100% parsing** of valid MBASIC 5.21 programs

We need:
- ⚠ **Interpreter** - Execute BASIC programs directly
- ⚠ **Compiler** - Generate code in target language

---

## Shared Architecture

Both interpreter and compiler will share:

```
┌─────────────┐
│   Source    │
│  .bas file  │
└──────┬──────┘
       │
       v
┌─────────────┐
│   Lexer     │  <- SHARED (src/lexer.py)
│  tokenize() │
└──────┬──────┘
       │
       v
┌─────────────┐
│   Parser    │  <- SHARED (src/parser.py)
│   parse()   │
└──────┬──────┘
       │
       v
┌─────────────┐
│     AST     │  <- SHARED (src/ast_nodes.py)
│ ProgramNode │
└──────┬──────┘
       │
       ├──────────────────┐
       │                  │
       v                  v
┌─────────────┐    ┌─────────────┐
│ Interpreter │    │  Compiler   │
│   (NEW)     │    │   (NEW)     │
└─────────────┘    └─────────────┘
```

---

## Interpreter Architecture (Phase 1)

### File Structure

```
src/
  lexer.py              # Existing
  parser.py             # Existing
  ast_nodes.py          # Existing
  tokens.py             # Existing

  runtime.py            # NEW - Runtime state
  interpreter.py        # NEW - Main interpreter
  builtins.py           # NEW - Built-in functions
```

### Components

#### 1. Runtime State (`src/runtime.py`)

Manages program execution state:

```python
class Runtime:
    """Runtime state for BASIC program execution"""

    def __init__(self, ast):
        self.ast = ast

        # Execution state
        self.variables = {}           # Variable storage
        self.arrays = {}              # Array storage
        self.current_line = None      # Current line being executed
        self.halted = False           # Program halted?

        # Control flow
        self.line_table = {}          # line_num -> LineNode
        self.gosub_stack = []         # Return addresses
        self.for_loops = []           # Active FOR loops

        # Data statements
        self.data_items = []          # All DATA values
        self.data_pointer = 0         # READ position

        # Functions
        self.user_functions = {}      # DEF FN definitions

        # I/O
        self.input_buffer = None      # For INPUT
        self.files = {}               # Open files

    def setup(self):
        """Initialize runtime (build tables)"""
        for line in self.ast.lines:
            self.line_table[line.line_number] = line

            for stmt in line.statements:
                if isinstance(stmt, DataStatementNode):
                    self.data_items.extend(stmt.values)
                elif isinstance(stmt, DefFnStatementNode):
                    self.user_functions[stmt.name] = stmt
```

#### 2. Interpreter (`src/interpreter.py`)

Executes AST nodes:

```python
class Interpreter:
    """Interpret MBASIC AST"""

    def __init__(self, runtime):
        self.runtime = runtime

    def run(self):
        """Execute the program"""
        self.runtime.setup()

        # Execute lines in order
        for line in self.runtime.ast.lines:
            self.runtime.current_line = line

            for stmt in line.statements:
                self.execute_statement(stmt)

                if self.runtime.halted:
                    return

    def execute_statement(self, stmt):
        """Execute a single statement"""
        if isinstance(stmt, PrintStatementNode):
            self.execute_print(stmt)
        elif isinstance(stmt, LetStatementNode):
            self.execute_let(stmt)
        elif isinstance(stmt, IfStatementNode):
            self.execute_if(stmt)
        elif isinstance(stmt, GotoStatementNode):
            self.execute_goto(stmt)
        elif isinstance(stmt, ForStatementNode):
            self.execute_for(stmt)
        # ... etc for all statement types

    def execute_print(self, stmt):
        """Execute PRINT statement"""
        output = []
        for expr in stmt.expressions:
            value = self.evaluate_expression(expr)
            output.append(str(value))
        print(''.join(output))

    def evaluate_expression(self, expr):
        """Evaluate an expression node"""
        if isinstance(expr, NumberNode):
            return expr.value
        elif isinstance(expr, StringNode):
            return expr.value
        elif isinstance(expr, VariableNode):
            return self.runtime.variables.get(expr.name, 0)
        elif isinstance(expr, BinaryOpNode):
            left = self.evaluate_expression(expr.left)
            right = self.evaluate_expression(expr.right)
            return self.apply_operator(expr.operator, left, right)
        # ... etc
```

#### 3. Built-in Functions (`src/builtins.py`)

All BASIC built-in functions:

```python
import math
import random

class BuiltinFunctions:
    """MBASIC built-in functions"""

    @staticmethod
    def ABS(x):
        return abs(x)

    @staticmethod
    def SIN(x):
        return math.sin(x)

    @staticmethod
    def INT(x):
        return math.floor(x)

    @staticmethod
    def RND(x=None):
        return random.random()

    @staticmethod
    def CHR(x):
        return chr(int(x))

    @staticmethod
    def ASC(s):
        return ord(s[0]) if s else 0

    # ... all other built-in functions
```

### Entry Point

```python
# mbasic_interpreter.py
from lexer import tokenize
from parser import Parser
from runtime import Runtime
from interpreter import Interpreter

def main():
    import sys

    with open(sys.argv[1], 'r') as f:
        code = f.read()

    # Parse
    tokens = list(tokenize(code))
    parser = Parser(tokens)
    ast = parser.parse()

    # Interpret
    runtime = Runtime(ast)
    interpreter = Interpreter(runtime)
    interpreter.run()

if __name__ == '__main__':
    main()
```

---

## Compiler Architecture (Phase 2)

### File Structure

```
src/
  lexer.py              # Existing
  parser.py             # Existing
  ast_nodes.py          # Existing

  semantic.py           # NEW - Semantic analysis
  codegen_python.py     # NEW - Generate Python
  codegen_c.py          # NEW - Generate C (later)
  codegen_js.py         # NEW - Generate JavaScript (later)
```

### Components

#### 1. Semantic Analyzer (`src/semantic.py`)

Validates and prepares AST:

```python
class SemanticAnalyzer:
    """Validate and prepare AST for code generation"""

    def __init__(self, ast):
        self.ast = ast
        self.line_table = {}
        self.data_items = []
        self.user_functions = {}
        self.errors = []

    def analyze(self):
        """Analyze AST"""
        self._build_tables()
        self._validate_jumps()
        self._validate_loops()

        if self.errors:
            raise SemanticError('\n'.join(self.errors))

        return self

    def _validate_jumps(self):
        """Ensure all GOTO/GOSUB targets exist"""
        for line in self.ast.lines:
            for stmt in line.statements:
                if isinstance(stmt, (GotoStatementNode, GosubStatementNode)):
                    if stmt.line_number not in self.line_table:
                        self.errors.append(
                            f"Line {line.line_number}: "
                            f"Jump to undefined line {stmt.line_number}"
                        )
```

#### 2. Code Generator - Python (`src/codegen_python.py`)

Generates Python code:

```python
class PythonCodeGenerator:
    """Generate Python code from MBASIC AST"""

    def __init__(self, ast, semantic_info):
        self.ast = ast
        self.semantic = semantic_info
        self.output = []

    def generate(self):
        """Generate complete Python program"""
        self._generate_header()
        self._generate_data()
        self._generate_functions()
        self._generate_main()

        return '\n'.join(self.output)

    def _generate_header(self):
        """Generate imports and setup"""
        self.output.extend([
            "#!/usr/bin/env python3",
            "import sys",
            "import math",
            "import random",
            "",
            "# MBASIC runtime state",
            "variables = {}",
            "arrays = {}",
            "data_items = []",
            "data_pointer = 0",
            "gosub_stack = []",
            "",
        ])

    def _generate_statement(self, stmt, indent=0):
        """Generate Python code for a statement"""
        prefix = "    " * indent

        if isinstance(stmt, PrintStatementNode):
            exprs = [self._generate_expr(e) for e in stmt.expressions]
            self.output.append(f"{prefix}print({', '.join(exprs)})")

        elif isinstance(stmt, LetStatementNode):
            var = stmt.variable.name
            expr = self._generate_expr(stmt.expression)
            self.output.append(f"{prefix}variables['{var}'] = {expr}")

        elif isinstance(stmt, GotoStatementNode):
            self.output.append(f"{prefix}goto_line_{stmt.line_number}()")

        # ... etc
```

### Entry Point

```python
# mbasic_compiler.py
from lexer import tokenize
from parser import Parser
from semantic import SemanticAnalyzer
from codegen_python import PythonCodeGenerator

def main():
    import sys

    with open(sys.argv[1], 'r') as f:
        code = f.read()

    # Parse
    tokens = list(tokenize(code))
    parser = Parser(tokens)
    ast = parser.parse()

    # Analyze
    semantic = SemanticAnalyzer(ast)
    semantic.analyze()

    # Generate
    codegen = PythonCodeGenerator(ast, semantic)
    python_code = codegen.generate()

    # Output
    output_file = sys.argv[1].replace('.bas', '.py')
    with open(output_file, 'w') as f:
        f.write(python_code)

    print(f"Compiled {sys.argv[1]} -> {output_file}")

if __name__ == '__main__':
    main()
```

---

## Development Order

### Phase 1: Interpreter (Priority)

Week 1-2: Core execution
1. Create `runtime.py` - State management
2. Create `interpreter.py` - Basic execution
3. Create `builtins.py` - Built-in functions
4. Implement core statements: PRINT, LET, GOTO, IF/THEN

Week 3-4: Complete features
5. Add loops: FOR/NEXT, WHILE/WEND
6. Add subroutines: GOSUB/RETURN, ON GOTO/GOSUB
7. Add I/O: INPUT, READ/DATA
8. Add arrays: DIM, array access
9. Add DEF FN

Week 5: Testing
10. Test with all 121 test programs
11. Fix bugs and edge cases

### Phase 2: Compiler (Later)

Week 6-7: Code generation
1. Create `semantic.py` - Validation
2. Create `codegen_python.py` - Python output
3. Implement statement generation
4. Implement expression generation

Week 8: Testing
5. Compile and test all 121 programs
6. Compare output with interpreter

### Phase 3: Additional Targets (Optional)

Later:
- `codegen_c.py` - Generate C code
- `codegen_js.py` - Generate JavaScript
- Optimizations

---

## Testing Strategy

### Use Existing Test Suite

We already have:
- ✓ 121 programs that parse correctly
- ✓ 1 test with expected output (test_operator_precedence.bas)

### Add More Tests with Expected Output

Create in `basic/tests_with_results/`:
- `test_variables.bas` - Variable operations
- `test_loops.bas` - FOR/NEXT, WHILE/WEND
- `test_gotos.bas` - GOTO, GOSUB, ON GOTO
- `test_arrays.bas` - DIM, array access
- `test_strings.bas` - String functions
- `test_math.bas` - Math functions
- `test_data.bas` - DATA/READ/RESTORE
- `test_functions.bas` - DEF FN

Each with corresponding `.txt` file showing expected output.

### Validation

```bash
# Interpreter
python3 mbasic_interpreter.py test.bas > output.txt
diff output.txt test.txt

# Compiler
python3 mbasic_compiler.py test.bas
python3 test.py > output.txt
diff output.txt test.txt
```

---

## Summary

### Your Question: "Is there really a phase between parser and code generator?"

**Answer**: For MBASIC:

**Interpreter**: Needs **lightweight runtime setup** (~100 lines)
- Build line number table
- Index DATA statements
- Extract DEF FN definitions

**Compiler**: Should have **semantic analysis** (~300 lines)
- Everything from runtime setup
- Plus validation (GOTO targets exist, etc.)
- Plus optional optimizations

### Next Steps

1. **Start with interpreter** (simpler, more useful)
2. Create `src/runtime.py`, `src/interpreter.py`, `src/builtins.py`
3. Implement statements one by one
4. Test with existing programs
5. Add more tests with expected output
6. **Later**: Add compiler with code generation

Both will share the same lexer, parser, and AST - only the backend differs.
