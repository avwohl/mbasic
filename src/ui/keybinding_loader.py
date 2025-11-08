"""
Keybinding loader for UI backends.

Loads keybindings from JSON config and provides utilities for applying them to UI frameworks.
"""

import json
from pathlib import Path
from typing import Dict, Optional, List, Tuple


class KeybindingLoader:
    """Loads and manages keybindings from JSON configuration."""

    def __init__(self, ui_name: str):
        """
        Initialize keybinding loader.

        Args:
            ui_name: Name of UI ('curses', 'tk', etc.)
        """
        self.ui_name = ui_name
        self.config = self._load_config()

    def _load_config(self) -> Dict:
        """Load keybindings configuration for current UI.

        Note: This loads keybindings for runtime event handling (binding keys to actions).
        help_macros.py loads the same JSON files but for macro expansion in help content
        (e.g., {{kbd:run}} -> "^R"). Both read the same data but use it differently:
        KeybindingLoader for runtime key event handling, HelpMacros for documentation display.
        """
        config_path = Path(__file__).parent / f"{self.ui_name}_keybindings.json"

        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    return json.load(f)
            except Exception:
                pass

        return {}

    def get_primary(self, section: str, action: str) -> Optional[str]:
        """
        Get primary keybinding for an action.

        Args:
            section: Section name (e.g., 'menu', 'editor', 'help_browser')
            action: Action name (e.g., 'file_save', 'run', 'help')

        Returns:
            Primary key combination or None if not found
        """
        if section in self.config and action in self.config[section]:
            return self.config[section][action].get('primary')
        return None

    def get_all_keys(self, section: str, action: str) -> List[str]:
        """
        Get all keybindings for an action (including alternatives).

        Args:
            section: Section name
            action: Action name

        Returns:
            List of key combinations
        """
        if section in self.config and action in self.config[section]:
            return self.config[section][action].get('keys', [])
        return []

    def get_description(self, section: str, action: str) -> Optional[str]:
        """
        Get description for an action.

        Args:
            section: Section name
            action: Action name

        Returns:
            Description string or None
        """
        if section in self.config and action in self.config[section]:
            return self.config[section][action].get('description')
        return None

    def get_tk_accelerator(self, section: str, action: str) -> str:
        """
        Get Tkinter menu accelerator string for display.

        Args:
            section: Section name
            action: Action name

        Returns:
            Accelerator string (e.g., "Ctrl+S") or empty string
        """
        primary = self.get_primary(section, action)
        return primary if primary else ""

    def get_tk_bindings(self, section: str, action: str) -> List[str]:
        """
        Get Tkinter event binding strings.

        Converts our keybinding format to Tkinter binding format.
        E.g., "Ctrl+S" → "<Control-s>"

        Args:
            section: Section name
            action: Action name

        Returns:
            List of Tkinter binding strings
        """
        keys = self.get_all_keys(section, action)
        tk_bindings = []

        for key in keys:
            tk_binding = self._to_tk_binding(key)
            if tk_binding:
                tk_bindings.append(tk_binding)

        return tk_bindings

    def _to_tk_binding(self, key: str) -> Optional[str]:
        """
        Convert our key format to Tkinter binding format.

        Examples:
            "Ctrl+S" → "<Control-s>"
            "Ctrl+?" → "<Control-question>"
            "Ctrl+/" → "<Control-slash>"
            "F5" → "<F5>"
            "ESC" → "<Escape>"

        Args:
            key: Key in our format

        Returns:
            Tkinter binding string or None
        """
        # Special cases
        special_map = {
            'ESC': '<Escape>',
            'Enter': '<Return>',
            'Return': '<Return>',
            'Tab': '<Tab>',
            'Space': '<space>',
            '?': '<question>',
            '/': '<slash>',
        }

        if key in special_map:
            return special_map[key]

        # Function keys
        if key.startswith('F') and key[1:].isdigit():
            return f"<{key}>"

        # Parse modifiers + key
        parts = key.split('+')
        if len(parts) == 1:
            # No modifiers, just a key
            return f"<{key.lower()}>"

        # Build binding with modifiers
        modifiers = parts[:-1]
        base_key = parts[-1]

        # Map our modifier names to Tkinter names
        modifier_map = {
            'Ctrl': 'Control',
            'Alt': 'Alt',
            'Shift': 'Shift',
            'Cmd': 'Command',  # macOS
        }

        tk_modifiers = []
        for mod in modifiers:
            if mod in modifier_map:
                tk_modifiers.append(modifier_map[mod])
            else:
                tk_modifiers.append(mod)

        # Handle special base keys
        if base_key in special_map:
            base_key_tk = special_map[base_key].strip('<>')
        else:
            base_key_tk = base_key.lower()

        # Build final binding string
        return f"<{'-'.join(tk_modifiers)}-{base_key_tk}>"

    def bind_all_to_tk(self, widget, section: str, action: str, handler) -> None:
        """
        Bind all keys for an action to a Tkinter widget.

        Args:
            widget: Tkinter widget (usually root window)
            section: Section name
            action: Action name
            handler: Function to call when key pressed
        """
        for binding in self.get_tk_bindings(section, action):
            widget.bind(binding, handler)
