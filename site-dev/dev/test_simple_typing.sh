#!/bin/bash
# Simple test - just type two lines

echo "Starting mbasic in curses mode..."
echo "Will type two lines and then quit"
echo ""

# Create a script to send keystrokes
(
    sleep 1
    # Type first line
    echo -n '10 PRINT "a"'
    sleep 0.2
    echo ""  # Enter
    sleep 0.5
    # Type second line
    echo -n '20 PRINT "b"'
    sleep 0.2
    echo ""  # Enter
    sleep 1
    # List
    echo "LIST"
    sleep 1
    # Quit
    echo -n $'\x11'  # Ctrl+Q
) | python3 mbasic --ui curses

echo ""
echo "Test complete"
