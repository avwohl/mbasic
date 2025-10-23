10 REM Sequential I/O LOC/LOF test
20 PRINT "=== Sequential LOC/LOF Test ==="
30 PRINT
40 PRINT "Test 1: Output file"
50 OPEN "O", 1, "OUT.DAT"
60 PRINT "After OPEN O: LOC(1)="; LOC(1); " LOF(1)="; LOF(1)
70 PRINT #1, "Line 1"
80 PRINT "After PRINT#: LOC(1)="; LOC(1); " LOF(1)="; LOF(1)
90 PRINT #1, "Line 2"
100 PRINT "After 2nd PRINT#: LOC(1)="; LOC(1); " LOF(1)="; LOF(1)
110 CLOSE #1
120 PRINT
130 PRINT "Test 2: Input file"
140 OPEN "I", 1, "OUT.DAT"
150 PRINT "After OPEN I: LOC(1)="; LOC(1); " LOF(1)="; LOF(1)
160 LINE INPUT #1, L$
170 PRINT "After 1st read: LOC(1)="; LOC(1); " LOF(1)="; LOF(1)
180 PRINT "  Read: ["; L$; "]"
190 LINE INPUT #1, L$
200 PRINT "After 2nd read: LOC(1)="; LOC(1); " LOF(1)="; LOF(1)
210 PRINT "  Read: ["; L$; "]"
220 PRINT "  EOF(1)="; EOF(1)
230 CLOSE #1
240 PRINT
250 PRINT "Test 3: Append mode"
260 OPEN "A", 1, "OUT.DAT"
270 PRINT "After OPEN A: LOC(1)="; LOC(1); " LOF(1)="; LOF(1)
280 PRINT #1, "Line 3"
290 PRINT "After append: LOC(1)="; LOC(1); " LOF(1)="; LOF(1)
300 CLOSE #1
310 PRINT
320 PRINT "=== Test complete ==="
330 END
