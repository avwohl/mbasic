#!/bin/bash

echo "=========================================="
echo "CLEAR BREAKPOINT TEST"
echo "=========================================="
echo
echo "I will launch the IDE."
echo "Please do these steps:"
echo
echo "1. Look at the screen - can you see BASIC code?"
echo "2. Press 'b' (just the letter b)"
echo "3. Look for a black dot (●) next to line 10"
echo "4. Press Ctrl+R (hold Ctrl and press R)"
echo "5. Look at the bottom of the screen for output"
echo "6. Press Ctrl+Q to quit"
echo
echo "Then I'll show you the debug log."
echo
read -p "Press ENTER to start the IDE..."
echo

# Run with debug
DEBUG_BP=1 python3 mbasic --backend curses test_continue.bas 2> /tmp/clear_test.log

echo
echo "=========================================="
echo "DEBUG LOG CONTENTS:"
echo "=========================================="
cat /tmp/clear_test.log
echo "=========================================="
echo
echo "PLEASE COPY AND PASTE EVERYTHING ABOVE THIS LINE"
