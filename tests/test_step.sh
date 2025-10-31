#!/bin/bash
# Test step mode

cat > /tmp/test_step.bas << 'EOF'
10 PRINT "Line 10"
20 PRINT "Line 20"
30 PRINT "Line 30"
40 PRINT "Line 40"
EOF

echo "Testing step mode..."
timeout 20 expect << 'EXPECT_EOF' 2>&1 | tee /tmp/step_test.log
log_user 1
set timeout 5

spawn python3 mbasic --backend curses /tmp/test_step.bas
sleep 1

# Set breakpoint on line 10
send "b"
sleep 0.5

# Run program
send "\x12"
sleep 1

# Should hit breakpoint at line 10
# Press 's' to step
send "s"
sleep 1

# Should now be at line 20 (stepped)
# Press 's' again to step
send "s"
sleep 1

# Should now be at line 30
# Press 'c' to continue to end
send "c"
sleep 1

# Exit
send "\x11"

expect eof
EXPECT_EOF

echo ""
echo "=== Test Results ==="
if grep -q "BREAKPOINT" /tmp/step_test.log; then
    echo "✓ Breakpoint system working"
else
    echo "✗ Breakpoint not detected"
fi

echo ""
echo "Step mode test completed!"
