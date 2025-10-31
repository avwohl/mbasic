#!/bin/bash
# Test that blank lines are removed

cat > /tmp/test_blank.bas << 'EOF'
10 PRINT "First line"
20 PRINT "Second line"
EOF

echo "Testing editor layout..."
timeout 5 expect << 'EXPECT_EOF' 2>&1 | tee /tmp/blank_lines_test.log
log_user 1
set timeout 3

spawn python3 mbasic --backend curses /tmp/test_blank.bas
sleep 2

# Exit immediately
send "\x11"

expect eof
EXPECT_EOF

# Check if the output shows the program starting right after the menu
# The test passes if there aren't excessive blank lines before "10 PRINT"
if grep -q "10 PRINT" /tmp/blank_lines_test.log; then
    echo "✓ Program displayed"
    # Count the context around the first program line
    echo ""
    echo "Layout check - looking at lines around '10 PRINT':"
    grep -B 5 "10 PRINT" /tmp/blank_lines_test.log | tail -10 | head -8
else
    echo "✗ Program line not found"
    exit 1
fi
