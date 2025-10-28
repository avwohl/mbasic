"""
Position-Aware AST Serialization

Serializes AST nodes back to source text while preserving the original
token positions and spacing. Includes debug tracking for position conflicts.
"""

from typing import List, Optional, Tuple
from dataclasses import dataclass
import ast_nodes


@dataclass
class PositionConflict:
    """Represents a position conflict during serialization"""
    token_text: str
    expected_column: int  # Where token says it should be
    actual_column: int    # Where we actually are in output
    node_type: str        # Type of AST node
    line_num: int         # Line number

    def __str__(self):
        return (f"Position conflict at line {self.line_num}: "
                f"'{self.token_text}' expects column {self.expected_column} "
                f"but output is at column {self.actual_column} "
                f"(node: {self.node_type})")


class PositionSerializer:
    """Serializes AST with position preservation and conflict tracking"""

    def __init__(self, debug=False):
        """Initialize serializer.

        Args:
            debug: If True, collect and report position conflicts
        """
        self.debug = debug
        self.conflicts: List[PositionConflict] = []
        self.current_column = 0
        self.current_line = 0

    def reset(self):
        """Reset serializer state for new line"""
        self.current_column = 0
        self.conflicts = []

    def emit_token(self, text, expected_column: Optional[int],
                   node_type: str = "unknown") -> str:
        """Emit a token at the expected column position.

        Args:
            text: Token text to emit (will be converted to string)
            expected_column: Column where token should appear (from original source)
            node_type: Type of AST node for debugging

        Returns:
            String with appropriate spacing + token text
        """
        # Convert to string if needed
        text = str(text)

        if expected_column is None:
            # No position info - use pretty printing (single space)
            result = " " + text if self.current_column > 0 else text
            self.current_column += len(result)
            return result

        # Calculate spacing needed
        if expected_column < self.current_column:
            # CONFLICT: Token expects to be earlier than current position
            if self.debug:
                conflict = PositionConflict(
                    token_text=text,
                    expected_column=expected_column,
                    actual_column=self.current_column,
                    node_type=node_type,
                    line_num=self.current_line
                )
                self.conflicts.append(conflict)

            # Strategy: Add single space to separate from previous token
            result = " " + text
            self.current_column += len(result)
            return result

        # Normal case: Add spaces to reach expected column
        spaces_needed = expected_column - self.current_column
        result = " " * spaces_needed + text
        self.current_column = expected_column + len(text)
        return result

    def serialize_line(self, line_node: ast_nodes.LineNode) -> Tuple[str, List[PositionConflict]]:
        """Serialize a complete line with position preservation.

        Args:
            line_node: LineNode to serialize

        Returns:
            Tuple of (serialized_text, list_of_conflicts)
        """
        self.reset()
        self.current_line = line_node.line_number

        # FAST PATH: If we have the original source text, use it directly!
        # This perfectly preserves all spacing, case, etc.
        if hasattr(line_node, 'source_text') and line_node.source_text:
            return line_node.source_text.strip(), []

        # FALLBACK: Reconstruct from AST (for generated/modified lines)
        # Start with line number
        line_num_text = str(line_node.line_number)
        output = self.emit_token(line_num_text, 0, "LineNumber")

        # Serialize each statement
        for stmt in line_node.statements:
            stmt_text = self.serialize_statement(stmt)
            output += stmt_text

        return output, self.conflicts.copy()

    def serialize_statement(self, stmt) -> str:
        """Serialize a statement node.

        Args:
            stmt: Statement node to serialize

        Returns:
            Serialized statement text (without leading spaces)
        """
        stmt_type = type(stmt).__name__

        if stmt_type == 'LetStatementNode':
            return self.serialize_let_statement(stmt)
        elif stmt_type == 'PrintStatementNode':
            return self.serialize_print_statement(stmt)
        elif stmt_type == 'IfStatementNode':
            return self.serialize_if_statement(stmt)
        elif stmt_type == 'GotoStatementNode':
            return self.serialize_goto_statement(stmt)
        elif stmt_type == 'GosubStatementNode':
            return self.serialize_gosub_statement(stmt)
        elif stmt_type == 'ForStatementNode':
            return self.serialize_for_statement(stmt)
        elif stmt_type == 'NextStatementNode':
            return self.serialize_next_statement(stmt)
        elif stmt_type == 'RemarkStatementNode':
            return self.serialize_rem_statement(stmt)
        else:
            # Fallback: Use pretty printing from ui_helpers
            from ui.ui_helpers import serialize_statement
            return " " + serialize_statement(stmt)

    def serialize_let_statement(self, stmt: ast_nodes.LetStatementNode) -> str:
        """Serialize LET or assignment statement"""
        result = ""

        # Variable
        var_text = self.serialize_expression(stmt.variable)
        result += var_text

        # Equals sign (TODO: track operator position)
        result += self.emit_token("=", None, "LetOperator")

        # Expression
        expr_text = self.serialize_expression(stmt.expression)
        result += expr_text

        return result

    def serialize_print_statement(self, stmt: ast_nodes.PrintStatementNode) -> str:
        """Serialize PRINT statement"""
        result = self.emit_token("PRINT", stmt.column, "PrintKeyword")

        # File number if present
        if stmt.file_number:
            result += self.emit_token("#", None, "FileSigil")
            result += self.serialize_expression(stmt.file_number)
            result += self.emit_token(",", None, "Comma")

        # Expressions with separators
        for i, expr in enumerate(stmt.expressions):
            result += self.serialize_expression(expr)
            if i < len(stmt.separators) and stmt.separators[i]:
                result += self.emit_token(stmt.separators[i], None, "Separator")

        return result

    def serialize_if_statement(self, stmt: ast_nodes.IfStatementNode) -> str:
        """Serialize IF statement"""
        result = self.emit_token("IF", stmt.column, "IfKeyword")
        result += self.serialize_expression(stmt.condition)
        result += self.emit_token("THEN", None, "ThenKeyword")

        # THEN statements
        for i, then_stmt in enumerate(stmt.then_statements):
            if i > 0:
                result += self.emit_token(":", None, "StatementSep")
            result += self.serialize_statement(then_stmt)

        # ELSE statements if present
        if stmt.else_statements:
            result += self.emit_token("ELSE", None, "ElseKeyword")
            for i, else_stmt in enumerate(stmt.else_statements):
                if i > 0:
                    result += self.emit_token(":", None, "StatementSep")
                result += self.serialize_statement(else_stmt)

        return result

    def serialize_goto_statement(self, stmt: ast_nodes.GotoStatementNode) -> str:
        """Serialize GOTO statement"""
        result = self.emit_token("GOTO", stmt.column, "GotoKeyword")
        result += self.emit_token(str(stmt.target_line), None, "LineNumber")
        return result

    def serialize_gosub_statement(self, stmt: ast_nodes.GosubStatementNode) -> str:
        """Serialize GOSUB statement"""
        result = self.emit_token("GOSUB", stmt.column, "GosubKeyword")
        result += self.emit_token(str(stmt.target_line), None, "LineNumber")
        return result

    def serialize_for_statement(self, stmt: ast_nodes.ForStatementNode) -> str:
        """Serialize FOR statement"""
        result = self.emit_token("FOR", stmt.column, "ForKeyword")
        result += self.serialize_expression(stmt.variable)
        result += self.emit_token("=", None, "Equals")
        result += self.serialize_expression(stmt.start_expr)
        result += self.emit_token("TO", None, "ToKeyword")
        result += self.serialize_expression(stmt.end_expr)
        if stmt.step_expr:
            result += self.emit_token("STEP", None, "StepKeyword")
            result += self.serialize_expression(stmt.step_expr)
        return result

    def serialize_next_statement(self, stmt: ast_nodes.NextStatementNode) -> str:
        """Serialize NEXT statement"""
        result = self.emit_token("NEXT", stmt.column, "NextKeyword")
        if stmt.variables:
            for i, var in enumerate(stmt.variables):
                if i > 0:
                    result += self.emit_token(",", None, "Comma")
                result += self.serialize_expression(var)
        return result

    def serialize_rem_statement(self, stmt: ast_nodes.RemarkStatementNode) -> str:
        """Serialize REM statement"""
        result = self.emit_token("REM", stmt.column, "RemKeyword")
        if stmt.comment:
            # Preserve original comment spacing
            result += " " + stmt.comment
        return result

    def serialize_expression(self, expr) -> str:
        """Serialize an expression node.

        Args:
            expr: Expression node to serialize

        Returns:
            Serialized expression text
        """
        expr_type = type(expr).__name__

        if expr_type == 'NumberNode':
            return self.emit_token(expr.literal if hasattr(expr, 'literal') else str(expr.value),
                                  expr.column, "Number")

        elif expr_type == 'StringNode':
            return self.emit_token(f'"{expr.value}"', expr.column, "String")

        elif expr_type == 'VariableNode':
            # Use original case if available, otherwise fall back to normalized name
            text = getattr(expr, 'original_case', expr.name) or expr.name
            # Only add type suffix if explicit
            if expr.type_suffix and getattr(expr, 'explicit_type_suffix', False):
                text += expr.type_suffix
            # Add subscripts if present
            if expr.subscripts:
                text += "("
                for i, sub in enumerate(expr.subscripts):
                    if i > 0:
                        text += ","
                    text += self.serialize_expression(sub).strip()
                text += ")"
            return self.emit_token(text, expr.column, "Variable")

        elif expr_type == 'BinaryOpNode':
            result = ""
            result += self.serialize_expression(expr.left)

            # Operator token
            from tokens import TokenType
            op_map = {
                TokenType.PLUS: '+',
                TokenType.MINUS: '-',
                TokenType.MULTIPLY: '*',
                TokenType.DIVIDE: '/',
                TokenType.POWER: '^',
                TokenType.EQUAL: '=',
                TokenType.LESS_THAN: '<',
                TokenType.GREATER_THAN: '>',
                TokenType.LESS_EQUAL: '<=',
                TokenType.GREATER_EQUAL: '>=',
                TokenType.NOT_EQUAL: '<>',
                TokenType.AND: 'AND',
                TokenType.OR: 'OR',
                TokenType.XOR: 'XOR',
                TokenType.MOD: 'MOD',
                TokenType.BACKSLASH: '\\',
            }
            op_str = op_map.get(expr.operator, str(expr.operator))
            result += self.emit_token(op_str, None, "Operator")

            result += self.serialize_expression(expr.right)
            return result

        elif expr_type == 'UnaryOpNode':
            op_str = '-' if expr.operator == TokenType.MINUS else str(expr.operator)
            result = self.emit_token(op_str, expr.column, "UnaryOp")
            result += self.serialize_expression(expr.operand)
            return result

        elif expr_type == 'FunctionCallNode':
            result = self.emit_token(expr.name, expr.column, "FunctionName")
            if expr.arguments:
                result += self.emit_token("(", None, "LParen")
                for i, arg in enumerate(expr.arguments):
                    if i > 0:
                        result += self.emit_token(",", None, "Comma")
                    result += self.serialize_expression(arg)
                result += self.emit_token(")", None, "RParen")
            return result

        else:
            # Fallback: use pretty printing
            from ui.ui_helpers import serialize_expression
            return " " + serialize_expression(expr)


def serialize_line_with_positions(line_node: ast_nodes.LineNode, debug=False) -> Tuple[str, List[PositionConflict]]:
    """Convenience function to serialize a line with position preservation.

    Args:
        line_node: LineNode to serialize
        debug: If True, collect position conflict information

    Returns:
        Tuple of (serialized_text, list_of_conflicts)
    """
    serializer = PositionSerializer(debug=debug)
    return serializer.serialize_line(line_node)
