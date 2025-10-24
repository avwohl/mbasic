# Parse Tree Structure - MBASIC 5.21 Parser

**Date**: 2025-10-22
**Question**: "Does the parser produce a parse tree?"

---

## Answer: YES!

The parser produces a complete **Abstract Syntax Tree (AST)** / **Parse Tree** representing the hierarchical structure of the BASIC program.

---

## Parse Tree Structure

### Root Node: ProgramNode

```python
ProgramNode(
    lines: List[LineNode],           # All program lines
    def_type_statements: Dict,       # Type definitions (DEFINT, DEFSNG, etc.)
    line_num: int,                   # Metadata
    column: int                      # Metadata
)
```

### Line Node: LineNode

Each line in the program becomes a LineNode:

```python
LineNode(
    line_number: int,                # BASIC line number (10, 20, 30, etc.)
    statements: List[StatementNode], # Statements on this line
    line_num: int,                   # Source line in file
    column: int                      # Source column in file
)
```

---

## Statement Nodes

### Assignment: LetStatementNode

```
LetStatementNode
  variable: VariableNode
  expression: ExpressionNode
```

Example: `20 X = 5 + 3`
```
LetStatementNode
  variable: VariableNode (name='X')
  expression: BinaryOpNode (op=PLUS)
    left: NumberNode (value=5.0)
    right: NumberNode (value=3.0)
```

### Conditional: IfStatementNode

```
IfStatementNode
  condition: ExpressionNode
  then_statements: List[StatementNode] or None
  then_line_number: int or None
  else_statements: List[StatementNode] or None
  else_line_number: int or None
```

Example: `30 IF X > 5 THEN PRINT "Big" ELSE PRINT "Small"`
```
IfStatementNode
  condition: BinaryOpNode (op=GREATER_THAN)
    left: VariableNode (name='X')
    right: NumberNode (value=5.0)
  then_statements[0]: PrintStatementNode
    expressions[0]: StringNode (value='Big')
  else_statements[0]: PrintStatementNode
    expressions[0]: StringNode (value='Small')
```

### Loop: ForStatementNode

```
ForStatementNode
  variable: VariableNode
  start_expr: ExpressionNode
  end_expr: ExpressionNode
  step_expr: ExpressionNode or None
```

Example: `40 FOR I = 1 TO 10 STEP 2`
```
ForStatementNode
  variable: VariableNode (name='I')
  start_expr: NumberNode (value=1.0)
  end_expr: NumberNode (value=10.0)
  step_expr: NumberNode (value=2.0)
```

### Jump: GotoStatementNode

```
GotoStatementNode
  line_number: int
```

Example: `50 GOTO 100`
```
GotoStatementNode (line=100)
```

### Subroutine: GosubStatementNode

```
GosubStatementNode
  line_number: int
```

Example: `60 GOSUB 1000`
```
GosubStatementNode (line=1000)
```

### Output: PrintStatementNode

```
PrintStatementNode
  expressions: List[ExpressionNode]
  separators: List[str]            # ',' or ';' or '\n'
  file_number: ExpressionNode or None
```

Example: `70 PRINT "Hello"; X; "World"`
```
PrintStatementNode
  expressions[0]: StringNode (value='Hello')
  expressions[1]: VariableNode (name='X')
  expressions[2]: StringNode (value='World')
  separators: [';', ';', '\n']
```

---

## Expression Nodes

### Binary Operation: BinaryOpNode

```
BinaryOpNode
  operator: TokenType              # PLUS, MINUS, MULTIPLY, etc.
  left: ExpressionNode
  right: ExpressionNode
```

Example: `5 + 3 * 2`
```
BinaryOpNode (op=PLUS)
  left: NumberNode (value=5.0)
  right: BinaryOpNode (op=MULTIPLY)
    left: NumberNode (value=3.0)
    right: NumberNode (value=2.0)
```

### Unary Operation: UnaryOpNode

```
UnaryOpNode
  operator: TokenType              # MINUS, NOT
  operand: ExpressionNode
```

Example: `-X`
```
UnaryOpNode (op=MINUS)
  operand: VariableNode (name='X')
```

### Variable: VariableNode

```
VariableNode
  name: str
  type_suffix: str or None         # $, %, !, #
  subscripts: List[ExpressionNode] or None
```

Examples:
- `X` → `VariableNode (name='X')`
- `A$` → `VariableNode (name='A', type_suffix='$')`
- `A(5)` → `VariableNode (name='A', subscripts=[NumberNode(5)])`

### Literal: NumberNode

```
NumberNode
  value: float
  literal: original string
```

Example: `42` → `NumberNode (value=42.0)`

### Literal: StringNode

```
StringNode
  value: str
```

Example: `"Hello"` → `StringNode (value='Hello')`

---

## Complete Example

### Input Program

```basic
10 REM Example
20 X = 5 + 3
30 IF X > 5 THEN PRINT "Big" ELSE PRINT "Small"
40 FOR I = 1 TO 10
50   PRINT I
60 NEXT I
70 END
```

### Parse Tree

