#!/bin/bash
# Manual test for breakpoint system

cat > /tmp/test_bp_manual.bas << 'EOF'
10 PRINT "Line 10"
20 PRINT "Line 20"
30 PRINT "Line 30"
40 PRINT "Line 40"
50 PRINT "Line 50"
EOF

echo "========================================="
echo "Breakpoint System Manual Test"
echo "========================================="
echo ""
echo "This program will open the IDE with a test program."
echo ""
echo "To test breakpoints:"
echo ""
echo "1. SET BREAKPOINT:"
echo "   - Move cursor to line 20"
echo "   - Press 'b' or F9"
echo "   - OR click left of the line number"
echo "   - You should see ● appear before line number"
echo ""
echo "2. RUN PROGRAM:"
echo "   - Press Ctrl+R"
echo "   - Program should stop at line 20"
echo "   - Screen shows breakpoint dialog with:"
echo "     * Header: BREAKPOINT HIT"
echo "     * Which line stopped"
echo "     * Program context (2 lines before/after)"
echo "     * >>> points to current line"
echo ""
echo "3. CONTINUE:"
echo "   - Press 'c' to continue"
echo "   - Program should complete and show all output"
echo ""
echo "4. EXIT:"
echo "   - Press Ctrl+Q"
echo ""
echo "Press Enter to start..."
read

python3 mbasic --backend curses /tmp/test_bp_manual.bas
