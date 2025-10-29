"""
Simple keyword case handling for MBASIC.

Keywords only need three policies:
- force_lower: all lowercase (default, MBASIC 5.21 style)
- force_upper: all UPPERCASE (classic BASIC)
- force_capitalize: Capitalize first letter (modern style)

Unlike variables, "first wins" doesn't make sense for keywords since
the interpreter registers them at startup.
"""


class SimpleKeywordCase:
    """Simple keyword case handler with just three sensible policies."""

    def __init__(self, policy: str = "force_lower"):
        """Initialize with a case policy.

        Args:
            policy: One of "force_lower", "force_upper", "force_capitalize"
        """
        if policy not in ["force_lower", "force_upper", "force_capitalize"]:
            # Fallback for old policies
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

        For compatibility with existing code. Just applies the policy.

        Args:
            keyword: Normalized (lowercase) keyword
            original_case: Original case as typed (ignored for keywords)
            line_num: Line number (unused)
            column: Column (unused)

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