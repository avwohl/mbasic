"""
Simple keyword case handling for MBASIC.

This is a simplified keyword case handler used by the lexer (src/lexer.py).
It supports only three force-based policies:
- force_lower: all lowercase (default, MBASIC 5.21 style)
- force_upper: all UPPERCASE (classic BASIC)
- force_capitalize: Capitalize first letter (modern style)

For advanced policies (first_wins, preserve, error) via CaseKeeperTable,
see KeywordCaseManager (src/keyword_case_manager.py) which is used by
src/parser.py and src/position_serializer.py.

ARCHITECTURE NOTE - Why Two Separate Case Handling Systems:

The lexer (src/lexer.py) uses SimpleKeywordCase because keywords only need
force-based policies in the tokenization phase. This lightweight handler applies
immediate transformations during tokenization without needing to track state.

The parser (src/parser.py) and serializer (src/position_serializer.py) use
KeywordCaseManager for advanced policies that require state tracking across the
entire program (first_wins, preserve, error). This separation allows:
1. Fast, stateless tokenization in the lexer
2. Complex, stateful case management in later phases
3. Settings changes between phases (though both should use consistent settings)

Note: Both systems SHOULD read from the same settings.get("case_style") setting
for consistency. SimpleKeywordCase receives policy via __init__ parameter (caller should
pass settings value), while KeywordCaseManager reads settings directly. Callers are responsible
for passing consistent policy values from settings to ensure matching behavior across phases.
"""


class SimpleKeywordCase:
    """Simple keyword case handler with just three sensible policies."""

    def __init__(self, policy: str = "force_lower"):
        """Initialize with a case policy.

        Args:
            policy: One of "force_lower", "force_upper", "force_capitalize"
        """
        if policy not in ["force_lower", "force_upper", "force_capitalize"]:
            # Fallback for invalid/unknown policy values (defensive programming)
            policy = "force_lower"
        self.policy = policy

    def apply_case(self, keyword: str) -> str:
        """Apply the case policy to a keyword.

        Args:
            keyword: The keyword (typically lowercase)

        Returns:
            The keyword with appropriate case applied
        """
        if self.policy == "force_lower":
            return keyword.lower()
        elif self.policy == "force_upper":
            return keyword.upper()
        elif self.policy == "force_capitalize":
            return keyword.capitalize()
        else:
            return keyword.lower()  # Default fallback

    def register_keyword(self, keyword: str, original_case: str, line_num: int = 0, column: int = 0) -> str:
        """Register a keyword and return the display case.

        Maintains signature compatibility with KeywordCaseManager.register_keyword()
        which uses line_num and column for advanced policies (first_wins, preserve, error).
        SimpleKeywordCase only supports force-based policies, so these parameters are unused.

        Args:
            keyword: Normalized (lowercase) keyword
            original_case: Original case as typed (ignored - force policies apply transformation)
            line_num: Line number (unused - required for KeywordCaseManager compatibility)
            column: Column (unused - required for KeywordCaseManager compatibility)

        Returns:
            The keyword with policy applied
        """
        return self.apply_case(keyword)

    def get_display_case(self, keyword: str) -> str:
        """Get the display case for a keyword.

        Args:
            keyword: Normalized (lowercase) keyword

        Returns:
            The keyword with policy applied
        """
        return self.apply_case(keyword)

    def clear(self):
        """Clear any state (no-op for simple case handler)."""
        pass