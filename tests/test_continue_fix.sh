#!/bin/bash

# Quick test for the continue fix
# This tests that the screen stays visible during breakpoint

echo "Testing Continue Feature - Screen Display Fix"
echo "=============================================="
echo
echo "Test program:"
cat test_continue.bas
echo
echo "=============================================="
echo "Instructions:"
echo "1. IDE will open with the test program"
echo "2. Set a breakpoint on line 20 (cursor to line 20, press 'b')"
echo "3. Press Ctrl+R to run"
echo "4. When breakpoint hits, you should SEE:"
echo "   - Your program code in the editor"
echo "   - Status line at top: 'BREAKPOINT at line 20...'"
echo "   - NOT a blank screen!"
echo "5. Press 'c' to continue"
echo "6. Check output window for results"
echo "7. Press Ctrl+Q to quit"
echo
echo "Press ENTER to start..."
read

python3 mbasic --backend curses test_continue.bas 2> /tmp/mbasic_debug.log

echo
echo "Test complete!"
echo
echo "Debug log (if any errors):"
cat /tmp/mbasic_debug.log 2>/dev/null || echo "(no errors)"
