"""
Test suite for ResourceLimits class
"""

import sys
import time
from pathlib import Path

# Add src directory to path so we can import modules
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from resource_limits import (
    ResourceLimits,
    create_web_limits,
    create_local_limits,
    create_unlimited_limits
)
from parser import TypeInfo


def test_gosub_stack_tracking():
    """Test GOSUB stack depth tracking"""
    print("Testing GOSUB stack tracking:")

    limits = ResourceLimits(max_gosub_depth=3)

    # Should succeed: depth 1
    try:
        limits.push_gosub(100)
        assert limits.current_gosub_depth == 1
        print("  ✓ GOSUB depth 1")
    except RuntimeError as e:
        print(f"  ✗ Unexpected error at depth 1: {e}")
        return False

    # Should succeed: depth 2
    try:
        limits.push_gosub(200)
        assert limits.current_gosub_depth == 2
        print("  ✓ GOSUB depth 2")
    except RuntimeError as e:
        print(f"  ✗ Unexpected error at depth 2: {e}")
        return False

    # Should succeed: depth 3
    try:
        limits.push_gosub(300)
        assert limits.current_gosub_depth == 3
        print("  ✓ GOSUB depth 3")
    except RuntimeError as e:
        print(f"  ✗ Unexpected error at depth 3: {e}")
        return False

    # Should fail: depth 4 exceeds limit
    try:
        limits.push_gosub(400)
        print(f"  ✗ Should have raised RuntimeError at depth 4")
        return False
    except RuntimeError as e:
        if "GOSUB stack overflow" in str(e):
            print(f"  ✓ Correctly raised error: {e}")
        else:
            print(f"  ✗ Wrong error message: {e}")
            return False

    # Test pop (depth is now 4 because the error was raised AFTER incrementing)
    limits.pop_gosub()
    assert limits.current_gosub_depth == 3
    limits.pop_gosub()
    assert limits.current_gosub_depth == 2
    print("  ✓ GOSUB pop works")

    print("✓ GOSUB stack tracking test passed\n")
    return True


def test_for_loop_tracking():
    """Test FOR loop depth tracking"""
    print("Testing FOR loop tracking:")

    limits = ResourceLimits(max_for_depth=2)

    # Should succeed: depth 1
    try:
        limits.push_for_loop("I")
        assert limits.current_for_depth == 1
        print("  ✓ FOR depth 1")
    except RuntimeError as e:
        print(f"  ✗ Unexpected error at depth 1: {e}")
        return False

    # Should succeed: depth 2
    try:
        limits.push_for_loop("J")
        assert limits.current_for_depth == 2
        print("  ✓ FOR depth 2")
    except RuntimeError as e:
        print(f"  ✗ Unexpected error at depth 2: {e}")
        return False

    # Should fail: depth 3 exceeds limit
    try:
        limits.push_for_loop("K")
        print(f"  ✗ Should have raised RuntimeError at depth 3")
        return False
    except RuntimeError as e:
        if "FOR loop nesting too deep" in str(e):
            print(f"  ✓ Correctly raised error: {e}")
        else:
            print(f"  ✗ Wrong error message: {e}")
            return False

    # Test pop (depth is now 3 because the error was raised AFTER incrementing)
    limits.pop_for_loop()
    assert limits.current_for_depth == 2
    limits.pop_for_loop()
    assert limits.current_for_depth == 1
    print("  ✓ FOR loop pop works")

    print("✓ FOR loop tracking test passed\n")
    return True


def test_while_loop_tracking():
    """Test WHILE loop depth tracking"""
    print("Testing WHILE loop tracking:")

    limits = ResourceLimits(max_while_depth=2)

    # Should succeed: depth 1
    try:
        limits.push_while_loop()
        assert limits.current_while_depth == 1
        print("  ✓ WHILE depth 1")
    except RuntimeError as e:
        print(f"  ✗ Unexpected error at depth 1: {e}")
        return False

    # Should succeed: depth 2
    try:
        limits.push_while_loop()
        assert limits.current_while_depth == 2
        print("  ✓ WHILE depth 2")
    except RuntimeError as e:
        print(f"  ✗ Unexpected error at depth 2: {e}")
        return False

    # Should fail: depth 3 exceeds limit
    try:
        limits.push_while_loop()
        print(f"  ✗ Should have raised RuntimeError at depth 3")
        return False
    except RuntimeError as e:
        if "WHILE loop nesting too deep" in str(e):
            print(f"  ✓ Correctly raised error: {e}")
        else:
            print(f"  ✗ Wrong error message: {e}")
            return False

    # Test pop (depth is now 3 because the error was raised AFTER incrementing)
    limits.pop_while_loop()
    assert limits.current_while_depth == 2
    limits.pop_while_loop()
    assert limits.current_while_depth == 1
    print("  ✓ WHILE loop pop works")

    print("✓ WHILE loop tracking test passed\n")
    return True


