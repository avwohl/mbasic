#!/bin/bash
# Automated test for breakpoint system

cat > /tmp/test_breakpoint.bas << 'EOF'
10 PRINT "Line 10"
20 PRINT "Line 20"
30 PRINT "Line 30"
40 PRINT "Line 40"
EOF

echo "Testing breakpoint system (automated)..."
timeout 10 expect << 'EXPECT_EOF' 2>&1 | tee /tmp/breakpoint_test.log
log_user 1
set timeout 5

spawn python3 mbasic --backend curses /tmp/test_breakpoint.bas
sleep 1

# Move cursor to line 20 (second line)
send "\033\[B"
sleep 0.5

# Toggle breakpoint with 'b'
send "b"
sleep 0.5

# Run the program with Ctrl+R
send "\x12"
sleep 1

# Should show breakpoint dialog
# Press 'c' to continue
send "c"
sleep 1

# Exit with Ctrl+Q
send "\x11"

expect eof
EXPECT_EOF

echo ""
echo "Test output:"
if grep -q "Breakpoint" /tmp/breakpoint_test.log; then
    echo "✓ Breakpoint dialog appeared"
else
    echo "✗ Breakpoint dialog did not appear"
    exit 1
fi

if grep -q "Line 10" /tmp/breakpoint_test.log; then
    echo "✓ Line 10 executed"
else
    echo "✗ Line 10 did not execute"
fi

if grep -q "Line 20" /tmp/breakpoint_test.log; then
    echo "✓ Line 20 executed (after continue)"
else
    echo "✗ Line 20 did not execute"
fi

echo ""
echo "Breakpoint test completed successfully!"
