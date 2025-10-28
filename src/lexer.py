"""
Lexer for MBASIC 5.21 (CP/M era Microsoft BASIC-80)
Based on BASIC-80 Reference Manual Version 5.21
"""
from typing import List, Optional
from tokens import Token, TokenType, KEYWORDS


class LexerError(Exception):
    """Exception raised for lexer errors"""
    def __init__(self, message: str, line: int, column: int):
        super().__init__(f"Lexer error at {line}:{column}: {message}")
        self.line = line
        self.column = column


class Lexer:
    """Tokenizes MBASIC 5.21 source code"""

    def __init__(self, source: str):
        self.source = source
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens: List[Token] = []

    def current_char(self) -> Optional[str]:
        """Return the current character or None if at end"""
        if self.pos >= len(self.source):
            return None
        return self.source[self.pos]

    def peek_char(self, offset: int = 1) -> Optional[str]:
        """Look ahead at a character without consuming it"""
        pos = self.pos + offset
        if pos >= len(self.source):
            return None
        return self.source[pos]

    def advance(self) -> Optional[str]:
        """Consume and return the current character"""
        if self.pos >= len(self.source):
            return None

        char = self.source[self.pos]
        self.pos += 1

        if char == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1

        return char

    def skip_whitespace(self, skip_newlines: bool = False):
        """Skip spaces and tabs (and optionally newlines/carriage returns)"""
        while self.current_char() is not None:
            char = self.current_char()
            if char == ' ' or char == '\t':
                self.advance()
            elif skip_newlines and (char == '\n' or char == '\r'):
                self.advance()
            else:
                break

    def read_number(self) -> Token:
        """
        Read a number literal
        - Integer: -32768 to 32767
        - Fixed point: with decimal point
        - Floating point: with E or D exponent notation
        - Octal: &O or & prefix
        - Hexadecimal: &H prefix
        """
        start_line = self.line
        start_column = self.column
        num_str = ''

        # Check for octal/hex prefix
        if self.current_char() == '&':
            num_str += self.advance()
            next_char = self.current_char()

            if next_char and next_char.upper() == 'H':
                # Hexadecimal
                num_str += self.advance()
                while self.current_char() and self.current_char() in '0123456789ABCDEFabcdef':
                    num_str += self.advance()
                try:
                    value = int(num_str[2:], 16) if len(num_str) > 2 else 0
                except ValueError:
                    raise LexerError(f"Invalid hex number: {num_str}", start_line, start_column)
                return Token(TokenType.NUMBER, value, start_line, start_column)

            elif next_char and next_char.upper() == 'O':
                # Octal with &O prefix
                num_str += self.advance()
                while self.current_char() and self.current_char() in '01234567':
                    num_str += self.advance()
                try:
                    value = int(num_str[2:], 8) if len(num_str) > 2 else 0
                except ValueError:
                    raise LexerError(f"Invalid octal number: {num_str}", start_line, start_column)
                return Token(TokenType.NUMBER, value, start_line, start_column)

            elif next_char and next_char in '01234567':
                # Octal with just & prefix
                while self.current_char() and self.current_char() in '01234567':
                    num_str += self.advance()
                try:
                    value = int(num_str[1:], 8) if len(num_str) > 1 else 0
                except ValueError:
                    raise LexerError(f"Invalid octal number: {num_str}", start_line, start_column)
                return Token(TokenType.NUMBER, value, start_line, start_column)

        # Check for leading decimal point (.5 syntax)
        if self.current_char() == '.' and self.peek_char() and self.peek_char().isdigit():
            num_str += self.advance()  # Consume '.'
            # Read digits after decimal point
            while self.current_char() is not None and self.current_char().isdigit():
                num_str += self.advance()
        else:
            # Read decimal digits before decimal point
            while self.current_char() is not None and self.current_char().isdigit():
                num_str += self.advance()

            # Check for decimal point
            # MBASIC allows trailing dot: 100. is valid (same as 100.0)
            if self.current_char() == '.':
                next_char = self.peek_char()
                # Allow trailing dot or dot followed by digits
                if next_char is None or next_char.isdigit() or not next_char.isalnum():
                    num_str += self.advance()  # Consume '.'
                    # Read digits after decimal point (if any)
                    while self.current_char() is not None and self.current_char().isdigit():
                        num_str += self.advance()

        # Check for scientific notation (E or D)
        if self.current_char() and self.current_char().upper() in ['E', 'D']:
            num_str += self.advance()
            # Optional sign
            if self.current_char() in ['+', '-']:
                num_str += self.advance()
            # Exponent digits
            if not (self.current_char() and self.current_char().isdigit()):
                raise LexerError(f"Invalid number format: {num_str}", start_line, start_column)
            while self.current_char() is not None and self.current_char().isdigit():
                num_str += self.advance()

        # Check for type suffix (! # %)
        type_suffix = None
        if self.current_char() in ['!', '#', '%']:
            type_suffix = self.advance()

        try:
            # Parse the number
            if '.' in num_str or 'E' in num_str.upper() or 'D' in num_str.upper():
                value = float(num_str.replace('D', 'E').replace('d', 'e'))
            else:
                value = int(num_str)
        except ValueError:
            raise LexerError(f"Invalid number: {num_str}", start_line, start_column)

        return Token(TokenType.NUMBER, value, start_line, start_column)

    def read_string(self) -> Token:
        """Read a string literal enclosed in double quotes"""
        start_line = self.line
        start_column = self.column

        self.advance()  # Skip opening quote
        string_val = ''

        while self.current_char() is not None and self.current_char() != '"':
            char = self.current_char()
            if char == '\n':
                raise LexerError("Unterminated string", self.line, self.column)
            string_val += self.advance()

        if self.current_char() is None:
            raise LexerError("Unterminated string", start_line, start_column)

        self.advance()  # Skip closing quote

        return Token(TokenType.STRING, string_val, start_line, start_column)

    def read_identifier(self) -> Token:
        """
        Read an identifier or keyword
        Identifiers can contain letters, digits, and end with type suffix $ % ! #
        In MBASIC, $ % ! # are considered part of the identifier

        Special handling: In old BASIC, keywords can run together with identifiers
        without spaces. E.g., "NEXTI" should be parsed as "NEXT" + "I".
        This method checks for statement keywords at the start of identifiers.
        """
        start_line = self.line
        start_column = self.column
        ident = ''

        # First character must be a letter
        if self.current_char() and self.current_char().isalpha():
            ident += self.advance()
        else:
            raise LexerError(f"Invalid identifier", start_line, start_column)

        # Subsequent characters can be letters, digits, or periods (in Extended BASIC)
        while self.current_char() is not None:
            char = self.current_char()
            if char.isalnum() or char == '.':
                ident += self.advance()
            elif char in ['$', '%', '!', '#']:
                # Type suffix - only allowed at end of identifier
                ident += self.advance()
                break
            else:
                break

        # Check if it's a keyword (case-insensitive, normalize to lowercase)
        ident_lower = ident.lower()
        if ident_lower in KEYWORDS:
            token = Token(KEYWORDS[ident_lower], ident_lower, start_line, start_column)
            token.original_case_keyword = ident  # Preserve original keyword case
            return token

        # Special handling for file I/O statements with # (file number follows)
        # In MBASIC, "PRINT#1,A" should be tokenized as PRINT + # + 1
        # But our lexer reads "PRINT#" as identifier because # is a type suffix
        # We need to split these specifically (use lowercase)
        FILE_IO_KEYWORDS = {
            'print#': TokenType.PRINT,
            'lprint#': TokenType.LPRINT,
            'input#': TokenType.INPUT,
            'write#': TokenType.WRITE,
            'field#': TokenType.FIELD,
            'get#': TokenType.GET,
            'put#': TokenType.PUT,
            'close#': TokenType.CLOSE,
        }

        if ident_lower in FILE_IO_KEYWORDS:
            # Put the # back into the source
            self.pos -= 1
            self.column -= 1
            # Return the keyword token without the #
            keyword = ident_lower[:-1]  # Remove the #
            token = Token(FILE_IO_KEYWORDS[ident_lower], keyword, start_line, start_column)
            token.original_case_keyword = ident[:-1]  # Preserve original case without the #
            return token

        # Check if identifier starts with a statement keyword (MBASIC compatibility)
        # In old BASIC, keywords could run together: "NEXTI" = "NEXT I", "FORI" = "FOR I"
        # We check for common statement keywords that might be concatenated
        # Note: Only include keywords that can START a statement or commonly appear before identifiers
        # Exclude TO and STEP as they're clause keywords, not statement starters (use lowercase)
        STATEMENT_KEYWORDS = ['next', 'for', 'if', 'then', 'else', 'goto', 'gosub',
                             'print', 'input', 'let', 'dim', 'read', 'data', 'end',
                             'stop', 'return', 'on']

        for keyword in STATEMENT_KEYWORDS:
            if ident_lower.startswith(keyword) and len(ident_lower) > len(keyword):
                # Check if character after keyword is valid identifier start (must be LETTER)
                # Don't split if followed by digit (e.g., STEP1 should stay as STEP1)
                next_char = ident_lower[len(keyword)]
                if next_char.isalpha():  # Only split if next char is a letter
                    # Split: return keyword token, put rest back in buffer
                    keyword_part = ident[:len(keyword)]
                    rest_part = ident[len(keyword):]

                    # Put the rest back into the source
                    for i in range(len(rest_part) - 1, -1, -1):
                        self.pos -= 1
                        self.column -= 1

                    # Return the keyword token
                    token = Token(KEYWORDS[keyword], keyword, start_line, start_column)
                    token.original_case_keyword = keyword_part  # Preserve original case of keyword part
                    return token

        # Otherwise it's an identifier
        # Normalize to lowercase (BASIC is case-insensitive) but preserve original case
        token = Token(TokenType.IDENTIFIER, ident.lower(), start_line, start_column)
        token.original_case = ident  # Preserve original case for display
        return token

    def read_line_number(self) -> Token:
        """Read a line number at the beginning of a line (0-65529)"""
        start_line = self.line
        start_column = self.column
        num_str = ''

        while self.current_char() is not None and self.current_char().isdigit():
            num_str += self.advance()

        line_num = int(num_str)
        if line_num > 65529:
            raise LexerError(f"Line number {line_num} exceeds maximum of 65529", start_line, start_column)

        return Token(TokenType.LINE_NUMBER, line_num, start_line, start_column)

    def skip_comment(self):
        """Skip a REM or ' comment (everything until end of line)"""
        while self.current_char() is not None and self.current_char() != '\n':
            self.advance()

    def read_comment(self):
        """Read comment text until end of line"""
        comment_text = []
        while self.current_char() is not None and self.current_char() != '\n':
            comment_text.append(self.current_char())
            self.advance()
        return ''.join(comment_text).strip()

    def tokenize(self) -> List[Token]:
        """Tokenize the entire source code"""
        self.tokens = []
        at_line_start = True

        while self.pos < len(self.source):
            self.skip_whitespace(skip_newlines=False)

            char = self.current_char()
            if char is None:
                break

            start_line = self.line
            start_column = self.column

            # Check for line number at start of line
            if at_line_start and char.isdigit():
                self.tokens.append(self.read_line_number())
                at_line_start = False
                continue

            # Newline (both \n and \r)
            # In CP/M BASIC, \r (carriage return) can be used as statement separator
            if char == '\n':
                self.tokens.append(Token(TokenType.NEWLINE, '\n', start_line, start_column))
                self.advance()
                # Skip following \r if present (handles \n\r sequences)
                if self.current_char() == '\r':
                    self.advance()
                at_line_start = True
                continue

            if char == '\r':
                self.tokens.append(Token(TokenType.NEWLINE, '\r', start_line, start_column))
                self.advance()
                # Skip following \n if present (handles \r\n sequences)
                if self.current_char() == '\n':
                    self.advance()
                at_line_start = True
                continue

            # Apostrophe comment (like REM)
            if char == "'":
                self.advance()  # Skip the apostrophe
                comment_text = self.read_comment()
                self.tokens.append(Token(TokenType.APOSTROPHE, comment_text, start_line, start_column))
                continue

            # Numbers (including &H hex, &O octal, and .5 leading decimal)
            if char.isdigit() or \
               (char == '&' and self.peek_char() and
                (self.peek_char().upper() in ['H', 'O'] or
                 self.peek_char().isdigit())) or \
               (char == '.' and self.peek_char() and self.peek_char().isdigit()):
                self.tokens.append(self.read_number())
                continue

            # Strings
            if char == '"':
                self.tokens.append(self.read_string())
                continue

            # Identifiers and keywords
            if char.isalpha():
                token = self.read_identifier()
                # Special handling for REM/REMARK - read comment text
                if token.type in (TokenType.REM, TokenType.REMARK):
                    comment_text = self.read_comment()
                    # Replace token value with comment text
                    token = Token(token.type, comment_text, token.line, token.column)
                    self.tokens.append(token)
                else:
                    self.tokens.append(token)
                at_line_start = False
                continue

            # Operators and delimiters
            if char == '+':
                self.tokens.append(Token(TokenType.PLUS, '+', start_line, start_column))
                self.advance()
            elif char == '-':
                self.tokens.append(Token(TokenType.MINUS, '-', start_line, start_column))
                self.advance()
            elif char == '*':
                self.tokens.append(Token(TokenType.MULTIPLY, '*', start_line, start_column))
                self.advance()
            elif char == '/':
                self.tokens.append(Token(TokenType.DIVIDE, '/', start_line, start_column))
                self.advance()
            elif char == '^':
                self.tokens.append(Token(TokenType.POWER, '^', start_line, start_column))
                self.advance()
            elif char == '\\':
                self.tokens.append(Token(TokenType.BACKSLASH, '\\', start_line, start_column))
                self.advance()
            elif char == '=':
                self.tokens.append(Token(TokenType.EQUAL, '=', start_line, start_column))
                self.advance()
            elif char == '<':
                self.advance()
                next_char = self.current_char()
                if next_char == '>':
                    self.tokens.append(Token(TokenType.NOT_EQUAL, '<>', start_line, start_column))
                    self.advance()
                elif next_char == '=':
                    self.tokens.append(Token(TokenType.LESS_EQUAL, '<=', start_line, start_column))
                    self.advance()
                else:
                    self.tokens.append(Token(TokenType.LESS_THAN, '<', start_line, start_column))
            elif char == '>':
                self.advance()
                next_char = self.current_char()
                if next_char == '<':
                    self.tokens.append(Token(TokenType.NOT_EQUAL, '><', start_line, start_column))
                    self.advance()
                elif next_char == '=':
                    self.tokens.append(Token(TokenType.GREATER_EQUAL, '>=', start_line, start_column))
                    self.advance()
                else:
                    self.tokens.append(Token(TokenType.GREATER_THAN, '>', start_line, start_column))
            elif char == '(':
                self.tokens.append(Token(TokenType.LPAREN, '(', start_line, start_column))
                self.advance()
            elif char == ')':
                self.tokens.append(Token(TokenType.RPAREN, ')', start_line, start_column))
                self.advance()
            elif char == ',':
                self.tokens.append(Token(TokenType.COMMA, ',', start_line, start_column))
                self.advance()
            elif char == ';':
                self.tokens.append(Token(TokenType.SEMICOLON, ';', start_line, start_column))
                self.advance()
            elif char == ':':
                self.tokens.append(Token(TokenType.COLON, ':', start_line, start_column))
                self.advance()
                at_line_start = False  # After colon, we're mid-line
            elif char == '?':
                self.tokens.append(Token(TokenType.QUESTION, '?', start_line, start_column))
                self.advance()
            elif char == '#':
                self.tokens.append(Token(TokenType.HASH, '#', start_line, start_column))
                self.advance()
            elif char == '&':
                # Standalone & operator (not hex/octal prefix)
                self.tokens.append(Token(TokenType.AMPERSAND, '&', start_line, start_column))
                self.advance()
            else:
                # Skip control characters gracefully
                if ord(char) < 32 and char not in ['\t', '\n', '\r']:
                    # Control character - skip it
                    self.advance()
                    continue
                raise LexerError(f"Unexpected character: '{char}' (0x{ord(char):02x})", start_line, start_column)

            at_line_start = False

        # Add EOF token
        self.tokens.append(Token(TokenType.EOF, None, self.line, self.column))
        return self.tokens


def tokenize(source: str) -> List[Token]:
    """Convenience function to tokenize source code"""
    lexer = Lexer(source)
    return lexer.tokenize()
