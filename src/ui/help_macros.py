"""
Macro substitution for help documentation.

Provides template variable replacement in markdown help files.
Macros use the format: {{macro_name}} or {{macro_name:context}}

Examples:
  {{kbd:help}} → looks up 'help' action in current UI's keybindings and returns
                  the primary keybinding for that action
  {{kbd:save:curses}} → looks up 'save' action in Curses UI specifically
  {{version}} → MBASIC version string
"""

import json
import re
from pathlib import Path
from typing import Dict, Optional


class HelpMacros:
    """Handles macro substitution in help markdown."""

    def __init__(self, ui_name: str, help_root: str):
        """
        Initialize macro processor.

        Args:
            ui_name: Name of UI ('curses', 'tk', etc.)
            help_root: Path to help documentation root
        """
        self.ui_name = ui_name
        self.help_root = Path(help_root)
        self.keybindings = self._load_keybindings()

    def _load_keybindings(self) -> Dict:
        """Load keybindings configuration for current UI.

        Note: This loads the same keybinding JSON files as keybinding_loader.py, but for
        a different purpose: macro expansion in help content (e.g., {{kbd:run}} -> "^R")
        rather than runtime event handling. This is separate from help_widget.py which
        uses hardcoded keys for navigation within the help system itself.
        """
        keybindings_path = Path(__file__).parent / f"{self.ui_name}_keybindings.json"

        if keybindings_path.exists():
            try:
                with open(keybindings_path, 'r') as f:
                    return json.load(f)
            except Exception:
                pass

        return {}

    def expand(self, text: str) -> str:
        """
        Expand all macros in text.

        Args:
            text: Markdown text with macros

        Returns:
            Text with macros replaced
        """
        # Pattern: {{macro_name}} or {{macro_name:arg}}
        pattern = r'\{\{([^:}]+)(?::([^}]+))?\}\}'

        def replacer(match):
            macro_name = match.group(1)
            macro_arg = match.group(2)

            return self._expand_macro(macro_name, macro_arg)

        return re.sub(pattern, replacer, text)

    def _expand_macro(self, name: str, arg: Optional[str]) -> str:
        """
        Expand a single macro.

        Args:
            name: Macro name (e.g., 'kbd', 'version')
            arg: Optional argument (e.g., 'help' for {{kbd:help}})

        Returns:
            Expanded value or original macro if not found
        """
        if name == 'kbd':
            return self._expand_kbd(arg)
        elif name == 'version':
            # Hardcoded MBASIC version for documentation
            # Note: Project has internal implementation version (src/version.py) separate from this
            return "5.21"  # MBASIC 5.21 language version
        elif name == 'ui':
            return self.ui_name.capitalize()
        else:
            # Unknown macro, return as-is
            return f"{{{{{name}{':' + arg if arg else ''}}}}}"

    def _expand_kbd(self, key_name: Optional[str]) -> str:
        """
        Expand keyboard shortcut macro by searching for action name across all sections.

        Args:
            key_name: Name of key action, optionally with UI specifier.
                     Formats:
                     - 'action' - searches current UI (e.g., 'help', 'save', 'run')
                     - 'action:ui' - searches specific UI (e.g., 'save:curses', 'run:tk')

        Returns:
            Primary key combination or original macro if not found

        Example:
            _expand_kbd('help') searches current UI for action 'help'
            _expand_kbd('save:curses') searches Curses UI for action 'save'
        """
        if not key_name:
            return "{{kbd}}"

        # Check if UI is specified (e.g., 'save:curses')
        if ':' in key_name:
            action, ui = key_name.split(':', 1)
            keybindings = self._load_keybindings_for_ui(ui)
        else:
            action = key_name
            keybindings = self.keybindings

        # Search in all sections of keybindings
        for section_name, section in keybindings.items():
            if action in section:
                return section[action]['primary']

        # Not found, return placeholder
        return f"{{{{kbd:{key_name}}}}}"

    def _load_keybindings_for_ui(self, ui_name: str) -> Dict:
        """
        Load keybindings configuration for a specific UI.

        Args:
            ui_name: Name of UI ('curses', 'tk', 'web', etc.)

        Returns:
            Dict of keybindings for that UI, or empty dict if not found
        """
        keybindings_path = Path(__file__).parent / f"{ui_name}_keybindings.json"

        if keybindings_path.exists():
            try:
                with open(keybindings_path, 'r') as f:
                    return json.load(f)
            except Exception:
                pass

        return {}

    def get_all_keys(self, section: Optional[str] = None) -> Dict[str, str]:
        """
        Get all keybindings for a section.

        Args:
            section: Section name ('editor', 'help_browser', etc.) or None for all

        Returns:
            Dict mapping action names to primary keys
        """
        result = {}

        if section:
            if section in self.keybindings:
                for action, config in self.keybindings[section].items():
                    result[action] = config['primary']
        else:
            # All sections
            for section_name, section_data in self.keybindings.items():
                for action, config in section_data.items():
                    result[f"{section_name}.{action}"] = config['primary']

        return result
