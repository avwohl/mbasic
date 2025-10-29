10 REM Test lexer fixes
20 REM Test that NextTime is an identifier, not NEXT + Time
30 NextTime = 100
40 PRINT "NextTime ="; NextTime
50 REM Test file I/O with #
60 OPEN "O", #1, "TEST.TXT"
70 PRINT#1, "Hello World"
80 CLOSE#1
90 REM Test double precision suffix
100 Value# = 3.14159265
110 PRINT "Value# ="; Value#
120 REM Mixed case keywords should work
130 print "lowercase print"
140 PRINT "UPPERCASE PRINT"
150 Print "Mixed case Print"
160 END