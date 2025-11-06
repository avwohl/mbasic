"""
Position-Aware AST Serialization

Serializes AST nodes back to source text while attempting to preserve original
token positions and spacing. Tracks position conflicts when actual output column
doesn't match expected token column (conflicts occur during AST modifications).

Key principle: AST is the single source of truth for CONTENT (what tokens exist
and their values). Original token positions are HINTS for formatting (where to
place tokens). When positions conflict with content, content wins and a
PositionConflict is recorded.
"""

from typing import List, Optional, Tuple, Dict
from dataclasses import dataclass
import src.ast_nodes as ast_nodes
from src.tokens import TokenType


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


def apply_keyword_case_policy(keyword: str, policy: str, keyword_tracker: Optional[Dict[str, str]] = None) -> str:
    """Apply keyword case policy to a keyword.

    Args:
        keyword: The keyword to transform (may be any case - function handles normalization internally)
        policy: Case policy to apply (force_lower, force_upper, force_capitalize, first_wins, error, preserve)
        keyword_tracker: Dictionary tracking first occurrence of each keyword (for first_wins policy)

    Returns:
        Keyword with case policy applied

    Note: The keyword argument is normalized to lowercase internally when needed (e.g., for
    first_wins policy lookup). Callers may pass keywords in any case.
    """
    if policy == "force_lower":
        return keyword.lower()

    elif policy == "force_upper":
        return keyword.upper()

    elif policy == "force_capitalize":
        # Capitalize first letter only
        return keyword.capitalize()

    elif policy == "first_wins":
        # Use the first occurrence seen for this keyword
        if keyword_tracker is not None:
            keyword_lower = keyword.lower()
            if keyword_lower in keyword_tracker:
                return keyword_tracker[keyword_lower]
        # If not tracked yet, use capitalized as default
        return keyword.capitalize()

    elif policy == "error":
        # Error policy is checked at parse/edit time, not serialization time
        # At serialization, we just use capitalize as fallback
        return keyword.capitalize()

    elif policy == "preserve":
        # The "preserve" policy should be handled by the caller passing in the original case
        # rather than calling this function. However, we provide a defensive fallback
        # (capitalize) in case this function is called with "preserve" policy.
        return keyword.capitalize()

    else:
        # Unknown policy - use lowercase (safest default)
        return keyword.lower()


