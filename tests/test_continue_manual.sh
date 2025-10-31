#!/bin/bash

# Manual test for continue functionality
# This demonstrates the 'c' (continue) command in the breakpoint debugger

echo "=========================================="
echo "Testing CONTINUE functionality"
echo "=========================================="
echo
echo "This test will run a BASIC program with multiple breakpoints."
echo "You'll practice using the 'c' (continue) command."
echo
echo "Test Program:"
cat test_continue.bas
echo
echo "=========================================="
echo "INSTRUCTIONS:"
echo "=========================================="
echo "1. The program will open in the curses IDE"
echo "2. Set breakpoints on lines 20 and 40:"
echo "   - Move cursor to line 20, press 'b'"
echo "   - Move cursor to line 40, press 'b'"
echo "   - You should see '●' markers appear"
echo "3. Press Ctrl+R to run"
echo "4. When it stops at line 20:"
echo "   - Status line says: 'BREAKPOINT at line 20 - Press c continue, s step, e end'"
echo "   - Press 'c' to CONTINUE to next breakpoint"
echo "5. When it stops at line 40:"
echo "   - Press 'c' again to continue to completion"
echo "6. Check output window - should see all PRINT statements"
echo "7. Press Ctrl+Q to quit"
echo
echo "Press ENTER to start the test..."
read

python3 mbasic --backend curses test_continue.bas
