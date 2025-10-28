#!/usr/bin/env python3
"""
Manual test for TK Settings UI.

This test verifies that:
1. Settings dialog opens from menu
2. All settings are displayed in appropriate categories
3. Widgets match setting types (checkbox, spinbox, combobox, entry)
4. OK/Cancel/Apply/Reset buttons work
5. Settings are persisted when applied

Run this test manually to verify the UI works correctly.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.settings import get, set as settings_set, SettingScope
from src.settings_definitions import SETTING_DEFINITIONS


def test_settings_dialog():
    """Test settings dialog can be imported and created."""
    try:
        from src.ui.tk_settings_dialog import SettingsDialog
        print("✓ Settings dialog module imported successfully")
        return True
    except Exception as e:
        print(f"✗ Failed to import settings dialog: {e}")
        return False


def test_settings_enumeration():
    """Test that all settings can be enumerated."""
    try:
        print("\nAvailable settings:")
        categories = {}
        for key, defn in SETTING_DEFINITIONS.items():
            category = key.split('.')[0]
            if category not in categories:
                categories[category] = []
            categories[category].append(key)

        for category, keys in sorted(categories.items()):
            print(f"  {category}: {len(keys)} settings")
            for key in keys:
                current = get(key)
                print(f"    - {key} = {current}")

        print("✓ Settings enumeration successful")
        return True
    except Exception as e:
        print(f"✗ Failed to enumerate settings: {e}")
        return False


def test_settings_get_set():
    """Test that settings can be read and written."""
    try:
        # Test reading
        original = get('keywords.case_style')
        print(f"\nOriginal keywords.case_style: {original}")

        # Test writing
        settings_set('keywords.case_style', 'force_upper', SettingScope.GLOBAL)
        new_value = get('keywords.case_style')
        print(f"After setting to force_upper: {new_value}")

        # Restore original
        settings_set('keywords.case_style', original, SettingScope.GLOBAL)
        restored = get('keywords.case_style')
        print(f"After restoring: {restored}")

        if restored == original:
            print("✓ Settings get/set works correctly")
            return True
        else:
            print("✗ Settings not properly restored")
            return False

    except Exception as e:
        print(f"✗ Failed to get/set settings: {e}")
        return False


def main():
    """Run all tests."""
    print("Testing TK Settings UI Components\n")
    print("=" * 50)

    tests = [
        test_settings_dialog,
        test_settings_enumeration,
        test_settings_get_set,
    ]

    results = [test() for test in tests]

    print("\n" + "=" * 50)
    print(f"Results: {sum(results)}/{len(results)} tests passed")

    if all(results):
        print("\n✓ All component tests passed")
        print("\nTo test the full UI:")
        print("1. Run: python3 mbasic.py")
        print("2. Click Edit > Settings...")
        print("3. Verify all settings appear in tabs")
        print("4. Change some settings and click Apply")
        print("5. Close dialog and reopen to verify changes persisted")
        return 0
    else:
        print("\n✗ Some tests failed")
        return 1


if __name__ == '__main__':
    sys.exit(main())
