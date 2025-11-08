#!/usr/bin/env python3
"""Test script for per-session Redis settings isolation.

This verifies that:
1. Different sessions have independent settings
2. Settings persist across SettingsManager instances with same session_id
3. Default settings are loaded from disk on first access
4. Changes don't affect other sessions
"""

import os
import sys
import redis

# Set Redis URL before importing settings modules
os.environ['NICEGUI_REDIS_URL'] = 'redis://localhost:6379/0'

from src.settings import SettingsManager
from src.settings_backend import create_settings_backend

def test_per_session_isolation():
    """Test that different sessions have isolated settings."""
    print("=" * 70)
    print("TEST: Per-Session Settings Isolation")
    print("=" * 70)

    # Clean up any existing test keys
    redis_client = redis.from_url(os.environ['NICEGUI_REDIS_URL'], decode_responses=True)
    for key in redis_client.scan_iter("nicegui:settings:session*"):
        redis_client.delete(key)

    # Create two different sessions
    session1_id = "session_a_12345"
    session2_id = "session_b_67890"

    print(f"\nCreating Session 1 (ID: {session1_id})")
    backend1 = create_settings_backend(session_id=session1_id)
    mgr1 = SettingsManager(backend=backend1)

    print(f"Creating Session 2 (ID: {session2_id})")
    backend2 = create_settings_backend(session_id=session2_id)
    mgr2 = SettingsManager(backend=backend2)

    # Verify both start with default settings
    print("\n--- Initial State ---")
    default_step = 10  # Default from settings_definitions.py
    print(f"Session 1 auto_number_step: {mgr1.get('editor.auto_number_step')} (expected: {default_step})")
    print(f"Session 2 auto_number_step: {mgr2.get('editor.auto_number_step')} (expected: {default_step})")

    assert mgr1.get('editor.auto_number_step') == default_step, "Session 1 should have default value"
    assert mgr2.get('editor.auto_number_step') == default_step, "Session 2 should have default value"
    print("✓ Both sessions start with defaults")

    # Modify settings in session 1
    print("\n--- Modifying Session 1 ---")
    from src.settings_definitions import SettingScope
    mgr1.set('editor.auto_number_step', 100)
    mgr1.save(SettingScope.GLOBAL)
    print(f"Session 1 changed auto_number_step to: {mgr1.get('editor.auto_number_step')}")

    # Verify session 2 is unaffected
    print("\n--- Checking Session 2 (should be unchanged) ---")
    print(f"Session 2 auto_number_step: {mgr2.get('editor.auto_number_step')} (expected: {default_step})")
    assert mgr2.get('editor.auto_number_step') == default_step, "Session 2 should still have default value"
    print("✓ Session 2 unaffected by Session 1 changes")

    # Modify settings in session 2
    print("\n--- Modifying Session 2 ---")
    mgr2.set('editor.auto_number_step', 1)
    mgr2.save(SettingScope.GLOBAL)
    print(f"Session 2 changed auto_number_step to: {mgr2.get('editor.auto_number_step')}")

    # Verify both sessions have different values
    print("\n--- Verifying Isolation ---")
    print(f"Session 1: {mgr1.get('editor.auto_number_step')} (expected: 100)")
    print(f"Session 2: {mgr2.get('editor.auto_number_step')} (expected: 1)")
    assert mgr1.get('editor.auto_number_step') == 100, "Session 1 should still have 100"
    assert mgr2.get('editor.auto_number_step') == 1, "Session 2 should have 1"
    print("✓ Sessions have independent settings")

    # Test persistence: recreate managers with same session IDs
    print("\n--- Testing Persistence (Simulating Page Refresh) ---")
    backend1_new = create_settings_backend(session_id=session1_id)
    mgr1_new = SettingsManager(backend=backend1_new)

    backend2_new = create_settings_backend(session_id=session2_id)
    mgr2_new = SettingsManager(backend=backend2_new)

    print(f"Session 1 (reloaded): {mgr1_new.get('editor.auto_number_step')} (expected: 100)")
    print(f"Session 2 (reloaded): {mgr2_new.get('editor.auto_number_step')} (expected: 1)")
    assert mgr1_new.get('editor.auto_number_step') == 100, "Session 1 settings should persist"
    assert mgr2_new.get('editor.auto_number_step') == 1, "Session 2 settings should persist"
    print("✓ Settings persist across manager instances")

    # Check Redis keys
    print("\n--- Redis Storage ---")
    keys = list(redis_client.scan_iter("nicegui:settings:session*"))
    print(f"Redis keys created: {len(keys)}")
    for key in sorted(keys):
        data = redis_client.get(key)
        print(f"  {key}: {data}")

    # Clean up
    print("\n--- Cleanup ---")
    for key in keys:
        redis_client.delete(key)
    print(f"Deleted {len(keys)} Redis keys")

    print("\n" + "=" * 70)
    print("ALL TESTS PASSED ✓")
    print("=" * 70)


def test_file_backend_fallback():
    """Test that file backend is used when Redis is not available."""
    print("\n" + "=" * 70)
    print("TEST: File Backend Fallback (No Redis)")
    print("=" * 70)

    # Temporarily remove Redis URL
    saved_url = os.environ.get('NICEGUI_REDIS_URL')
    if saved_url:
        del os.environ['NICEGUI_REDIS_URL']

    try:
        backend = create_settings_backend(session_id="test_session")
        from src.settings_backend import FileSettingsBackend

        print(f"Backend type: {type(backend).__name__}")
        assert isinstance(backend, FileSettingsBackend), "Should use FileSettingsBackend when no Redis"
        print("✓ File backend used when NICEGUI_REDIS_URL not set")

    finally:
        # Restore Redis URL
        if saved_url:
            os.environ['NICEGUI_REDIS_URL'] = saved_url

    print("=" * 70)


if __name__ == '__main__':
    try:
        test_per_session_isolation()
        test_file_backend_fallback()
        print("\n✅ All Redis settings tests passed!")
        sys.exit(0)
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
