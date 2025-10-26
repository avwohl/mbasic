#!/usr/bin/env python3
"""
Test keybinding loader.

Verifies that keybindings are correctly loaded from JSON and converted to Tkinter format.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from ui.keybinding_loader import KeybindingLoader

def test_tk_loader():
    """Test Tk keybinding loader."""
    print("Tk Keybinding Loader Test")
    print("=" * 60)
    print()

    loader = KeybindingLoader('tk')

    test_cases = [
        # (section, action, expected_primary, expected_tk_binding)
        ('menu', 'file_new', 'Ctrl+N', '<Control-n>'),
        ('menu', 'file_open', 'Ctrl+O', '<Control-o>'),
        ('menu', 'file_save', 'Ctrl+S', '<Control-s>'),
        ('menu', 'file_quit', 'Ctrl+Q', '<Control-q>'),
        ('menu', 'run_program', 'F5', '<F5>'),
        ('menu', 'help_topics', 'Ctrl+?', '<Control-question>'),
    ]

    all_passed = True
    for section, action, expected_primary, expected_binding in test_cases:
        # Test get_primary
        primary = loader.get_primary(section, action)
        primary_ok = primary == expected_primary

        # Test get_tk_bindings
        bindings = loader.get_tk_bindings(section, action)
        binding_ok = expected_binding in bindings if bindings else False

        # Test get_tk_accelerator
        accelerator = loader.get_tk_accelerator(section, action)
        accel_ok = accelerator == expected_primary

        status = "✓" if (primary_ok and binding_ok and accel_ok) else "✗"
        if not (primary_ok and binding_ok and accel_ok):
            all_passed = False

        print(f"{status} {section}:{action:20} → {primary or 'NONE':10} → {expected_binding}")

        if not primary_ok:
            print(f"   ERROR: Expected primary '{expected_primary}', got '{primary}'")
        if not binding_ok:
            print(f"   ERROR: Expected binding '{expected_binding}', got {bindings}")
        if not accel_ok:
            print(f"   ERROR: Expected accelerator '{expected_primary}', got '{accelerator}'")

    print()
    return all_passed

def test_curses_loader():
    """Test Curses keybinding loader."""
    print("Curses Keybinding Loader Test")
    print("=" * 60)
    print()

    loader = KeybindingLoader('curses')

    test_cases = [
        ('editor', 'help', 'Ctrl+H'),
        ('editor', 'save', 'Ctrl+S'),
        ('editor', 'run', 'Ctrl+R'),
        ('editor', 'new', 'Ctrl+N'),
        ('editor', 'quit', 'Ctrl+Q'),
        ('help_browser', 'search', '/'),
        ('help_browser', 'back', 'U'),
        ('help_browser', 'quit', 'ESC'),
    ]

    all_passed = True
    for section, action, expected_primary in test_cases:
        primary = loader.get_primary(section, action)
        status = "✓" if primary == expected_primary else "✗"
        if primary != expected_primary:
            all_passed = False

        print(f"{status} {section}:{action:20} → {primary or 'NONE':10} (expected: {expected_primary})")

    print()
    return all_passed

def test_multi_key_bindings():
    """Test actions with multiple key bindings."""
    print("Multi-Key Binding Test")
    print("=" * 60)
    print()

    loader = KeybindingLoader('tk')

    # help_topics has both Ctrl+? and Ctrl+/
    all_keys = loader.get_all_keys('menu', 'help_topics')
    expected = ['Ctrl+?', 'Ctrl+/']

    keys_ok = set(all_keys) == set(expected)
    status = "✓" if keys_ok else "✗"

    print(f"{status} help_topics has multiple keys: {all_keys}")
    if not keys_ok:
        print(f"   Expected: {expected}")

    # Check both are converted to Tk bindings
    bindings = loader.get_tk_bindings('menu', 'help_topics')
    expected_bindings = ['<Control-question>', '<Control-slash>']

    bindings_ok = set(bindings) == set(expected_bindings)
    status = "✓" if bindings_ok else "✗"

    print(f"{status} Tk bindings: {bindings}")
    if not bindings_ok:
        print(f"   Expected: {expected_bindings}")

    print()
    return keys_ok and bindings_ok

if __name__ == '__main__':
    print("MBASIC Keybinding Loader Test")
    print()

    success = True

    # Test 1: Tk loader
    if not test_tk_loader():
        success = False

    # Test 2: Curses loader
    if not test_curses_loader():
        success = False

    # Test 3: Multi-key bindings
    if not test_multi_key_bindings():
        success = False

    if success:
        print("✅ All tests passed!")
        sys.exit(0)
    else:
        print("❌ Some tests failed")
        sys.exit(1)
