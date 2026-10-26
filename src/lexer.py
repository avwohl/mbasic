"""
Lexer for MBASIC 5.21 (CP/M era MBASIC-80)
Based on BASIC-80 Reference Manual Version 5.21

This implementation includes the full set of keywords and tokenization rules from MBASIC 5.21,
with support for Extended BASIC features such as periods in identifiers (e.g., "RECORD.FIELD").

Note: 'Based on' means implementation follows the MBASIC 5.21 specification for lexical analysis.
All documented MBASIC 5.21 tokens and keywords are supported.
"""
from typing import List, Optional
from src.tokens import Token, TokenType, KEYWORDS
from src.simple_keyword_case import SimpleKeywordCase
from src.number_format import exceeds_range, literal_precision, machine_infinity


def create_keyword_case_manager() -> SimpleKeywordCase:
    """Create a SimpleKeywordCase handler configured from settings.

    The lexer uses SimpleKeywordCase which supports force-based case policies:
    - force_lower: Convert all keywords to lowercase (default)
    - force_upper: Convert all keywords to UPPERCASE
    - force_capitalize: Convert all keywords to Capitalized form

    Note: SimpleKeywordCase validates policy strings in its __init__ method. Invalid
    policy values (not in: force_lower, force_upper, force_capitalize) are automatically
    corrected to force_lower. See src/simple_keyword_case.py for implementation.

    Returns:
        SimpleKeywordCase with policy from settings (validated), or default (force_lower)
    """
    try:
        from src.settings import get
        policy = get("case_style", "force_lower")
        return SimpleKeywordCase(policy=policy)
    except Exception:
        # If settings unavailable, use default
        return SimpleKeywordCase(policy="force_lower")


class LexerError(Exception):
    """Exception raised for lexer errors"""
    def __init__(self, message: str, line: int, column: int):
        super().__init__(f"Lexer error at {line}:{column}: {message}")
        self.line = line
        self.column = column


class LexerRefused(LexerError):
    """A line MBASIC refuses at entry with Syntax error (&O9, &19): it is not stored."""


class LexerOverflow(LexerError):
    """A &H, &O or & constant that does not fit 16 bits (MBASIC: Overflow)."""


def radix_constant_value(digits: str, base: int, line: int, column: int) -> int:
    """The value of an &H, &O or & constant: a signed 16-bit integer.

    MBASIC reads &HFFFF and &O177777 as -1 and &H8000 as -32768. At line entry
    it stops with Overflow for a hex constant of more than four digits (even
    &H00010) and for an octal constant above 65535 (&O0177777 is fine).
    """
    if base == 16 and len(digits) > 4:
        raise LexerOverflow("Overflow", line, column)
    value = int(digits, base) if digits else 0
    if value > 65535:
        raise LexerOverflow("Overflow", line, column)
    return value - 65536 if value >= 32768 else value


# Reserved words of MBASIC 5.21 (the CRUNCH table in bintrp.mac) that are plain
# words, without "$" or "(" inside.  CRUNCH takes one of these as a keyword
# when the next character is not a letter, a digit or ".", so "NAME$", "LEN%"
# and "FOR$" are the keyword followed by a stray type character.  Words of
# this implementation that the binary does not reserve (HELP, SHOW, SET and so
# on) are not here: "SHOW%" is an ordinary variable.
RESERVED_STEMS = frozenset((
    "auto and abs atn asc close cont clear cint csng cdbl cvi cvs cvd cos call "
    "common chain delete data dim defstr defint defsng defdbl def else end "
    "erase edit error erl err exp eof eqv for field files fix fre goto gosub "
    "get input if instr int inp imp kill lprint llist lpos let line load lset "
    "list log loc len lof merge mod name new not open out on or option print "
    "put poke pos peek return read run restore rem resume rset rnd renum "
    "reset randomize stop swap save step sgn sqr sin system then tron troff "
    "to tan using val varptr width wait while wend write xor next usr").split()) & frozenset(KEYWORDS)


