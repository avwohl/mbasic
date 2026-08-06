10 REM Test DEF Type Statements Parse Correctly
20 REM Note: Type coercion is not yet implemented in interpreter
30 PRINT "Testing DEF Type Statement Parsing"
40 PRINT "==================================="
50 PRINT
60 REM Define type ranges
70 DEFINT i-k
80 DEFSNG a-c
90 DEFDBL d-f
100 DEFSTR s
110 PRINT "DEFINT i-k parsed successfully"
120 PRINT "DEFSNG a-c parsed successfully"
130 PRINT "DEFDBL d-f parsed successfully"
140 PRINT "DEFSTR s parsed successfully"
150 PRINT
160 REM Test explicit type suffixes (these work)
170 i% = 10.9
180 j% = 20.7
190 PRINT "Explicit % suffix forces integer:"
200 PRINT "i% = 10.9 becomes"; i%
210 PRINT "j% = 20.7 becomes"; j%
220 PRINT
230 REM Test string suffix
240 nm$ = "MBASIC"
250 version$ = "5.21"
260 PRINT "String variables with $ suffix:"
270 PRINT "nm$ ="; nm$
280 PRINT "version$ ="; version$
290 PRINT
300 REM Test mixed case variables
310 a = 100
320 A = 200
330 PRINT "Case insensitivity test:"
340 PRINT "Set a=100, then A=200"
350 PRINT "a now equals"; a; "(should be 200)"
360 PRINT
370 PRINT "DEF statement parsing test complete!"
380 END
