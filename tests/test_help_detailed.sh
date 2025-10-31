#!/bin/bash
# Detailed test of help menu behavior

cat > /tmp/test_help.bas << 'EOF'
10 PRINT "Hello World"
EOF

# Use expect with full logging to see what happens
expect -d << 'EXPECT_EOF' 2>&1 | grep -E "(send|expect|Help|Ctrl|OK|exit)"
set timeout 10
spawn python3 mbasic --backend curses /tmp/test_help.bas

# Wait for UI to load
sleep 2

# Open menu with Ctrl+X
puts ">>> Sending Ctrl+X to open menu"
send "\x18"
sleep 0.5

# Navigate to Help
puts ">>> Navigating to Help menu item"
send "\t\t\t\t\t"
sleep 0.3

puts ">>> Pressing Enter to open Help"
send "\r"
sleep 1

puts ">>> Help should be open now"
puts ">>> Attempting Ctrl+C to close help"
send "\x03"
sleep 2

puts ">>> Checking if we're back at main screen"
# If we're back, pressing Tab should move focus
send "\t"
sleep 0.5

puts ">>> Trying Ctrl+Q to exit"
send "\x11"
sleep 0.5

expect eof
catch wait result
puts ">>> Exit status: [lindex $result 3]"
EXPECT_EOF
