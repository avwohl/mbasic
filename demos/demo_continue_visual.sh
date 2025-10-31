#!/bin/bash

# Visual demonstration of the continue feature
# This script explains what happens at each step

clear
cat << 'EOF'
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║        MBASIC DEBUGGER - CONTINUE FEATURE DEMO              ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

This demonstration will show you how the 'c' (continue) command
works in the MBASIC debugger.

SCENARIO: You're debugging a program with three phases.
          You want to verify each phase starts correctly,
          but you don't need to see every line execute.

THE PROGRAM:
════════════════════════════════════════════════════════════════
 100 PRINT "PHASE 1: Initialization"
 110 PRINT "Setting up variables..."
 120 LET X = 10
 130 LET Y = 20
 140 LET Z = 30
 150 PRINT "Variables: X="; X; " Y="; Y; " Z="; Z
 160 PRINT "Phase 1 complete!"

 200 PRINT "PHASE 2: Calculations"
 210 PRINT "Computing sum..."
 220 LET SUM = X + Y + Z
 230 PRINT "Sum = "; SUM
 240 PRINT "Computing product..."
 250 LET PROD = X * Y
 260 PRINT "Product = "; PROD
 270 PRINT "Phase 2 complete!"

 300 PRINT "PHASE 3: Loop demonstration"
 310 PRINT "Counting from 1 to 5..."
 320 FOR I = 1 TO 5
 330   PRINT "  Count: "; I
 340 NEXT I
 350 PRINT "Phase 3 complete!"
════════════════════════════════════════════════════════════════

DEBUGGING STRATEGY:
───────────────────────────────────────────────────────────────
Set breakpoints at the START of each phase (lines 100, 200, 300)
Use 'c' (continue) to jump from phase to phase
This lets you verify each phase begins, without stepping through
every single line!

WHAT YOU'LL DO:
───────────────────────────────────────────────────────────────
Step 1: Set breakpoints
   • Cursor to line 100, press 'b'  → See ● appear
   • Cursor to line 200, press 'b'  → See ● appear
   • Cursor to line 300, press 'b'  → See ● appear

Step 2: Run the program
   • Press Ctrl+R
   • Program stops at line 100
   • Status shows: "BREAKPOINT at line 100 - Press 'c' continue..."

Step 3: Continue to next checkpoint
   • Press 'c'
   • Lines 100-160 execute (you see "Phase 1 complete!")
   • Program stops at line 200
   • Status shows: "BREAKPOINT at line 200..."

Step 4: Continue to next checkpoint
   • Press 'c'
   • Lines 200-270 execute (you see "Phase 2 complete!")
   • Program stops at line 300
   • Status shows: "BREAKPOINT at line 300..."

Step 5: Continue to end
   • Press 'c'
   • Lines 300-350 execute (you see loop output)
   • Program completes
   • Output window shows all three phases!

Step 6: Exit
   • Press Ctrl+Q to quit

THE MAGIC:
───────────────────────────────────────────────────────────────
Without 'c' (continue), you'd have to:
   • Press 's' 29 times to step through all lines, OR
   • Let program run without any control

With 'c' (continue), you get:
   • Stop at strategic checkpoints
   • Verify phase transitions
   • Skip over routine code
   • Full control with minimal effort

ALTERNATIVE: What if Phase 2 had a bug?
───────────────────────────────────────────────────────────────
At line 200 (start of Phase 2):
   • Press 's' instead of 'c'
   • Step through lines 200, 210, 220, 230... one at a time
   • Watch variables and output carefully
   • When you find the bug, press 'e' to end
   • Fix the code and run again!

READY TO TRY IT?
───────────────────────────────────────────────────────────────
EOF

echo
echo -n "Press ENTER to launch the IDE with demo program..."
read

# Launch the actual IDE
python3 mbasic --backend curses demo_continue.bas

# After they exit
clear
cat << 'EOF'
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║                   DEMO COMPLETE!                             ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

What you just experienced:
───────────────────────────────────────────────────────────────
✓ Setting multiple breakpoints with 'b'
✓ Running with Ctrl+R
✓ Using 'c' to continue between breakpoints
✓ Seeing checkpoint output in the output window
✓ Full control over program flow

KEY TAKEAWAYS:
───────────────────────────────────────────────────────────────
1. 'c' (continue) is the fastest way to jump between points
   of interest in your program

2. Combine 'c' with 's' (step): continue to problem area,
   then step through it carefully

3. Set breakpoints liberally - you can always skip them
   with 'c', but you can't add them while running

4. The output window accumulates all output, so you can see
   what happened between breakpoints

NEXT STEPS:
───────────────────────────────────────────────────────────────
• Try with your own programs!
• Read DEBUGGER_COMMANDS.md for full command reference
• Read CONTINUE_FEATURE.md for advanced techniques
• Read QUICK_REFERENCE.md for all IDE shortcuts

Happy debugging! 🐛🔍

EOF