class PositionSerializer:
    """Serializes AST with position preservation and conflict tracking"""

    def __init__(self, debug=False, keyword_case_manager=None):
        """Initialize serializer.

        Args:
            debug: If True, collect and report position conflicts
            keyword_case_manager: KeywordCaseManager instance (from parser) with keyword case table
        """
        self.debug = debug
        self.conflicts: List[PositionConflict] = []
        self.current_column = 0
        self.current_line = 0

        # Store reference to keyword case manager from parser
        self.keyword_case_manager = keyword_case_manager

    def reset(self):
        """Reset serializer state for new line"""
        self.current_column = 0
        self.conflicts = []

    def emit_keyword(self, keyword: str, expected_column: Optional[int], node_type: str = "Keyword") -> str:
        """Emit a keyword token with case from keyword case table.

        Args:
            keyword: The keyword to emit (normalized lowercase)
            expected_column: Column where keyword should appear
            node_type: Type of AST node for debugging

        Returns:
            String with appropriate spacing + keyword text (with case from table)
        """
        # Get display case from keyword case manager table
        if self.keyword_case_manager:
            keyword_with_case = self.keyword_case_manager.get_display_case(keyword)
        else:
            # Fallback if no manager (shouldn't happen)
            keyword_with_case = keyword.lower()

        # Use regular emit_token for positioning
        return self.emit_token(keyword_with_case, expected_column, node_type)

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

        # AST is the source of truth for content (what tokens exist) - serialize from AST
        # while attempting to preserve original token positions/spacing as formatting hints
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
            from src.ui.ui_helpers import serialize_statement
            return " " + serialize_statement(stmt)

    def serialize_let_statement(self, stmt: ast_nodes.LetStatementNode) -> str:
        """Serialize LET or assignment statement.

        Note: LetStatementNode represents both explicit LET statements (LET A=5)
        and implicit assignments (A=5) in MBASIC. The node name 'LetStatementNode'
        is used consistently throughout the codebase.

        In _adjust_statement_positions(), 'AssignmentStatementNode' was used historically
        but has been replaced by 'LetStatementNode' for consistency.
        """
        result = ""

        # Variable
        var_text = self.serialize_expression(stmt.variable)
        result += var_text

        # Equals sign (operator position not tracked - using None for column)
        # Operators are not stored as separate tokens in AST, so position is inferred
        result += self.emit_token("=", None, "LetOperator")

        # Expression
        expr_text = self.serialize_expression(stmt.expression)
        result += expr_text

        return result

    def serialize_print_statement(self, stmt: ast_nodes.PrintStatementNode) -> str:
        """Serialize PRINT statement"""
        result = self.emit_keyword("print", stmt.column, "PrintKeyword")

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
        result = self.emit_keyword("if", stmt.column, "IfKeyword")
        result += self.serialize_expression(stmt.condition)
        result += self.emit_keyword("then", None, "ThenKeyword")

        # Direct THEN line number (e.g., IF X>5 THEN 100)
        if stmt.then_line_number is not None:
            result += self.emit_token(str(stmt.then_line_number), None, "LineNumber")
        # THEN statements
        elif stmt.then_statements:
            for i, then_stmt in enumerate(stmt.then_statements):
                if i > 0:
                    result += self.emit_token(":", None, "StatementSep")
                result += self.serialize_statement(then_stmt)

        # ELSE statements or line number
        if stmt.else_line_number is not None:
            result += self.emit_keyword("else", None, "ElseKeyword")
            result += self.emit_token(str(stmt.else_line_number), None, "LineNumber")
        elif stmt.else_statements:
            result += self.emit_keyword("else", None, "ElseKeyword")
            for i, else_stmt in enumerate(stmt.else_statements):
                if i > 0:
                    result += self.emit_token(":", None, "StatementSep")
                result += self.serialize_statement(else_stmt)

        return result

    def serialize_goto_statement(self, stmt: ast_nodes.GotoStatementNode) -> str:
        """Serialize GOTO statement"""
        result = self.emit_keyword("goto", stmt.column, "GotoKeyword")
        result += self.emit_token(str(stmt.line_number), None, "LineNumber")
        return result

    def serialize_gosub_statement(self, stmt: ast_nodes.GosubStatementNode) -> str:
        """Serialize GOSUB statement"""
        result = self.emit_keyword("gosub", stmt.column, "GosubKeyword")
        result += self.emit_token(str(stmt.line_number), None, "LineNumber")
        return result

    def serialize_for_statement(self, stmt: ast_nodes.ForStatementNode) -> str:
        """Serialize FOR statement"""
        result = self.emit_keyword("for", stmt.column, "ForKeyword")
        result += self.serialize_expression(stmt.variable)
        result += self.emit_token("=", None, "Equals")
        result += self.serialize_expression(stmt.start_expr)
        result += self.emit_keyword("to", None, "ToKeyword")
        result += self.serialize_expression(stmt.end_expr)
        if stmt.step_expr:
            result += self.emit_keyword("step", None, "StepKeyword")
            result += self.serialize_expression(stmt.step_expr)
        return result

    def serialize_next_statement(self, stmt: ast_nodes.NextStatementNode) -> str:
        """Serialize NEXT statement"""
        result = self.emit_keyword("next", stmt.column, "NextKeyword")
        if stmt.variables:
            for i, var in enumerate(stmt.variables):
                if i > 0:
                    result += self.emit_token(",", None, "Comma")
                result += self.serialize_expression(var)
        return result

    def serialize_rem_statement(self, stmt: ast_nodes.RemarkStatementNode) -> str:
        """Serialize REM statement"""
        # Use comment_type to preserve original syntax (REM, REMARK, or ')
        if stmt.comment_type == "APOSTROPHE":
            result = self.emit_token("'", stmt.column, "RemKeyword")
        else:
            # Apply keyword case to REM/REMARK
            result = self.emit_keyword(stmt.comment_type.lower(), stmt.column, "RemKeyword")

        if stmt.text:
            # Preserve original comment spacing
            result += " " + stmt.text
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

            # Operator token - keywords need case policy applied
            keyword_ops = {
                TokenType.AND: 'and',
                TokenType.OR: 'or',
                TokenType.XOR: 'xor',
                TokenType.MOD: 'mod',
            }
            symbol_ops = {
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
                TokenType.BACKSLASH: '\\',
            }

            # Use emit_keyword for keyword operators, emit_token for symbols
            if expr.operator in keyword_ops:
                result += self.emit_keyword(keyword_ops[expr.operator], None, "Operator")
            elif expr.operator in symbol_ops:
                result += self.emit_token(symbol_ops[expr.operator], None, "Operator")
            else:
                result += self.emit_token(str(expr.operator), None, "Operator")

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
            from src.ui.ui_helpers import serialize_expression
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