class Lexer:
    """Tokenizes MBASIC 5.21 source code

    With defer_errors, text the lexer cannot read (a stray "$" after a
    reserved word, say) becomes an ILLEGAL token that holds the rest of the
    line, so the parser can store the line and fail when it runs, as MBASIC
    does.  Overflow still raises LexerOverflow: MBASIC refuses such a line.
    """

    def __init__(self, source: str, keyword_case_manager: Optional[SimpleKeywordCase] = None,
                 defer_errors: bool = False):
        self.defer_errors = defer_errors
        self.source = source
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens: List[Token] = []
        #: Literals replaced by machine infinity because they were infinite in
        #: their precision (1E39). MBASIC says "Overflow" at line entry.
        self.overflow_literals = 0

        # Keyword case handler - uses SimpleKeywordCase (see create_keyword_case_manager())
        self.keyword_case_manager = keyword_case_manager or SimpleKeywordCase(policy="force_lower")

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
                    value = self._radix(num_str[2:], 16, start_line, start_column)
                except ValueError:
                    raise LexerError(f"Invalid hex number: {num_str}", start_line, start_column)
                return Token(TokenType.NUMBER, value, start_line, start_column,
                             literal_text=num_str)

            elif next_char and next_char.upper() == 'O':
                # Octal with &O prefix
                num_str += self.advance()
                while self.current_char() and self.current_char() in '01234567':
                    num_str += self.advance()
                self._refuse_octal_89(start_line, start_column)
                try:
                    value = self._radix(num_str[2:], 8, start_line, start_column)
                except ValueError:
                    raise LexerError(f"Invalid octal number: {num_str}", start_line, start_column)
                return Token(TokenType.NUMBER, value, start_line, start_column,
                             literal_text=num_str)

            elif next_char and next_char in '0123456789':
                # Octal with just & prefix
                while self.current_char() and self.current_char() in '01234567':
                    num_str += self.advance()
                self._refuse_octal_89(start_line, start_column)
                try:
                    value = self._radix(num_str[1:], 8, start_line, start_column)
                except ValueError:
                    raise LexerError(f"Invalid octal number: {num_str}", start_line, start_column)
                return Token(TokenType.NUMBER, value, start_line, start_column,
                             literal_text=num_str)

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
                # Allow trailing dot or dot followed by digits.  "5.E2" is 500: the
                # dot is part of the number when an exponent with digits follows.
                # FIN takes the dot first, so "1.E" and "1.ELSE" both keep the
                # dot; the E+L/Q rule below then ends the number before ELSE/EQV.
                exp_follows = next_char is not None and next_char.upper() in ['E', 'D']
                if next_char is None or next_char.isdigit() or not next_char.isalnum() or exp_follows:
                    num_str += self.advance()  # Consume '.'
                    # Read digits after decimal point (if any)
                    while self.current_char() is not None and self.current_char().isdigit():
                        num_str += self.advance()

        # Check for scientific notation (E or D).  MBASIC 5.21 FIN takes the
        # letter as an exponent marker even when no digits follow ("1E" is 1),
        # with one exception: E followed by L or Q ends the number, because
        # that is the start of ELSE or EQV ("PRINT 1ELSE PRINT 2").
        if self.current_char() and self.current_char().upper() in ['E', 'D'] and \
           not (self.current_char().upper() == 'E' and
                self.peek_char() is not None and self.peek_char().upper() in ['L', 'Q']):
            num_str += self.advance()
            # Optional sign
            if self.current_char() in ['+', '-']:
                num_str += self.advance()
            # Exponent digits (none is allowed)
            while self.current_char() is not None and self.current_char().isdigit():
                num_str += self.advance()

        # Check for type suffix (! # %)
        type_suffix = None
        if self.current_char() in ['!', '#', '%']:
            type_suffix = self.advance()

        try:
            # Parse the number
            if '.' in num_str or 'E' in num_str.upper() or 'D' in num_str.upper():
                # An exponent without digits ("1E", "1D+") means exponent 0
                value_str = num_str.replace('D', 'E').replace('d', 'e')
                if value_str[-1] in 'Ee+-':
                    value_str = value_str.rstrip('+-').rstrip('Ee')
                value = float(value_str)
            else:
                value = int(num_str)
        except ValueError:
            raise LexerError(f"Invalid number: {num_str}", start_line, start_column)

        literal_text = num_str + (type_suffix or '')
        if type_suffix != '%':
            value = self._literal_in_range(value, literal_text)

        # Keep the source text: the type suffix decides whether this literal
        # is single or double precision, and it cannot be recovered from the
        # value afterwards - 1# and 1 both arrive as 1.0.
        return Token(TokenType.NUMBER, value, start_line, start_column,
                     literal_text=num_str + (type_suffix or ''))

    def _literal_in_range(self, value, literal_text):
        """A decimal literal that its precision cannot hold becomes machine infinity.

        1E39 is a single, and a single stops at 3.4E38 (binary32 here; the MBF
        range is not emulated, see docs/dev/MBASIC_521_DIVERGENCES_TODO.md,
        section 10). MBASIC prints Overflow when the line is entered and
        keeps the largest number instead.
        """
        if self._in_data_statement():
            return value        # DATA text is raw: no Overflow at entry
        digits = literal_precision(literal_text, value)
        try:
            if not exceeds_range(value, digits):
                return value
        except OverflowError:       # an int too big even for a float
            pass
        self.overflow_literals += 1
        return machine_infinity(digits)

    def _read_go_to_sub(self, ident: str, start_line: int, start_column: int) -> Optional[Token]:
        """Join "GO TO" / "GO SUB" into GOTO / GOSUB.

        MBASIC 5.21 CRUNCH joins the bare word GO, one space, and TO or SUB.
        Real MBASIC mishandles the odd forms: "GO  TO" (two spaces) becomes
        GOSUB, "GO  SUB" stays two words, and "GO TO30" is a syntax error.
        This method joins only the form that works in real MBASIC: one space,
        TO or SUB, then a character that cannot continue a name.  Any other
        text stays an ordinary identifier.
        Returns None, with nothing consumed, when the text is not that form.
        """
        if ident.lower() != 'go' or self.current_char() != ' ':
            return None
        rest = self.source[self.pos + 1:self.pos + 6].lower()
        for word, keyword in (('to', 'goto'), ('sub', 'gosub')):
            if rest.startswith(word):
                after = rest[len(word):len(word) + 1]
                if after.isalnum() or after == '.':
                    return None
                typed = ident + self.source[self.pos + 1:self.pos + 1 + len(word)]
                for _ in range(1 + len(word)):
                    self.advance()
                token = Token(KEYWORDS[keyword], keyword, start_line, start_column)
                token.original_case_keyword = self.keyword_case_manager.register_keyword(
                    keyword, typed, start_line, start_column)
                return token
        return None

    def read_string(self) -> Token:
        """Read a string literal enclosed in double quotes"""
        start_line = self.line
        start_column = self.column

        self.advance()  # Skip opening quote
        string_val = ''

        # MBASIC 5.21 accepts a string that the end of the line closes.
        while self.current_char() is not None and self.current_char() not in '"\r\n':
            string_val += self.advance()

        if self.current_char() is None or self.current_char() in '\r\n':
            return Token(TokenType.STRING, string_val, start_line, start_column)

        self.advance()  # Skip closing quote

        return Token(TokenType.STRING, string_val, start_line, start_column)

    def _radix(self, digits: str, base: int, line: int, column: int) -> int:
        """radix_constant_value, except that DATA text is raw: no Overflow there."""
        try:
            return radix_constant_value(digits, base, line, column)
        except LexerOverflow:
            if self._in_data_statement():
                return 0
            raise

    def _refuse_octal_89(self, line: int, column: int):
        """MBASIC reads an 8 or 9 inside an octal constant as an error that refuses the whole line."""
        if self.current_char() is not None and self.current_char() in '89':
            raise LexerRefused("Syntax error", line, column)

    def _in_data_statement(self) -> bool:
        """True when the tokens so far in this statement start with DATA (its text is kept raw)."""
        for tok in reversed(self.tokens):
            if tok.type in (TokenType.COLON, TokenType.NEWLINE, TokenType.LINE_NUMBER):
                return False
            if tok.type == TokenType.DATA:
                return True
        return False

    def read_identifier(self) -> Token:
        """
        Read an identifier or keyword.
        Identifiers can contain letters, digits, and end with type suffix $ % ! #
        In MBASIC, $ % ! # are considered part of the identifier.

        This lexer parses properly-formed MBASIC 5.21 which generally requires spaces
        between keywords and identifiers. Exception: PRINT# and INPUT# where # is part
        of the keyword. Old BASIC with NEXTI instead of NEXT I should be preprocessed.
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
                # Type suffix - terminates identifier (e.g., A$ reads as A$, not A$B)
                # Note: For PRINT#, INPUT#, etc., special handling occurs before this point
                # (see PRINT# check earlier) where the # is excluded and re-tokenized separately.
                # This general handling applies to user-defined identifiers like "A$", "B%", "C!".
                ident += self.advance()
                break
            else:
                break

        # "GO TO" / "GO SUB" with spaces (MBASIC 5.21 CRUNCH joins them)
        go_token = self._read_go_to_sub(ident, start_line, start_column)
        if go_token is not None:
            return go_token

        # Check if it's a keyword (case-insensitive, normalize to lowercase)
        ident_lower = ident.lower()
        if ident_lower in KEYWORDS:
            token = Token(KEYWORDS[ident_lower], ident_lower, start_line, start_column)
            # Register keyword and get display case based on policy
            display_case = self.keyword_case_manager.register_keyword(ident_lower, ident, start_line, start_column)
            token.original_case_keyword = display_case  # Use policy-determined case
            return token

        # Special case: File I/O keywords followed by # (e.g., PRINT#1)
        # MBASIC allows "PRINT#1" with no space, which should tokenize as:
        #   PRINT (keyword) + # (operator) + 1 (number)
        # The read_identifier() method treated # as a type suffix and consumed it,
        # so we now have "PRINT#" as ident. For file I/O keywords, we split it back out:
        # return PRINT keyword token and rewind pos to re-tokenize # separately.
        if ident_lower.endswith('#') and ident_lower[:-1] in KEYWORDS:
            keyword_part = ident_lower[:-1]
            # Check if this is a file I/O keyword that can be followed by #
            if keyword_part in ['print', 'lprint', 'input', 'write', 'field', 'get', 'put', 'close']:
                # Put the # back to be tokenized separately
                self.pos -= 1
                self.column -= 1
                # Return the keyword token without the #
                token = Token(KEYWORDS[keyword_part], keyword_part, start_line, start_column)
                # Apply keyword case policy
                display_case = self.keyword_case_manager.register_keyword(keyword_part, ident[:-1], start_line, start_column)
                token.original_case_keyword = display_case
                return token

        # A reserved word followed by a type character ("NAME$", "LEN%", "FOR$")
        # is the keyword: CRUNCH ends a reserved word at any character that is
        # not a letter, a digit or ".".  The type character stays in the input
        # and nothing can use it, which is a Syntax error when the line runs.
        if (len(ident) > 1 and ident[-1] in '$%!#' and ident_lower[:-1] == 'null'
                and not self._in_data_statement()):
            # NULL is reserved in the binary but not a keyword here
            raise LexerError("Syntax error", start_line, start_column)
        if (len(ident) > 1 and ident[-1] in '$%!#' and ident_lower[:-1] in RESERVED_STEMS
                and not self._in_data_statement()):
            keyword_part = ident_lower[:-1]
            self.pos -= 1
            self.column -= 1
            token = Token(KEYWORDS[keyword_part], keyword_part, start_line, start_column)
            token.original_case_keyword = self.keyword_case_manager.register_keyword(
                keyword_part, ident[:-1], start_line, start_column)
            return token

        # USR0 to USR9 and DEF USR are the reserved word USR and a digit; a
        # name that starts with USR (USRX, USR1X, USR10) is the word USR and
        # the rest, which the parser refuses as the binary does.  The other
        # reserved words are not split off the front of a name here.
        if (len(ident) > 3 and ident_lower.startswith('usr')
                and not self._in_data_statement()):
            back = len(ident) - 3
            self.pos -= back
            self.column -= back
            token = Token(KEYWORDS['usr'], 'usr', start_line, start_column)
            token.original_case_keyword = self.keyword_case_manager.register_keyword(
                'usr', ident[:3], start_line, start_column)
            return token

        # NOTE: We do NOT handle old BASIC where keywords run together (NEXTI, FORI).
        # MBASIC 5.21 is properly-formed and requires spaces between keywords.
        # Special case handled above: PRINT# and similar file I/O keywords in MBASIC 5.21
        # allow # without a space (MBASIC 5.21 feature, not old BASIC syntax).
        # Other old BASIC syntax should be preprocessed with conversion scripts.

        # Otherwise it's an identifier
        # Normalize to lowercase (BASIC is case-insensitive) but preserve original case
        token = Token(TokenType.IDENTIFIER, ident.lower(), start_line, start_column)
        # Preserve original case for display. For identifiers (user-defined variables),
        # store the exact case as typed in the original_case field for later display.
        # (Keywords handle case separately via original_case_keyword - see Token class in tokens.py)
        token.original_case = ident
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
        self._at_line_start = True
        while True:
            try:
                return self._tokenize_rest()
            except (LexerOverflow, LexerRefused):
                raise
            except LexerError:
                if (not self.defer_errors or not self.tokens
                        or self.tokens[-1].type == TokenType.NEWLINE):
                    raise       # a bad line number cannot be kept
                self._skip_bad_text()

    def _skip_bad_text(self):
        """Turn the text from the token that failed to the end of the line into one ILLEGAL token."""
        start = self._token_start
        end = start
        while end < len(self.source) and self.source[end] not in '\r\n':
            end += 1
        self.tokens.append(Token(TokenType.ILLEGAL, self.source[start:end],
                                 self._token_line, self._token_column))
        self.column += end - self.pos
        self.pos = end
        self._at_line_start = False

    def _tokenize_rest(self) -> List[Token]:
        at_line_start = self._at_line_start

        while self.pos < len(self.source):
            self.skip_whitespace(skip_newlines=False)

            char = self.current_char()
            if char is None:
                break

            start_line = self.line
            start_column = self.column
            self._token_start = self.pos
            self._token_line = start_line
            self._token_column = start_column

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

            # Apostrophe comment - distinct token type (unlike REM/REMARK which are keywords)
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
                if self.defer_errors and self.tokens and self.tokens[-1].type != TokenType.NEWLINE:
                    # Only this character is bad (a "$" behind a reserved word,
                    # say); the statements around it still run.
                    self.tokens.append(Token(TokenType.ILLEGAL, char, start_line, start_column))
                    self.advance()
                    at_line_start = False
                    continue
                raise LexerError(f"Unexpected character: '{char}' (0x{ord(char):02x})", start_line, start_column)

            at_line_start = False

        # Add EOF token
        self.tokens.append(Token(TokenType.EOF, None, self.line, self.column))
        return self.tokens


def tokenize(source: str) -> List[Token]:
    """Convenience function to tokenize source code"""
    keyword_mgr = create_keyword_case_manager()
    lexer = Lexer(source, keyword_case_manager=keyword_mgr)
    return lexer.tokenize()
