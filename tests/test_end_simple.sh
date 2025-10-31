#!/bin/bash
# Simple manual test for end command

# Create test program
cat > test_end_manual.bas <<EOF
10 PRINT "Line 10"
20 PRINT "Line 20 - BREAKPOINT"
30 PRINT "Line 30"
40 PRINT "Done!"
EOF

echo "==================================="
echo "MANUAL TEST: End Command"
echo "==================================="
echo ""
echo "Test program created: test_end_manual.bas"
echo ""
echo "Instructions:"
echo "1. Press DOWN ARROW to move to line 20"
echo "2. Press 'b' to set a breakpoint"
echo "3. Press Ctrl+R to run"
echo "4. When it pauses at line 20, press 'e' to end"
echo "5. You should see:"
echo "   - Output window shows 'Line 10' and 'Line 20'"
echo "   - Output window shows '*** Execution stopped by user ***'"
echo "   - Output window does NOT show 'Line 30' or 'Done!'"
echo "6. Press Ctrl+Q to quit"
echo ""
echo "Press ENTER to start..."
read

# Run with stderr redirected to a file
python3 mbasic --backend curses test_end_manual.bas 2>test_end_manual_stderr.log

echo ""
echo "==================================="
echo "STDERR OUTPUT:"
echo "==================================="
cat test_end_manual_stderr.log

echo ""
echo "Test complete!"
