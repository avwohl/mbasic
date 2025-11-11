10 REM Simple binary data test
20 PRINT "Testing MKI$/CVI"
30 I = 256
40 B$ = MKI$(I)
50 I2 = CVI(B$)
60 PRINT "Original:"; I; " Back:"; I2
70 IF I = I2 THEN PRINT "PASS" ELSE PRINT "FAIL"
80 END