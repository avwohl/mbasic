10 REM Test PRINT USING formatted output
20 PRINT "=== PRINT USING Test ==="
30 PRINT
40 REM Test numeric formatting
50 PRINT "Numeric formats:"
60 PRINT USING "###"; 42
70 PRINT USING "###.##"; 123.456
80 PRINT USING "$###.##"; 19.99
90 PRINT USING "#,###.##"; 1234.567
100 PRINT
110 REM Test string formatting
120 PRINT "String formats:"
130 A$ = "HELLO"
140 B$ = "WORLD"
150 PRINT USING "!"; A$
160 PRINT USING "&"; B$
170 PRINT USING "\    \"; "TEST"
180 PRINT
190 REM Test multiple values
200 PRINT "Multiple values:"
210 PRINT USING "### ###.##"; 10; 3.14159
220 PRINT USING "& costs $###.##"; "Widget"; 25.50
230 PRINT
240 REM Test with variables
250 X = 123.456
260 Y = 78.9
270 N$ = "Product"
280 PRINT USING "& ###.## ###.##"; N$; X; Y
290 PRINT
300 PRINT "=== End of test ==="
310 END