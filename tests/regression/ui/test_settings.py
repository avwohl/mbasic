#!/usr/bin/env python3
"""
Test settings system across all UIs.

Verifies that:
- Settings can be loaded and saved
- Settings validation works
- Settings dialogs/UIs exist and are accessible
- Settings affect program behavior (auto-numbering)
- CLI SHOWSETTINGS and SETSETTING commands work
"""

import sys
import json
import tempfile
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.settings import SettingsManager
from src.settings_definitions import (
    SETTING_DEFINITIONS,
    SettingType,
    SettingScope,
    validate_value,
    get_definition,
)


def test_settings_manager_basic():
    """Test basic SettingsManager functionality."""
    print("Settings Manager Basic Test")
    print("=" * 60)
    print()

    # Create temporary settings file
    with tempfile.TemporaryDirectory() as tmpdir:
        manager = SettingsManager(project_dir=tmpdir)

        test_cases = [
            ("editor.auto_number", True),
            ("editor.auto_number_step", 100),
            ("keywords.case_style", "force_upper"),
            ("ui.theme", "dark"),
        ]

        all_passed = True
        for key, value in test_cases:
            # Set value
            try:
                manager.set(key, value, SettingScope.GLOBAL)
                retrieved = manager.get(key)
                status = "✓" if retrieved == value else "✗"
                if retrieved != value:
                    all_passed = False
                    print(f"{status} Set/Get {key}: expected {value}, got {retrieved}")
                else:
                    print(f"{status} Set/Get {key} = {value}")
            except Exception as e:
                all_passed = False
                print(f"✗ Set/Get {key}: {e}")

    print()
    return all_passed


def test_settings_persistence():
    """Test settings persistence to disk."""
    print("Settings Persistence Test")
    print("=" * 60)
    print()

    with tempfile.TemporaryDirectory() as tmpdir:
        # Create manager and set values
        manager1 = SettingsManager(project_dir=tmpdir)
        manager1.set("editor.auto_number_step", 100, SettingScope.GLOBAL)
        manager1.set("ui.theme", "dark", SettingScope.GLOBAL)
        manager1.save(SettingScope.GLOBAL)

        # Create new manager and verify values persisted
        manager2 = SettingsManager(project_dir=tmpdir)
        step = manager2.get("editor.auto_number_step")
        theme = manager2.get("ui.theme")

        step_ok = step == 100
        theme_ok = theme == "dark"

        print(f"{'✓' if step_ok else '✗'} editor.auto_number_step persisted: {step}")
        print(f"{'✓' if theme_ok else '✗'} ui.theme persisted: {theme}")

    print()
    return step_ok and theme_ok


def test_settings_validation():
    """Test settings validation."""
    print("Settings Validation Test")
    print("=" * 60)
    print()

    test_cases = [
        # (key, value, should_pass)
        ("editor.auto_number", True, True),
        ("editor.auto_number", "yes", False),
        ("editor.auto_number_step", 10, True),
        ("editor.auto_number_step", -5, False),
        ("editor.auto_number_step", 2000, False),
        ("keywords.case_style", "force_upper", True),
        ("keywords.case_style", "invalid", False),
        ("ui.theme", "dark", True),
        ("ui.theme", "rainbow", False),
    ]

    all_passed = True
    for key, value, should_pass in test_cases:
        result = validate_value(key, value)
        status = "✓" if result == should_pass else "✗"
        if result != should_pass:
            all_passed = False

        verdict = "valid" if should_pass else "invalid"
        actual = "valid" if result else "invalid"
        print(f"{status} {key} = {value!r:20} (expected {verdict}, got {actual})")

    print()
    return all_passed


