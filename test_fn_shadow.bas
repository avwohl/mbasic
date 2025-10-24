10 REM Test DEF FN parameter shadowing
20 X = 100
30 Y = 200
40 PRINT "Before DEF FN:"
50 PRINT "X ="; X
60 PRINT "Y ="; Y
70 REM Define function with parameter X
80 DEF FNA(X) = X * 2
90 PRINT "After DEF FN, before call:"
100 PRINT "X ="; X
110 PRINT "Y ="; Y
120 REM Call function with Y as argument
130 RESULT = FNA(Y)
140 PRINT "After FNA(Y) call:"
150 PRINT "RESULT ="; RESULT
160 PRINT "X ="; X
170 PRINT "Y ="; Y
180 REM Call function with X as argument
190 RESULT = FNA(X)
200 PRINT "After FNA(X) call:"
210 PRINT "RESULT ="; RESULT
220 PRINT "X ="; X
230 PRINT "Y ="; Y
240 END
