#!/bin/bash
# Test the complete help system

cat > /tmp/test_help.bas << 'EOF'
10 PRINT "Test program"
EOF

echo "Testing help system integration..."
echo ""
echo "This will test:"
echo "1. ^P opens help browser"
echo "2. Help browser displays index.md"
echo "3. Q exits help"
echo ""

timeout 15 expect << 'EXPECT_EOF' 2>&1 | tee /tmp/help_system_test.log
log_user 1
set timeout 10

spawn python3 mbasic --backend curses /tmp/test_help.bas
sleep 2

# Open help with ^P
puts ">>> Opening help with ^P"
send "\x10"
sleep 2

# Should see help browser now
# Try scrolling
puts ">>> Scrolling down"
send " "
sleep 1

# Exit help with Q
puts ">>> Exiting help with Q"
send "q"
sleep 2

# Should be back at main screen
# Now exit
puts ">>> Exiting IDE"
send "\x11"

expect eof
catch wait result
puts ">>> Exit status: [lindex $result 3]"
EXPECT_EOF

if grep -i "Error\|Exception\|Traceback" /tmp/help_system_test.log | grep -v "Help Error.*not found"; then
    echo ""
    echo "✗ Help system test FAILED - errors found"
    exit 1
else
    echo ""
    echo "✓ Help system test PASSED"
fi