def test_array_allocation():
    """Test array allocation tracking"""
    print("Testing array allocation:")

    limits = ResourceLimits(
        max_array_size=100,     # 100 bytes max per array
        max_total_memory=200    # 200 bytes total
    )

    # Array of 10 doubles (10 * 8 = 80 bytes) - should succeed
    try:
        limits.allocate_array("A", [9], TypeInfo.DOUBLE)  # 0-9 = 10 elements
        assert limits.current_memory_usage == 80
        print(f"  ✓ Allocated array A: 10 doubles = 80 bytes")
    except RuntimeError as e:
        print(f"  ✗ Unexpected error allocating A: {e}")
        return False

    # Array of 20 doubles (20 * 8 = 160 bytes) - should fail per-array limit
    try:
        limits.allocate_array("B", [19], TypeInfo.DOUBLE)  # 0-19 = 20 elements
        print(f"  ✗ Should have raised error for array B (exceeds per-array limit)")
        return False
    except RuntimeError as e:
        if "Array B too large" in str(e):
            print(f"  ✓ Correctly raised error: {e}")
        else:
            print(f"  ✗ Wrong error message: {e}")
            return False

    # Array of 12 doubles (12 * 8 = 96 bytes) - should succeed individually,
    # and fit in total limit (80 + 96 = 176)
    try:
        limits.allocate_array("C", [11], TypeInfo.DOUBLE)  # 0-11 = 12 elements
        assert limits.current_memory_usage == 176  # 80 + 96
        print(f"  ✓ Allocated array C: 12 doubles = 96 bytes (total: 176/200)")
    except RuntimeError as e:
        print(f"  ✗ Unexpected error allocating C: {e}")
        return False

    # Array of 4 doubles (4 * 8 = 32 bytes) - would push total to 208, exceeding 200 limit
    try:
        limits.allocate_array("D", [3], TypeInfo.DOUBLE)  # 0-3 = 4 elements = 32 bytes
        print(f"  ✗ Should have raised error for array D (exceeds total memory)")
        return False
    except RuntimeError as e:
        if "Out of memory" in str(e):
            print(f"  ✓ Correctly raised error: {e}")
        else:
            print(f"  ✗ Wrong error message: {e}")
            return False

    # Re-dimension existing array (should free old allocation)
    try:
        limits.allocate_array("A", [4], TypeInfo.DOUBLE)  # 0-4 = 5 elements = 40 bytes
        # Should free 80 and allocate 40, total = 96 + 40 = 136
        assert limits.current_memory_usage == 136
        print(f"  ✓ Re-dimensioned array A: 5 doubles = 40 bytes (total: 136/200)")
    except RuntimeError as e:
        print(f"  ✗ Unexpected error re-dimensioning A: {e}")
        return False

    print("✓ Array allocation test passed\n")
    return True


def test_variable_allocation():
    """Test variable allocation tracking"""
    print("Testing variable allocation:")

    limits = ResourceLimits(max_total_memory=50)

    # Allocate integer (2 bytes)
    limits.allocate_variable("X%", 10, TypeInfo.INTEGER)
    assert limits.current_memory_usage == 2
    print(f"  ✓ Allocated X% (INTEGER): 2 bytes")

    # Allocate single (4 bytes)
    limits.allocate_variable("Y!", 3.14, TypeInfo.SINGLE)
    assert limits.current_memory_usage == 6
    print(f"  ✓ Allocated Y! (SINGLE): 4 bytes")

    # Allocate double (8 bytes)
    limits.allocate_variable("Z#", 2.718, TypeInfo.DOUBLE)
    assert limits.current_memory_usage == 14
    print(f"  ✓ Allocated Z# (DOUBLE): 8 bytes")

    # Allocate string (length + 4)
    limits.allocate_variable("S$", "Hello", TypeInfo.STRING)
    assert limits.current_memory_usage == 23  # 14 + 5 + 4 = 23
    print(f"  ✓ Allocated S$ (STRING): 9 bytes")

    # Re-assign variable (should free old)
    limits.allocate_variable("X%", 20, TypeInfo.INTEGER)
    assert limits.current_memory_usage == 23  # No change
    print(f"  ✓ Re-assigned X%: still 2 bytes")

    # Free variable
    limits.free_variable("Z#")
    assert limits.current_memory_usage == 15  # 23 - 8
    print(f"  ✓ Freed Z#: 8 bytes freed")

    # Clear all
    limits.clear_all()
    assert limits.current_memory_usage == 0
    print(f"  ✓ Cleared all: 0 bytes")

    print("✓ Variable allocation test passed\n")
    return True


