#!/bin/bash
# Test help menu and capture any Python errors

cat > /tmp/test_help.bas << 'EOF'
10 PRINT "Test"
EOF

echo "=== Test 1: Opening help from menu ==="
timeout 10 expect << 'EXPECT_EOF' 2>&1 | tee /tmp/help_test.log
log_user 1
set timeout 5

spawn python3 -u mbasic --backend curses /tmp/test_help.bas
sleep 2

# Open menu
send "\x18"
sleep 0.5

# Navigate to Help (5 tabs to get there)
send "\t\t\t\t\t"
sleep 0.5

# Select Help
send "\r"
sleep 2

# Exit
send "\x03\x11"
expect eof
EXPECT_EOF

if grep -i "AttributeError\|splitlines\|Exception\|Traceback" /tmp/help_test.log; then
    echo "✗ MENU HELP FAILED - errors above"
    exit 1
else
    echo "✓ Menu help opened without errors"
fi

echo ""
echo "=== Test 2: Using ^P shortcut ==="
timeout 10 expect << 'EXPECT_EOF' 2>&1 | tee /tmp/help_ctrlp_test.log
log_user 1
set timeout 5

spawn python3 -u mbasic --backend curses /tmp/test_help.bas
sleep 2

# Try Ctrl+P
send "\x10"
sleep 2

# Exit
send "\x03\x11"
expect eof
EXPECT_EOF

if grep -i "AttributeError\|Exception\|Traceback" /tmp/help_ctrlp_test.log; then
    echo "✗ ^P HELP FAILED - errors above"
    exit 1
else
    echo "✓ ^P help worked without errors"
fi

echo ""
echo "=== All tests passed ==="
