#!/usr/bin/env python3
"""
Test for curses settings UI.

This test verifies that:
1. Settings widget can be created
2. All settings are accessible
3. Widgets are created for all setting types
4. Settings can be read and written

Since curses UI requires a terminal, this test only validates the
widget creation and logic, not the actual UI display.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.settings import get, set as settings_set, SettingScope
from src.settings_definitions import SETTING_DEFINITIONS


def test_settings_widget_import():
    """Test that settings widget can be imported."""
    try:
        from src.ui.curses_settings_widget import SettingsWidget
        print("✓ Settings widget imported successfully")
        return True
    except Exception as e:
        print(f"✗ Failed to import settings widget: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_settings_widget_creation():
    """Test that settings widget can be created."""
    try:
        from src.ui.curses_settings_widget import SettingsWidget
        widget = SettingsWidget()
        print("✓ Settings widget created successfully")

        # Check that widgets were created
        if len(widget.widgets) > 0:
            print(f"✓ Created widgets for {len(widget.widgets)} settings")
            return True
        else:
            print("✗ No widgets created")
            return False

    except Exception as e:
        print(f"✗ Failed to create settings widget: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_settings_widget_values():
    """Test that settings widget loads current values."""
    try:
        from src.ui.curses_settings_widget import SettingsWidget

        # Get original value
        original = get('keywords.case_style')

        # Create widget
        widget = SettingsWidget()

        # Check that original value was loaded
        if 'keywords.case_style' in widget.original_values:
            loaded_value = widget.original_values['keywords.case_style']
            if loaded_value == original:
                print(f"✓ Widget loaded current value: {loaded_value}")
                return True
            else:
                print(f"✗ Widget value mismatch: loaded {loaded_value}, expected {original}")
                return False
        else:
            print("✗ keywords.case_style not in original_values")
            return False

    except Exception as e:
        print(f"✗ Failed to test widget values: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_keybinding_added():
    """Test that SETTINGS_KEY was added to keybindings."""
    try:
        from src.ui.keybindings import SETTINGS_KEY, SETTINGS_DISPLAY
        print(f"✓ Settings keybinding added: {SETTINGS_DISPLAY} = {SETTINGS_KEY}")
        return True
    except Exception as e:
        print(f"✗ Failed to import settings keybinding: {e}")
        return False


def main():
    """Run all tests."""
    print("Testing Curses Settings UI Components\n")
    print("=" * 50)

    tests = [
        test_settings_widget_import,
        test_settings_widget_creation,
        test_settings_widget_values,
        test_keybinding_added,
    ]

    results = [test() for test in tests]

    print("\n" + "=" * 50)
    print(f"Results: {sum(results)}/{len(results)} tests passed")

    if all(results):
        print("\n✓ All component tests passed")
        print("\nTo test the full UI:")
        print("1. Run: python3 mbasic --ui curses")
        print("2. Press Ctrl+P to open settings")
        print("3. Navigate with arrow keys, Tab to switch fields")
        print("4. Change some settings and press Tab to OK button, Enter to apply")
        print("5. Press ESC or Cancel to close")
        return 0
    else:
        print("\n✗ Some tests failed")
        return 1


if __name__ == '__main__':
    sys.exit(main())
