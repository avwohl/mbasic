#!/bin/bash
# Test breakpoint system

cat > /tmp/test_breakpoint.bas << 'EOF'
10 PRINT "Line 10"
20 PRINT "Line 20"
30 PRINT "Line 30"
40 PRINT "Line 40"
EOF

echo "Testing breakpoint system..."
echo ""
echo "Instructions:"
echo "1. Press 'b' or F9 to toggle breakpoint on line 20"
echo "2. Press ^R to run"
echo "3. When breakpoint hits, press 'c' to continue or 's' to stop"
echo "4. Press ^Q to quit"
echo ""

python3 mbasic --backend curses /tmp/test_breakpoint.bas
