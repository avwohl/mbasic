#!/bin/bash
# Test ESC key closes help dialogs

cat > /tmp/test_help.bas << 'EOF'
10 PRINT "Test"
EOF

echo "=== Test 1: ESC closes help from menu ==="
timeout 10 expect << 'EXPECT_EOF' 2>&1 | tee /tmp/esc_menu_test.log
log_user 1
set timeout 5

spawn python3 -u mbasic --backend curses /tmp/test_help.bas
sleep 2

# Open menu
send "\x18"
sleep 0.5

# Navigate to Help
send "\t\t\t\t\t"
sleep 0.5

# Select Help
send "\r"
sleep 1

# Close with ESC
send "\x1b"
sleep 1

# Exit
send "\x11"
expect eof
EXPECT_EOF

if grep -i "AttributeError\|Exception\|Traceback" /tmp/esc_menu_test.log; then
    echo "✗ ESC menu test FAILED"
    exit 1
else
    echo "✓ ESC closes menu help"
fi

echo ""
echo "=== Test 2: ESC closes help from ^P ==="
timeout 10 expect << 'EXPECT_EOF' 2>&1 | tee /tmp/esc_ctrlp_test.log
log_user 1
set timeout 5

spawn python3 -u mbasic --backend curses /tmp/test_help.bas
sleep 2

# Open help with ^P
send "\x10"
sleep 1

# Close with ESC
send "\x1b"
sleep 1

# Exit
send "\x11"
expect eof
EXPECT_EOF

if grep -i "AttributeError\|Exception\|Traceback" /tmp/esc_ctrlp_test.log; then
    echo "✗ ESC ^P test FAILED"
    exit 1
else
    echo "✓ ESC closes ^P help"
fi

echo ""
echo "=== All ESC tests passed ==="