```
Program: ProgramNode
  lines[0]: LineNode (line=10)
    statements[0]: RemarkStatementNode
  lines[1]: LineNode (line=20)
    statements[0]: LetStatementNode
      variable: VariableNode (name='X')
      expression: BinaryOpNode (op=PLUS)
        left: NumberNode (value=5.0)
        right: NumberNode (value=3.0)
  lines[2]: LineNode (line=30)
    statements[0]: IfStatementNode
      condition: BinaryOpNode (op=GREATER_THAN)
        left: VariableNode (name='X')
        right: NumberNode (value=5.0)
      then_statements[0]: PrintStatementNode
        expressions[0]: StringNode (value='Big')
      else_statements[0]: PrintStatementNode
        expressions[0]: StringNode (value='Small')
  lines[3]: LineNode (line=40)
    statements[0]: ForStatementNode
      variable: VariableNode (name='I')
      start_expr: NumberNode (value=1.0)
      end_expr: NumberNode (value=10.0)
  lines[4]: LineNode (line=50)
    statements[0]: PrintStatementNode
      expressions[0]: VariableNode (name='I')
  lines[5]: LineNode (line=60)
    statements[0]: NextStatementNode
      variables[0]: VariableNode (name='I')
  lines[6]: LineNode (line=70)
    statements[0]: EndStatementNode
```

---

## All Node Types

The parser produces over 60 different AST node types covering all MBASIC 5.21 statements and expressions:

### Statement Nodes (40+)
- **Assignment**: LetStatementNode
- **Control Flow**: IfStatementNode, ForStatementNode, NextStatementNode, WhileStatementNode, WendStatementNode
- **Jumps**: GotoStatementNode, GosubStatementNode, OnGotoStatementNode, OnGosubStatementNode
- **I/O**: PrintStatementNode, InputStatementNode, LineInputStatementNode, ReadStatementNode, WriteStatementNode
- **File I/O**: OpenStatementNode, CloseStatementNode, FieldStatementNode, GetStatementNode, PutStatementNode
- **Arrays**: DimStatementNode, EraseStatementNode, OptionBaseStatementNode
- **Functions**: DefFnStatementNode
- **Type Definitions**: DefIntStatementNode, DefSngStatementNode, DefDblStatementNode, DefStrStatementNode
- **Data**: DataStatementNode, RestoreStatementNode
- **System**: PokeStatementNode, OutStatementNode, SystemStatementNode, EndStatementNode, StopStatementNode
- **Other**: RemarkStatementNode, ClearStatementNode, SwapStatementNode, RandomizeStatementNode, ChainStatementNode
- And more...

### Expression Nodes (20+)
- **Literals**: NumberNode, StringNode
- **Variables**: VariableNode
- **Operators**: BinaryOpNode, UnaryOpNode
- **Functions**: FunctionCallNode, BuiltinFunctionNode
- **Arrays**: ArrayAccessNode

---

## Metadata

Each node includes source location information:
- `line_num`: Source line number in file
- `column`: Source column number in file

This enables:
- Error messages with precise locations
- Source mapping for debugging
- Code transformation preserving locations

---

## Usage

### Visualize Parse Tree

```bash
# Show parse tree for a program
python3 utils/show_parse_tree.py path/to/program.bas

# Or run on example program
python3 utils/show_parse_tree.py
```

### Programmatic Access

```python
from lexer import tokenize
from parser import Parser

code = '10 PRINT "Hello"\n20 END'
tokens = list(tokenize(code))
parser = Parser(tokens)
ast = parser.parse()

# Access the tree
for line in ast.lines:
    print(f"Line {line.line_number}:")
    for stmt in line.statements:
        print(f"  {type(stmt).__name__}")
```

---

## Applications

The parse tree can be used for:

1. **Code Analysis**
   - Static analysis
   - Complexity metrics
   - Variable usage tracking

2. **Code Generation**
   - Compile to other languages
   - Generate bytecode
   - Optimize code

3. **Code Transformation**
   - Refactoring
   - Modernization
   - Minification

4. **Interpretation**
   - Direct AST interpretation
   - Tree-walking interpreter

5. **Documentation**
   - Generate call graphs
   - Extract program structure
   - Create documentation

---

## Implementation Details

### Location: src/ast_nodes.py

All AST node types are defined as Python dataclasses in `src/ast_nodes.py`:
- Over 60 node types
- Strongly typed structure
- Includes source location metadata

### Parser Output

The `Parser.parse()` method returns a complete AST:
```python
def parse(self) -> ProgramNode:
    """Parse tokens into an Abstract Syntax Tree"""
    # Returns ProgramNode containing entire program structure
```

### Tree Properties

- **Hierarchical**: Nodes contain child nodes
- **Typed**: Each node has a specific type (class)
- **Complete**: Preserves all program information
- **Traversable**: Can walk the tree recursively
- **Serializable**: Can be converted to/from other formats

---

## Conclusion

**Yes, the parser produces a complete parse tree (AST).**

The AST:
- ✓ Represents the full program structure hierarchically
- ✓ Preserves all semantic information
- ✓ Includes source location metadata
- ✓ Uses strongly-typed nodes
- ✓ Supports all MBASIC 5.21 constructs
- ✓ Can be traversed and analyzed
- ✓ Ready for code generation, interpretation, or transformation

Use `utils/show_parse_tree.py` to visualize the parse tree for any BASIC program.
