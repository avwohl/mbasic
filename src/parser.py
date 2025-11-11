"""
Parser for MBASIC 5.21

This is a two-pass recursive descent parser:
1. First pass: Collect all DEFINT/DEFSNG/DEFDBL/DEFSTR statements
2. Second pass: Parse the program with global type information

Key differences from interpreter:
- DEF type statements are applied globally at compile time
- Array dimensions must be constant expressions
- Variable types are fixed throughout the program

Expression parsing notes:
- Functions generally require parentheses: SIN(X), CHR$(65)
- Exception: Only RND and INKEY$ can be called without parentheses in MBASIC 5.21
  (this is specific to these two functions, not a general MBASIC feature)
"""

from typing import List, Optional, Dict, Tuple
from src.tokens import Token, TokenType
from src.ast_nodes import *
from src.keyword_case_manager import KeywordCaseManager


class ParseError(Exception):
    """Exception raised during parsing"""
    def __init__(self, message: str, token: Optional[Token] = None):
        self.message = message
        self.token = token
        if token:
            super().__init__(f"Parse error at line {token.line}, column {token.column}: {message}")
        else:
            super().__init__(f"Parse error: {message}")


class Parser:
    """
    Recursive descent parser for MBASIC 5.21

    Two-pass compilation:
    1. collect_def_types() - Gather all DEFINT/DEFSNG/DEFDBL/DEFSTR statements
    2. parse_program() - Parse program with global type information
    """

    def __init__(self, tokens: List[Token], def_type_map: Dict[str, str] = None, source: str = "", keyword_case_manager: Optional[KeywordCaseManager] = None):
        self.tokens = tokens
        self.position = 0
        self.source = source  # Original source code for statement highlighting
        self.source_lines = source.split('\n') if source else []  # Split into lines for easy access

        # Global type mapping from DEF statements
        # Maps first letter (a-z) to type (INTEGER, SINGLE, DOUBLE, STRING)
        if def_type_map is not None:
            # Use provided def_type_map (for interactive mode)
            self.def_type_map = def_type_map
        else:
            # Create new def_type_map (for batch mode)
            self.def_type_map: Dict[str, str] = {}
            # Default type is SINGLE for all letters (use lowercase since lexer normalizes to lowercase)
            for letter in 'abcdefghijklmnopqrstuvwxyz':
                self.def_type_map[letter] = TypeInfo.SINGLE

        # Symbol table - maps variable names to their types
        self.symbol_table: Dict[str, str] = {}

        # Keyword case manager - passed from lexer (already populated during tokenization)
        self.keyword_case_manager = keyword_case_manager or KeywordCaseManager(policy="force_lower")

        # Line number to position mapping for GOTO/GOSUB
        self.line_map: Dict[int, int] = {}

        # User-defined functions (DEF FN)
        self.functions: Dict[str, DefFnStatementNode] = {}

    # ========================================================================
    # Token Management
    # ========================================================================

    def current(self) -> Optional[Token]:
        """Get current token without advancing"""
        if self.position < len(self.tokens):
            return self.tokens[self.position]
        return None

    def peek(self, offset: int = 1) -> Optional[Token]:
        """Look ahead at token without advancing position.

        Args:
            offset: Number of positions to look ahead (default 1 = next token)
                    peek(1) returns next token, peek(2) returns token after that, etc.

        Returns:
            Token at position + offset, or None if past end
        """
        pos = self.position + offset
        if pos < len(self.tokens):
            return self.tokens[pos]
        return None

    def advance(self) -> Token:
        """Consume and return current token"""
        token = self.current()
        if self.at_end_of_tokens():
            raise ParseError("Unexpected end of tokens")
        self.position += 1
        return token

    def expect(self, token_type: TokenType) -> Token:
        """Consume token of expected type or raise error"""
        token = self.current()
        if self.at_end_of_tokens():
            raise ParseError(f"Expected {token_type.name}, got end of tokens")
        if token.type != token_type:
            raise ParseError(f"Expected {token_type.name}, got {token.type.name}", token)
        return self.advance()

    def match(self, *token_types: TokenType) -> bool:
        """Check if current token matches any of the given types"""
        if self.at_end_of_tokens():
            return False
        token = self.current()
        return token.type in token_types

    def at_end(self) -> bool:
        """Check if at end of tokens"""
        return self.position >= len(self.tokens) or self.current().type == TokenType.EOF

    def has_more_tokens(self) -> bool:
        """Check if there are more tokens to parse"""
        return self.current() is not None

    def at_end_of_tokens(self) -> bool:
        """Check if we've exhausted all tokens (alias for current() is None)"""
        return self.current() is None

    def at_end_of_line(self) -> bool:
        """Check if at end of logical line (NEWLINE or EOF)

        Use cases:
        - Line-level parsing in parse_program() where COLON separates statements on same line
        - Collecting DEF type statements across the program
        - Parsing function bodies in DEF FN where entire line is function definition

        Important: This does NOT check for COLON or comment tokens. For statement parsing,
        use at_end_of_statement() instead to properly stop at colons and comments.

        Note: Most statement parsing should use at_end_of_statement(), not this method.
        Using at_end_of_line() in statement parsing can cause bugs where comments are
        parsed as part of the statement instead of ending it.
        """
        if self.at_end_of_tokens():
            return True
        token = self.current()
        return token.type in (TokenType.NEWLINE, TokenType.EOF)

    def at_end_of_statement(self) -> bool:
        """Check if at end of current statement.

        A statement ends at:
        - End of line (NEWLINE or EOF)
        - Statement separator (COLON) - allows multiple statements per line
        - Comment (REM, REMARK, or APOSTROPHE) - everything after is ignored

        Use cases:
        - Parsing statement arguments (INPUT variables, NEXT variables, etc.)
        - Parsing expression lists in most statements
        - General statement boundary detection

        Special case: PRINT/LPRINT inside IF...THEN...ELSE need custom logic that
        also checks for ELSE token, since they can be nested in conditionals.

        Note: For PRINT/LPRINT, use at_end_of_statement() AND check for ELSE explicitly.
        """
        if self.at_end_of_tokens():
            return True
        token = self.current()
        return token.type in (TokenType.NEWLINE, TokenType.EOF, TokenType.COLON,
                              TokenType.REM, TokenType.REMARK, TokenType.APOSTROPHE)

    # ========================================================================
    # Two-Pass Compilation
    # ========================================================================

    def parse(self) -> ProgramNode:
        """
        Main entry point - performs two-pass compilation

        Returns:
            ProgramNode representing the parsed program
        """
        # Pass 1: Collect DEF type statements
        self.collect_def_types()

        # Reset position for second pass
        self.position = 0

        # Pass 2: Parse the program
        return self.parse_program()

    def collect_def_types(self):
        """
        First pass: Scan program for DEFINT/DEFSNG/DEFDBL/DEFSTR statements
        and build global type mapping.

        In compiled BASIC, these statements are applied globally to all
        variables, not executed sequentially like in interpreter.
        """
        while not self.at_end():
            token = self.current()

            # Skip to next line if we hit newline or EOF
            if token.type in (TokenType.NEWLINE, TokenType.EOF):
                self.advance()
                continue

            # Skip line numbers
            if token.type == TokenType.LINE_NUMBER:
                self.advance()
                continue

            # Check for DEF type statements
            if token.type in (TokenType.DEFINT, TokenType.DEFSNG, TokenType.DEFDBL, TokenType.DEFSTR):
                self.parse_def_type_declaration()
            else:
                # Skip to next statement or line
                self.skip_to_next_statement()

    def parse_def_type_declaration(self):
        """
        Parse DEFINT/DEFSNG/DEFDBL/DEFSTR statement and update type map

        Syntax: DEFINT A-Z or DEFINT A,B,C or DEFINT A-C,X-Z
        """
        def_token = self.advance()
        var_type = TypeInfo.from_def_statement(def_token.type)

        # Parse letter ranges
        while not self.at_end_of_line():
            # Skip COLON - it's a statement separator
            if self.match(TokenType.COLON):
                self.advance()
                break

            # Get first letter (already lowercase from lexer)
            token = self.current()
            if token.type != TokenType.IDENTIFIER:
                raise ParseError(f"Expected letter in DEF statement, got {token.type.name}", token)

            first_letter = token.value[0]
            self.advance()

            # Check for range (a-z)
            if self.match(TokenType.MINUS):
                self.advance()

                token = self.current()
                if token.type != TokenType.IDENTIFIER:
                    raise ParseError(f"Expected letter in DEF statement range, got {token.type.name}", token)

                last_letter = token.value[0]
                self.advance()

                # Apply type to range
                for letter in range(ord(first_letter), ord(last_letter) + 1):
                    self.def_type_map[chr(letter)] = var_type
            else:
                # Single letter
                self.def_type_map[first_letter] = var_type

            # Check for comma (more letters)
            if self.match(TokenType.COMMA):
                self.advance()

    def skip_to_next_statement(self):
        """Skip tokens until we reach a statement separator or newline"""
        while not self.at_end():
            token = self.current()
            if token.type in (TokenType.COLON, TokenType.NEWLINE, TokenType.EOF):
                if token.type == TokenType.COLON:
                    self.advance()
                return
            self.advance()

    # ========================================================================
    # Program Structure
    # ========================================================================

    def parse_program(self) -> ProgramNode:
        """
        Parse entire BASIC program

        A program is a sequence of numbered lines
        """
        lines: List[LineNode] = []

        # Build line number map first
        self.build_line_map()
        self.position = 0

        while not self.at_end():
            # Skip empty lines
            if self.match(TokenType.NEWLINE):
                self.advance()
                continue

            # Parse line
            line = self.parse_line()
            if line:
                lines.append(line)

        return ProgramNode(
            lines=lines,
            def_type_statements=self.def_type_map.copy()
        )

    def build_line_map(self):
        """
        Build mapping from line numbers to token positions
        for GOTO/GOSUB resolution
        """
        self.line_map.clear()
        pos = 0

        while pos < len(self.tokens):
            token = self.tokens[pos]

            # Look for line numbers at start of lines
            if token.type == TokenType.LINE_NUMBER:
                line_num = int(token.value)
                self.line_map[line_num] = pos

            pos += 1

    def parse_line(self) -> Optional[LineNode]:
        """
        Parse a single line

        Syntax: line_number statement [: statement]* NEWLINE
        """
        # Expect line number
        if not self.match(TokenType.LINE_NUMBER):
            # Skip to next line if no line number
            self.skip_to_next_line()
            return None

        line_num_token = self.advance()
        line_number = int(line_num_token.value)

        # Parse statements on this line
        # Note: We don't store source_text itself - AST is the source of truth
        # (but we do track char positions for highlighting)
        statements: List[StatementNode] = []

        while not self.at_end_of_line():
            # Handle empty statements (multiple colons or colon at start of line)
            if self.match(TokenType.COLON):
                self.advance()
                continue

            # Track statement start position (column of first token)
            stmt_start_token = self.current()
            stmt_start_col = stmt_start_token.column if stmt_start_token else 0

            stmt = self.parse_statement()

            if stmt:
                # Track statement end position (column after last token consumed)
                # Use the position before we advance to the colon/newline
                prev_pos = self.position - 1
                if prev_pos >= 0 and prev_pos < len(self.tokens):
                    last_token = self.tokens[prev_pos]
                    # Estimate end position as start + length of token value
                    if hasattr(last_token, 'value') and last_token.value:
                        stmt_end_col = last_token.column + len(str(last_token.value))
                    else:
                        stmt_end_col = last_token.column + 1
                else:
                    stmt_end_col = stmt_start_col + 1

                # Set character positions on statement for highlighting
                # Convert from 1-based column to 0-based array index
                stmt.char_start = stmt_start_col - 1 if stmt_start_col > 0 else 0
                stmt.char_end = stmt_end_col - 1 if stmt_end_col > 0 else 0

                statements.append(stmt)

            # Check for statement separator
            if self.match(TokenType.COLON):
                self.advance()
            elif self.match(TokenType.SEMICOLON):
                # Allow trailing semicolon at end of line only (treat as no-op).
                # Context matters: Semicolons have different meanings in different contexts:
                # - WITHIN PRINT/LPRINT: item separators (parsed there, not at statement level)
                # - BETWEEN statements: MBASIC primarily uses COLON (:) to separate statements
                # - Trailing semicolon: Allowed only at end-of-line or before colon (acts as no-op)
                self.advance()
                # If there's more content after the semicolon (not end-of-line, not colon), it's an error.
                if not self.at_end_of_line() and not self.match(TokenType.COLON):
                    token = self.current()
                    raise ParseError(f"Expected : or newline after ;, got {token.type.name}", token)
            elif self.match(TokenType.REM, TokenType.REMARK, TokenType.APOSTROPHE):
                # Allow REM/REMARK/' without colon after statement (standard MBASIC)
                # These consume rest of line as a comment
                stmt = self.parse_remark()
                if stmt:
                    statements.append(stmt)
                break  # Comment ends the line
            elif not self.at_end_of_line():
                # Expected COLON or NEWLINE
                token = self.current()
                raise ParseError(f"Expected : or newline, got {token.type.name}", token)

        # Consume NEWLINE
        if self.match(TokenType.NEWLINE):
            self.advance()

        return LineNode(
            line_number=line_number,
            statements=statements,
            line_num=line_num_token.line,
            column=line_num_token.column
        )

    def skip_to_next_line(self):
        """Skip tokens until next NEWLINE"""
        while not self.at_end():
            if self.match(TokenType.NEWLINE):
                self.advance()
                return
            self.advance()

    # ========================================================================
    # Statement Parsing
    # ========================================================================

    def parse_statement(self) -> Optional[StatementNode]:
        """
        Parse a single statement

        Dispatches to specific statement parsers based on keyword
        """
        if self.at_end_of_tokens():
            return None
        token = self.current()

        # Comments
        if token.type in (TokenType.REM, TokenType.REMARK, TokenType.APOSTROPHE):
            return self.parse_remark()

        # I/O statements
        elif token.type in (TokenType.PRINT, TokenType.QUESTION):
            return self.parse_print()
        elif token.type == TokenType.LPRINT:
            return self.parse_lprint()
        elif token.type == TokenType.INPUT:
            return self.parse_input()
        elif token.type == TokenType.LINE_INPUT:
            return self.parse_line_input()
        elif token.type == TokenType.WRITE:
            return self.parse_write()
        elif token.type == TokenType.READ:
            return self.parse_read()
        elif token.type == TokenType.DATA:
            return self.parse_data()
        elif token.type == TokenType.RESTORE:
            return self.parse_restore()

        # Control flow
        elif token.type == TokenType.IF:
            return self.parse_if()
        elif token.type == TokenType.FOR:
            return self.parse_for()
        elif token.type == TokenType.NEXT:
            return self.parse_next()
        elif token.type == TokenType.WHILE:
            return self.parse_while()
        elif token.type == TokenType.WEND:
            return self.parse_wend()
        elif token.type == TokenType.GOTO:
            return self.parse_goto()
        elif token.type == TokenType.GOSUB:
            return self.parse_gosub()
        elif token.type == TokenType.RETURN:
            return self.parse_return()
        elif token.type == TokenType.ON:
            return self.parse_on()
        elif token.type == TokenType.CHAIN:
            return self.parse_chain()

        # Variable declarations
        elif token.type == TokenType.DIM:
            return self.parse_dim()
        elif token.type == TokenType.ERASE:
            return self.parse_erase()
        elif token.type in (TokenType.DEFINT, TokenType.DEFSNG, TokenType.DEFDBL, TokenType.DEFSTR):
            return self.parse_deftype()
        elif token.type == TokenType.DEF:
            return self.parse_deffn()
        elif token.type == TokenType.COMMON:
            return self.parse_common()

        # File I/O
        elif token.type == TokenType.OPEN:
            return self.parse_open()
        elif token.type == TokenType.CLOSE:
            return self.parse_close()
        elif token.type == TokenType.RESET:
            return self.parse_reset()
        elif token.type == TokenType.KILL:
            return self.parse_kill()
        elif token.type == TokenType.NAME:
            return self.parse_name()
        elif token.type == TokenType.LSET:
            return self.parse_lset()
        elif token.type == TokenType.RSET:
            return self.parse_rset()
        elif token.type == TokenType.FIELD:
            return self.parse_field()
        elif token.type == TokenType.GET:
            return self.parse_get()
        elif token.type == TokenType.PUT:
            return self.parse_put()

        # Other statements
        elif token.type == TokenType.LET:
            return self.parse_let()
        elif token.type == TokenType.END:
            return self.parse_end()
        elif token.type == TokenType.STOP:
            return self.parse_stop()
        elif token.type == TokenType.TRON:
            return self.parse_tron()
        elif token.type == TokenType.TROFF:
            return self.parse_troff()
        elif token.type == TokenType.SYSTEM:
            return self.parse_system()
        elif token.type == TokenType.LIMITS:
            return self.parse_limits()
        elif token.type == TokenType.SHOWSETTINGS:
            return self.parse_showsettings()
        elif token.type == TokenType.SETSETTING:
            return self.parse_setsetting()
        elif token.type == TokenType.RUN:
            return self.parse_run()
        elif token.type == TokenType.LOAD:
            return self.parse_load()
        elif token.type == TokenType.SAVE:
            return self.parse_save()
        elif token.type == TokenType.MERGE:
            return self.parse_merge()
        elif token.type == TokenType.NEW:
            return self.parse_new()
        elif token.type == TokenType.DELETE:
            return self.parse_delete()
        elif token.type == TokenType.RENUM:
            return self.parse_renum()
        elif token.type == TokenType.FILES:
            return self.parse_files()
        elif token.type == TokenType.LIST:
            return self.parse_list()
        elif token.type == TokenType.STOP:
            return self.parse_stop()
        elif token.type == TokenType.CONT:
            return self.parse_cont()
        elif token.type == TokenType.STEP:
            return self.parse_step()
        elif token.type == TokenType.RANDOMIZE:
            return self.parse_randomize()
        elif token.type == TokenType.SWAP:
            return self.parse_swap()
        elif token.type == TokenType.CLEAR:
            return self.parse_clear()
        elif token.type == TokenType.OPTION:
            return self.parse_option()
        elif token.type == TokenType.WIDTH:
            return self.parse_width()
        elif token.type == TokenType.POKE:
            return self.parse_poke()
        elif token.type == TokenType.OUT:
            return self.parse_out()
        elif token.type == TokenType.WAIT:
            return self.parse_wait()
        elif token.type == TokenType.CALL:
            return self.parse_call()

        # Settings commands
        elif token.type == TokenType.SET:
            return self.parse_set_setting()
        elif token.type == TokenType.SHOW:
            # Check if followed by SETTINGS
            if self.peek() and self.peek().type == TokenType.SETTINGS:
                return self.parse_show_settings()
            else:
                raise ParseError(f"SHOW must be followed by SETTINGS", token)
        elif token.type == TokenType.HELP:
            # Check if followed by SET
            if self.peek() and self.peek().type == TokenType.SET:
                return self.parse_help_setting()
            else:
                raise ParseError(f"HELP must be followed by SET for setting help", token)

        # Error handling
        elif token.type == TokenType.ERROR:
            return self.parse_error()
        elif token.type == TokenType.RESUME:
            return self.parse_resume()

        # MID$ statement (substring assignment)
        # Detect MID$ used as statement: MID$(var, start, len) = value
        elif token.type == TokenType.MID:
            # Look ahead to distinguish MID$ statement from MID$ function call
            # MID$ statement has pattern: MID$ ( ... ) =
            # MID$ function has pattern: MID$ ( ... ) in expression context
            # Note: The lexer tokenizes 'MID$' (including the $) as a single token with type TokenType.MID
            # Lookahead strategy: scan past balanced parentheses, check for = sign
            saved_pos = self.position
            try:
                self.advance()  # Skip MID token
                if self.match(TokenType.LPAREN):
                    # Scan to find matching RPAREN, tracking nested parentheses
                    paren_depth = 1
                    self.advance()  # Skip opening (
                    while not self.at_end_of_line() and paren_depth > 0:
                        if self.match(TokenType.LPAREN):
                            paren_depth += 1
                        elif self.match(TokenType.RPAREN):
                            paren_depth -= 1
                        self.advance()
                    # Check if next token is EQUAL (indicates MID$ assignment statement)
                    if self.match(TokenType.EQUAL):
                        # This is MID$ statement, not function
                        self.position = saved_pos  # Restore position to parse properly
                        return self.parse_mid_assignment()
            except (IndexError, ParseError):
                # Catch lookahead failures during MID$ statement detection
                # IndexError: if we run past end of tokens
                # ParseError: if malformed syntax encountered during lookahead
                # Position is restored below, so proper error will be reported later if needed
                pass
            # Restore position - either not a statement or error in lookahead
            self.position = saved_pos
            # MID$ at statement level without assignment pattern is an error
            # (MID$ function calls only valid in expression context)
            raise ParseError(f"MID$ must be used as function (in expression) or assignment statement", token)

        # Assignment (implicit LET)
        elif token.type == TokenType.IDENTIFIER:
            # Check if next token is = or ( (assignment)
            # Note: ( indicates array subscript like A%(0) = 99
            next_token = self.peek()
            if next_token and next_token.type in (TokenType.EQUAL, TokenType.LPAREN):
                return self.parse_assignment()
            else:
                # Not an assignment - this is an error
                raise ParseError(f"Unknown statement or command: '{token.value}'", token)

        # Unknown statement
        else:
            raise ParseError(f"Unexpected token in statement: {token.type.name}", token)

    # ========================================================================
    # Expression Parsing (Operator Precedence)
    # ========================================================================

    def parse_expression(self) -> ExpressionNode:
        """
        Parse expression with operator precedence

        Precedence (lowest to highest):
        1. Logical: IMP
        2. Logical: EQV
        3. Logical: XOR
        4. Logical: OR
        5. Logical: AND
        6. Logical: NOT
        7. Relational: =, <>, <, >, <=, >=
        8. Additive: +, -
        9. Multiplicative: *, /, \\, MOD
        10. Unary: -, +
        11. Power: ^
        12. Primary: numbers, strings, variables, functions, parentheses
        """
        return self.parse_imp()

    def parse_imp(self) -> ExpressionNode:
        """Parse IMP (implication) operator"""
        left = self.parse_eqv()

        while self.match(TokenType.IMP):
            op = self.advance()
            right = self.parse_eqv()
            left = BinaryOpNode(
                operator=op.type,
                left=left,
                right=right,
                line_num=op.line,
                column=op.column
            )

        return left

    def parse_eqv(self) -> ExpressionNode:
        """Parse EQV (equivalence) operator"""
        left = self.parse_xor()

        while self.match(TokenType.EQV):
            op = self.advance()
            right = self.parse_xor()
            left = BinaryOpNode(
                operator=op.type,
                left=left,
                right=right,
                line_num=op.line,
                column=op.column
            )

        return left

    def parse_xor(self) -> ExpressionNode:
        """Parse XOR operator"""
        left = self.parse_or()

        while self.match(TokenType.XOR):
            op = self.advance()
            right = self.parse_or()
            left = BinaryOpNode(
                operator=op.type,
                left=left,
                right=right,
                line_num=op.line,
                column=op.column
            )

        return left

    def parse_or(self) -> ExpressionNode:
        """Parse OR operator"""
        left = self.parse_and()

        while self.match(TokenType.OR):
            op = self.advance()
            right = self.parse_and()
            left = BinaryOpNode(
                operator=op.type,
                left=left,
                right=right,
                line_num=op.line,
                column=op.column
            )

        return left

    def parse_and(self) -> ExpressionNode:
        """Parse AND operator"""
        left = self.parse_not()

        while self.match(TokenType.AND):
            op = self.advance()
            right = self.parse_not()
            left = BinaryOpNode(
                operator=op.type,
                left=left,
                right=right,
                line_num=op.line,
                column=op.column
            )

        return left

    def parse_not(self) -> ExpressionNode:
        """Parse NOT operator (unary)"""
        if self.match(TokenType.NOT):
            op = self.advance()
            operand = self.parse_not()
            return UnaryOpNode(
                operator=op.type,
                operand=operand,
                line_num=op.line,
                column=op.column
            )

        return self.parse_relational()

    def parse_relational(self) -> ExpressionNode:
        """Parse relational operators: =, <>, <, >, <=, >="""
        left = self.parse_additive()

        while self.match(TokenType.EQUAL, TokenType.NOT_EQUAL, TokenType.LESS_THAN,
                         TokenType.GREATER_THAN, TokenType.LESS_EQUAL, TokenType.GREATER_EQUAL):
            op = self.advance()
            right = self.parse_additive()
            left = BinaryOpNode(
                operator=op.type,
                left=left,
                right=right,
                line_num=op.line,
                column=op.column
            )

        return left

    def parse_additive(self) -> ExpressionNode:
        """Parse addition and subtraction: +, -"""
        left = self.parse_multiplicative()

        while self.match(TokenType.PLUS, TokenType.MINUS):
            op = self.advance()
            right = self.parse_multiplicative()
            left = BinaryOpNode(
                operator=op.type,
                left=left,
                right=right,
                line_num=op.line,
                column=op.column
            )

        return left

    def parse_multiplicative(self) -> ExpressionNode:
        """Parse multiplication, division, integer division, modulo: *, /, \\, MOD"""
        left = self.parse_unary()

        while self.match(TokenType.MULTIPLY, TokenType.DIVIDE, TokenType.BACKSLASH, TokenType.MOD):
            op = self.advance()
            right = self.parse_unary()
            left = BinaryOpNode(
                operator=op.type,
                left=left,
                right=right,
                line_num=op.line,
                column=op.column
            )

        return left

    def parse_unary(self) -> ExpressionNode:
        """Parse unary operators: -, +"""
        if self.match(TokenType.MINUS, TokenType.PLUS):
            op = self.advance()
            operand = self.parse_unary()
            return UnaryOpNode(
                operator=op.type,
                operand=operand,
                line_num=op.line,
                column=op.column
            )

        return self.parse_power()

    def parse_power(self) -> ExpressionNode:
        """Parse exponentiation: ^"""
        left = self.parse_primary()

        # Right associative
        if self.match(TokenType.POWER):
            op = self.advance()
            right = self.parse_power()
            return BinaryOpNode(
                operator=op.type,
                left=left,
                right=right,
                line_num=op.line,
                column=op.column
            )

        return left

    def parse_primary(self) -> ExpressionNode:
        """
        Parse primary expressions:
        - Numbers
        - Strings
        - Variables (with optional array subscripts)
        - Built-in functions
        - User-defined functions (FN name)
        - Parenthesized expressions
        """
        if self.at_end_of_tokens():
            raise ParseError("Unexpected end of input in expression")
        token = self.current()

        # Numbers
        if token.type == TokenType.NUMBER:
            self.advance()
            return NumberNode(
                value=float(token.value),
                literal=token.value,
                line_num=token.line,
                column=token.column
            )

        # Strings
        elif token.type == TokenType.STRING:
            self.advance()
            return StringNode(
                value=token.value,
                line_num=token.line,
                column=token.column
            )

        # Parenthesized expression
        elif token.type == TokenType.LPAREN:
            self.advance()
            expr = self.parse_expression()
            self.expect(TokenType.RPAREN)
            return expr

        # Variables and functions
        elif token.type == TokenType.IDENTIFIER:
            return self.parse_variable_or_function()

        # Built-in functions (keywords that are also functions)
        elif self.is_builtin_function(token.type):
            return self.parse_builtin_function()

        # FN (user-defined function call)
        elif token.type == TokenType.FN:
            return self.parse_fn_call()

        # ERR and ERL are system variables (integer type)
        elif token.type in (TokenType.ERR, TokenType.ERL):
            self.advance()
            return VariableNode(
                name=token.type.name,  # 'ERR' or 'ERL'
                type_suffix='%',       # Integer type
                subscripts=[],
                line_num=token.line,
                column=token.column
            )

        else:
            raise ParseError(f"Unexpected token in expression: {token.type.name}", token)

    def parse_variable_or_function(self) -> ExpressionNode:
        """Parse variable reference or function call"""
        token = self.advance()
        name = token.value  # Normalized lowercase name
        original_case = getattr(token, 'original_case', name)  # Original case from lexer

        # Extract type suffix and strip it from name
        type_suffix = self.get_type_suffix(name)
        explicit_type_suffix = False
        if type_suffix:
            name = name[:-1]  # Remove the suffix character from the name
            # Also strip from original case
            if original_case and len(original_case) > 0:
                original_case = original_case[:-1]
            explicit_type_suffix = True  # Suffix was in the original source
        else:
            # No explicit suffix - check DEF type map
            first_letter = name[0].lower()
            if first_letter in self.def_type_map:
                var_type = self.def_type_map[first_letter]
                # Determine suffix based on DEF type
                if var_type == TypeInfo.STRING:
                    type_suffix = '$'
                elif var_type == TypeInfo.INTEGER:
                    type_suffix = '%'
                elif var_type == TypeInfo.DOUBLE:
                    type_suffix = '#'
                elif var_type == TypeInfo.SINGLE:
                    type_suffix = '!'
                # Note: We don't modify name here, just set type_suffix
                # explicit_type_suffix remains False (inferred from DEF)

        # Check for array subscripts or function arguments
        if self.match(TokenType.LPAREN):
            self.advance()

            # Parse arguments/subscripts
            args: List[ExpressionNode] = []
            while not self.match(TokenType.RPAREN):
                args.append(self.parse_expression())

                if self.match(TokenType.COMMA):
                    self.advance()
                elif not self.match(TokenType.RPAREN):
                    raise ParseError("Expected , or ) in function/array", self.current())

            self.expect(TokenType.RPAREN)

            # Determine if it's a user-defined function or array
            # User-defined functions start with "fn" (e.g., fna, fnd, fntest)
            if name.startswith('fn'):
                # It's a user-defined function call
                return FunctionCallNode(
                    name=name,
                    arguments=args,
                    line_num=token.line,
                    column=token.column
                )
            else:
                # It's an array with subscripts
                return VariableNode(
                    name=name,
                    original_case=original_case,
                    type_suffix=type_suffix,
                    subscripts=args,
                    explicit_type_suffix=explicit_type_suffix,
                    line_num=token.line,
                    column=token.column
                )
        else:
            # Simple variable or parameterless function
            # Check if it's a user-defined function (starts with "fn")
            if name.startswith('fn'):
                # It's a parameterless user-defined function call
                return FunctionCallNode(
                    name=name,
                    arguments=[],
                    line_num=token.line,
                    column=token.column
                )
            else:
                # Simple variable
                return VariableNode(
                    name=name,
                    original_case=original_case,
                    type_suffix=type_suffix,
                    subscripts=None,
                    explicit_type_suffix=explicit_type_suffix,
                    line_num=token.line,
                    column=token.column
                )

    def is_builtin_function(self, token_type: TokenType) -> bool:
        """Check if token type is a built-in function"""
        builtin_functions = {
            TokenType.ABS, TokenType.ATN, TokenType.COS, TokenType.SIN, TokenType.TAN,
            TokenType.EXP, TokenType.LOG, TokenType.SQR, TokenType.INT, TokenType.FIX,
            TokenType.RND, TokenType.SGN, TokenType.ASC, TokenType.VAL, TokenType.LEN,
            TokenType.PEEK, TokenType.INP, TokenType.USR, TokenType.VARPTR, TokenType.EOF_FUNC, TokenType.FRE,
            TokenType.LOC, TokenType.LOF, TokenType.POS, TokenType.TAB, TokenType.SPC,
            # String functions
            TokenType.LEFT, TokenType.RIGHT, TokenType.MID, TokenType.CHR, TokenType.STR,
            TokenType.INKEY, TokenType.INPUT_FUNC, TokenType.SPACE, TokenType.STRING_FUNC,
            TokenType.INSTR, TokenType.HEX, TokenType.OCT,
            # Type conversion
            TokenType.CINT, TokenType.CSNG, TokenType.CDBL,
            # Binary conversion
            TokenType.CVI, TokenType.CVS, TokenType.CVD,
            TokenType.MKI, TokenType.MKS, TokenType.MKD,
        }
        # Note: ERR and ERL are not functions, they are system variables
        return token_type in builtin_functions

    def parse_builtin_function(self) -> FunctionCallNode:
        """Parse built-in function call"""
        func_token = self.advance()
        func_name = func_token.type.name

        # Map token names to actual function names
        # (Some tokens have _FUNC suffix to avoid conflicts)
        name_map = {
            'EOF_FUNC': 'EOF',
            'INPUT_FUNC': 'INPUT$',
            'STRING_FUNC': 'STRING$',
        }
        func_name = name_map.get(func_name, func_name)

        # RND can be called without parentheses - MBASIC 5.21 compatibility feature
        # Syntax: RND returns random in [0,1), RND(n) for seeding (n>0 same sequence, n<0 reseed, n=0 repeat)
        if func_token.type == TokenType.RND and not self.match(TokenType.LPAREN):
            # RND without parentheses - valid in MBASIC 5.21
            return FunctionCallNode(
                name=func_name,
                arguments=[],
                line_num=func_token.line,
                column=func_token.column
            )

        # INKEY$ can be called without parentheses - MBASIC 5.21 compatibility feature
        # Returns keyboard input character or "" if no key pressed
        if func_token.type == TokenType.INKEY and not self.match(TokenType.LPAREN):
            # INKEY$ without parentheses - valid in MBASIC 5.21
            return FunctionCallNode(
                name=func_name,
                arguments=[],
                line_num=func_token.line,
                column=func_token.column
            )

        # Expect opening parenthesis for other functions or RND/INKEY$ with args
        self.expect(TokenType.LPAREN)

        # Parse arguments
        args: List[ExpressionNode] = []
        while not self.match(TokenType.RPAREN):
            args.append(self.parse_expression())

            if self.match(TokenType.COMMA):
                self.advance()
            elif not self.match(TokenType.RPAREN):
                raise ParseError(f"Expected , or ) in {func_name} function", self.current())

        self.expect(TokenType.RPAREN)

        return FunctionCallNode(
            name=func_name,
            arguments=args,
            line_num=func_token.line,
            column=func_token.column
        )

    def parse_fn_call(self) -> FunctionCallNode:
        """Parse user-defined function call (FN name)"""
        self.expect(TokenType.FN)

        name_token = self.expect(TokenType.IDENTIFIER)
        raw_name = name_token.value
        # Strip type suffix from the name (e.g., "ucase$" -> "ucase")
        type_suffix = self.get_type_suffix(raw_name)
        if type_suffix:
            raw_name = raw_name[:-1]
        func_name = "fn" + raw_name  # Use lowercase 'fn' to match function definitions

        # Parse arguments if present
        args: List[ExpressionNode] = []
        if self.match(TokenType.LPAREN):
            self.advance()

            while not self.match(TokenType.RPAREN):
                args.append(self.parse_expression())

                if self.match(TokenType.COMMA):
                    self.advance()
                elif not self.match(TokenType.RPAREN):
                    raise ParseError(f"Expected , or ) in FN call", self.current())

            self.expect(TokenType.RPAREN)

        return FunctionCallNode(
            name=func_name,
            arguments=args,
            line_num=name_token.line,
            column=name_token.column
        )

    def get_type_suffix(self, name: str) -> Optional[str]:
        """Extract type suffix from variable name"""
        if name and name[-1] in '$%!#':
            return name[-1]
        return None

    def split_name_and_suffix(self, name: str) -> tuple[str, Optional[str]]:
        """Split variable name into base name and type suffix

        Returns:
            (base_name, type_suffix) tuple
            If no suffix, returns (name, None)

        Example:
            "A$" -> ("A", "$")
            "X" -> ("X", None)
        """
        type_suffix = self.get_type_suffix(name)
        if type_suffix:
            return (name[:-1], type_suffix)
        return (name, None)

    def get_variable_type(self, name: str) -> str:
        """
        Determine variable type based on suffix or DEF statement

        Type precedence:
        1. Explicit suffix ($, %, !, #)
        2. DEF statement for first letter
        3. Default (SINGLE)
        """
        # Check for explicit type suffix
        if name and name[-1] in '$%!#':
            return TypeInfo.from_suffix(name[-1])

        # Check DEF type mapping
        # name[0] is already lowercase from lexer normalization
        first_letter = name[0]
        if first_letter in self.def_type_map:
            return self.def_type_map[first_letter]

        # Default to SINGLE
        return TypeInfo.SINGLE

    # ========================================================================
    # Statement Implementations (Stubs - to be filled in)
    # ========================================================================

    def parse_remark(self) -> RemarkStatementNode:
        """Parse REM, REMARK, or APOSTROPHE comment statement

        The lexer already captured the comment text in the token value.
        """
        token = self.advance()

        # Comment text is stored in token.value by the lexer
        comment_text = token.value if isinstance(token.value, str) else ""

        # Preserve the original comment syntax
        comment_type = token.type.name  # "REM", "REMARK", or "APOSTROPHE"

        return RemarkStatementNode(
            text=comment_text,
            comment_type=comment_type,
            line_num=token.line,
            column=token.column
        )

    def parse_print(self):
        """Parse PRINT or ? statement

        Syntax:
            PRINT expr1, expr2          - Print to screen
            PRINT #filenum, expr1       - Print to file
            PRINT USING format$; expr1  - Formatted print to screen
            PRINT #filenum, USING format$; expr1 - Formatted print to file
        """
        token = self.advance()

        # Check for file number: PRINT #n, ...
        file_number = None
        if self.match(TokenType.HASH):
            self.advance()  # Skip #
            file_number = self.parse_expression()
            # Optionally consume comma after file number
            # Note: MBASIC 5.21 typically requires comma (PRINT #1, "text").
            # Our parser makes the comma optional for compatibility with BASIC variants
            # that allow PRINT #1; "text" or PRINT #1 "text".
            # If semicolon appears instead of comma, it will be treated as an item
            # separator in the expression list below (not as a file number separator).
            if self.match(TokenType.COMMA):
                self.advance()

        # Check for USING keyword
        if self.match(TokenType.USING):
            return self.parse_print_using(token, file_number)

        expressions: List[ExpressionNode] = []
        separators: List[str] = []

        while not self.at_end_of_line() and not self.match(TokenType.COLON) and not self.match(TokenType.ELSE) and not self.match(TokenType.REM, TokenType.REMARK, TokenType.APOSTROPHE):
            # Check for separator first
            if self.match(TokenType.SEMICOLON):
                separators.append(';')
                self.advance()
                # Check if more expressions follow
                if self.at_end_of_line() or self.match(TokenType.COLON) or self.match(TokenType.ELSE) or self.match(TokenType.REM, TokenType.REMARK, TokenType.APOSTROPHE):
                    break
                continue
            elif self.match(TokenType.COMMA):
                separators.append(',')
                self.advance()
                # Check if more expressions follow
                if self.at_end_of_line() or self.match(TokenType.COLON) or self.match(TokenType.ELSE) or self.match(TokenType.REM, TokenType.REMARK, TokenType.APOSTROPHE):
                    break
                continue

            # Parse expression
            expr = self.parse_expression()
            expressions.append(expr)

        # Add newline if there's no trailing separator
        # Logic: After parsing N expressions, we have either N-1 or N separators.
        # - N-1 separators: No trailing separator after last expression → add newline
        # - N separators: Trailing separator after last expression → no newline
        # Examples: "PRINT A;B;C" has 3 expressions, 2 separators (no trailing) → adds \n
        #           "PRINT A;B;C;" has 3 expressions, 3 separators (trailing ;) → no \n
        if len(separators) < len(expressions):
            separators.append('\n')

        return PrintStatementNode(
            expressions=expressions,
            separators=separators,
            file_number=file_number,
            line_num=token.line,
            column=token.column
        )

    def parse_print_using(self, print_token, file_number) -> PrintUsingStatementNode:
        """Parse PRINT USING statement

        Syntax:
            PRINT USING format$; expr1; expr2
            PRINT #filenum, USING format$; expr1

        The format string is parsed as an expression, allowing:
        - String literals: PRINT USING "###.##"; X
        - String variables: PRINT USING F$; X
        - Any expression that evaluates to a string

        Note: Semicolon after format string is required (separates format from value list).
        """
        # Advance past USING keyword
        self.advance()

        # Parse format string as an expression (literal, variable, or computed)
        format_string = self.parse_expression()

        # Expect semicolon after format string
        if not self.match(TokenType.SEMICOLON):
            raise ParseError(f"Expected ';' after PRINT USING format string at line {self.current().line}")
        self.advance()

        # Parse list of expressions (separated by semicolons)
        expressions: List[ExpressionNode] = []

        while not self.at_end_of_line() and not self.match(TokenType.COLON) and not self.match(TokenType.ELSE):
            # Check for separator first (skip it)
            if self.match(TokenType.SEMICOLON):
                self.advance()
                # Check if more expressions follow
                if self.at_end_of_line() or self.match(TokenType.COLON) or self.match(TokenType.ELSE):
                    break
                continue

            # Parse expression
            expr = self.parse_expression()
            expressions.append(expr)

        return PrintUsingStatementNode(
            format_string=format_string,
            expressions=expressions,
            file_number=file_number,
            line_num=print_token.line,
            column=print_token.column
        )

    def parse_lprint(self) -> LprintStatementNode:
        """Parse LPRINT statement - print to line printer

        Syntax:
            LPRINT expr1, expr2         - Print to printer
            LPRINT #filenum, expr1      - Print to file
        """
        token = self.advance()

        # Check for file number: LPRINT #n, ...
        file_number = None
        if self.match(TokenType.HASH):
            self.advance()  # Skip #
            file_number = self.parse_expression()
            # Expect comma after file number
            if self.match(TokenType.COMMA):
                self.advance()

        expressions: List[ExpressionNode] = []
        separators: List[str] = []

        while not self.at_end_of_line() and not self.match(TokenType.COLON) and not self.match(TokenType.ELSE):
            # Check for separator first
            if self.match(TokenType.SEMICOLON):
                separators.append(';')
                self.advance()
                # Check if more expressions follow
                if self.at_end_of_line() or self.match(TokenType.COLON) or self.match(TokenType.ELSE):
                    break
                continue
            elif self.match(TokenType.COMMA):
                separators.append(',')
                self.advance()
                # Check if more expressions follow
                if self.at_end_of_line() or self.match(TokenType.COLON) or self.match(TokenType.ELSE):
                    break
                continue

            # Parse expression
            expr = self.parse_expression()
            expressions.append(expr)

        # Add newline if there's no trailing separator
        # Separator count vs expression count:
        # - If separators < expressions: no trailing separator, add newline
        # - If separators >= expressions: has trailing separator, no newline added
        # Examples: "LPRINT A;B;C" has 2 separators for 3 items (no trailing sep, adds \n)
        #           "LPRINT A;B;C;" has 3 separators for 3 items (trailing sep, no \n)
        #           "LPRINT ;" has 1 separator for 0 items (trailing sep, no \n)
        if len(separators) < len(expressions):
            separators.append('\n')

        return LprintStatementNode(
            expressions=expressions,
            separators=separators,
            file_number=file_number,
            line_num=token.line,
            column=token.column
        )

    def parse_input(self) -> InputStatementNode:
        """Parse INPUT statement

        Syntax:
            INPUT var1, var2           - Read from keyboard
            INPUT "prompt"; var1       - Read with prompt
            INPUT "prompt", var1       - Read with prompt (comma suppresses ?)
            INPUT; var1                - Read without ? prompt (semicolon variant)
            INPUT; "prompt"; var1      - Read with prompt, no default ?
            INPUT #filenum, var1       - Read from file
            INPUT "prompt";LINE var$   - Read entire line including commas

        Note: The semicolon immediately after INPUT keyword (INPUT;) suppresses
        the default '?' prompt. The LINE modifier allows reading an entire line
        including commas without treating them as delimiters.
        """
        token = self.advance()

        # Check for semicolon immediately after INPUT (suppresses ? prompt)
        # Syntax: INPUT;"prompt"; var  or  INPUT; var
        suppress_question = False
        if self.match(TokenType.SEMICOLON):
            suppress_question = True
            self.advance()

        # Check for file number: INPUT #n, ...
        file_number = None
        if self.match(TokenType.HASH):
            self.advance()  # Skip #
            file_number = self.parse_expression()
            # Expect comma after file number
            if self.match(TokenType.COMMA):
                self.advance()

        # Optional prompt string (only for keyboard input, not file input)
        prompt = None
        if file_number is None and self.match(TokenType.STRING):
            prompt = StringNode(
                value=self.advance().value,
                line_num=token.line,
                column=token.column
            )
            # Consume separator after prompt (comma or semicolon)
            # Note: In MBASIC 5.21, the SEPARATOR AFTER PROMPT affects "?" display:
            # Semicolon after prompt: INPUT "Name"; X  displays "Name? " (shows '?')
            # Comma after prompt:    INPUT "Name", X  displays "Name " (suppresses '?')
            # This is different from suppressing '?' ENTIRELY, which requires:
            # INPUT; (semicolon IMMEDIATELY after INPUT keyword with NO prompt).
            # See suppress_question flag above for that behavior.
            if self.match(TokenType.SEMICOLON):
                self.advance()
            elif self.match(TokenType.COMMA):
                self.advance()

        # Check for LINE modifier (e.g., INPUT "prompt";LINE var$)
        # LINE allows input of entire line including commas
        # Note: The lexer tokenizes LINE keyword as LINE_INPUT token both when standalone
        # (LINE INPUT statement) and when used as modifier (INPUT...LINE). The parser
        # distinguishes these cases by context - LINE INPUT is a statement, INPUT...LINE
        # uses LINE as a modifier within the INPUT statement.
        line_mode = False
        if self.match(TokenType.LINE_INPUT):
            line_mode = True
            self.advance()

        # Parse variable list
        variables: List[VariableNode] = []
        while not self.at_end_of_statement():
            var_token = self.expect(TokenType.IDENTIFIER)

            # Check for array subscripts
            subscripts = None
            if self.match(TokenType.LPAREN):
                self.advance()
                subscripts = []

                # Parse subscript expressions
                while not self.match(TokenType.RPAREN):
                    subscripts.append(self.parse_expression())

                    if self.match(TokenType.COMMA):
                        self.advance()
                    elif not self.match(TokenType.RPAREN):
                        raise ParseError("Expected , or ) in array subscript", self.current())

                self.expect(TokenType.RPAREN)

            # Extract type suffix and strip from name
            var_name, type_suffix = self.split_name_and_suffix(var_token.value)

            variables.append(VariableNode(
                name=var_name,
                type_suffix=type_suffix,
                subscripts=subscripts,
                line_num=var_token.line,
                column=var_token.column
            ))

            if self.match(TokenType.COMMA):
                self.advance()
            else:
                break

        return InputStatementNode(
            prompt=prompt,
            variables=variables,
            file_number=file_number,
            suppress_question=suppress_question,
            line_num=token.line,
            column=token.column
        )

    def parse_let(self) -> LetStatementNode:
        """Parse LET statement"""
        token = self.advance()
        return self.parse_assignment_impl(token)

    def parse_assignment(self) -> LetStatementNode:
        """Parse implicit assignment (without LET keyword)"""
        token = self.current()
        return self.parse_assignment_impl(token)

    def parse_assignment_impl(self, start_token: Token) -> LetStatementNode:
        """Parse assignment statement"""
        # Parse variable (may have array subscripts)
        var = self.parse_variable_or_function()

        if not isinstance(var, VariableNode):
            raise ParseError("Expected variable in assignment", start_token)

        # Expect = sign
        self.expect(TokenType.EQUAL)

        # Parse expression
        expr = self.parse_expression()

        return LetStatementNode(
            variable=var,
            expression=expr,
            line_num=start_token.line,
            column=start_token.column
        )

    def parse_goto(self) -> GotoStatementNode:
        """Parse GOTO statement"""
        token = self.advance()

        # GOTO target can be NUMBER or LINE_NUMBER token
        line_num_token = self.current()
        if line_num_token and line_num_token.type in (TokenType.NUMBER, TokenType.LINE_NUMBER):
            self.advance()
            line_number = int(line_num_token.value)
        else:
            raise ParseError("Expected line number after GOTO", line_num_token)

        return GotoStatementNode(
            line_number=line_number,
            line_num=token.line,
            column=token.column
        )

    def parse_gosub(self) -> GosubStatementNode:
        """Parse GOSUB statement"""
        token = self.advance()

        # GOSUB target can be NUMBER or LINE_NUMBER token
        line_num_token = self.current()
        if line_num_token and line_num_token.type in (TokenType.NUMBER, TokenType.LINE_NUMBER):
            self.advance()
            line_number = int(line_num_token.value)
        else:
            raise ParseError("Expected line number after GOSUB", line_num_token)

        return GosubStatementNode(
            line_number=line_number,
            line_num=token.line,
            column=token.column
        )

    def parse_return(self) -> ReturnStatementNode:
        """Parse RETURN statement"""
        token = self.advance()

        return ReturnStatementNode(
            line_num=token.line,
            column=token.column
        )

    def parse_end(self) -> EndStatementNode:
        """Parse END statement"""
        token = self.advance()

        return EndStatementNode(
            line_num=token.line,
            column=token.column
        )

    def parse_tron(self) -> TronStatementNode:
        """Parse TRON statement"""
        token = self.advance()

        return TronStatementNode(
            line_num=token.line,
            column=token.column
        )

    def parse_troff(self) -> TroffStatementNode:
        """Parse TROFF statement"""
        token = self.advance()

        return TroffStatementNode(
            line_num=token.line,
            column=token.column
        )

    def parse_system(self) -> SystemStatementNode:
        """Parse SYSTEM statement"""
        token = self.advance()

        return SystemStatementNode(
            line_num=token.line,
            column=token.column
        )

    def parse_limits(self) -> LimitsStatementNode:
        """Parse LIMITS statement"""
        token = self.advance()

        return LimitsStatementNode(
            line_num=token.line,
            column=token.column
        )

    def parse_showsettings(self) -> ShowSettingsStatementNode:
        """Parse SHOWSETTINGS statement

        Syntax:
            SHOWSETTINGS          - Show all settings
            SHOWSETTINGS pattern  - Show settings matching pattern

        Args:
            pattern: Optional string expression to filter which settings to display
        """
        token = self.advance()

        # Check for optional pattern expression
        pattern_expr = None
        if not self.is_at_end() and self.current_token().type not in (TokenType.COLON, TokenType.NEWLINE, TokenType.EOF):
            pattern_expr = self.parse_expression()

        return ShowSettingsStatementNode(
            pattern=pattern_expr,
            line_num=token.line,
            column=token.column
        )

    def parse_setsetting(self) -> SetSettingStatementNode:
        """Parse SETSETTING statement

        Syntax:
            SETSETTING setting_name value

        Args:
            setting_name: String expression identifying the setting (e.g., "auto_number")
            value: Expression to evaluate and assign to the setting
        """
        token = self.advance()

        # Parse setting_name (typically a string expression like "auto_number")
        setting_name_expr = self.parse_expression()

        # Parse value expression
        value_expr = self.parse_expression()

        return SetSettingStatementNode(
            setting_name=setting_name_expr,
            value=value_expr,
            line_num=token.line,
            column=token.column
        )

    def parse_chain(self) -> ChainStatementNode:
        """Parse CHAIN statement

        Syntax:
            CHAIN [MERGE] filename$ [, [line_number] [, ALL] [, DELETE range]]
        """
        token = self.advance()

        # Check for MERGE option
        merge = False
        if self.match(TokenType.MERGE):
            merge = True
            self.advance()

        # Parse filename expression (must be string)
        filename = self.parse_expression()

        # Optional: starting line number
        start_line = None
        all_flag = False
        delete_range = None

        if self.match(TokenType.COMMA):
            self.advance()

            # Check for line number (optional - can be empty)
            if not self.match(TokenType.COMMA) and not self.match(TokenType.ALL) and not self.match(TokenType.DELETE):
                start_line = self.parse_expression()

            # Check for ALL option
            if self.match(TokenType.COMMA):
                self.advance()

            if self.match(TokenType.ALL):
                all_flag = True
                self.advance()

            # Check for DELETE option
            if self.match(TokenType.COMMA):
                self.advance()

            if self.match(TokenType.DELETE):
                self.advance()
                # Parse range: start_line-end_line
                delete_start = self.parse_expression()
                if self.match(TokenType.MINUS):
                    self.advance()
                    delete_end = self.parse_expression()
                    # Evaluate to get numbers
                    delete_range = (delete_start, delete_end)

        return ChainStatementNode(
            filename=filename,
            start_line=start_line,
            merge=merge,
            all_flag=all_flag,
            delete_range=delete_range,
            line_num=token.line,
            column=token.column
        )

    def parse_run(self) -> RunStatementNode:
        """Parse RUN statement

        Syntax:
            RUN                - Restart current program from beginning
            RUN line_number    - Start execution at specific line number
            RUN "filename"     - Load and run another program file
        """
        token = self.advance()

        target = None

        # Check if there's a target (filename or line number)
        if not self.at_end_of_line() and not self.match(TokenType.COLON):
            # Parse target expression (could be string filename or line number)
            target = self.parse_expression()

        return RunStatementNode(
            target=target,
            line_num=token.line,
            column=token.column
        )

    def parse_load(self) -> LoadStatementNode:
        """Parse LOAD statement

        Syntax:
            LOAD "filename"    - Load program file
            LOAD "filename",R  - Load and run program file
        """
        token = self.advance()

        # Parse filename expression (must be string)
        filename = self.parse_expression()

        # Check for optional ,R flag
        run_flag = False
        if self.match(TokenType.COMMA):
            self.advance()
            # Expect R identifier
            if self.match(TokenType.IDENTIFIER):
                r_token = self.advance()
                if r_token.value.upper() == 'R':
                    run_flag = True
                else:
                    raise ParseError(f"Expected R after comma in LOAD, got {r_token.value}", r_token)
            else:
                raise ParseError("Expected R after comma in LOAD", self.current())

        return LoadStatementNode(
            filename=filename,
            run_flag=run_flag,
            line_num=token.line,
            column=token.column
        )

    def parse_save(self) -> SaveStatementNode:
        """Parse SAVE statement

        Syntax:
            SAVE "filename"    - Save program file
            SAVE "filename",A  - Save as ASCII text
        """
        token = self.advance()

        # Parse filename expression (must be string)
        filename = self.parse_expression()

        # Check for optional ,A flag
        ascii_flag = False
        if self.match(TokenType.COMMA):
            self.advance()
            # Expect A identifier
            if self.match(TokenType.IDENTIFIER):
                a_token = self.advance()
                if a_token.value.upper() == 'A':
                    ascii_flag = True
                else:
                    raise ParseError(f"Expected A after comma in SAVE, got {a_token.value}", a_token)
            else:
                raise ParseError("Expected A after comma in SAVE", self.current())

        return SaveStatementNode(
            filename=filename,
            ascii_flag=ascii_flag,
            line_num=token.line,
            column=token.column
        )

    def parse_merge(self) -> MergeStatementNode:
        """Parse MERGE statement

        Syntax:
            MERGE "filename"   - Merge program from file
        """
        token = self.advance()

        # Parse filename expression (must be string)
        filename = self.parse_expression()

        return MergeStatementNode(
            filename=filename,
            line_num=token.line,
            column=token.column
        )

    def parse_new(self) -> NewStatementNode:
        """Parse NEW statement

        Syntax:
            NEW    - Clear program and variables
        """
        token = self.advance()

        return NewStatementNode(
            line_num=token.line,
            column=token.column
        )

    def parse_randomize(self) -> RandomizeStatementNode:
        """
        Parse RANDOMIZE statement

        Syntax:
            RANDOMIZE           - Use timer as seed
            RANDOMIZE seed      - Use specific seed value
            RANDOMIZE(seed)     - With parentheses
        """
        token = self.advance()

        seed = None

        # Check if there's a seed value
        if not self.at_end_of_line() and not self.match(TokenType.COLON):
            # Parse seed expression
            seed = self.parse_expression()

        return RandomizeStatementNode(
            seed=seed,
            line_num=token.line,
            column=token.column
        )

    def parse_delete(self) -> DeleteStatementNode:
        """Parse DELETE statement

        Syntax:
            DELETE 40          - Delete single line 40
            DELETE 40-100      - Delete lines from start to end
            DELETE -40         - Delete from beginning to end
            DELETE 40-         - Delete from start to end of program
        """
        token = self.advance()

        # Parse the range: start-end, -end, start-, or just start
        # We need to parse this specially because minus is used as separator, not operator
        start = None
        end = None

        # Check if starts with minus (DELETE -end)
        if self.match(TokenType.MINUS):
            self.advance()
            # Parse just a number (not full expression to avoid operator precedence issues)
            if self.match(TokenType.NUMBER):
                end_token = self.advance()
                end = NumberNode(value=end_token.value, literal=str(end_token.value), line_num=end_token.line, column=end_token.column)
        else:
            # Parse start as a number
            if self.match(TokenType.NUMBER):
                start_token = self.advance()
                start = NumberNode(value=start_token.value, literal=str(start_token.value), line_num=start_token.line, column=start_token.column)

                # Check for minus (range)
                if self.match(TokenType.MINUS):
                    self.advance()
                    # Check if there's an end value
                    if self.match(TokenType.NUMBER):
                        end_token = self.advance()
                        end = NumberNode(value=end_token.value, literal=str(end_token.value), line_num=end_token.line, column=end_token.column)
                    # else: DELETE start- (to end of program, end stays None)
                else:
                    # No minus: single line deletion (DELETE 40)
                    # Set end to same as start
                    end = NumberNode(value=start_token.value, literal=str(start_token.value), line_num=start_token.line, column=start_token.column)

        return DeleteStatementNode(
            start=start,
            end=end,
            line_num=token.line,
            column=token.column
        )

    def parse_renum(self) -> RenumStatementNode:
        """Parse RENUM statement

        Syntax:
            RENUM                              - Renumber starting at 10, increment 10
            RENUM new_start                    - Renumber starting at new_start, increment 10
            RENUM new_start,old_start          - Renumber from old_start onwards
            RENUM new_start,old_start,increment - Full control over renumbering

        Parameters can be omitted using commas:
            RENUM 100,,20  - new_start=100, old_start=0 (default), increment=20
            RENUM ,50,20   - new_start=10 (default), old_start=50, increment=20
        """
        token = self.advance()

        new_start = None
        old_start = None
        increment = None

        # Check if there are arguments
        if not self.at_end_of_line() and not self.match(TokenType.COLON):
            # Parse new_start (unless leading comma)
            if not self.match(TokenType.COMMA):
                new_start = self.parse_expression()

            # Check for comma and old_start
            if self.match(TokenType.COMMA):
                self.advance()
                # Parse old_start (unless another comma or end of line)
                if not self.at_end_of_line() and not self.match(TokenType.COLON) and not self.match(TokenType.COMMA):
                    old_start = self.parse_expression()

                # Check for comma and increment
                if self.match(TokenType.COMMA):
                    self.advance()
                    if not self.at_end_of_line() and not self.match(TokenType.COLON):
                        increment = self.parse_expression()

        return RenumStatementNode(
            new_start=new_start,
            old_start=old_start,
            increment=increment,
            line_num=token.line,
            column=token.column
        )

    def parse_files(self) -> FilesStatementNode:
        """Parse FILES statement

        Syntax:
            FILES            - List all .bas files
            FILES filespec   - List files matching pattern
        """
        token = self.advance()

        filespec = None

        # Check if there's a filespec argument
        if not self.at_end_of_line() and not self.match(TokenType.COLON):
            filespec = self.parse_expression()

        return FilesStatementNode(
            filespec=filespec,
            line_num=token.line,
            column=token.column
        )

    def parse_list(self) -> ListStatementNode:
        """Parse LIST statement

        Syntax:
            LIST             - List all lines
            LIST line        - List single line
            LIST start-end   - List range of lines
            LIST -end        - List from beginning to end
            LIST start-      - List from start to end
        """
        token = self.advance()

        # Parse the range similar to DELETE
        start = None
        end = None
        single_line = False

        # Check if there are any arguments
        if self.at_end_of_line() or self.match(TokenType.COLON):
            # LIST with no arguments - list all
            return ListStatementNode(
                start=None,
                end=None,
                single_line=False,
                line_num=token.line,
                column=token.column
            )

        # Check if starts with minus (LIST -end)
        if self.match(TokenType.MINUS):
            self.advance()
            if self.match(TokenType.NUMBER):
                end_token = self.advance()
                end = NumberNode(value=end_token.value, literal=str(end_token.value), line_num=end_token.line, column=end_token.column)
        else:
            # Parse start as a number
            if self.match(TokenType.NUMBER):
                start_token = self.advance()
                start = NumberNode(value=start_token.value, literal=str(start_token.value), line_num=start_token.line, column=start_token.column)

                # Check for minus (range)
                if self.match(TokenType.MINUS):
                    self.advance()
                    # Check if there's an end value
                    if self.match(TokenType.NUMBER):
                        end_token = self.advance()
                        end = NumberNode(value=end_token.value, literal=str(end_token.value), line_num=end_token.line, column=end_token.column)
                    # If no end after dash, it means "start to end of program"
                else:
                    # No dash means single line
                    single_line = True
                    end = start

        return ListStatementNode(
            start=start,
            end=end,
            single_line=single_line,
            line_num=token.line,
            column=token.column
        )

    def parse_stop(self) -> StopStatementNode:
        """Parse STOP statement

        Syntax: STOP

        STOP halts program execution and returns to interactive mode,
        preserving all state (variables, call stack, loop stack).
        """
        token = self.advance()
        return StopStatementNode(
            line_num=token.line,
            column=token.column
        )

    def parse_cont(self) -> ContStatementNode:
        """Parse CONT statement

        Syntax: CONT

        CONT resumes execution after a STOP or Break (Ctrl+C).
        """
        token = self.advance()
        return ContStatementNode(
            line_num=token.line,
            column=token.column
        )

    def parse_step(self):
        """Parse STEP statement (debug command)

        Syntax: STEP [count]

        STEP executes one or more statements in debug mode.
        """
        token = self.advance()
        count = None

        # Check if there's a count argument
        if not self.at_end_of_line() and not self.match(TokenType.COLON):
            next_token = self.peek()
            if next_token and next_token.type == TokenType.NUMBER:
                count_token = self.advance()
                count = int(count_token.value)

        from src.ast_nodes import StepStatementNode
        return StepStatementNode(
            count=count,
            line_num=token.line,
            column=token.column
        )

    # Additional statement parsers would go here...
    # (IF, FOR, NEXT, WHILE, WEND, DIM, etc.)
    # These follow similar patterns to the above

    # Placeholder implementations for remaining statements
    def parse_if(self) -> IfStatementNode:
        """
        Parse IF statement

        Syntax variations:
        - IF condition THEN statement
        - IF condition THEN line_number
        - IF condition THEN line_number ELSE line_number (or :ELSE with lookahead)
        - IF condition THEN statement : statement
        - IF condition THEN statement ELSE statement
        - IF condition GOTO line_number

        Note: :ELSE syntax requires lookahead to distinguish from statement separator colon
        """
        token = self.advance()

        # Parse condition
        condition = self.parse_expression()

        # Check for THEN or GOTO
        then_line_number = None
        then_statements: List[StatementNode] = []
        else_line_number = None
        else_statements: Optional[List[StatementNode]] = None

        if self.match(TokenType.THEN):
            then_token = self.advance()

            # Check if THEN is followed by line number
            if self.match(TokenType.LINE_NUMBER, TokenType.NUMBER):
                then_line_number = int(self.advance().value)

                # Allow optional REM after THEN line_number (without colon)
                # Syntax: IF condition THEN 100 REM comment
                if self.match(TokenType.REM, TokenType.REMARK):
                    # REM consumes rest of line, we're done
                    self.parse_remark()
                    # Don't check for ELSE since REM consumed the line
                # Check for ELSE after THEN line_number
                # Can be either :ELSE or just ELSE (without colon)
                elif self.match(TokenType.COLON):
                    # Peek ahead to see if ELSE follows the colon
                    saved_pos = self.position
                    self.advance()  # Temporarily skip colon
                    if self.match(TokenType.ELSE):
                        # Yes, this is :ELSE syntax - consume both
                        self.advance()  # Skip ELSE
                        # Check if ELSE is followed by line number or statement
                        if self.match(TokenType.LINE_NUMBER, TokenType.NUMBER):
                            else_line_number = int(self.advance().value)
                        else:
                            # Parse else statement(s)
                            else_statements = []
                            stmt = self.parse_statement()
                            if stmt:
                                else_statements.append(stmt)
                    else:
                        # Not :ELSE, restore position to before colon
                        self.position = saved_pos
                elif self.match(TokenType.ELSE):
                    # ELSE without colon: IF...THEN line ELSE ...
                    self.advance()  # Skip ELSE
                    # Check if ELSE is followed by line number or statement
                    if self.match(TokenType.LINE_NUMBER, TokenType.NUMBER):
                        else_line_number = int(self.advance().value)
                    else:
                        # Parse else statement(s)
                        else_statements = []
                        stmt = self.parse_statement()
                        if stmt:
                            else_statements.append(stmt)
            else:
                # Parse statements until end of line or ELSE
                # Pattern: IF cond THEN stmt1 :stmt2 :stmt3 ELSE stmt4
                # or: IF cond THEN stmt1 :stmt2 :ELSE stmt3
                while not self.at_end_of_line() and not self.match(TokenType.ELSE):
                    stmt = self.parse_statement()
                    if stmt:
                        then_statements.append(stmt)

                    # Check what comes next
                    if self.match(TokenType.COLON):
                        # Peek ahead to see if ELSE follows the colon
                        saved_pos = self.position
                        self.advance()  # Temporarily skip colon
                        if self.match(TokenType.ELSE):
                            # Yes, this is :ELSE syntax
                            self.advance()  # Skip ELSE
                            # Check if ELSE is followed by line number or statement
                            if self.match(TokenType.LINE_NUMBER, TokenType.NUMBER):
                                else_line_number = int(self.advance().value)
                            else:
                                # Parse else statement(s)
                                else_statements = []
                                stmt = self.parse_statement()
                                if stmt:
                                    else_statements.append(stmt)
                            break  # Done with THEN clause
                        else:
                            # Not :ELSE, just a statement separator - continue loop
                            self.position = saved_pos
                            self.advance()  # Skip the colon
                    elif self.match(TokenType.ELSE):
                        # ELSE without preceding colon
                        self.advance()  # Skip ELSE
                        # Check if ELSE is followed by line number or statement
                        if self.match(TokenType.LINE_NUMBER, TokenType.NUMBER):
                            else_line_number = int(self.advance().value)
                        else:
                            # Parse else statement(s)
                            else_statements = []
                            stmt = self.parse_statement()
                            if stmt:
                                else_statements.append(stmt)
                        break  # Done with THEN clause
                    else:
                        # No more statements
                        break

        elif self.match(TokenType.GOTO):
            # IF condition GOTO line_number [ELSE ...] (alternate syntax)
            self.advance()
            line_token = self.current()
            if line_token and line_token.type in (TokenType.NUMBER, TokenType.LINE_NUMBER):
                then_line_number = int(self.advance().value)

                # Check for ELSE clause after GOTO line_number
                if self.match(TokenType.ELSE):
                    self.advance()  # Skip ELSE
                    # Check if ELSE is followed by line number or statement
                    if self.match(TokenType.LINE_NUMBER, TokenType.NUMBER):
                        else_line_number = int(self.advance().value)
                    else:
                        # Parse else statement(s)
                        else_statements = []
                        stmt = self.parse_statement()
                        if stmt:
                            else_statements.append(stmt)
            else:
                raise ParseError("Expected line number after GOTO", line_token)

        else:
            raise ParseError(f"Expected THEN or GOTO after IF condition", self.current())

        return IfStatementNode(
            condition=condition,
            then_statements=then_statements,
            then_line_number=then_line_number,
            else_statements=else_statements,
            else_line_number=else_line_number,
            line_num=token.line,
            column=token.column
        )

    def parse_for(self) -> ForStatementNode:
        """
        Parse FOR statement

        Syntax: FOR variable = start TO end [STEP step]
        """
        token = self.advance()

        # Check if we have a proper variable or just a number (malformed)
        var_token = self.current()
        if var_token and var_token.type == TokenType.IDENTIFIER:
            self.advance()
            # Extract type suffix and strip from name
            var_name, type_suffix = self.split_name_and_suffix(var_token.value)

            # If no explicit suffix, check DEF type map
            if not type_suffix:
                first_letter = var_name[0].lower()
                if first_letter in self.def_type_map:
                    var_type = self.def_type_map[first_letter]
                    # Determine suffix based on DEF type
                    # Note: This method modifies type_suffix variable (unlike parse_dim which
                    # modifies the name directly). Both approaches are functionally equivalent.
                    if var_type == TypeInfo.STRING:
                        type_suffix = '$'
                    elif var_type == TypeInfo.INTEGER:
                        type_suffix = '%'
                    elif var_type == TypeInfo.DOUBLE:
                        type_suffix = '#'
                    elif var_type == TypeInfo.SINGLE:
                        type_suffix = '!'

            variable = VariableNode(
                name=var_name,
                type_suffix=type_suffix,
                subscripts=None,
                line_num=var_token.line,
                column=var_token.column
            )

            # Expect =
            self.expect(TokenType.EQUAL)

            # Parse start expression
            start_expr = self.parse_expression()
        else:
            raise ParseError("Expected variable after FOR", var_token)

        # Expect TO
        to_token = self.expect(TokenType.TO)

        # Parse end expression
        end_expr = self.parse_expression()

        # Optional STEP
        step_expr = None
        if self.match(TokenType.STEP):
            step_token = self.advance()
            step_expr = self.parse_expression()

        return ForStatementNode(
            variable=variable,
            start_expr=start_expr,
            end_expr=end_expr,
            step_expr=step_expr,
            line_num=token.line,
            column=token.column
        )

    def parse_next(self) -> NextStatementNode:
        """
        Parse NEXT statement

        Syntax: NEXT [variable [, variable ...]]
        """
        token = self.advance()

        variables: List[VariableNode] = []

        # Parse optional variable list
        while not self.at_end_of_statement():
            if self.match(TokenType.IDENTIFIER):
                var_token = self.advance()
                # Extract type suffix and strip from name
                var_name, type_suffix = self.split_name_and_suffix(var_token.value)

                # If no explicit suffix, check DEF type map
                if not type_suffix:
                    first_letter = var_name[0].lower()
                    if first_letter in self.def_type_map:
                        var_type = self.def_type_map[first_letter]
                        # Determine suffix based on DEF type
                        if var_type == TypeInfo.STRING:
                            type_suffix = '$'
                        elif var_type == TypeInfo.INTEGER:
                            type_suffix = '%'
                        elif var_type == TypeInfo.DOUBLE:
                            type_suffix = '#'
                        elif var_type == TypeInfo.SINGLE:
                            type_suffix = '!'

                variables.append(VariableNode(
                    name=var_name,
                    type_suffix=type_suffix,
                    subscripts=None,
                    line_num=var_token.line,
                    column=var_token.column
                ))

                # Check for comma
                if self.match(TokenType.COMMA):
                    self.advance()
                else:
                    break
            else:
                break

        return NextStatementNode(
            variables=variables,
            line_num=token.line,
            column=token.column
        )

    def parse_while(self) -> WhileStatementNode:
        """
        Parse WHILE statement

        Syntax: WHILE condition
        """
        token = self.advance()

        # Parse condition
        condition = self.parse_expression()

        return WhileStatementNode(
            condition=condition,
            line_num=token.line,
            column=token.column
        )

    def parse_wend(self) -> WendStatementNode:
        """
        Parse WEND statement

        Syntax: WEND
        """
        token = self.advance()

        return WendStatementNode(
            line_num=token.line,
            column=token.column
        )

    def parse_on(self) -> StatementNode:
        """
        Parse ON statement

        Syntax:
        - ON expression GOTO line1, line2, ...
        - ON expression GOSUB line1, line2, ...
        - ON ERROR GOTO line_number
        """
        token = self.advance()

        # Check for ON ERROR
        if self.match(TokenType.ERROR):
            self.advance()

            # Check for GOTO or GOSUB
            is_gosub = False
            if self.match(TokenType.GOTO):
                self.advance()
                is_gosub = False
            elif self.match(TokenType.GOSUB):
                self.advance()
                is_gosub = True
            else:
                raise ParseError("Expected GOTO or GOSUB after ON ERROR", self.current())

            # Parse line number (0 means disable error handling)
            line_num_token = self.current()
            if line_num_token and line_num_token.type in (TokenType.NUMBER, TokenType.LINE_NUMBER):
                self.advance()
                return OnErrorStatementNode(
                    line_number=int(line_num_token.value),
                    is_gosub=is_gosub,
                    line_num=token.line,
                    column=token.column
                )
            else:
                raise ParseError("Expected line number after ON ERROR GOTO/GOSUB", line_num_token)

        # Parse expression
        expr = self.parse_expression()

        # Expect GOTO or GOSUB
        if self.match(TokenType.GOTO):
            self.advance()

            # Parse line number list
            line_numbers: List[int] = []
            while True:
                line_num_token = self.current()
                if line_num_token and line_num_token.type in (TokenType.NUMBER, TokenType.LINE_NUMBER):
                    self.advance()
                    line_numbers.append(int(line_num_token.value))
                else:
                    raise ParseError("Expected line number in ON GOTO list", line_num_token)

                if self.match(TokenType.COMMA):
                    self.advance()
                else:
                    break

            return OnGotoStatementNode(
                expression=expr,
                line_numbers=line_numbers,
                line_num=token.line,
                column=token.column
            )

        elif self.match(TokenType.GOSUB):
            self.advance()

            # Parse line number list
            line_numbers: List[int] = []
            while True:
                line_num_token = self.current()
                if line_num_token and line_num_token.type in (TokenType.NUMBER, TokenType.LINE_NUMBER):
                    self.advance()
                    line_numbers.append(int(line_num_token.value))
                else:
                    raise ParseError("Expected line number in ON GOSUB list", line_num_token)

                if self.match(TokenType.COMMA):
                    self.advance()
                else:
                    break

            return OnGosubStatementNode(
                expression=expr,
                line_numbers=line_numbers,
                line_num=token.line,
                column=token.column
            )

        else:
            raise ParseError(f"Expected GOTO or GOSUB after ON expression", self.current())

    def parse_dim(self) -> DimStatementNode:
        """
        Parse DIM statement

        Syntax: DIM array1(dims), array2(dims), ...

        Dimension expressions: This implementation accepts any expression for array dimensions
        (e.g., DIM A(X*2, Y+1)), with dimensions evaluated at runtime. This matches MBASIC 5.21
        behavior which evaluates dimension expressions at runtime (not compile-time).
        Note: Some compiled BASICs (e.g., QuickBASIC) may require constants only.
        """
        token = self.advance()

        arrays: List[ArrayDeclNode] = []

        while not self.at_end_of_line() and not self.match(TokenType.COLON):
            # Parse array name
            name_token = self.expect(TokenType.IDENTIFIER)
            name = name_token.value

            # Determine type suffix based on explicit suffix or DEF type
            # If no explicit suffix, check DEF type map and add appropriate suffix
            if name and name[-1] not in '$%!#':
                # No explicit suffix - check DEF type map
                first_letter = name[0].lower()
                if first_letter in self.def_type_map:
                    var_type = self.def_type_map[first_letter]
                    # Append appropriate suffix based on DEF type
                    if var_type == TypeInfo.STRING:
                        name = name + '$'
                    elif var_type == TypeInfo.INTEGER:
                        name = name + '%'
                    elif var_type == TypeInfo.DOUBLE:
                        name = name + '#'
                    # SINGLE (!) is the default, no need to add suffix

            # Expect opening parenthesis
            self.expect(TokenType.LPAREN)

            # Parse dimensions
            dimensions: List[ExpressionNode] = []
            while not self.match(TokenType.RPAREN):
                dim_expr = self.parse_expression()
                dimensions.append(dim_expr)

                if self.match(TokenType.COMMA):
                    self.advance()
                elif not self.match(TokenType.RPAREN):
                    raise ParseError("Expected , or ) in DIM statement", self.current())

            self.expect(TokenType.RPAREN)

            arrays.append(ArrayDeclNode(
                name=name,
                dimensions=dimensions,
                line_num=name_token.line,
                column=name_token.column
            ))

            # Check for comma (more arrays)
            if self.match(TokenType.COMMA):
                self.advance()
            else:
                break

        return DimStatementNode(
            arrays=arrays,
            line_num=token.line,
            column=token.column
        )

    def parse_erase(self) -> EraseStatementNode:
        """Parse ERASE statement

        Syntax:
            ERASE array1, array2, ...

        Examples:
            ERASE A, B$, C
            ERASE M : DIM M(64)   (two statements on one line, separated by colon)
        """
        token = self.advance()

        array_names: List[str] = []

        while not self.at_end_of_line() and not self.match(TokenType.COLON):
            # Parse array name (just identifier, no subscripts)
            name_token = self.expect(TokenType.IDENTIFIER)
            array_names.append(name_token.value)

            # Check for comma (more arrays)
            if self.match(TokenType.COMMA):
                self.advance()
            else:
                break

        return EraseStatementNode(
            array_names=array_names,
            line_num=token.line,
            column=token.column
        )

    def parse_mid_assignment(self) -> MidAssignmentStatementNode:
        """Parse MID$ assignment statement

        Syntax:
            MID$(string_var, start, length) = value

        Example:
            MID$(A$, 3, 5) = "HELLO"
            MID$(P$(I), J, 1) = " "

        Note: The lexer tokenizes 'MID$' from source as TokenType.MID. The token TYPE is
        named 'MID' (enum constant), but the token represents the full 'MID$' keyword with
        the dollar sign as an integral part (not a separate type suffix token).
        """
        token = self.current()  # MID token (TokenType.MID represents 'MID$' from source)
        self.advance()  # Skip MID token

        # Expect opening parenthesis
        self.expect(TokenType.LPAREN)

        # Parse string variable (can be array element)
        string_var = self.parse_expression()

        # Expect comma
        self.expect(TokenType.COMMA)

        # Parse start position
        start = self.parse_expression()

        # Expect comma
        self.expect(TokenType.COMMA)

        # Parse length
        length = self.parse_expression()

        # Expect closing parenthesis
        self.expect(TokenType.RPAREN)

        # Expect equals sign
        self.expect(TokenType.EQUAL)

        # Parse value expression
        value = self.parse_expression()

        return MidAssignmentStatementNode(
            string_var=string_var,
            start=start,
            length=length,
            value=value,
            line_num=token.line,
            column=token.column
        )

    def parse_deftype(self) -> DefTypeStatementNode:
        """Parse DEFINT/DEFSNG/DEFDBL/DEFSTR statement

        Design decision: This method updates def_type_map during PARSING, not during execution.
        This is necessary because:
        1. The type map must be available when parsing subsequent variable declarations
           (DIM, FOR, etc.) to infer their types
        2. In batch mode, DEFTYPE statements can appear anywhere and affect variables
           declared before or after them in the source
        3. The map must be consistent across all statements in a program

        The def_type_map is shared across all statements (both interactive and batch modes).
        The AST node is created for program serialization/documentation.
        """
        token = self.advance()
        var_type = TypeInfo.from_def_statement(token.type)

        letters: set = set()

        # Parse letter ranges
        while not self.at_end_of_line() and not self.match(TokenType.COLON):
            # Get first letter (normalize to lowercase for def_type_map)
            letter_token = self.expect(TokenType.IDENTIFIER)
            first_letter_lower = letter_token.value[0].lower()

            # Check for range (A-Z)
            if self.match(TokenType.MINUS):
                self.advance()
                last_letter_token = self.expect(TokenType.IDENTIFIER)
                last_letter_lower = last_letter_token.value[0].lower()

                # Update def_type_map and letters set for range (use lowercase)
                for letter in range(ord(first_letter_lower), ord(last_letter_lower) + 1):
                    letter_char = chr(letter)
                    self.def_type_map[letter_char] = var_type
                    letters.add(letter_char)
            else:
                # Single letter
                # Update def_type_map and letters set for single letter (use lowercase)
                self.def_type_map[first_letter_lower] = var_type
                letters.add(first_letter_lower)

            # Check for comma (more letters)
            if self.match(TokenType.COMMA):
                self.advance()

        return DefTypeStatementNode(
            var_type=var_type,
            letters=letters,
            line_num=token.line,
            column=token.column
        )

    def parse_deffn(self) -> DefFnStatementNode:
        """
        Parse DEF FN statement - user-defined function

        Syntax: DEF FNname[(param1, param2, ...)] = expression
        Note: FN is part of the function name, e.g., "FNR", "FNA$"

        Function name normalization: All function names are normalized to lowercase with
        'fn' prefix (e.g., "FNR" becomes "fnr", "FNA$" becomes "fna") for consistent
        lookup. Type suffixes are stripped from the name during normalization. This matches
        the lexer's identifier normalization and ensures function calls match their
        definitions regardless of case or type suffix.

        Key points:
        - Type suffix characters ($, %, !, #) are STRIPPED during normalization
        - Only the 'fn' + base name is kept for function lookup
        - "DEF FNA$" and "DEF FNA" define the SAME function (both become "fna")

        Examples:
            DEF FNR(X) = INT(X*100+.5)/100        -> function name "fnr"
            DEF FNA$(U,V) = P1$+CHR$(31+U*2)...   -> function name "fna" ($ stripped)
            DEF FNB = 42  (no parameters)          -> function name "fnb"
        """
        token = self.advance()  # Consume DEF

        # Next token should be identifier starting with "FN"
        # In MBASIC, "DEF FNR(X)" means function name is "FNR"
        fn_name_token = self.current()

        if fn_name_token and fn_name_token.type == TokenType.FN:
            # Handle "DEF FN name" with space (FN is separate token)
            # Lexer tokenizes "DEF FN R" as: DEF token, FN token, IDENTIFIER "r"
            self.advance()
            fn_name_token = self.expect(TokenType.IDENTIFIER)
            raw_name = fn_name_token.value
            # Strip type suffix from the name (e.g., "test$" -> "test")
            type_suffix = self.get_type_suffix(raw_name)
            if type_suffix:
                raw_name = raw_name[:-1]
            function_name = "fn" + raw_name  # Add 'fn' prefix to match function calls
        elif fn_name_token and fn_name_token.type == TokenType.IDENTIFIER:
            # Handle "DEF FNR" without space (FN and name are single identifier token)
            # Lexer tokenizes "DEF FNR" as: DEF token, IDENTIFIER "fnr"
            # The lexer already normalized to lowercase and kept 'fn' as part of identifier
            if not fn_name_token.value.startswith("fn"):
                raise ParseError("DEF function name must start with FN", fn_name_token)
            self.advance()
            raw_name = fn_name_token.value
            # Strip type suffix from the name (e.g., "fntest$" -> "fntest")
            type_suffix = self.get_type_suffix(raw_name)
            if type_suffix:
                raw_name = raw_name[:-1]
            function_name = raw_name  # Already has 'fn' prefix from lexer
        else:
            raise ParseError("Expected function name after DEF", fn_name_token)

        # Parse parameters (optional)
        parameters = []
        if self.match(TokenType.LPAREN):
            self.advance()

            # Parse parameter list
            if not self.match(TokenType.RPAREN):
                while True:
                    param_token = self.expect(TokenType.IDENTIFIER)
                    # Split parameter name and type suffix (e.g., "z$" -> name="z", suffix="$")
                    param_name = param_token.value
                    param_type_suffix = self.get_type_suffix(param_name)
                    if param_type_suffix:
                        param_name = param_name[:-1]  # Remove suffix from name
                    # Create VariableNode for each parameter
                    param_var = VariableNode(
                        name=param_name,
                        type_suffix=param_type_suffix,
                        subscripts=None,
                        line_num=param_token.line,
                        column=param_token.column
                    )
                    parameters.append(param_var)

                    if self.match(TokenType.COMMA):
                        self.advance()
                    else:
                        break

            self.expect(TokenType.RPAREN)

        # Expect = sign
        self.expect(TokenType.EQUAL)

        # Parse function body expression
        expression = self.parse_expression()

        return DefFnStatementNode(
            name=function_name,
            parameters=parameters,
            expression=expression,
            line_num=token.line,
            column=token.column
        )

    def parse_common(self) -> CommonStatementNode:
        """Parse COMMON statement

        Syntax:
            COMMON variable1, variable2, array1(), string$, ...

        The empty parentheses () indicate an array variable (all elements shared).
        These parentheses are consumed during parsing but not stored in the AST.
        The resulting CommonStatementNode contains only the variable names (without
        any indicator of whether they were arrays or scalars). Non-empty parentheses
        are an error (parser enforces empty parens only).

        Examples:
            COMMON A, B, C           - Simple variables
            COMMON X, Y(), NAME$     - Mix of simple var, array, and string
        """
        token = self.advance()

        variables = []

        # Parse comma-separated list of variables
        while True:
            var_token = self.current()
            if not var_token or var_token.type != TokenType.IDENTIFIER:
                raise ParseError("Expected variable name in COMMON", var_token)

            var_name = var_token.value
            self.advance()

            # Check for array indicator ()
            # We consume the parentheses but don't need to store array dimension info
            # (COMMON shares the entire array, not specific subscripts)
            if self.match(TokenType.LPAREN):
                self.advance()
                if not self.match(TokenType.RPAREN):
                    raise ParseError("COMMON arrays must use empty parentheses () - subscripts not allowed", self.current())
                self.advance()

            # Just store the variable name as a string
            variables.append(var_name)

            # Check for more variables
            if self.match(TokenType.COMMA):
                self.advance()
            else:
                break

        return CommonStatementNode(
            variables=variables,
            line_num=token.line,
            column=token.column
        )

    def parse_open(self) -> OpenStatementNode:
        """
        Parse OPEN statement

        Syntax variations:
        - OPEN "R", #1, "FILENAME"
        - OPEN "I", #1, "FILENAME"
        - OPEN "O", #1, "FILENAME"
        - OPEN "R", #1, "FILENAME", record_length
        - OPEN filename$ FOR INPUT AS #1
        - OPEN filename$ FOR OUTPUT AS #1
        - OPEN filename$ FOR APPEND AS #1
        """
        token = self.advance()

        # Check for modern syntax: OPEN filename$ FOR mode AS #n
        # vs classic syntax: OPEN mode, #n, filename$

        # Look ahead to determine syntax
        if self.match(TokenType.STRING):
            # Could be either: OPEN "mode" or OPEN "filename" FOR
            # Parse as expression and decide based on what follows
            first_arg = self.parse_expression()

            if self.match(TokenType.FOR):
                # Modern syntax: OPEN filename$ FOR mode AS #n
                self.advance()

                # Parse mode (INPUT/OUTPUT/APPEND)
                mode_token = self.current()
                if mode_token and mode_token.type in (TokenType.INPUT, TokenType.OUTPUT):
                    mode = mode_token.type.name[0]  # "I" or "O"
                    self.advance()
                elif mode_token and mode_token.type == TokenType.IDENTIFIER and mode_token.value.upper() == "APPEND":
                    mode = "A"
                    self.advance()
                else:
                    raise ParseError("Expected INPUT, OUTPUT, or APPEND after FOR", mode_token)

                # Expect AS
                if self.match(TokenType.AS):
                    self.advance()

                # Expect # and file number
                if self.match(TokenType.HASH):
                    self.advance()

                file_number = self.parse_expression()

                return OpenStatementNode(
                    mode=mode,
                    file_number=file_number,
                    filename=first_arg,
                    record_length=None,
                    line_num=token.line,
                    column=token.column
                )
            else:
                # Classic syntax: OPEN "mode", #n, filename$
                # First arg is mode string - extract mode letter
                if isinstance(first_arg, StringNode):
                    mode = first_arg.value[0].upper()
                else:
                    mode = "I"  # Default

                # Expect comma
                self.expect(TokenType.COMMA)

                # Expect # and file number
                if self.match(TokenType.HASH):
                    self.advance()

                file_number = self.parse_expression()

                # Expect comma
                self.expect(TokenType.COMMA)

                # Parse filename
                filename = self.parse_expression()

                # Optional record length
                record_length = None
                if self.match(TokenType.COMMA):
                    self.advance()
                    record_length = self.parse_expression()

                return OpenStatementNode(
                    mode=mode,
                    file_number=file_number,
                    filename=filename,
                    record_length=record_length,
                    line_num=token.line,
                    column=token.column
                )
        else:
            # Parse mode expression
            mode_expr = self.parse_expression()

            # Extract mode character
            if isinstance(mode_expr, StringNode):
                mode = mode_expr.value[0].upper()
            else:
                mode = "I"  # Default

            # Expect comma
            self.expect(TokenType.COMMA)

            # Expect # and file number
            if self.match(TokenType.HASH):
                self.advance()

            file_number = self.parse_expression()

            # Expect comma
            self.expect(TokenType.COMMA)

            # Parse filename
            filename = self.parse_expression()

            # Optional record length
            record_length = None
            if self.match(TokenType.COMMA):
                self.advance()
                record_length = self.parse_expression()

            return OpenStatementNode(
                mode=mode,
                file_number=file_number,
                filename=filename,
                record_length=record_length,
                line_num=token.line,
                column=token.column
            )

    def parse_close(self) -> CloseStatementNode:
        """
        Parse CLOSE statement

        Syntax: CLOSE [#]n [, [#]n ...]
        """
        token = self.advance()

        file_numbers: List[ExpressionNode] = []

        # CLOSE can be called without arguments to close all files
        if not self.at_end_of_line() and not self.match(TokenType.COLON):
            while True:
                # Optional # before file number
                if self.match(TokenType.HASH):
                    self.advance()

                file_number = self.parse_expression()
                file_numbers.append(file_number)

                if self.match(TokenType.COMMA):
                    self.advance()
                else:
                    break

        return CloseStatementNode(
            file_numbers=file_numbers,
            line_num=token.line,
            column=token.column
        )

    def parse_reset(self) -> ResetStatementNode:
        """
        Parse RESET statement

        Syntax: RESET

        RESET closes all open files. No parameters.
        """
        token = self.advance()

        return ResetStatementNode(
            line_num=token.line,
            column=token.column
        )

    def parse_kill(self) -> KillStatementNode:
        """Parse KILL statement

        Syntax:
            KILL filename$
        """
        token = self.advance()

        # Parse filename expression (must be string)
        filename = self.parse_expression()

        return KillStatementNode(
            filename=filename,
            line_num=token.line,
            column=token.column
        )

    def parse_name(self) -> NameStatementNode:
        """Parse NAME statement

        Syntax:
            NAME oldfile$ AS newfile$
        """
        token = self.advance()

        # Parse old filename expression (must be string)
        old_filename = self.parse_expression()

        # Expect AS keyword
        self.expect(TokenType.AS)

        # Parse new filename expression (must be string)
        new_filename = self.parse_expression()

        return NameStatementNode(
            old_filename=old_filename,
            new_filename=new_filename,
            line_num=token.line,
            column=token.column
        )

    def parse_lset(self) -> LsetStatementNode:
        """Parse LSET statement

        Syntax:
            LSET field_var = string_expr
        """
        token = self.advance()

        # Parse variable
        var = self.parse_variable_or_function()
        if not isinstance(var, VariableNode):
            raise ParseError("Expected variable in LSET statement", token)

        # Expect =
        self.expect(TokenType.EQUAL)

        # Parse expression
        expr = self.parse_expression()

        return LsetStatementNode(
            variable=var,
            expression=expr,
            line_num=token.line,
            column=token.column
        )

    def parse_rset(self) -> RsetStatementNode:
        """Parse RSET statement

        Syntax:
            RSET field_var = string_expr
        """
        token = self.advance()

        # Parse variable
        var = self.parse_variable_or_function()
        if not isinstance(var, VariableNode):
            raise ParseError("Expected variable in RSET statement", token)

        # Expect =
        self.expect(TokenType.EQUAL)

        # Parse expression
        expr = self.parse_expression()

        return RsetStatementNode(
            variable=var,
            expression=expr,
            line_num=token.line,
            column=token.column
        )

    def parse_field(self) -> FieldStatementNode:
        """
        Parse FIELD statement

        Syntax: FIELD #n, width AS variable$ [, width AS variable$ ...]
        """
        token = self.advance()

        # Expect # and file number
        if self.match(TokenType.HASH):
            self.advance()

        file_number = self.parse_expression()

        # Expect comma
        self.expect(TokenType.COMMA)

        # Parse field definitions
        fields: List[tuple] = []

        while not self.at_end_of_line() and not self.match(TokenType.COLON):
            # Parse width
            width = self.parse_expression()

            # Expect AS
            self.expect(TokenType.AS)

            # Parse variable (may have subscripts for array elements)
            variable = self.parse_variable_or_function()
            if not isinstance(variable, VariableNode):
                raise ParseError("Expected variable after AS in FIELD statement", self.current())

            fields.append((width, variable))

            # Check for more fields
            if self.match(TokenType.COMMA):
                self.advance()
            else:
                break

        return FieldStatementNode(
            file_number=file_number,
            fields=fields,
            line_num=token.line,
            column=token.column
        )

    def parse_get(self) -> GetStatementNode:
        """
        Parse GET statement

        Syntax: GET #n [, record_number]
        """
        token = self.advance()

        # Expect # and file number
        if self.match(TokenType.HASH):
            self.advance()

        file_number = self.parse_expression()

        # Optional record number
        record_number = None
        if self.match(TokenType.COMMA):
            self.advance()
            record_number = self.parse_expression()

        return GetStatementNode(
            file_number=file_number,
            record_number=record_number,
            line_num=token.line,
            column=token.column
        )

    def parse_put(self) -> PutStatementNode:
        """
        Parse PUT statement

        Syntax: PUT #n [, record_number]
        """
        token = self.advance()

        # Expect # and file number
        if self.match(TokenType.HASH):
            self.advance()

        file_number = self.parse_expression()

        # Optional record number
        record_number = None
        if self.match(TokenType.COMMA):
            self.advance()
            record_number = self.parse_expression()

        return PutStatementNode(
            file_number=file_number,
            record_number=record_number,
            line_num=token.line,
            column=token.column
        )

    def parse_line_input(self) -> LineInputStatementNode:
        """
        Parse LINE INPUT statement

        Syntax:
        - LINE INPUT variable$
        - LINE INPUT "prompt"; variable$
        - LINE INPUT #n, variable$

        LINE INPUT reads an entire line including commas (unlike INPUT which treats
        commas as field separators).
        """
        token = self.advance()

        # Handle tokenization quirk: lexer may produce separate INPUT token after LINE
        if self.match(TokenType.INPUT):
            self.advance()

        file_number = None
        prompt = None

        # Check for # (file input)
        if self.match(TokenType.HASH):
            self.advance()
            file_number = self.parse_expression()
            self.expect(TokenType.COMMA)
        else:
            # Check for optional prompt string
            if self.match(TokenType.STRING):
                prompt = StringNode(
                    value=self.advance().value,
                    line_num=token.line,
                    column=token.column
                )
                # Expect semicolon or comma after prompt
                if self.match(TokenType.SEMICOLON, TokenType.COMMA):
                    self.advance()

        # Parse variable
        var_token = self.expect(TokenType.IDENTIFIER)
        # Extract type suffix and strip from name
        var_name, type_suffix = self.split_name_and_suffix(var_token.value)
        variable = VariableNode(
            name=var_name,
            type_suffix=type_suffix,
            subscripts=None,
            line_num=var_token.line,
            column=var_token.column
        )

        return LineInputStatementNode(
            file_number=file_number,
            prompt=prompt,
            variable=variable,
            line_num=token.line,
            column=token.column
        )

    def parse_write(self) -> WriteStatementNode:
        """
        Parse WRITE statement

        Syntax:
        - WRITE expr1, expr2, ...
        - WRITE #n, expr1, expr2, ...
        """
        token = self.advance()

        file_number = None

        # Check for # (file output)
        if self.match(TokenType.HASH):
            self.advance()
            file_number = self.parse_expression()

            if self.match(TokenType.COMMA):
                self.advance()

        # Parse expressions
        expressions: List[ExpressionNode] = []

        if not self.at_end_of_line() and not self.match(TokenType.COLON):
            while True:
                expr = self.parse_expression()
                expressions.append(expr)

                if self.match(TokenType.COMMA):
                    self.advance()
                else:
                    break

        return WriteStatementNode(
            file_number=file_number,
            expressions=expressions,
            line_num=token.line,
            column=token.column
        )

    def parse_read(self) -> ReadStatementNode:
        """
        Parse READ statement

        Syntax: READ var1, var2, var3(subscript), ...

        Variables can be simple or array elements
        """
        token = self.advance()

        variables: List[VariableNode] = []
        while not self.at_end_of_line() and not self.match(TokenType.COLON):
            var_token = self.expect(TokenType.IDENTIFIER)

            # Check for array subscripts
            subscripts = None
            if self.match(TokenType.LPAREN):
                self.advance()
                subscripts = []

                # Parse subscript expressions
                while not self.match(TokenType.RPAREN):
                    subscripts.append(self.parse_expression())

                    if self.match(TokenType.COMMA):
                        self.advance()
                    elif not self.match(TokenType.RPAREN):
                        raise ParseError("Expected , or ) in array subscript", self.current())

                self.expect(TokenType.RPAREN)

            # Extract type suffix and strip from name
            var_name, type_suffix = self.split_name_and_suffix(var_token.value)

            # If no explicit suffix, check DEF type map
            if not type_suffix:
                first_letter = var_name[0].lower()
                if first_letter in self.def_type_map:
                    var_type = self.def_type_map[first_letter]
                    # Determine suffix based on DEF type
                    if var_type == TypeInfo.STRING:
                        type_suffix = '$'
                    elif var_type == TypeInfo.INTEGER:
                        type_suffix = '%'
                    elif var_type == TypeInfo.DOUBLE:
                        type_suffix = '#'
                    elif var_type == TypeInfo.SINGLE:
                        type_suffix = '!'

            variables.append(VariableNode(
                name=var_name,
                type_suffix=type_suffix,
                subscripts=subscripts,
                line_num=var_token.line,
                column=var_token.column
            ))

            if self.match(TokenType.COMMA):
                self.advance()
            else:
                break

        return ReadStatementNode(
            variables=variables,
            line_num=token.line,
            column=token.column
        )

    def parse_data(self) -> DataStatementNode:
        """Parse DATA statement - Syntax: DATA value1, value2, ...

        DATA items can be:
        - Numbers: DATA 1, 2, 3
        - Quoted strings: DATA "HELLO", "WORLD"
        - Unquoted strings: DATA HELLO WORLD, FOO BAR

        Unquoted strings extend until comma, colon, end of line, or unrecognized token.
        Line numbers (e.g., DATA 100 200): These are tokenized as LINE_NUMBER tokens
        but are converted to strings and included in unquoted string values.
        """
        token = self.advance()

        values: List[ExpressionNode] = []
        while not self.at_end_of_line() and not self.match(TokenType.COLON):
            # Try to parse as expression (handles numbers and quoted strings)
            # If that fails or we encounter identifiers, treat as unquoted string

            if self.at_end_of_tokens():
                break
            current_token = self.current()

            # If it's a string literal, number, or signed number, parse as expression
            if current_token.type in (TokenType.STRING, TokenType.NUMBER):
                value = self.parse_expression()
                values.append(value)
            elif current_token.type in (TokenType.MINUS, TokenType.PLUS):
                # Could be a signed number - parse as expression
                value = self.parse_expression()
                values.append(value)
            else:
                # Unquoted string - collect identifiers/keywords until comma or end
                string_parts = []
                while not self.at_end_of_line() and not self.match(TokenType.COLON) and not self.match(TokenType.COMMA):
                    tok = self.current()
                    if tok is None:
                        break

                    # Accept identifiers, numbers (as text), and keywords as part of unquoted strings
                    if tok.type == TokenType.IDENTIFIER:
                        string_parts.append(tok.value)
                        self.advance()
                    elif tok.type == TokenType.NUMBER:
                        string_parts.append(str(tok.value))
                        self.advance()
                    elif tok.type == TokenType.LINE_NUMBER:
                        string_parts.append(str(tok.value))
                        self.advance()
                    elif tok.type in (TokenType.MINUS, TokenType.PLUS):
                        # Allow +/- in unquoted strings (for things like "E-5")
                        string_parts.append(tok.value if hasattr(tok, 'value') else tok.type.name)
                        self.advance()
                    elif tok.value is not None and isinstance(tok.value, str):
                        # Any keyword with a string value - treat as part of unquoted string
                        # This handles keywords like TO, FOR, IF, etc. in DATA statements
                        string_parts.append(tok.value)
                        self.advance()
                    else:
                        # Unknown token type without string value - stop here
                        break

                # Join the parts with spaces to form the unquoted string
                unquoted_str = ' '.join(string_parts).strip()
                if unquoted_str:
                    values.append(StringNode(
                        value=unquoted_str,
                        line_num=token.line,
                        column=token.column
                    ))

            # Check for comma separator
            if self.match(TokenType.COMMA):
                self.advance()
            elif not self.at_end_of_line() and not self.match(TokenType.COLON):
                # No comma but more tokens - this shouldn't happen if parsing is correct
                break

        return DataStatementNode(
            values=values,
            line_num=token.line,
            column=token.column
        )

    def parse_restore(self) -> RestoreStatementNode:
        """Parse RESTORE statement - Syntax: RESTORE [line_number]"""
        token = self.advance()

        line_number = None
        if self.match(TokenType.LINE_NUMBER, TokenType.NUMBER):
            line_number = int(self.advance().value)

        return RestoreStatementNode(
            line_number=line_number,
            line_num=token.line,
            column=token.column
        )

    def parse_swap(self) -> SwapStatementNode:
        """Parse SWAP statement - Syntax: SWAP var1, var2

        Variables can be simple variables or array elements with subscripts.
        """
        token = self.advance()

        # Parse first variable (may have subscripts)
        var1 = self.parse_variable_or_function()
        if not isinstance(var1, VariableNode):
            raise ParseError("Expected variable in SWAP statement", token)

        self.expect(TokenType.COMMA)

        # Parse second variable (may have subscripts)
        var2 = self.parse_variable_or_function()
        if not isinstance(var2, VariableNode):
            raise ParseError("Expected variable in SWAP statement", self.current())

        return SwapStatementNode(
            var1=var1,
            var2=var2,
            line_num=token.line,
            column=token.column
        )

    def parse_clear(self) -> ClearStatementNode:
        """Parse CLEAR statement - Syntax: CLEAR [,][string_space][,stack_space]"""
        token = self.advance()

        string_space = None
        stack_space = None

        # CLEAR can have optional arguments
        if not self.at_end_of_line() and not self.match(TokenType.COLON):
            # Parse first argument (string space or comma)
            if not self.match(TokenType.COMMA):
                string_space = self.parse_expression()

            # Check for second argument
            if self.match(TokenType.COMMA):
                self.advance()
                if not self.at_end_of_line() and not self.match(TokenType.COLON):
                    stack_space = self.parse_expression()

        return ClearStatementNode(
            string_space=string_space,
            stack_space=stack_space,
            line_num=token.line,
            column=token.column
        )

    def parse_option(self) -> OptionBaseStatementNode:
        """Parse OPTION BASE statement

        Syntax: OPTION BASE 0 | 1

        Sets the lower bound for array indices. Default is 0.
        Must appear before any DIM statements.
        """
        token = self.advance()  # Consume OPTION

        # Expect BASE keyword
        if not self.match(TokenType.BASE):
            raise ParseError("Expected BASE after OPTION", self.current())
        self.advance()  # Consume BASE

        # Expect 0 or 1
        base_token = self.current()
        if base_token.type != TokenType.NUMBER:
            raise ParseError("Expected 0 or 1 after OPTION BASE", base_token)

        base_value = int(base_token.value)
        if base_value not in (0, 1):
            raise ParseError("OPTION BASE must be 0 or 1", base_token)

        self.advance()  # Consume number

        return OptionBaseStatementNode(
            base=base_value,
            line_num=token.line,
            column=token.column
        )

    def parse_width(self) -> WidthStatementNode:
        """Parse WIDTH statement.

        Syntax: WIDTH width [, device]

        Parses a WIDTH statement that specifies output width for a device.
        Both the width and optional device parameters are parsed as expressions.

        The parsed statement contains:
        - width: Column width expression (typically 40 or 80)
        - device: Optional device expression (e.g., file number like 1, or device name).
          In MBASIC 5.21, common values are file numbers or omitted for console.
          The parser accepts any expression; validation occurs at runtime.
        """
        token = self.advance()

        width = self.parse_expression()

        device = None
        if self.match(TokenType.COMMA):
            self.advance()
            device = self.parse_expression()

        return WidthStatementNode(
            width=width,
            device=device,
            line_num=token.line,
            column=token.column
        )

    def parse_poke(self) -> PokeStatementNode:
        """Parse POKE statement - Syntax: POKE address, value"""
        token = self.advance()

        address = self.parse_expression()
        self.expect(TokenType.COMMA)
        value = self.parse_expression()

        return PokeStatementNode(
            address=address,
            value=value,
            line_num=token.line,
            column=token.column
        )

    def parse_out(self) -> OutStatementNode:
        """Parse OUT statement - Syntax: OUT port, value"""
        token = self.advance()

        port = self.parse_expression()
        self.expect(TokenType.COMMA)
        value = self.parse_expression()

        return OutStatementNode(
            port=port,
            value=value,
            line_num=token.line,
            column=token.column
        )

    def parse_wait(self) -> WaitStatementNode:
        """Parse WAIT statement - Syntax: WAIT port, mask [, select]"""
        token = self.advance()

        port = self.parse_expression()
        self.expect(TokenType.COMMA)
        mask = self.parse_expression()

        select = None
        if self.match(TokenType.COMMA):
            self.advance()
            select = self.parse_expression()

        return WaitStatementNode(
            port=port,
            mask=mask,
            select=select,
            line_num=token.line,
            column=token.column
        )

    def parse_call(self) -> CallStatementNode:
        """
        Parse CALL statement - call machine language routine

        MBASIC 5.21 syntax:
            CALL address           - Call machine code at numeric address

        Extended syntax (for compatibility with other BASIC dialects):
            CALL ROUTINE(X,Y)      - Call with arguments

        Note: MBASIC 5.21 primarily uses the simple numeric address form. This parser
        also accepts the extended syntax (CALL routine_name(args)) for compatibility
        with code from other BASIC dialects, though this form is not validated against
        the MBASIC 5.21 specification.

        Examples:
            CALL 16384             - Call decimal address
            CALL &HC000            - Call hex address
            CALL A                 - Call address in variable
            CALL DIO+1             - Call computed address
            CALL MYSUB(X,Y)        - Call with arguments (extended syntax)
        """
        token = self.advance()

        # Parse the target (can be address or identifier)
        target = self.parse_expression()

        # Check if there are arguments
        # Note: CALL ROUTINE(X,Y) is parsed as VariableNode with subscripts
        arguments = []
        if isinstance(target, VariableNode) and target.subscripts:
            # Target was parsed as array access, but it's actually a call with args
            arguments = target.subscripts
            # Create a new variable node without subscripts for the target
            target = VariableNode(
                name=target.name,
                type_suffix=target.type_suffix,
                subscripts=None,
                line_num=target.line_num,
                column=target.column
            )
        elif isinstance(target, FunctionCallNode):
            # Target was parsed as function call with arguments
            arguments = target.arguments
            # Create a variable node for the subroutine name
            target = VariableNode(
                name=target.name,
                type_suffix=None,
                subscripts=None,
                line_num=token.line,
                column=token.column
            )

        return CallStatementNode(
            target=target,
            arguments=arguments,
            line_num=token.line,
            column=token.column
        )

    def parse_error(self) -> ErrorStatementNode:
        """Parse ERROR statement

        Syntax: ERROR error_code

        Simulates an error with the specified error code.
        Sets ERR to error_code and ERL to current line number.
        """
        token = self.advance()  # Consume ERROR

        # Parse error code expression
        error_code = self.parse_expression()

        return ErrorStatementNode(
            error_code=error_code,
            line_num=token.line,
            column=token.column
        )

    def parse_resume(self) -> ResumeStatementNode:
        """Parse RESUME statement - Syntax: RESUME [NEXT | 0 | line_number]

        Note: RESUME with no argument retries the statement that caused the error.
        RESUME 0 also retries the error statement (same as RESUME with no argument).
        RESUME NEXT continues at the statement after the error.
        RESUME line_number continues at the specified line.

        AST representation:
        - RESUME (no arg) → line_number=None
        - RESUME 0 → line_number=0 (interpreter handles 0 same as None)
        - RESUME NEXT → line_number=-1 (sentinel value)
        - RESUME 100 → line_number=100
        """
        token = self.advance()

        line_number = None
        if self.match(TokenType.NEXT):
            self.advance()
            line_number = -1  # -1 sentinel means RESUME NEXT
        elif self.match(TokenType.LINE_NUMBER, TokenType.NUMBER):
            # Store the actual value (0 or other line number) in the AST
            # The interpreter handles line_number=0 the same as line_number=None
            line_number = int(self.advance().value)

        return ResumeStatementNode(
            line_number=line_number,
            line_num=token.line,
            column=token.column
        )

    def parse_set_setting(self) -> SetSettingStatementNode:
        """Parse SET statement for settings

        Syntax:
            SET "setting.name" value
            SET "setting.name" = value

        Examples:
            SET "case_conflict" "first_wins"
            SET "auto_number" 1
            SET "ui.font_size" 14

        Note: Setting names must be string literals to support dots.
        """
        token = self.advance()  # Consume SET

        # Parse setting name as string literal (to support dots in names)
        if not self.match(TokenType.STRING):
            raise ParseError(f"Expected setting name (string) after SET", self.current_token())

        setting_name = self.advance().value

        # Optional equals sign
        if self.match(TokenType.EQUAL):
            self.advance()

        # Parse value expression
        if self.at_end_of_line():
            raise ParseError(f"Expected value after SET {setting_name}", self.current_token())

        value = self.parse_expression()

        return SetSettingStatementNode(
            setting_name=setting_name,
            value=value,
            line_num=token.line,
            column=token.column
        )

    def parse_show_settings(self) -> ShowSettingsStatementNode:
        """Parse SHOW SETTINGS statement

        Syntax:
            SHOW SETTINGS              - Show all settings
            SHOW SETTINGS "pattern"    - Show settings matching pattern

        Examples:
            SHOW SETTINGS
            SHOW SETTINGS "variables"
            SHOW SETTINGS "editor.auto"

        Note: Pattern must be string literal to support dots.
        """
        token = self.advance()  # Consume SHOW
        self.expect(TokenType.SETTINGS)  # Consume SETTINGS

        # Optional pattern (string literal)
        pattern = None
        if not self.at_end_of_line() and not self.match(TokenType.COLON):
            if self.match(TokenType.STRING):
                pattern = self.advance().value

        return ShowSettingsStatementNode(
            pattern=pattern,
            line_num=token.line,
            column=token.column
        )

    def parse_help_setting(self) -> HelpSettingStatementNode:
        """Parse HELP SET statement

        Syntax:
            HELP SET "setting.name"

        Examples:
            HELP SET "case_conflict"
            HELP SET "auto_number"

        Note: Setting name must be string literal to support dots.
        """
        token = self.advance()  # Consume HELP
        self.expect(TokenType.SET)  # Consume SET

        # Parse setting name as string literal
        if not self.match(TokenType.STRING):
            raise ParseError(f"Expected setting name (string) after HELP SET", self.current_token())

        setting_name = self.advance().value

        return HelpSettingStatementNode(
            setting_name=setting_name,
            line_num=token.line,
            column=token.column
        )


def parse(tokens: List[Token]) -> ProgramNode:
    """
    Convenience function to parse tokens into AST

    Args:
        tokens: List of tokens from lexer

    Returns:
        ProgramNode representing the parsed program
    """
    parser = Parser(tokens)
    return parser.parse()