def renumber_with_spacing_preservation(program_lines: dict, start: int, step: int, debug=False):
    """Renumber program lines while preserving spacing.

    AST is the single source of truth. This function:
    1. Updates line numbers in the AST
    2. Updates all line number references (GOTO, GOSUB, etc.)
    3. Adjusts token column positions to account for line number length changes
    4. Text can then be regenerated from updated AST using serialize_line()
       (caller should call serialize_line() on each returned LineNode to regenerate text)

    Args:
        program_lines: Dict of line_number -> LineNode
        start: New starting line number
        step: Increment between lines
        debug: If True, print debug information

    Returns:
        Dict of new_line_number -> LineNode (with updated positions)
        Caller should serialize these LineNodes using serialize_line() to get text
    """
    # Build mapping of old -> new line numbers
    old_line_nums = sorted(program_lines.keys())
    line_num_map = {}
    new_num = start

    for old_num in old_line_nums:
        line_num_map[old_num] = new_num
        new_num += step

    # Process each line
    new_program_lines = {}

    for old_num in old_line_nums:
        line_node = program_lines[old_num]
        new_num = line_num_map[old_num]

        # Update line number in the AST
        old_line_str = str(old_num)
        new_line_str = str(new_num)
        line_node.line_number = new_num

        # Update all line number references (GOTO, GOSUB, IF THEN, etc.)
        _update_line_refs_in_node(line_node, line_num_map)

        # Adjust token positions if line number length changed
        line_num_offset = len(new_line_str) - len(old_line_str)
        if line_num_offset != 0:
            _adjust_token_positions(line_node, line_num_offset)

        new_program_lines[new_num] = line_node

    return new_program_lines


def _adjust_token_positions(line_node, offset):
    """Adjust all token column positions in a LineNode by the given offset.

    Args:
        line_node: The LineNode to adjust
        offset: Amount to shift columns (positive = right, negative = left)
    """
    # Adjust positions in all statements
    for stmt in line_node.statements:
        _adjust_statement_positions(stmt, offset)


def _adjust_statement_positions(stmt, offset):
    """Recursively adjust token positions in a statement.

    Args:
        stmt: Statement node to adjust
        offset: Amount to shift columns
    """
    # Adjust column if present
    if hasattr(stmt, 'column'):
        stmt.column += offset

    # Recurse into sub-structures
    stmt_type = type(stmt).__name__

    if stmt_type == 'LetStatementNode':
        _adjust_expression_positions(stmt.variable, offset)
        _adjust_expression_positions(stmt.expression, offset)

    elif stmt_type in ['PrintStatementNode', 'InputStatementNode']:
        if hasattr(stmt, 'expressions'):
            for expr in stmt.expressions:
                _adjust_expression_positions(expr, offset)

    elif stmt_type == 'IfStatementNode':
        _adjust_expression_positions(stmt.condition, offset)
        if stmt.then_statements:
            for then_stmt in stmt.then_statements:
                _adjust_statement_positions(then_stmt, offset)
        if stmt.else_statements:
            for else_stmt in stmt.else_statements:
                _adjust_statement_positions(else_stmt, offset)

    elif stmt_type == 'ForStatementNode':
        _adjust_expression_positions(stmt.variable, offset)
        _adjust_expression_positions(stmt.start_expr, offset)
        _adjust_expression_positions(stmt.end_expr, offset)
        if stmt.step_expr:
            _adjust_expression_positions(stmt.step_expr, offset)

    elif stmt_type == 'NextStatementNode':
        if stmt.variables:
            for var in stmt.variables:
                _adjust_expression_positions(var, offset)

    elif stmt_type == 'DimStatementNode':
        for var in stmt.variables:
            _adjust_expression_positions(var, offset)

    elif stmt_type == 'OnGotoStatementNode' or stmt_type == 'OnGosubStatementNode':
        _adjust_expression_positions(stmt.expression, offset)


def _adjust_expression_positions(expr, offset):
    """Recursively adjust token positions in an expression.

    Args:
        expr: Expression node to adjust
        offset: Amount to shift columns
    """
    if not expr:
        return

    # Adjust column if present
    if hasattr(expr, 'column'):
        expr.column += offset

    expr_type = type(expr).__name__

    if expr_type == 'BinaryOpNode':
        _adjust_expression_positions(expr.left, offset)
        _adjust_expression_positions(expr.right, offset)

    elif expr_type == 'UnaryOpNode':
        _adjust_expression_positions(expr.operand, offset)

    elif expr_type == 'FunctionCallNode':
        if expr.arguments:
            for arg in expr.arguments:
                _adjust_expression_positions(arg, offset)

    elif expr_type == 'VariableNode':
        if expr.subscripts:
            for sub in expr.subscripts:
                _adjust_expression_positions(sub, offset)


