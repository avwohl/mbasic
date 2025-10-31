#!/bin/bash
# Test that the menu structure has been updated

cat > /tmp/test_menu.bas << 'EOF'
10 PRINT "Testing menu"
20 PRINT "Hello World"
EOF

echo "Testing menu structure..."
echo ""
echo "This test will:"
echo "1. Start the IDE"
echo "2. Open the menu with Ctrl+X"
echo "3. You should see: New, Load, Save, Quit, Run Program, List, Help"
echo "4. All items should be at the top level (no Run submenu)"
echo "5. Press ESC to close menu"
echo "6. Press Ctrl+Q to quit"
echo ""
echo "Starting in 3 seconds..."
sleep 3

python3 mbasic --backend curses /tmp/test_menu.bas

echo ""
echo "Menu structure test completed!"
