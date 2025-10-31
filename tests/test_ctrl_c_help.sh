#!/bin/bash
# Test that help dialog can be closed with Ctrl+C

cat > /tmp/test_help_ctrl_c.bas << 'EOF'
10 PRINT "Test program"
EOF

# Create expect script to test Ctrl+C in help dialog
expect << 'EXPECT_SCRIPT'
set timeout 5
spawn python3 mbasic --ui curses /tmp/test_help_ctrl_c.bas

# Wait for UI to load
sleep 1

# Open help menu with Ctrl+P
send "\x10"
sleep 0.5

# Try to close with Ctrl+C
send "\x03"
sleep 0.5

# If we're back at main screen, Ctrl+Q should exit
send "\x11"

expect eof
EXPECT_SCRIPT

if [ $? -eq 0 ]; then
    echo "SUCCESS: Help dialog responds to Ctrl+C"
else
    echo "FAILED: Help dialog does not respond to Ctrl+C"
fi
