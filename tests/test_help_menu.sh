#!/bin/bash
# Test help menu in curses UI

cat > /tmp/test_help.bas << 'EOF'
10 PRINT "Hello World"
EOF

# Use expect to test the help menu
expect << 'EXPECT_EOF'
set timeout 10
spawn python3 mbasic --backend curses /tmp/test_help.bas

# Wait for UI to load
sleep 2

# Try to access menu (Ctrl+X activates menu in npyscreen)
send "\x18"
sleep 0.5

# Navigate to Help and select it
send "\t\t"
sleep 0.5
send "\r"
sleep 0.5

# Capture any error output
expect {
    "Error" {
        puts "ERROR FOUND"
        send "\r"
        sleep 0.5
    }
    "Help" {
        puts "Help dialog opened"
        sleep 0.5
    }
    timeout {
        puts "Timeout waiting for help"
    }
}

# Try Ctrl+C to close
send "\x03"
sleep 1

# Exit with Ctrl+Q
send "\x11"

expect eof
catch wait result
set exit_status [lindex $result 3]
puts "Exit status: $exit_status"
exit $exit_status
EXPECT_EOF
