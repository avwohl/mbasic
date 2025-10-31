#!/bin/bash
# Simple breakpoint test - set breakpoint on first line

cat > /tmp/test_bp_simple.bas << 'EOF'
10 PRINT "Line 10"
20 PRINT "Line 20"
30 PRINT "Line 30"
EOF

echo "Simple breakpoint test..."
timeout 15 expect << 'EXPECT_EOF' 2>&1 | tee /tmp/bp_simple_test.log
log_user 1
set timeout 5

spawn python3 mbasic --backend curses /tmp/test_bp_simple.bas
sleep 1

# Toggle breakpoint on current line (line 10)
send "b"
sleep 1

# Run program - should stop at line 10
send "\x12"
sleep 2

# Continue
send "c"
sleep 1

# Exit
send "\x11"

expect eof
EXPECT_EOF

echo ""
if grep -q "BREAKPOINT" /tmp/bp_simple_test.log; then
    echo "✓ Breakpoint triggered"
else
    echo "✗ Breakpoint did not trigger"
fi