def test_string_length_limit():
    """Test string length limit"""
    print("Testing string length limit:")

    limits = ResourceLimits(max_string_length=10)

    # Short string - should succeed
    try:
        limits.check_string_length("Hello")
        print("  ✓ Short string (5 bytes) allowed")
    except RuntimeError as e:
        print(f"  ✗ Unexpected error: {e}")
        return False

    # Exactly at limit - should succeed
    try:
        limits.check_string_length("0123456789")
        print("  ✓ Exact limit string (10 bytes) allowed")
    except RuntimeError as e:
        print(f"  ✗ Unexpected error: {e}")
        return False

    # Over limit - should fail
    try:
        limits.check_string_length("01234567890")  # 11 bytes
        print("  ✗ Should have raised error for 11-byte string")
        return False
    except RuntimeError as e:
        if "String too long" in str(e):
            print(f"  ✓ Correctly raised error: {e}")
        else:
            print(f"  ✗ Wrong error message: {e}")
            return False

    print("✓ String length limit test passed\n")
    return True


def test_execution_time_limit():
    """Test execution time limit"""
    print("Testing execution time limit:")

    limits = ResourceLimits(max_execution_time=0.1)  # 100ms limit

    # Start execution
    limits.start_execution()
    print("  ✓ Started execution timer")

    # Check immediately - should succeed
    try:
        limits.check_execution_time()
        print("  ✓ Immediate check passed")
    except RuntimeError as e:
        print(f"  ✗ Unexpected error: {e}")
        return False

    # Wait and check again - should succeed
    time.sleep(0.05)  # 50ms
    try:
        limits.check_execution_time()
        print("  ✓ Check at 50ms passed")
    except RuntimeError as e:
        print(f"  ✗ Unexpected error: {e}")
        return False

    # Wait past limit - should fail
    time.sleep(0.06)  # Total 110ms
    try:
        limits.check_execution_time()
        print("  ✗ Should have raised error after 110ms")
        return False
    except RuntimeError as e:
        if "Execution time limit exceeded" in str(e):
            print(f"  ✓ Correctly raised error: {e}")
        else:
            print(f"  ✗ Wrong error message: {e}")
            return False

    print("✓ Execution time limit test passed\n")
    return True


def test_usage_report():
    """Test usage report generation"""
    print("Testing usage report:")

    limits = ResourceLimits(
        max_total_memory=1000,
        max_gosub_depth=10,
        max_for_depth=5,
        max_while_depth=3
    )

    # Allocate some resources
    limits.allocate_array("BIGARRAY", [9, 9], TypeInfo.DOUBLE)  # 10*10*8 = 800 bytes
    limits.allocate_variable("X", 42, TypeInfo.INTEGER)  # 2 bytes
    limits.push_gosub(100)
    limits.push_for_loop("I")
    limits.start_execution()

    # Generate report
    report = limits.get_usage_report()
    print(report)

    # Check report contains expected information
    if "Resource Usage:" not in report:
        print("  ✗ Report missing 'Resource Usage:' header")
        return False

    if "Memory:" not in report:
        print("  ✗ Report missing 'Memory:' line")
        return False

    if "GOSUB depth: 1 / 10" not in report:
        print("  ✗ Report missing GOSUB depth")
        return False

    if "FOR depth: 1 / 5" not in report:
        print("  ✗ Report missing FOR depth")
        return False

    if "BIGARRAY" not in report:
        print("  ✗ Report missing BIGARRAY allocation")
        return False

    print("  ✓ Report contains expected information")
    print("✓ Usage report test passed\n")
    return True


