"""
Keyword Case Management - Single source of truth for keyword display case

Similar to variable case handling, maintains a table mapping normalized (lowercase)
keywords to their display case based on the configured policy.

The keyword table is the single source of truth for how keywords should be displayed.

ARCHITECTURE - Two Case Handling Systems:

This class provides advanced case policies (first_wins, preserve, error) via
CaseKeeperTable and is used by parser.py and position_serializer.py. For simpler
force-based policies in the lexer, see SimpleKeywordCase (src/simple_keyword_case.py).

Why two systems:
- SimpleKeywordCase: Used by lexer for fast, stateless tokenization (force-based policies only)
- KeywordCaseManager: Used by parser/serializer for complex state tracking (all policies including first_wins, preserve, error)

When to use which:
- Lexer (tokenization phase): SimpleKeywordCase with force_lower/force_upper/force_capitalize
- Parser/Serializer (later phases): KeywordCaseManager for any policy including first_wins/preserve/error
- Both should read the same settings.get("case_style") to ensure consistency

See simple_keyword_case.py for detailed architecture notes on the separation.
"""

from src.case_keeper import CaseKeeperTable


class KeywordCaseManager:
    """Manages keyword display case according to configured policy.

    Uses CaseKeeperTable for case-insensitive storage with display case preservation.
    """

    def __init__(self, policy: str = "force_lower"):
        """Initialize keyword case manager.

        Args:
            policy: Case policy - "force_lower", "force_upper", "force_capitalize",
                    "first_wins", "error", "preserve"
        """
        self.policy = policy
        # Use CaseKeeperTable for case-insensitive storage
        self._keyword_table = CaseKeeperTable(policy=policy)

    def register_keyword(self, keyword: str, original_case: str, line_num: int = 0, column: int = 0) -> str:
        """Register a keyword occurrence and return the display case to use.

        Args:
            keyword: Normalized (lowercase) keyword
            original_case: Original case as typed in source
            line_num: Line number where keyword appears (for error reporting)
            column: Column where keyword appears (for error reporting)

        Returns:
            The display case to use for this keyword

        Raises:
            ValueError: If policy is "error" and case conflict detected
        """
        # CaseKeeperTable handles all the policy logic
        return self._keyword_table.set(keyword, original_case, line_num, column)

    def get_display_case(self, keyword: str) -> str:
        """Get the display case for a keyword.

        Args:
            keyword: Normalized (lowercase) keyword

        Returns:
            Display case for this keyword
        """
        result = self._keyword_table.get(keyword)
        if result is not None:
            return result

        # Not in table - register with default case
        return self.register_keyword(keyword, keyword)

    def clear(self):
        """Clear the keyword table (e.g., when loading new program)"""
        self._keyword_table.clear()
