"""
Parser for MBASIC 5.21

This is a two-pass recursive descent parser:
1. First pass: Collect all DEFINT/DEFSNG/DEFDBL/DEFSTR statements
2. Second pass: Parse the program with global type information

Key differences from interpreter:
- DEF type statements are applied globally at compile time
- Array dimensions must be constant expressions
- Variable types are fixed throughout the program
"""

from typing import List, Optional, Dict, Tuple
from tokens import Token, TokenType
from ast_nodes import *


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

    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.position = 0

        # Global type mapping from DEF statements
        # Maps first letter (a-z) to type (INTEGER, SINGLE, DOUBLE, STRING)
        self.def_type_map: Dict[str, str] = {}

        # Default type is SINGLE for all letters (use lowercase since lexer normalizes to lowercase)
        for letter in 'abcdefghijklmnopqrstuvwxyz':
            self.def_type_map[letter] = TypeInfo.SINGLE

        # Symbol table - maps variable names to their types
        self.symbol_table: Dict[str, str] = {}

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
        """Look ahead at token without advancing"""
        pos = self.position + offset
        if pos < len(self.tokens):
            return self.tokens[pos]
        return None

    def advance(self) -> Token:
        """Consume and return current token"""
        token = self.current()
        if token is None:
            raise ParseError("Unexpected end of input")
        self.position += 1
        return token

    def expect(self, token_type: TokenType) -> Token:
        """Consume token of expected type or raise error"""
        token = self.current()
        if token is None:
            raise ParseError(f"Expected {token_type.name}, got end of input")
        if token.type != token_type:
            raise ParseError(f"Expected {token_type.name}, got {token.type.name}", token)
        return self.advance()

    def match(self, *token_types: TokenType) -> bool:
        """Check if current token matches any of the given types"""
        token = self.current()
        if token is None:
            return False
        return token.type in token_types

    def at_end(self) -> bool:
        """Check if at end of tokens"""
        return self.position >= len(self.tokens) or self.current().type == TokenType.EOF

    def at_end_of_line(self) -> bool:
        """Check if at end of logical line (NEWLINE or APOSTROPHE or EOF)

        Note: APOSTROPHE starts a comment, which effectively ends the statement
        """
        token = self.current()
        if token is None:
            return True
        return token.type in (TokenType.NEWLINE, TokenType.EOF, TokenType.APOSTROPHE)

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
        var_type = TypeInfo.from_def_statement(def_token.type.name)

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
        statements: List[StatementNode] = []

        while not self.at_end_of_line():
            # Handle empty statements (multiple colons or colon at start of line)
            if self.match(TokenType.COLON):
                self.advance()
                continue

            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)

            # Check for statement separator
            if self.match(TokenType.COLON):
                self.advance()
            elif self.match(TokenType.SEMICOLON):
                # Allow trailing semicolon (treat as no-op, like some dialects)
                self.advance()
                # If there's more after the semicolon, treat it as error
                # But allow end of line or colon after semicolon
                if not self.at_end_of_line() and not self.match(TokenType.COLON):
                    token = self.current()
                    raise ParseError(f"Expected : or newline after ;, got {token.type.name}", token)
            elif self.match(TokenType.REM, TokenType.REMARK):
                # Allow REM without colon after statement (standard MBASIC)
                # REM consumes rest of line
                self.parse_remark()
                break  # REM ends the line
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
        token = self.current()
        if token is None:
            return None

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
        elif token.type == TokenType.SYSTEM:
            return self.parse_system()
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
        elif token.type == TokenType.RANDOMIZE:
            return self.parse_randomize()
        elif token.type == TokenType.SWAP:
            return self.parse_swap()
        elif token.type == TokenType.CLEAR:
            return self.parse_clear()
        elif token.type == TokenType.WIDTH:
            return self.parse_width()
        elif token.type == TokenType.POKE:
            return self.parse_poke()
        elif token.type == TokenType.OUT:
            return self.parse_out()
        elif token.type == TokenType.CALL:
            return self.parse_call()

        # Error handling
        elif token.type == TokenType.ERROR:
            # Check if this is "ON ERROR GOTO"
            raise ParseError(f"Unexpected ERROR keyword (use ON ERROR GOTO)", token)
        elif token.type == TokenType.RESUME:
            return self.parse_resume()

        # MID$ statement (substring assignment)
        # Detect MID$ used as statement: MID$(var, start, len) = value
        elif token.type == TokenType.MID:
            # Look ahead to distinguish MID$ statement from MID$ function
            # MID$ statement has pattern: MID$ ( ... ) =
            # MID$ is tokenized as single MID token ($ is part of the keyword)
            # We need to peek past the parentheses to see if there's an =
            saved_pos = self.position
            try:
                self.advance()  # Skip MID
                # MID$ is a single token, no need to check for DOLLAR separately
                if self.match(TokenType.LPAREN):
                    # Try to find matching RPAREN followed by EQUAL
                    paren_depth = 1
                    self.advance()  # Skip opening (
                    while not self.at_end_of_line() and paren_depth > 0:
                        if self.match(TokenType.LPAREN):
                            paren_depth += 1
                        elif self.match(TokenType.RPAREN):
                            paren_depth -= 1
                        self.advance()
                    # Now check if next token is EQUAL
                    if self.match(TokenType.EQUAL):
                        # This is MID$ statement!
                        self.position = saved_pos  # Restore position
                        return self.parse_mid_assignment()
            except:
                pass
            # Not a MID$ statement, restore and fall through to error
            self.position = saved_pos
            # If we get here, MID$ is being used in an unsupported way
            raise ParseError(f"MID$ must be used as function or assignment statement", token)

        # Assignment (implicit LET)
        elif token.type == TokenType.IDENTIFIER:
            return self.parse_assignment()

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
        token = self.current()
        if token is None:
            raise ParseError("Unexpected end of input in expression")

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

        else:
            raise ParseError(f"Unexpected token in expression: {token.type.name}", token)

    def parse_variable_or_function(self) -> ExpressionNode:
        """Parse variable reference or function call"""
        token = self.advance()
        name = token.value

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

            # Determine if it's a function or array
            # For now, treat it as a variable with subscripts
            # (function calls are handled separately for built-in functions)
            return VariableNode(
                name=name,
                type_suffix=self.get_type_suffix(name),
                subscripts=args,
                line_num=token.line,
                column=token.column
            )
        else:
            # Simple variable
            return VariableNode(
                name=name,
                type_suffix=self.get_type_suffix(name),
                subscripts=None,
                line_num=token.line,
                column=token.column
            )

    def is_builtin_function(self, token_type: TokenType) -> bool:
        """Check if token type is a built-in function"""
        builtin_functions = {
            TokenType.ABS, TokenType.ATN, TokenType.COS, TokenType.SIN, TokenType.TAN,
            TokenType.EXP, TokenType.LOG, TokenType.SQR, TokenType.INT, TokenType.FIX,
            TokenType.RND, TokenType.SGN, TokenType.ASC, TokenType.VAL, TokenType.LEN,
            TokenType.PEEK, TokenType.INP, TokenType.USR, TokenType.EOF_FUNC,
            # String functions
            TokenType.LEFT, TokenType.RIGHT, TokenType.MID, TokenType.CHR, TokenType.STR,
            TokenType.INKEY, TokenType.INPUT_FUNC, TokenType.SPACE, TokenType.STRING_FUNC,
            TokenType.INSTR, TokenType.HEX, TokenType.OCT,
            # Type conversion
            TokenType.CINT, TokenType.CSNG, TokenType.CDBL,
        }
        return token_type in builtin_functions

    def parse_builtin_function(self) -> FunctionCallNode:
        """Parse built-in function call"""
        func_token = self.advance()
        func_name = func_token.type.name

        # RND can be called without parentheses (RND returns random in [0,1))
        # RND(n) where n>0 returns same sequence, n<0 reseeds, n=0 repeats last
        if func_token.type == TokenType.RND and not self.match(TokenType.LPAREN):
            # RND without arguments
            return FunctionCallNode(
                name=func_name,
                arguments=[],
                line_num=func_token.line,
                column=func_token.column
            )

        # INKEY$ can be called without parentheses (returns keyboard input or "")
        if func_token.type == TokenType.INKEY and not self.match(TokenType.LPAREN):
            # INKEY$ without arguments
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
        func_name = "FN" + name_token.value

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
        """Parse REM or REMARK statement"""
        token = self.advance()

        # Read rest of line as comment text
        text_parts = []
        while not self.at_end_of_line():
            text_parts.append(self.advance().value)

        return RemarkStatementNode(
            text=' '.join(text_parts),
            line_num=token.line,
            column=token.column
        )

    def parse_print(self) -> PrintStatementNode:
        """Parse PRINT or ? statement

        Syntax:
            PRINT expr1, expr2          - Print to screen
            PRINT #filenum, expr1       - Print to file
        """
        token = self.advance()

        # Check for file number: PRINT #n, ...
        file_number = None
        if self.match(TokenType.HASH):
            self.advance()  # Skip #
            file_number = self.parse_expression()
            # Expect comma after file number
            if self.match(TokenType.COMMA):
                self.advance()
            # Note: Some dialects allow semicolon, but MBASIC uses comma

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

        # If no trailing separator, add newline
        if len(separators) <= len(expressions):
            separators.append('\n')

        return PrintStatementNode(
            expressions=expressions,
            separators=separators,
            file_number=file_number,
            line_num=token.line,
            column=token.column
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

        # If no trailing separator, add newline
        if len(separators) <= len(expressions):
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
            INPUT #filenum, var1       - Read from file
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
            # Expect semicolon or comma after prompt
            if self.match(TokenType.SEMICOLON, TokenType.COMMA):
                self.advance()

        # Check for LINE modifier after semicolon: INPUT "prompt";LINE var$
        # LINE allows input of entire line including commas
        line_mode = False
        if self.match(TokenType.LINE_INPUT):
            line_mode = True
            self.advance()

        # Parse variable list
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

            variables.append(VariableNode(
                name=var_token.value,
                type_suffix=self.get_type_suffix(var_token.value),
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

    def parse_stop(self) -> StopStatementNode:
        """Parse STOP statement"""
        token = self.advance()

        return StopStatementNode(
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

    def parse_chain(self) -> ChainStatementNode:
        """Parse CHAIN statement

        Syntax:
            CHAIN filename$
        """
        token = self.advance()

        # Parse filename expression (must be string)
        filename = self.parse_expression()

        return ChainStatementNode(
            filename=filename,
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
            DELETE start-end   - Delete lines from start to end
            DELETE -end        - Delete from beginning to end
            DELETE start-      - Delete from start to end of program
        """
        token = self.advance()

        # Parse the range: start-end, -end, or start-
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

                # Expect minus
                if self.match(TokenType.MINUS):
                    self.advance()
                    # Check if there's an end value
                    if self.match(TokenType.NUMBER):
                        end_token = self.advance()
                        end = NumberNode(value=end_token.value, literal=str(end_token.value), line_num=end_token.line, column=end_token.column)

        return DeleteStatementNode(
            start=start,
            end=end,
            line_num=token.line,
            column=token.column
        )

    def parse_renum(self) -> RenumStatementNode:
        """Parse RENUM statement

        Syntax:
            RENUM                     - Renumber starting at 10, increment 10
            RENUM new_start           - Renumber starting at new_start, increment 10
            RENUM new_start,increment - Renumber starting at new_start with increment
        """
        token = self.advance()

        new_start = None
        increment = None

        # Check if there are arguments
        if not self.at_end_of_line() and not self.match(TokenType.COLON):
            # Parse new_start
            new_start = self.parse_expression()

            # Check for comma and increment
            if self.match(TokenType.COMMA):
                self.advance()
                if not self.at_end_of_line() and not self.match(TokenType.COLON):
                    increment = self.parse_expression()

        return RenumStatementNode(
            new_start=new_start,
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
        - IF condition THEN line_number :ELSE line_number
        - IF condition THEN statement : statement
        - IF condition THEN statement ELSE statement
        - IF condition GOTO line_number
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
            self.advance()

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

        Note: Some files may have degenerate FOR loops like "FOR 1 TO 100"
        which we'll try to handle gracefully
        """
        token = self.advance()

        # Check if we have a proper variable or just a number (malformed)
        var_token = self.current()
        if var_token and var_token.type == TokenType.IDENTIFIER:
            self.advance()
            variable = VariableNode(
                name=var_token.value,
                type_suffix=self.get_type_suffix(var_token.value),
                subscripts=None,
                line_num=var_token.line,
                column=var_token.column
            )

            # Expect =
            self.expect(TokenType.EQUAL)

            # Parse start expression
            start_expr = self.parse_expression()
        elif var_token and var_token.type == TokenType.NUMBER:
            # Malformed FOR loop like "FOR 1 TO 100"
            # Create a dummy variable "I" and use the number as start
            start_expr = NumberNode(
                value=float(var_token.value),
                literal=var_token.value,
                line_num=var_token.line,
                column=var_token.column
            )
            self.advance()

            variable = VariableNode(
                name="I",  # Dummy variable
                type_suffix=None,
                subscripts=None,
                line_num=var_token.line,
                column=var_token.column
            )
        else:
            raise ParseError("Expected variable or number after FOR", var_token)

        # Expect TO
        self.expect(TokenType.TO)

        # Parse end expression
        end_expr = self.parse_expression()

        # Optional STEP
        step_expr = None
        if self.match(TokenType.STEP):
            self.advance()
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
        while not self.at_end_of_line() and not self.match(TokenType.COLON):
            if self.match(TokenType.IDENTIFIER):
                var_token = self.advance()
                variables.append(VariableNode(
                    name=var_token.value,
                    type_suffix=self.get_type_suffix(var_token.value),
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
            self.expect(TokenType.GOTO)
            line_num_token = self.current()
            if line_num_token and line_num_token.type in (TokenType.NUMBER, TokenType.LINE_NUMBER):
                self.advance()
                return OnErrorStatementNode(
                    line_number=int(line_num_token.value),
                    line_num=token.line,
                    column=token.column
                )
            else:
                raise ParseError("Expected line number after ON ERROR GOTO", line_num_token)

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

        Note: In compiled BASIC, dimensions must be constant expressions
        """
        token = self.advance()

        arrays: List[ArrayDeclNode] = []

        while not self.at_end_of_line() and not self.match(TokenType.COLON):
            # Parse array name
            name_token = self.expect(TokenType.IDENTIFIER)
            name = name_token.value

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

        Example:
            ERASE A, B$, C
            ERASE M:DIM M(64)
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

        Note: MID$ is tokenized as a single MID token
        """
        token = self.current()  # MID token
        self.advance()  # Skip MID (which includes the $)

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

        Note: Type collection already happened in first pass.
        This just creates the AST node for documentation purposes.
        """
        token = self.advance()
        var_type = TypeInfo.from_def_statement(token.type.name)

        letter_ranges: List[Tuple[str, str]] = []

        # Parse letter ranges
        while not self.at_end_of_line() and not self.match(TokenType.COLON):
            # Get first letter
            letter_token = self.expect(TokenType.IDENTIFIER)
            first_letter = letter_token.value[0].upper()

            # Check for range (A-Z)
            if self.match(TokenType.MINUS):
                self.advance()
                last_letter_token = self.expect(TokenType.IDENTIFIER)
                last_letter = last_letter_token.value[0].upper()
                letter_ranges.append((first_letter, last_letter))
            else:
                # Single letter
                letter_ranges.append((first_letter, first_letter))

            # Check for comma (more letters)
            if self.match(TokenType.COMMA):
                self.advance()

        return DefTypeStatementNode(
            var_type=var_type,
            letter_ranges=letter_ranges,
            line_num=token.line,
            column=token.column
        )

    def parse_deffn(self) -> DefFnStatementNode:
        """
        Parse DEF FN statement - user-defined function

        Syntax: DEF FNname[(param1, param2, ...)] = expression
        Note: FN is part of the function name, e.g., "FNR", "FNA$"

        Examples:
            DEF FNR(X) = INT(X*100+.5)/100
            DEF FNA$(U,V) = P1$+CHR$(31+U*2)+CHR$(48+V*5)
            DEF FNB = 42  (no parameters)
        """
        token = self.advance()  # Consume DEF

        # Next token should be identifier starting with "FN"
        # In MBASIC, "DEF FNR(X)" means function name is "FNR"
        fn_name_token = self.current()

        if fn_name_token and fn_name_token.type == TokenType.FN:
            # Handle "DEF FN name" with space (optional FN keyword)
            self.advance()
            fn_name_token = self.expect(TokenType.IDENTIFIER)
            function_name = "FN" + fn_name_token.value
        elif fn_name_token and fn_name_token.type == TokenType.IDENTIFIER:
            # "DEF FNR" without space - identifier is "FNR"
            if not fn_name_token.value.startswith("FN"):
                raise ParseError("DEF function name must start with FN", fn_name_token)
            self.advance()
            function_name = fn_name_token.value
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
                    # Create VariableNode for each parameter
                    param_var = VariableNode(
                        name=param_token.value,
                        type_suffix=self.get_type_suffix(param_token.value),
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
        raise NotImplementedError("COMMON parsing not yet implemented")

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

        Note: Lexer produces LINE_INPUT token, but INPUT keyword may follow
        """
        token = self.advance()

        # The lexer may produce INPUT as next token - consume it if present
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
        variable = VariableNode(
            name=var_token.value,
            type_suffix=self.get_type_suffix(var_token.value),
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

            variables.append(VariableNode(
                name=var_token.value,
                type_suffix=self.get_type_suffix(var_token.value),
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

        Unquoted strings extend until comma, colon, or end of line
        """
        token = self.advance()

        values: List[ExpressionNode] = []
        while not self.at_end_of_line() and not self.match(TokenType.COLON):
            # Try to parse as expression (handles numbers and quoted strings)
            # If that fails or we encounter identifiers, treat as unquoted string

            current_token = self.current()
            if current_token is None:
                break

            # If it's a string literal or number, parse as expression
            if current_token.type in (TokenType.STRING, TokenType.NUMBER):
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

    def parse_width(self) -> WidthStatementNode:
        """Parse WIDTH statement - Syntax: WIDTH width [, device]"""
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

    def parse_call(self) -> CallStatementNode:
        """
        Parse CALL statement - call machine language routine (MBASIC 5.21)

        Standard MBASIC 5.21 Syntax:
            CALL address           - Call machine code at numeric address

        Examples:
            CALL 16384             - Call decimal address
            CALL &HC000            - Call hex address
            CALL A                 - Call address in variable
            CALL DIO+1             - Call computed address

        Note: Also accepts extended syntax for other BASIC dialects.
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

    def parse_resume(self) -> ResumeStatementNode:
        """Parse RESUME statement - Syntax: RESUME [NEXT | line_number]"""
        token = self.advance()

        line_number = None
        if self.match(TokenType.NEXT):
            self.advance()
            line_number = 0  # 0 means RESUME NEXT
        elif self.match(TokenType.LINE_NUMBER, TokenType.NUMBER):
            line_number = int(self.advance().value)

        return ResumeStatementNode(
            line_number=line_number,
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
