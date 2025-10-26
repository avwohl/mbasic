10 REM Test RESUME forms
20 ON ERROR GOTO 1000
30 PRINT "Testing RESUME"
40 X = 1 / 0
50 PRINT "After error - should not print"
60 END
1000 REM Error handler
1010 PRINT "Error "; ERR; " at line "; ERL
1020 PRINT "Using RESUME to retry"
1030 X = 1
1040 RESUME 50
1050 END
