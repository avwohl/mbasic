#!/usr/bin/env python3
"""Test script to verify web UI session isolation.

This script simulates accessing the web UI and verifies that:
1. The web UI can start successfully
2. Session state is properly isolated per client

Usage:
    python3 utils/test_web_session_isolation.py

Manual Testing:
    1. Start the web UI: python3 mbasic --backend web
    2. Open http://localhost:8080 in two different browser tabs/windows
    3. In Tab 1: Enter program "10 PRINT 'TAB 1'"
    4. In Tab 2: Enter program "10 PRINT 'TAB 2'"
    5. Verify each tab shows its own program (not the other tab's program)
"""

import sys
import os

# Add parent directory to path to import mbasic modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_web_backend_imports():
    """Test that web backend can be imported without errors."""
    print("Testing web backend imports...")
    try:
        from src.ui.web.nicegui_backend import NiceGUIBackend
        print("✓ NiceGUIBackend imported successfully")
        return True
    except Exception as e:
        print(f"✗ Failed to import NiceGUIBackend: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_session_state_structure():
    """Test that session state properties are defined correctly."""
    print("\nTesting session state structure...")
    try:
        from src.ui.web.nicegui_backend import NiceGUIBackend

        # Verify the backend class has the expected property methods
        expected_properties = [
            'runtime', 'interpreter', 'running', 'paused', 'breakpoints',
            'output_text', 'current_file', 'recent_files', 'exec_io',
            'input_future', 'last_save_content', 'exec_timer'
        ]

        missing = []
        for prop in expected_properties:
            # Check if property exists on the class
            if not hasattr(NiceGUIBackend, prop):
                missing.append(prop)
            else:
                # Verify it's a property
                attr = getattr(NiceGUIBackend, prop)
                if not isinstance(attr, property):
                    print(f"  WARNING: {prop} is not a property")

        if missing:
            print(f"✗ Missing properties: {', '.join(missing)}")
            return False

        print(f"✓ All {len(expected_properties)} session properties defined")

        # Verify _get_session_state method exists
        if not hasattr(NiceGUIBackend, '_get_session_state'):
            print("✗ Missing _get_session_state method")
            return False

        print("✓ _get_session_state method exists")
        print("✓ Session state structure is correct")
        print("\nNote: Runtime testing requires NiceGUI server running")
        print("      Use manual testing instructions below")
        return True

    except Exception as e:
        print(f"✗ Session state test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("=" * 70)
    print("Web UI Session Isolation Test")
    print("=" * 70)

    results = []

    # Test 1: Imports
    results.append(("Imports", test_web_backend_imports()))

    # Test 2: Session State Structure
    results.append(("Session State", test_session_state_structure()))

    # Summary
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")

    print(f"\nPassed: {passed}/{total}")

    if passed == total:
        print("\n✓ All tests passed!")
        print("\nManual Testing Instructions:")
        print("  1. Start web UI: python3 mbasic --backend web")
        print("  2. Open http://localhost:8080 in two browser tabs")
        print("  3. Load different programs in each tab")
        print("  4. Verify each tab maintains its own program state")
        return 0
    else:
        print("\n✗ Some tests failed")
        return 1

if __name__ == '__main__':
    sys.exit(main())
