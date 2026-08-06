10 REM Test MERGE Statement
20 REM MERGE returns to command level on MBASIC 5.21, so
30 REM nothing after line 130 runs on the real binary.
40 REM The KILL on 140 is what tidies up here, where
50 REM execution does carry on; both print nothing, so
60 REM the two engines produce the same output.
70 PRINT "Testing MERGE"
80 PRINT "============="
90 PRINT
100 PRINT "Test 1: MERGE an overlay program"
110 OPEN "O", 1, "MRGOVL.BAS"
120 PRINT #1, "1000 PRINT ""In the merged subroutine"""
130 PRINT #1, "1010 RETURN"
140 PRINT #1, "2000 PRINT ""In the second merged subroutine"""
150 PRINT #1, "2010 RETURN"
160 CLOSE 1
170 PRINT "Overlay written: lines 1000-2010"
180 MERGE "MRGOVL.BAS"
190 KILL "MRGOVL.BAS"
200 END