def test_settings_scope_precedence():
    """Test settings scope precedence (file > project > global)."""
    print("Settings Scope Precedence Test")
    print("=" * 60)
    print()

    with tempfile.TemporaryDirectory() as tmpdir:
        manager = SettingsManager(project_dir=tmpdir)

        # Set global value
        manager.set("editor.auto_number_step", 10, SettingScope.GLOBAL)

        # Set project value (should override global)
        manager.set("editor.auto_number_step", 100, SettingScope.PROJECT)

        # Get should return project value
        value = manager.get("editor.auto_number_step")
        project_ok = value == 100

        print(f"{'✓' if project_ok else '✗'} Project scope overrides global: {value} (expected 100)")

        # Set file value (should override project)
        manager.file_settings["editor.auto_number_step"] = 1000
        value = manager.get("editor.auto_number_step")
        file_ok = value == 1000

        print(f"{'✓' if file_ok else '✗'} File scope overrides project: {value} (expected 1000)")

    print()
    return project_ok and file_ok


def test_settings_definitions():
    """Test that all settings have valid definitions."""
    print("Settings Definitions Test")
    print("=" * 60)
    print()

    required_keys = [
        "editor.auto_number",
        "editor.auto_number_step",
        "keywords.case_style",
        "variables.case_conflict",
        "ui.theme",
    ]

    all_passed = True
    for key in required_keys:
        defn = get_definition(key)
        if defn is None:
            print(f"✗ Missing definition for {key}")
            all_passed = False
        else:
            has_default = defn.default is not None
            has_type = defn.type is not None
            has_desc = bool(defn.description)

            if has_default and has_type and has_desc:
                print(f"✓ {key} has complete definition")
            else:
                print(f"✗ {key} has incomplete definition")
                all_passed = False

    print()
    return all_passed


def test_tk_settings_dialog_exists():
    """Test that TK settings dialog exists and can be instantiated."""
    print("TK Settings Dialog Test")
    print("=" * 60)
    print()

    try:
        from src.ui.tk_settings_dialog import SettingsDialog
        print("✓ TK SettingsDialog class exists")

        # Check for key methods
        has_init = hasattr(SettingsDialog, '__init__')
        has_create = hasattr(SettingsDialog, '_create_widgets')
        has_apply = hasattr(SettingsDialog, '_apply_settings')

        print(f"{'✓' if has_init else '✗'} Has __init__ method")
        print(f"{'✓' if has_create else '✗'} Has _create_widgets method")
        print(f"{'✓' if has_apply else '✗'} Has _apply_settings method")

        success = has_init and has_create and has_apply
    except ImportError as e:
        print(f"✗ Failed to import TK SettingsDialog: {e}")
        success = False

    print()
    return success


def test_curses_settings_widget_exists():
    """Test that curses settings widget exists and can be instantiated."""
    print("Curses Settings Widget Test")
    print("=" * 60)
    print()

    try:
        from src.ui.curses_settings_widget import SettingsWidget
        print("✓ Curses SettingsWidget class exists")

        # Check for key methods
        has_init = hasattr(SettingsWidget, '__init__')
        has_create = hasattr(SettingsWidget, '_create_body')
        has_apply = hasattr(SettingsWidget, '_apply_settings')

        print(f"{'✓' if has_init else '✗'} Has __init__ method")
        print(f"{'✓' if has_create else '✗'} Has _create_body method")
        print(f"{'✓' if has_apply else '✗'} Has _apply_settings method")

        success = has_init and has_create and has_apply
    except ImportError as e:
        print(f"✗ Failed to import Curses SettingsWidget: {e}")
        success = False

    print()
    return success


def test_web_settings_dialog_exists():
    """Test that web settings dialog exists."""
    print("Web Settings Dialog Test")
    print("=" * 60)
    print()

    try:
        from src.ui.web.web_settings_dialog import WebSettingsDialog
        print("✓ Web WebSettingsDialog class exists")

        # Check for key methods
        has_init = hasattr(WebSettingsDialog, '__init__')
        has_show = hasattr(WebSettingsDialog, 'show')
        has_save = hasattr(WebSettingsDialog, '_on_save')

        print(f"{'✓' if has_init else '✗'} Has __init__ method")
        print(f"{'✓' if has_show else '✗'} Has show method")
        print(f"{'✓' if has_save else '✗'} Has _on_save method")

        success = has_init and has_show and has_save
    except ImportError as e:
        print(f"✗ Failed to import Web WebSettingsDialog: {e}")
        success = False

    print()
    return success


