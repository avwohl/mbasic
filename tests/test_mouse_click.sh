#!/bin/bash
# Test mouse click on breakpoint character

cat > /tmp/test_mouse.bas << 'EOF'
10 PRINT "Line 10"
20 PRINT "Line 20"
30 PRINT "Line 30"
40 PRINT "Line 40"
EOF

echo "Testing mouse click on breakpoint character..."
echo ""
echo "This test requires manual interaction:"
echo "1. The program will start"
echo "2. Try clicking on the space before line 10 (where ● would appear)"
echo "3. It should toggle a breakpoint (● appears/disappears)"
echo "4. Try clicking on other lines"
echo "5. Press Ctrl+Q to quit"
echo ""
echo "Starting in 3 seconds..."
sleep 3

python3 mbasic --backend curses /tmp/test_mouse.bas

echo ""
echo "Mouse click test completed!"
