"""
TK Settings Dialog for MBASIC

Provides a GUI dialog for modifying settings.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Any
from src.settings_definitions import SETTING_DEFINITIONS, SettingType, SettingScope
from src.settings import get, set as set_setting


class SettingsDialog(tk.Toplevel):
    """Dialog for modifying MBASIC settings."""

    def __init__(self, parent):
        """Initialize settings dialog.

        Args:
            parent: Parent TK widget
        """
        super().__init__(parent)

        self.title("MBASIC Settings")
        self.geometry("700x600")
        self.resizable(True, True)

        # Store original values for cancel
        self.original_values: Dict[str, Any] = {}
        self.widgets: Dict[str, tk.Widget] = {}

        # Load current settings
        self._load_current_values()

        # Create UI
        self._create_widgets()

        # Make modal (prevents interaction with parent, but doesn't block code execution - no wait_window())
        self.transient(parent)
        self.grab_set()

        # Center on parent
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (self.winfo_width() // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")

    def _load_current_values(self):
        """Load current setting values."""
        for key in SETTING_DEFINITIONS.keys():
            self.original_values[key] = get(key)

    def _create_widgets(self):
        """Create all dialog widgets."""
        # Main container with padding
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Create notebook for categories
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

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

        # Create tab for each category
        for category, settings in sorted(categories.items()):
            if settings:  # Only create tab if category has settings
                tab = self._create_category_tab(notebook, category, settings)
                notebook.add(tab, text=category.title())

        # Buttons at bottom
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)

        ttk.Button(button_frame, text="OK", command=self._on_ok, width=10).pack(side=tk.RIGHT, padx=2)
        ttk.Button(button_frame, text="Cancel", command=self._on_cancel, width=10).pack(side=tk.RIGHT, padx=2)
        ttk.Button(button_frame, text="Apply", command=self._on_apply, width=10).pack(side=tk.RIGHT, padx=2)
        ttk.Button(button_frame, text="Reset to Defaults", command=self._on_reset).pack(side=tk.LEFT, padx=2)

    def _create_category_tab(self, notebook, category, settings):
        """Create a tab for a category of settings.

        Args:
            notebook: Parent notebook widget
            category: Category name
            settings: List of (key, definition) tuples

        Returns:
            Frame containing the tab contents
        """
        # Create scrollable frame
        tab_frame = ttk.Frame(notebook)

        canvas = tk.Canvas(tab_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(tab_frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor=tk.NW)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Add settings to scrollable frame
        for key, defn in sorted(settings):
            self._create_setting_widget(scrollable_frame, key, defn)

        return tab_frame

    def _create_setting_widget(self, parent, key, defn):
        """Create widget for a single setting.

        Args:
            parent: Parent frame
            key: Setting key
            defn: Setting definition
        """
        frame = ttk.Frame(parent, padding=5)
        frame.pack(fill=tk.X, pady=2)

        # Label
        label_text = key.split('.')[-1].replace('_', ' ').title()
        label = ttk.Label(frame, text=label_text + ":", width=25, anchor=tk.W)
        label.pack(side=tk.LEFT, padx=(0, 10))

        # Widget based on type
        current_value = self.original_values[key]

        if defn.type == SettingType.BOOLEAN:
            var = tk.BooleanVar(value=current_value)
            widget = ttk.Checkbutton(frame, variable=var)
            widget.pack(side=tk.LEFT)
            self.widgets[key] = var

        elif defn.type == SettingType.INTEGER:
            var = tk.IntVar(value=current_value)
            widget = ttk.Spinbox(frame, from_=0, to=1000, textvariable=var, width=10)
            widget.pack(side=tk.LEFT)
            self.widgets[key] = var

        elif defn.type == SettingType.ENUM:
            var = tk.StringVar(value=current_value)
            widget = ttk.Combobox(frame, textvariable=var, values=defn.choices,
                                 state='readonly', width=20)
            widget.pack(side=tk.LEFT)
            self.widgets[key] = var

        elif defn.type == SettingType.STRING:
            var = tk.StringVar(value=current_value)
            widget = ttk.Entry(frame, textvariable=var, width=30)
            widget.pack(side=tk.LEFT)
            self.widgets[key] = var

        # Help button
        if defn.help_text and len(defn.help_text) > 50:
            help_btn = ttk.Button(frame, text="?", width=3,
                                 command=lambda k=key, d=defn: self._show_help(k, d))
            help_btn.pack(side=tk.LEFT, padx=(5, 0))
        else:
            # Show short help as inline label (not a hover tooltip, just a gray label)
            if defn.help_text:
                help_label = ttk.Label(frame, text=defn.help_text,
                                      foreground='gray', font=('TkDefaultFont', 9))
                help_label.pack(side=tk.LEFT, padx=(10, 0))

    def _show_help(self, key, defn):
        """Show help dialog for a setting.

        Args:
            key: Setting key
            defn: Setting definition
        """
        messagebox.showinfo(
            f"Help: {key}",
            f"{defn.description}\n\n{defn.help_text}",
            parent=self
        )

    def _get_current_widget_values(self) -> Dict[str, Any]:
        """Get current values from all widgets.

        Returns:
            Dictionary of setting key -> current value
        """
        values = {}
        for key, widget in self.widgets.items():
            # All entries in self.widgets dict are tk.Variable instances (BooleanVar, StringVar, IntVar),
            # not the actual widget objects (Checkbutton, Spinbox, Entry, Combobox).
            # The variables are associated with widgets via textvariable/variable parameters.
            values[key] = widget.get()
        return values

    def _apply_settings(self):
        """Apply current widget values to settings."""
        values = self._get_current_widget_values()

        for key, value in values.items():
            try:
                set_setting(key, value, SettingScope.GLOBAL)
            except Exception as e:
                messagebox.showerror(
                    "Error",
                    f"Failed to set {key}: {e}",
                    parent=self
                )
                return False

        return True

    def _on_apply(self):
        """Handle Apply button."""
        if self._apply_settings():
            # Update original values so Cancel won't revert
            self._load_current_values()
            messagebox.showinfo("Settings", "Settings applied successfully", parent=self)

    def _on_ok(self):
        """Handle OK button."""
        if self._apply_settings():
            self.destroy()

    def _on_cancel(self):
        """Handle Cancel button."""
        # Restore original values
        failed_keys = []
        for key, value in self.original_values.items():
            try:
                set_setting(key, value, SettingScope.GLOBAL)
            except Exception as e:
                # Track failed restores - user should know if settings couldn't be restored
                failed_keys.append(key)

        # If any settings failed to restore, warn the user
        if failed_keys:
            messagebox.showwarning(
                "Settings Restore Warning",
                f"Some settings could not be restored to their original values:\n" +
                "\n".join(f"  - {key}" for key in failed_keys) +
                "\n\nThese settings may remain in their modified state.",
                parent=self
            )

        self.destroy()

    def _on_reset(self):
        """Handle Reset to Defaults button."""
        if messagebox.askyesno(
            "Reset Settings",
            "Reset all settings to their default values?",
            parent=self
        ):
            # Set all widgets to default values
            for key, defn in SETTING_DEFINITIONS.items():
                if key in self.widgets:
                    widget = self.widgets[key]
                    if isinstance(widget, tk.Variable):
                        widget.set(defn.default)