def _update_line_refs_in_node(line_node, line_num_map):
    """Update all line number references in a LineNode's statements.

    Args:
        line_node: LineNode to update
        line_num_map: Dict mapping old line numbers to new ones
    """
    for stmt in line_node.statements:
        _update_line_refs_in_statement(stmt, line_num_map)


def _update_line_refs_in_statement(stmt, line_num_map):
    """Recursively update line number references in a statement.

    Args:
        stmt: Statement node to update
        line_num_map: Dict mapping old line numbers to new ones
    """
    stmt_type = type(stmt).__name__

    if stmt_type == 'GotoStatementNode':
        if stmt.line_number in line_num_map:
            stmt.line_number = line_num_map[stmt.line_number]

    elif stmt_type == 'GosubStatementNode':
        if stmt.line_number in line_num_map:
            stmt.line_number = line_num_map[stmt.line_number]

    elif stmt_type == 'OnGotoStatementNode':
        stmt.line_numbers = [line_num_map.get(ln, ln) for ln in stmt.line_numbers]

    elif stmt_type == 'OnGosubStatementNode':
        stmt.line_numbers = [line_num_map.get(ln, ln) for ln in stmt.line_numbers]

    elif stmt_type == 'OnErrorStatementNode':
        if stmt.line_number in line_num_map:
            stmt.line_number = line_num_map[stmt.line_number]

    elif stmt_type == 'RestoreStatementNode':
        if stmt.line_number and stmt.line_number in line_num_map:
            stmt.line_number = line_num_map[stmt.line_number]

    elif stmt_type == 'ResumeStatementNode':
        if stmt.line_number and stmt.line_number in line_num_map:
            stmt.line_number = line_num_map[stmt.line_number]

    elif stmt_type == 'IfStatementNode':
        # Handle THEN line_number (direct branch)
        if hasattr(stmt, 'then_line_number') and stmt.then_line_number:
            if stmt.then_line_number in line_num_map:
                stmt.then_line_number = line_num_map[stmt.then_line_number]
        # Handle ELSE line_number (direct branch)
        if hasattr(stmt, 'else_line_number') and stmt.else_line_number:
            if stmt.else_line_number in line_num_map:
                stmt.else_line_number = line_num_map[stmt.else_line_number]
        # Recurse into THEN/ELSE statements
        if hasattr(stmt, 'then_statements') and stmt.then_statements:
            for then_stmt in stmt.then_statements:
                _update_line_refs_in_statement(then_stmt, line_num_map)
        if hasattr(stmt, 'else_statements') and stmt.else_statements:
            for else_stmt in stmt.else_statements:
                _update_line_refs_in_statement(else_stmt, line_num_map)

        # Handle ERL comparisons in condition
        if hasattr(stmt, 'condition'):
            _update_erl_in_expression(stmt.condition, line_num_map)


def _update_erl_in_expression(expr, line_num_map):
    """Update ERL comparisons in expressions (e.g., IF ERL = 10 THEN).

    Args:
        expr: Expression node to check
        line_num_map: Dict mapping old line numbers to new ones
    """
    expr_type = type(expr).__name__

    if expr_type == 'BinaryOpNode':
        # Check if this is ERL comparison: ERL = line_number
        left_type = type(expr.left).__name__
        right_type = type(expr.right).__name__

        # ERL = number or number = ERL
        if left_type == 'FunctionCallNode' and expr.left.name.lower() == 'erl':
            if right_type == 'NumberNode':
                line_num = int(expr.right.value)
                if line_num in line_num_map:
                    expr.right.value = float(line_num_map[line_num])
        elif right_type == 'FunctionCallNode' and expr.right.name.lower() == 'erl':
            if left_type == 'NumberNode':
                line_num = int(expr.left.value)
                if line_num in line_num_map:
                    expr.left.value = float(line_num_map[line_num])

        # Recurse
        _update_erl_in_expression(expr.left, line_num_map)
        _update_erl_in_expression(expr.right, line_num_map)

    elif expr_type == 'UnaryOpNode':
        _update_erl_in_expression(expr.operand, line_num_map)
