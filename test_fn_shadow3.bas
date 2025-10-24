10 REM Test parameter shadowing when same name used in expression
20 X = 100
30 Y = 200
40 PRINT "Initial: X ="; X; ", Y ="; Y
50 REM Function with parameters X and Y, expression uses X and Y
60 DEF FNA(X, Y) = X * 10 + Y
70 PRINT "After DEF FN: X ="; X; ", Y ="; Y
80 REM Call with different values
90 RESULT = FNA(5, 7)
100 PRINT "FNA(5, 7) ="; RESULT; " (expect 57)"
110 PRINT "After call: X ="; X; ", Y ="; Y
120 REM Call with globals as arguments
130 RESULT = FNA(X, Y)
140 PRINT "FNA(X, Y) ="; RESULT; " (expect 1200)"
150 PRINT "After call: X ="; X; ", Y ="; Y
160 END
