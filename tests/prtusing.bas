10 REM Test PRINT USING with various formats
20 PRINT "=== Number Formatting ==="
30 PRINT USING "###.##"; 123.456
40 PRINT USING "###.##"; 12.3
50 PRINT USING "###.##"; 1.23456
60 PRINT ""
70 PRINT "=== String Formatting ==="
80 PRINT USING "!"; "HELLO"
90 PRINT USING "\    \"; "HELLO"
100 PRINT USING "&"; "HELLO WORLD"
110 PRINT ""
120 PRINT "=== Currency Formatting ==="
130 PRINT USING "$$###.##"; 123.45
140 PRINT USING "**###.##"; 45.67
150 PRINT ""
160 PRINT "=== Multiple Values ==="
170 PRINT USING "Name: \ \ Amount: ###.##"; "JOHN"; 99.99
180 END
