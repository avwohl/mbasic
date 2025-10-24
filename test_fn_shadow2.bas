10 REM Test if non-parameter variables in function body use globals
20 X = 100
30 Y = 200
40 Z = 300
50 PRINT "Initial values:"
60 PRINT "X ="; X; ", Y ="; Y; ", Z ="; Z
70 REM Function has parameter X, but uses Y in expression
80 DEF FNA(X) = X + Y + Z
90 PRINT "After DEF FN:"
100 PRINT "X ="; X; ", Y ="; Y; ", Z ="; Z
110 REM Call function
120 RESULT = FNA(10)
130 PRINT "After FNA(10):"
140 PRINT "RESULT ="; RESULT
150 PRINT "X ="; X; ", Y ="; Y; ", Z ="; Z
160 REM Now change Y and Z
170 Y = 500
180 Z = 600
190 RESULT = FNA(10)
200 PRINT "After changing Y and Z, FNA(10):"
210 PRINT "RESULT ="; RESULT
220 PRINT "X ="; X; ", Y ="; Y; ", Z ="; Z
230 END