def test_preset_configurations():
    """Test preset configuration factory functions"""
    print("Testing preset configurations:")

    # Test web limits
    web = create_web_limits()
    assert web.max_gosub_depth == 50
    assert web.max_total_memory == 5*1024*1024
    assert web.max_execution_time == 30.0
    print("  ✓ Web limits: 50 GOSUB, 5MB memory, 30s timeout")

    # Test local limits
    local = create_local_limits()
    assert local.max_gosub_depth == 500
    assert local.max_total_memory == 100*1024*1024
    assert local.max_execution_time == 300.0
    print("  ✓ Local limits: 500 GOSUB, 100MB memory, 5min timeout")

    # Test unlimited limits
    unlimited = create_unlimited_limits()
    assert unlimited.max_gosub_depth == 10000
    assert unlimited.max_total_memory == 1024*1024*1024
    assert unlimited.max_execution_time == 3600.0
    print("  ✓ Unlimited limits: 10000 GOSUB, 1GB memory, 1hr timeout")

    print("✓ Preset configurations test passed\n")
    return True


def test_multidimensional_arrays():
    """Test multi-dimensional array size calculation"""
    print("Testing multi-dimensional arrays:")

    limits = ResourceLimits(
        max_array_size=1000,
        max_total_memory=2000
    )

    # 10x10 array of doubles (10*10*8 = 800 bytes)
    try:
        limits.allocate_array("A", [9, 9], TypeInfo.DOUBLE)
        assert limits.current_memory_usage == 800
        print("  ✓ 10x10 DOUBLE array: 800 bytes")
    except RuntimeError as e:
        print(f"  ✗ Unexpected error: {e}")
        return False

    # 5x5x5 array of integers (5*5*5*2 = 250 bytes)
    try:
        limits.allocate_array("B", [4, 4, 4], TypeInfo.INTEGER)
        assert limits.current_memory_usage == 1050
        print("  ✓ 5x5x5 INTEGER array: 250 bytes")
    except RuntimeError as e:
        print(f"  ✗ Unexpected error: {e}")
        return False

    # 20x20 array of doubles (20*20*8 = 3200 bytes) - exceeds per-array limit
    try:
        limits.allocate_array("C", [19, 19], TypeInfo.DOUBLE)
        print("  ✗ Should have raised error for 20x20 array")
        return False
    except RuntimeError as e:
        if "Array C too large" in str(e) and "3200 bytes" in str(e):
            print(f"  ✓ Correctly raised error: {e}")
        else:
            print(f"  ✗ Wrong error message: {e}")
            return False

    print("✓ Multi-dimensional array test passed\n")
    return True


def test_memory_size_estimation():
    """Test memory size estimation for different types"""
    print("Testing memory size estimation:")

    limits = ResourceLimits()

    # Test INTEGER
    size = limits.estimate_size(42, TypeInfo.INTEGER)
    assert size == 2
    print("  ✓ INTEGER: 2 bytes")

    # Test SINGLE
    size = limits.estimate_size(3.14, TypeInfo.SINGLE)
    assert size == 4
    print("  ✓ SINGLE: 4 bytes")

    # Test DOUBLE
    size = limits.estimate_size(2.718, TypeInfo.DOUBLE)
    assert size == 8
    print("  ✓ DOUBLE: 8 bytes")

    # Test STRING
    size = limits.estimate_size("Hello", TypeInfo.STRING)
    assert size == 9  # 5 bytes + 4 overhead
    print("  ✓ STRING 'Hello': 9 bytes (5 + 4 overhead)")

    # Test empty STRING
    size = limits.estimate_size("", TypeInfo.STRING)
    assert size == 4  # Just overhead
    print("  ✓ Empty STRING: 4 bytes")

    print("✓ Memory size estimation test passed\n")
    return True


def run_all_tests():
    """Run all tests and report results"""
    tests = [
        test_gosub_stack_tracking,
        test_for_loop_tracking,
        test_while_loop_tracking,
        test_array_allocation,
        test_variable_allocation,
        test_string_length_limit,
        test_execution_time_limit,
        test_usage_report,
        test_preset_configurations,
        test_multidimensional_arrays,
        test_memory_size_estimation,
    ]

    print("=" * 60)
    print("RESOURCE LIMITS TEST SUITE")
    print("=" * 60)
    print()

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"✗ Test {test.__name__} crashed: {e}\n")
            failed += 1

    print("=" * 60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
