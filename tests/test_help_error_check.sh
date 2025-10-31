#!/bin/bash
# Test if help menu shows any error

cat > /tmp/test_help.bas << 'EOF'
10 PRINT "Hello World"
EOF

# Run with Python error tracebacks visible
expect << 'EXPECT_EOF' 2>&1 | tee /tmp/help_test_output.txt
set timeout 10
spawn python3 -u mbasic --backend curses /tmp/test_help.bas
log_user 1

# Wait for UI to load
sleep 2

# Open menu
send "\x18"
sleep 0.5

# Navigate to Help (down arrow through menu items)
send "\t\t\t\t\t"
sleep 0.3

# Select Help
send "\r"
sleep 2

# Close with Enter (the expected way)
send "\r"
sleep 1

# Exit
send "\x11"

expect eof
EXPECT_EOF

# Check for errors in the output
if grep -q "Error\|Traceback\|Exception" /tmp/help_test_output.txt; then
    echo "=== ERRORS FOUND ==="
    grep -A 5 "Error\|Traceback\|Exception" /tmp/help_test_output.txt
else
    echo "No errors found in help menu"
fi
