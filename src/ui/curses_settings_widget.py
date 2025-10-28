"""Settings widget for curses UI.

Provides an interactive settings editor with:
- Category-based navigation
- Appropriate input widgets for each setting type
- Apply/Cancel/Reset functionality
"""

import urwid
from typing import Dict, Any, Optional
from src.settings_definitions import SETTING_DEFINITIONS, SettingType, SettingScope
from src.settings import get, set as set_setting


class SettingsWidget(urwid.WidgetWrap):
    """Interactive settings editor for curses UI."""

    def __init__(self):
        """Initialize settings widget."""
        # Store original values for cancel
        self.original_values: Dict[str, Any] = {}
        self.widgets: Dict[str, urwid.Widget] = {}

        # Load current settings
        self._load_current_values()

        # Create UI
        body = self._create_body()
        super().__init__(body)

    def _load_current_values(self):
        """Load current setting values."""
        for key in SETTING_DEFINITIONS.keys():
            self.original_values[key] = get(key)

    def _create_body(self):
        """Create the settings UI body.

        Returns:
            Widget containing the settings interface
        """
        # Group settings by category
        categories = {
            'editor': [],
            'interpreter': [],
            'keywords': [],
            'variables': [],
            'ui': []
        }

        for key, defn in SETTING_DEFINITIONS.items():
            category = key.split('.')[0]
            if category in categories:
                categories[category].append((key, defn))

        # Create widgets for all settings
        content = []

        for category, settings in sorted(categories.items()):
            if not settings:
                continue

            # Category header
            content.append(urwid.Divider())
            content.append(urwid.AttrMap(
                urwid.Text(f'  {category.upper()}', align='left'),
                'reversed'
            ))
            content.append(urwid.Divider())

            # Settings in category
            for key, defn in sorted(settings):
                widget_group = self._create_setting_widget(key, defn)
                if widget_group:
                    content.extend(widget_group)

        # Add buttons at bottom
        content.append(urwid.Divider())
        content.append(urwid.Divider())

        buttons = urwid.Columns([
            ('weight', 1, urwid.Button('OK', on_press=lambda btn: self._on_ok())),
            ('weight', 1, urwid.Button('Cancel', on_press=lambda btn: self._on_cancel())),
            ('weight', 1, urwid.Button('Apply', on_press=lambda btn: self._on_apply())),
            ('weight', 1, urwid.Button('Reset', on_press=lambda btn: self._on_reset())),
        ], dividechars=2)
        content.append(urwid.AttrMap(buttons, 'body'))

        # Create scrollable list
        listbox = urwid.ListBox(urwid.SimpleFocusListWalker(content))

        # Wrap in line box with title
        box = urwid.LineBox(listbox, title="Settings")

        return box

    def _create_setting_widget(self, key: str, defn) -> list:
        """Create widget(s) for a single setting.

        Args:
            key: Setting key
            defn: Setting definition

        Returns:
            List of widgets for this setting
        """
        widgets = []

        # Label
        label_text = key.split('.')[-1].replace('_', ' ').title()
        label = urwid.Text(f'  {label_text}:')
        widgets.append(label)

        # Widget based on type
        current_value = self.original_values[key]

        if defn.type == SettingType.BOOLEAN:
            checkbox = urwid.CheckBox('', state=current_value)
            self.widgets[key] = checkbox
            widgets.append(urwid.Padding(urwid.AttrMap(checkbox, 'body'), left=4))

        elif defn.type == SettingType.INTEGER:
            edit = urwid.IntEdit(default=current_value)
            self.widgets[key] = edit
            widgets.append(urwid.Padding(urwid.AttrMap(edit, 'body'), left=4, right=2))

        elif defn.type == SettingType.ENUM:
            # Create radio button group for enum
            group = []
            for choice in defn.choices:
                rb = urwid.RadioButton(group, choice, state=(choice == current_value))
                widgets.append(urwid.Padding(urwid.AttrMap(rb, 'body'), left=6))
            # Store the group so we can get the selected value
            self.widgets[key] = group

        elif defn.type == SettingType.STRING:
            edit = urwid.Edit(edit_text=str(current_value))
            self.widgets[key] = edit
            widgets.append(urwid.Padding(urwid.AttrMap(edit, 'body'), left=4, right=2))

        # Help text
        if defn.help_text:
            help_text = urwid.Text(('dim', f'    {defn.help_text}'))
            widgets.append(help_text)

        widgets.append(urwid.Divider())

        return widgets

    def _get_current_widget_values(self) -> Dict[str, Any]:
        """Get current values from all widgets.

        Returns:
            Dictionary of setting key -> current value
        """
        values = {}

        for key, widget in self.widgets.items():
            defn = SETTING_DEFINITIONS[key]

            if defn.type == SettingType.BOOLEAN:
                values[key] = widget.get_state()

            elif defn.type == SettingType.INTEGER:
                try:
                    values[key] = int(widget.get_edit_text())
                except ValueError:
                    # Use current value if invalid
                    values[key] = self.original_values[key]

            elif defn.type == SettingType.ENUM:
                # Find selected radio button
                for rb in widget:
                    if rb.get_state():
                        values[key] = rb.get_label()
                        break

            elif defn.type == SettingType.STRING:
                values[key] = widget.get_edit_text()

        return values

    def _apply_settings(self) -> bool:
        """Apply current widget values to settings.

        Returns:
            True if successful, False if error
        """
        values = self._get_current_widget_values()

        for key, value in values.items():
            try:
                set_setting(key, value, SettingScope.GLOBAL)
            except Exception as e:
                # Show error (in real implementation would show dialog)
                return False

        return True

    def _on_apply(self):
        """Handle Apply button."""
        if self._apply_settings():
            # Update original values so Cancel won't revert
            self._load_current_values()
            # Signal success (parent will show message)
            self._emit('applied')

    def _on_ok(self):
        """Handle OK button."""
        if self._apply_settings():
            self._emit('close')

    def _on_cancel(self):
        """Handle Cancel button."""
        # Restore original values
        for key, value in self.original_values.items():
            try:
                set_setting(key, value, SettingScope.GLOBAL)
            except Exception:
                pass  # Ignore errors on cancel

        self._emit('close')

    def _on_reset(self):
        """Handle Reset to Defaults button."""
        # Set all widgets to default values
        for key, defn in SETTING_DEFINITIONS.items():
            if key in self.widgets:
                widget = self.widgets[key]

                if defn.type == SettingType.BOOLEAN:
                    widget.set_state(defn.default)

                elif defn.type == SettingType.INTEGER:
                    widget.set_edit_text(str(defn.default))

                elif defn.type == SettingType.ENUM:
                    # Set radio button to default
                    for rb in widget:
                        rb.set_state(rb.get_label() == defn.default)

                elif defn.type == SettingType.STRING:
                    widget.set_edit_text(str(defn.default))

    def keypress(self, size, key):
        """Handle keypress events.

        Args:
            size: Widget size tuple
            key: Key pressed

        Returns:
            None if key was handled, otherwise the key
        """
        if key == 'esc':
            self._on_cancel()
            return None

        # Let parent handle other keys
        return super().keypress(size, key)

    def _emit(self, signal: str):
        """Emit a signal to parent.

        Args:
            signal: Signal name ('close', 'applied')
        """
        # Store signal for parent to check
        self.signal = signal
