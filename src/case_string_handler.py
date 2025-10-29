"""
Unified case handling for identifiers and keywords in MBASIC.
Provides a single function for applying case policies based on settings.
"""

from typing import Optional
from src.case_keeper import CaseKeeperTable


class CaseStringHandler:
    """Unified handler for case-sensitive string processing."""

    # Shared tables for consistency across lexer and parser
    _keyword_table: Optional[CaseKeeperTable] = None
    _identifier_table: Optional[CaseKeeperTable] = None

    @classmethod
    def get_keyword_table(cls, policy: str = "force_lower") -> CaseKeeperTable:
        """Get or create the keyword case keeper table."""
        if cls._keyword_table is None:
            cls._keyword_table = CaseKeeperTable(policy=policy)
        return cls._keyword_table

    @classmethod
    def get_identifier_table(cls, policy: str = "force_lower") -> CaseKeeperTable:
        """Get or create the identifier case keeper table."""
        if cls._identifier_table is None:
            cls._identifier_table = CaseKeeperTable(policy=policy)
        return cls._identifier_table

    @classmethod
    def clear_tables(cls):
        """Clear all case keeper tables."""
        if cls._keyword_table:
            cls._keyword_table.clear()
        if cls._identifier_table:
            cls._identifier_table.clear()

    @classmethod
    def case_keepy_string(cls, text: str, original_text: str, setting_prefix: str,
                          line: int = 0, column: int = 0) -> str:
        """
        Apply case-keeping rules based on settings.

        Args:
            text: The canonicalized (lowercase) string
            original_text: The original string as typed
            setting_prefix: "keywords" or "idents" to check settings
            line: Line number for error reporting
            column: Column number for error reporting

        Returns:
            Display case string according to policy
        """
        try:
            from src.settings import get

            if setting_prefix == "keywords":
                policy = get("keywords.case_style", "force_lower")
                table = cls.get_keyword_table(policy)
            elif setting_prefix == "idents":
                # Identifier case handling would go here if needed
                # For now, identifiers preserve their original case
                return original_text
            else:
                # Unknown prefix, return original
                return original_text

            # Register and get display case
            display_case = table.register(text, original_text, line, column)
            return display_case

        except Exception:
            # If settings unavailable, return original text
            return original_text


def case_keepy_string(text: str, original_text: str, setting_prefix: str,
                      line: int = 0, column: int = 0) -> str:
    """
    Convenience function for case-keeping.

    Args:
        text: The canonicalized (lowercase) string
        original_text: The original string as typed
        setting_prefix: "keywords" or "idents" to check settings
        line: Line number for error reporting
        column: Column number for error reporting

    Returns:
        Display case string according to policy
    """
    return CaseStringHandler.case_keepy_string(text, original_text, setting_prefix, line, column)