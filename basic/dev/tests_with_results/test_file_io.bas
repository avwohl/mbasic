10 REM Test File I/O Operations
20 PRINT "Testing File I/O"
30 PRINT "================"
40 PRINT
50 REM Test 1: Write to file
60 PRINT "Test 1: Writing to file"
70 OPEN "O", 1, "TESTFIL.TXT"
80 PRINT #1, "Line 1: Hello from MBASIC"
90 PRINT #1, "Line 2: Testing file output"
100 PRINT #1, "Line 3: Numbers:"; 10; 20; 30
110 CLOSE 1
120 PRINT "File written successfully"
130 PRINT
140 REM Test 2: Read from file
150 PRINT "Test 2: Reading from file"
160 OPEN "I", 1, "TESTFIL.TXT"
170 LINE INPUT #1, L$
180 PRINT "Read: "; L$
190 LINE INPUT #1, L$
200 PRINT "Read: "; L$
210 LINE INPUT #1, L$
220 PRINT "Read: "; L$
230 CLOSE 1
240 PRINT
250 REM Test 3: Append to file
260 PRINT "Test 3: Appending to file"
270 OPEN "A", 1, "TESTFIL.TXT"
280 PRINT #1, "Line 4: Appended line"
290 CLOSE 1
300 PRINT "Appended to file"
310 PRINT
320 REM Test 4: Read appended content
330 PRINT "Test 4: Reading all lines"
340 OPEN "I", 1, "TESTFIL.TXT"
350 C = 0
360 WHILE NOT EOF(1)
370 LINE INPUT #1, L$
380 C = C + 1
390 PRINT "Line"; C; ": "; L$
400 WEND
410 CLOSE 1
420 PRINT
430 REM Test 5: WRITE# (comma-delimited)
440 PRINT "Test 5: WRITE# with delimiters"
450 OPEN "O", 1, "TESTDAT.TXT"
460 WRITE #1, "Alice", 25, 1250.50
470 WRITE #1, "Bob", 30, 1500.75
480 CLOSE 1
490 PRINT "Data written with WRITE#"
500 PRINT
510 REM Test 6: INPUT# (read delimited data)
520 PRINT "Test 6: INPUT# reading delimited data"
530 OPEN "I", 1, "TESTDAT.TXT"
540 INPUT #1, N$, A, S
550 PRINT "Name:"; N$; "Age:"; A; "Salary:"; S
560 INPUT #1, N$, A, S
570 PRINT "Name:"; N$; "Age:"; A; "Salary:"; S
580 CLOSE 1
590 PRINT
600 REM Test 7: EOF function
610 PRINT "Test 7: EOF function"
620 OPEN "I", 1, "TESTFIL.TXT"
630 LC = 0
640 WHILE NOT EOF(1)
650 LINE INPUT #1, L$
660 LC = LC + 1
670 WEND
680 PRINT "Total lines read:"; LC
690 CLOSE 1
700 PRINT
710 REM Cleanup
720 KILL "TESTFIL.TXT"
730 KILL "TESTDAT.TXT"
740 PRINT "Test files deleted"
750 PRINT
760 PRINT "File I/O tests complete!"
770 END
