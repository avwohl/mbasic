#!/bin/bash
# Test both help fixes: ^P shortcut and menu-based help

cat > /tmp/test_help.bas << 'EOF'
10 PRINT "Hello World"
EOF

echo "=== Test 1: Opening help from menu ==="
expect << 'EXPECT_EOF'
set timeout 10
spawn python3 mbasic --backend curses /tmp/test_help.bas

# Wait for UI to load
sleep 2

# Open menu with Ctrl+X
send "\x18"
sleep 0.5

# Navigate to Help
send "\t\t\t\t\t"
sleep 0.3

# Open help
send "\r"
sleep 1

# Try to close with Ctrl+C
send "\x03"
sleep 1

# Exit
send "\x11"

expect eof
catch wait result
set exit_status [lindex $result 3]
exit $exit_status
EXPECT_EOF

if [ $? -eq 0 ]; then
    echo "✓ Test 1 PASSED: Menu help works"
else
    echo "✗ Test 1 FAILED: Menu help has errors"
    exit 1
fi

echo ""
echo "=== Test 2: Opening help with ^P shortcut ==="
expect << 'EXPECT_EOF'
set timeout 10
spawn python3 mbasic --backend curses /tmp/test_help.bas

# Wait for UI to load
sleep 2

# Try Ctrl+P to open help directly
send "\x10"
sleep 1

# Close with Ctrl+C
send "\x03"
sleep 1

# Exit
send "\x11"

expect eof
catch wait result
set exit_status [lindex $result 3]
exit $exit_status
EXPECT_EOF

if [ $? -eq 0 ]; then
    echo "✓ Test 2 PASSED: ^P shortcut works"
else
    echo "✗ Test 2 FAILED: ^P shortcut has errors"
    exit 1
fi

echo ""
echo "=== All tests passed! ==="
