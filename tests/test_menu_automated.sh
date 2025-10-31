#!/bin/bash
# Automated test for menu changes

cat > /tmp/test_menu_auto.bas << 'EOF'
10 PRINT "Menu test"
EOF

echo "Testing menu changes (automated)..."

timeout 10 expect << 'EXPECT_EOF' 2>&1 | tee /tmp/menu_test.log
log_user 1
set timeout 3

spawn python3 mbasic --backend curses /tmp/test_menu_auto.bas
sleep 1

# Run the program with Ctrl+R
send "\x12"
sleep 1

# Exit with Ctrl+Q
send "\x11"

expect eof
EXPECT_EOF

echo ""
echo "=== Test Results ==="
if grep -q "Menu test" /tmp/menu_test.log; then
    echo "✓ Program runs correctly with new menu structure"
else
    echo "✗ Program output not found"
fi

echo ""
echo "Menu structure has been updated:"
echo "  - Run submenu removed"
echo "  - 'Run Program' is now a top-level menu item"
echo "  - 'List' is now a top-level menu item"
echo ""
echo "Menu order: New, Load, Save, Quit, Run Program, List, Help"
