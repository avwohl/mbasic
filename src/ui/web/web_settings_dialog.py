"""
Web UI Settings Dialog for MBASIC

Provides a NiceGUI dialog for viewing and modifying settings.
"""

from nicegui import ui
from typing import Dict, Any
from src.settings_definitions import SETTING_DEFINITIONS, SettingType
from src.settings import get_settings_manager


class WebSettingsDialog(ui.dialog):
    """Dialog for viewing and modifying MBASIC settings."""

    def __init__(self, backend):
        """Initialize settings dialog.

        Args:
            backend: NiceGUIBackend instance
        """
        super().__init__()
        self.backend = backend
        self.settings_manager = backend.settings_manager

        # Store widgets for each setting
        self.widgets: Dict[str, Any] = {}

        # Store original values for cancel
        self.original_values: Dict[str, Any] = {}

    def show(self):
        """Show the settings dialog."""
        # Load current values
        self._load_current_values()

        # Clear any previous content
        self.clear()

        # Create dialog content
        with self, ui.card().classes('w-full max-w-2xl'):
            # Title
            ui.label('Settings').classes('text-2xl font-bold mb-4')

            # Create tabs for categories
            with ui.tabs().classes('w-full') as tabs:
                editor_tab = ui.tab('Editor')
                limits_tab = ui.tab('Limits')

            with ui.tab_panels(tabs, value=editor_tab).classes('w-full'):
                # Editor Settings Tab
                with ui.tab_panel(editor_tab):
                    self._create_editor_settings()

                # Limits Tab
                with ui.tab_panel(limits_tab):
                    self._create_limits_settings()

            # Buttons
            with ui.row().classes('w-full justify-end gap-2 mt-4'):
                ui.button('Cancel', on_click=self._on_cancel).props('outline')
                ui.button('Save', on_click=self._on_save).props('color=primary')

        # Open the dialog
        self.open()

    def _load_current_values(self):
        """Load current setting values."""
        for key in SETTING_DEFINITIONS.keys():
            self.original_values[key] = self.settings_manager.get(key)

    def _create_editor_settings(self):
        """Create editor settings controls."""
        ui.label('Auto-Numbering').classes('text-lg font-semibold mb-2')

        # Auto-number enable
        auto_num_enabled = self.settings_manager.get('auto_number')
        self.widgets['auto_number'] = ui.checkbox(
            'Enable auto-numbering',
            value=auto_num_enabled
        ).classes('mb-2')

        # Auto-number start
        auto_num_start = self.settings_manager.get('auto_number_start')
        with ui.row().classes('items-center gap-2'):
            ui.label('Starting line number:').classes('min-w-40')
            self.widgets['auto_number_start'] = ui.number(
                value=auto_num_start,
                min=0,
                max=65529,
                step=1
            ).props('outlined dense').classes('w-32')

        # Auto-number step
        auto_num_step = self.settings_manager.get('auto_number_step')
        with ui.row().classes('items-center gap-2'):
            ui.label('Line number increment:').classes('min-w-40')
            self.widgets['auto_number_step'] = ui.number(
                value=auto_num_step,
                min=1,
                max=1000,
                step=1
            ).props('outlined dense').classes('w-32')

        ui.label('Common values: Start 10 or 100, Step 10 (classic) or 1 (dense)').classes('text-sm text-gray-600 mt-1')

    def _create_limits_settings(self):
        """Create resource limits settings (read-only for now)."""
        ui.label('Resource Limits').classes('text-lg font-semibold mb-2')
        ui.label('(View only - modify in code for now)').classes('text-sm text-gray-600 mb-4')

        # Show key limits
        limits_to_show = [
            ('limits.max_variables', 'Maximum variables'),
            ('limits.max_string_length', 'Maximum string length'),
            ('limits.max_array_dimensions', 'Maximum array dimensions'),
        ]

        for key, label in limits_to_show:
            if key in SETTING_DEFINITIONS:
                value = self.settings_manager.get(key)
                with ui.row().classes('items-center gap-2 mb-2'):
                    ui.label(f'{label}:').classes('min-w-60')
                    ui.label(str(value)).classes('font-mono')

    def _on_save(self):
        """Handle Save button click."""
        try:
            # Update settings from widgets
            if 'auto_number' in self.widgets:
                self.settings_manager.set(
                    'auto_number',
                    self.widgets['auto_number'].value
                )

            if 'auto_number_start' in self.widgets:
                start_value = int(self.widgets['auto_number_start'].value)
                self.settings_manager.set(
                    'auto_number_start',
                    start_value
                )

            if 'auto_number_step' in self.widgets:
                step_value = int(self.widgets['auto_number_step'].value)
                self.settings_manager.set(
                    'auto_number_step',
                    step_value
                )

            # Save to disk
            from src.settings_definitions import SettingScope
            self.settings_manager.save(SettingScope.GLOBAL)

            # Notify backend
            self.backend._notify('Settings saved - will take effect on next auto-number', type='positive')

            # Close dialog
            self.close()

        except Exception as e:
            ui.notify(f'Error saving settings: {e}', type='negative')

    def _on_cancel(self):
        """Handle Cancel button click."""
        self.close()
