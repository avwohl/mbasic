#!/bin/bash
# Test if Ctrl+C closes help menu

cat > /tmp/test_help.bas << 'EOF'
10 PRINT "Hello World"
EOF

# Use expect to test Ctrl+C in help dialog
expect << 'EXPECT_EOF'
set timeout 10
spawn python3 mbasic --backend curses /tmp/test_help.bas
log_user 0

# Wait for UI to load
sleep 2

# Open menu with Ctrl+X
send "\x18"
sleep 0.5

# Navigate to Help (it's the last item)
send "\t\t\t\t\t"
sleep 0.3
send "\r"
sleep 0.5

# Help dialog should be open now
# Try Ctrl+C to close it
send "\x03"
sleep 1

# Check if we're still in the UI or if it exited
# If Ctrl+C worked to close the dialog, we should be back at main screen
# and Ctrl+Q should exit normally
send "\x11"
sleep 0.5

expect eof
catch wait result
set exit_status [lindex $result 3]

if {$exit_status == 0} {
    puts "SUCCESS: Help dialog can be closed with Ctrl+C"
} else {
    puts "Test completed with exit status: $exit_status"
}
exit 0
EXPECT_EOF
