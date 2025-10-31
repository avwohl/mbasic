#!/bin/bash

# Test breakpoints with debug output

echo "Testing breakpoints with DEBUG_BP enabled"
echo "=========================================="
echo
echo "Test program (test_continue.bas):"
cat test_continue.bas
echo
echo "=========================================="
echo "Instructions:"
echo "1. IDE will open"
echo "2. Set breakpoint on line 20 (move cursor to line 20, press 'b')"
echo "   - You should see ● appear"
echo "3. Press Ctrl+R to run"
echo "4. Watch terminal for debug output showing:"
echo "   - [BP_CHECK] messages for each line"
echo "   - [BP_HIT] when breakpoint is reached"
echo "   - [BP_RESULT] showing what callback returned"
echo "5. If breakpoint triggers, press 'c' to continue"
echo "6. Press Ctrl+Q to quit"
echo
echo "Debug output will be saved to /tmp/bp_debug.log"
echo
echo "Press ENTER to start..."
read

DEBUG_BP=1 python3 mbasic --backend curses test_continue.bas 2> /tmp/bp_debug.log

echo
echo "Test complete. Debug output:"
echo "=========================================="
cat /tmp/bp_debug.log
echo "=========================================="
echo
echo "Analysis:"
if grep -q "\[BP_HIT\]" /tmp/bp_debug.log; then
    echo "✓ Breakpoint was HIT!"
    grep "\[BP" /tmp/bp_debug.log
else
    echo "✗ Breakpoint was NOT hit"
    echo
    echo "Checking what happened:"
    if grep -q "\[BP_CHECK\]" /tmp/bp_debug.log; then
        echo "  - Lines were checked for breakpoints"
        echo "  - Breakpoint info:"
        grep "breakpoints=" /tmp/bp_debug.log | head -3
    else
        echo "  - NO breakpoint checking happened at all!"
        echo "  - This means breakpoint callback wasn't set up"
    fi
fi
