10 REM Test new compiler features
20 CLS
30 PRINT "=== Testing New Compiler Features ==="
40 PRINT
50 REM Test TAB and SPC
60 PRINT "Test 1: TAB and SPC functions"
70 PRINT TAB(5); "TAB(5)"; TAB(20); "TAB(20)"
80 PRINT "Text"; SPC(5); "with"; SPC(3); "spaces"
90 PRINT
100 REM Test MID$ statement
110 PRINT "Test 2: MID$ statement"
120 A$ = "Hello World!"
130 PRINT "Original: "; A$
140 MID$(A$, 7, 5) = "BASIC"
150 PRINT "After MID$(A$,7,5)=""BASIC"": "; A$
160 MID$(A$, 1, 5) = "Hi"
170 PRINT "After MID$(A$,1,5)=""Hi"": "; A$
180 PRINT
190 REM Test PRINT USING with files
200 PRINT "Test 3: PRINT USING to file"
210 OPEN "O", 1, "format.txt"
220 PRINT #1, USING "###.##"; 123.456
230 PRINT #1, USING "$#,###.##"; 1234.56
240 PRINT #1, USING "& - ###"; "Total"; 999
250 CLOSE 1
260 PRINT "Formatted data written to format.txt"
270 PRINT
280 REM Read it back
290 PRINT "Reading formatted file:"
300 OPEN "I", 1, "format.txt"
310 WHILE NOT EOF(1)
320   LINE INPUT #1, L$
330   PRINT "  "; L$
340 WEND
350 CLOSE 1
360 KILL "format.txt"
370 PRINT
380 REM Test multiple formats
390 PRINT "Test 4: Complex PRINT USING"
400 PRINT USING "Item: & Qty: ### Price: $###.##"; "Widget"; 15; 29.99
410 PRINT
420 PRINT "=== All tests complete ==="
430 END