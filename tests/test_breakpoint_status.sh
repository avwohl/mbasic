#!/bin/bash
# Test breakpoint with status line (no popup)

cat > /tmp/test_bp_status.bas << 'EOF'
10 PRINT "Line 10"
20 PRINT "Line 20"
30 PRINT "Line 30"
40 PRINT "Line 40"
EOF

echo "Testing breakpoint with status line..."
echo ""
echo "Instructions:"
echo "1. Press 'b' to toggle breakpoint on line 20"
echo "2. Press ^R to run"
echo "3. Status line should show 'BREAKPOINT at line 20'"
echo "4. Press 'c' to continue"
echo "5. Press ^Q to quit"
echo ""

timeout 15 expect << 'EXPECT_EOF' 2>&1 | tee /tmp/bp_status_test.log
log_user 1
set timeout 5

spawn python3 mbasic --backend curses /tmp/test_bp_status.bas
sleep 1

# Move to line 2 (line 20)
send "\033\[B"
sleep 0.3

# Toggle breakpoint
send "b"
sleep 0.5

# Run program
send "\x12"
sleep 2

# Continue from breakpoint
send "c"
sleep 1

# Exit
send "\x11"

expect eof
EXPECT_EOF

echo ""
echo "=== Test Results ==="
if grep -q "BREAKPOINT" /tmp/bp_status_test.log; then
    echo "✓ Breakpoint status appeared"
else
    echo "✗ Breakpoint status did not appear"
fi

if grep -q "Line 10" /tmp/bp_status_test.log && grep -q "Line 20" /tmp/bp_status_test.log; then
    echo "✓ Program executed"
else
    echo "✗ Program did not execute properly"
fi