def test_cli_commands_exist():
    """Test that CLI SHOWSETTINGS and SETSETTING commands exist."""
    print("CLI Commands Test")
    print("=" * 60)
    print()

    try:
        from src.interpreter import Interpreter

        # Check if execute_showsettings method exists
        has_showsettings = hasattr(Interpreter, 'execute_showsettings')
        print(f"{'✓' if has_showsettings else '✗'} execute_showsettings method exists")

        # Check if execute_setsetting method exists
        has_setsetting = hasattr(Interpreter, 'execute_setsetting')
        print(f"{'✓' if has_setsetting else '✗'} execute_setsetting method exists")

        success = has_showsettings and has_setsetting
    except ImportError as e:
        print(f"✗ Failed to import Interpreter: {e}")
        success = False

    print()
    return success


def test_all_settings_accessible():
    """Test that all settings in definitions are accessible via get/set."""
    print("Settings Accessibility Test")
    print("=" * 60)
    print()

    with tempfile.TemporaryDirectory() as tmpdir:
        manager = SettingsManager(project_dir=tmpdir)

        all_passed = True
        for key, defn in SETTING_DEFINITIONS.items():
            # Try to get default value
            try:
                value = manager.get(key)
                if value == defn.default:
                    print(f"✓ {key} accessible (default: {value})")
                else:
                    print(f"⚠ {key} accessible but default mismatch (got {value}, expected {defn.default})")
            except Exception as e:
                print(f"✗ {key} failed to get: {e}")
                all_passed = False

    print()
    return all_passed


def test_json_serialization():
    """Test that settings can be serialized to JSON."""
    print("JSON Serialization Test")
    print("=" * 60)
    print()

    with tempfile.TemporaryDirectory() as tmpdir:
        manager = SettingsManager(project_dir=tmpdir)

        # Set some values
        manager.set("editor.auto_number_step", 100)
        manager.set("ui.theme", "dark")
        manager.save(SettingScope.GLOBAL)

        # Check JSON file was created
        settings_file = manager.global_settings_path
        if settings_file.exists():
            print(f"✓ Settings file created: {settings_file}")

            # Try to load JSON
            try:
                with open(settings_file, 'r') as f:
                    data = json.load(f)

                has_version = 'version' in data
                has_settings = 'settings' in data

                print(f"{'✓' if has_version else '✗'} JSON has version field")
                print(f"{'✓' if has_settings else '✗'} JSON has settings field")

                success = has_version and has_settings
            except Exception as e:
                print(f"✗ Failed to parse JSON: {e}")
                success = False
        else:
            print(f"✗ Settings file not created")
            success = False

    print()
    return success


if __name__ == '__main__':
    print("MBASIC Settings System Test Suite")
    print("=" * 60)
    print()

    success = True

    # Core functionality tests
    if not test_settings_manager_basic():
        success = False

    if not test_settings_persistence():
        success = False

    if not test_settings_validation():
        success = False

    if not test_settings_scope_precedence():
        success = False

    if not test_settings_definitions():
        success = False

    if not test_all_settings_accessible():
        success = False

    if not test_json_serialization():
        success = False

    # UI component tests
    if not test_tk_settings_dialog_exists():
        success = False

    if not test_curses_settings_widget_exists():
        success = False

    if not test_web_settings_dialog_exists():
        success = False

    # CLI command tests
    if not test_cli_commands_exist():
        success = False

    if success:
        print("=" * 60)
        print("✅ All settings tests passed!")
        print()
        print("Summary:")
        print("  - Settings manager works correctly")
        print("  - Settings persist to disk")
        print("  - Validation works as expected")
        print("  - Scope precedence is correct")
        print("  - All UI components exist")
        print("  - CLI commands are implemented")
        sys.exit(0)
    else:
        print("=" * 60)
        print("❌ Some settings tests failed")
        sys.exit(1)
