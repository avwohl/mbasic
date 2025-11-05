"""
Case-preserving string utilities for BASIC

Provides case-insensitive comparison while preserving display case.
Used for both keywords and variables in BASIC.
"""

from typing import Dict, Optional, List, Tuple


class CaseKeeperTable:
    """A dictionary that stores strings with case-insensitive keys but preserves display case.

    Example (with default "first_wins" policy):
        table = CaseKeeperTable()
        table.set("PRINT", "Print")  # Key: "print", Display: "Print"
        table.get("print")  # Returns: "Print"
        table.get("PRINT")  # Returns: "Print" (same - case insensitive)
        table.set("print", "PRINT")  # Ignored - first wins, keeps "Print"
    """

    def __init__(self, policy: str = "first_wins"):
        """Initialize case keeper table.

        Args:
            policy: How to handle case - "first_wins", "force_lower", "force_upper",
                    "force_capitalize", "prefer_upper", "prefer_lower", "prefer_mixed", "error"
        """
        self.policy = policy
        # Maps normalized (lowercase) key -> display case
        self._table: Dict[str, str] = {}
        # For error/prefer policies: tracks all variants seen
        self._variants: Dict[str, List[Tuple[str, int, int]]] = {}  # normalized -> [(case, line, col), ...]

    def set(self, key: str, display_case: str, line_num: int = 0, column: int = 0) -> str:
        """Set a value with case-insensitive key, preserving display case according to policy.

        Args:
            key: The key (will be normalized to lowercase for lookup)
            display_case: The case to display (as typed in source)
            line_num: Line number (for error reporting)
            column: Column number (for error reporting)

        Returns:
            The display case that will actually be used (after applying policy)

        Raises:
            ValueError: If policy is "error" and case conflict detected
        """
        normalized = key.lower()

        # Track variant
        if normalized not in self._variants:
            self._variants[normalized] = []
        self._variants[normalized].append((display_case, line_num, column))

        # Apply policy
        if self.policy == "first_wins":
            if normalized not in self._table:
                self._table[normalized] = display_case
            # Else keep existing

        elif self.policy == "force_lower":
            self._table[normalized] = normalized

        elif self.policy == "force_upper":
            self._table[normalized] = normalized.upper()

        elif self.policy == "force_capitalize":
            self._table[normalized] = normalized.capitalize()

        elif self.policy == "prefer_upper":
            # Choose the variant with most uppercase letters
            if normalized not in self._table:
                self._table[normalized] = display_case
            else:
                current = self._table[normalized]
                if sum(1 for c in display_case if c.isupper()) > sum(1 for c in current if c.isupper()):
                    self._table[normalized] = display_case

        elif self.policy == "prefer_lower":
            # Choose the variant with most lowercase letters
            if normalized not in self._table:
                self._table[normalized] = display_case
            else:
                current = self._table[normalized]
                if sum(1 for c in display_case if c.islower()) > sum(1 for c in current if c.islower()):
                    self._table[normalized] = display_case

        elif self.policy == "prefer_mixed":
            # Prefer mixed case (camelCase/PascalCase) over all-upper or all-lower
            def is_mixed(s):
                has_upper = any(c.isupper() for c in s)
                has_lower = any(c.islower() for c in s)
                return has_upper and has_lower

            if normalized not in self._table:
                self._table[normalized] = display_case
            else:
                current = self._table[normalized]
                current_mixed = is_mixed(current)
                new_mixed = is_mixed(display_case)
                # Prefer mixed over non-mixed
                if new_mixed and not current_mixed:
                    self._table[normalized] = display_case

        elif self.policy == "error":
            # Check for conflicts
            if normalized in self._table:
                if self._table[normalized] != display_case:
                    variants = self._variants[normalized]
                    first_case, first_line, first_col = variants[0]
                    raise ValueError(
                        f"Case conflict: '{display_case}' at line {line_num}:{column} "
                        f"vs '{first_case}' at line {first_line}:{first_col}"
                    )
            else:
                self._table[normalized] = display_case

        else:
            # Unknown policy - use first_wins
            if normalized not in self._table:
                self._table[normalized] = display_case

        return self._table[normalized]

    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get the display case for a key (case-insensitive lookup).

        Args:
            key: The key to look up (will be normalized)
            default: Default value if key not found

        Returns:
            Display case for this key, or default if not found
        """
        normalized = key.lower()
        return self._table.get(normalized, default)

    def contains(self, key: str) -> bool:
        """Check if key exists (case-insensitive).

        Args:
            key: The key to check

        Returns:
            True if key exists (in any case)
        """
        return key.lower() in self._table

    def clear(self):
        """Clear the table"""
        self._table.clear()
        self._variants.clear()

    def __contains__(self, key: str) -> bool:
        """Support 'in' operator"""
        return self.contains(key)

    def __getitem__(self, key: str) -> str:
        """Support table[key] syntax"""
        result = self.get(key)
        if result is None:
            raise KeyError(f"Key not found: {key}")
        return result

    def __setitem__(self, key: str, display_case: str):
        """Support table[key] = value syntax"""
        self.set(key, display_case)
