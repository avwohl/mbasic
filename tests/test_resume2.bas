10 REM Test RESUME (retry)
20 ON ERROR GOTO 1000
30 PRINT "Enter 1 to test RESUME, 2 for RESUME NEXT"
40 A = 1
50 X = 1 / (A - 1)
60 PRINT "Success, X = "; X
70 END
1000 REM Error handler
1010 PRINT "Error at line "; ERL
1020 A = 2
1030 PRINT "Fixed A, using RESUME"
1040 RESUME
1050 END
