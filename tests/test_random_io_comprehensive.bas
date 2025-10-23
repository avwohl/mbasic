10 REM Comprehensive random file I/O test
20 REM Tests: OPEN R, FIELD, LSET, RSET, PUT, GET, LOC, LOF
30 PRINT "=== Random File I/O Comprehensive Test ==="
40 PRINT
50 REM ===== Test 1: Basic FIELD and LSET =====
60 PRINT "Test 1: Basic FIELD and LSET"
70 OPEN "R", 1, "/tmp/testrand.dat", 50
80 FIELD #1, 20 AS NAME$, 10 AS CITY$, 20 AS NOTES$
90 LSET NAME$ = "Alice Johnson"
100 LSET CITY$ = "NYC"
110 LSET NOTES$ = "First record"
120 PUT #1, 1
130 PRINT "  Wrote record 1"
140 PRINT
150 REM ===== Test 2: RSET for right-justified data =====
160 PRINT "Test 2: RSET for numeric fields"
170 FIELD #1, 20 AS N$, 10 AS AMT$, 20 AS D$
180 LSET N$ = "Bob Smith"
190 RSET AMT$ = "12345"
200 LSET D$ = "Amount field"
210 PUT #1, 2
220 PRINT "  Wrote record 2 with RSET amount"
230 PRINT
240 REM ===== Test 3: Read back and verify =====
250 PRINT "Test 3: Reading records back"
260 GET #1, 1
270 PRINT "  Rec 1: ["; NAME$; "] ["; CITY$; "] ["; NOTES$; "]"
280 GET #1, 2
290 PRINT "  Rec 2: ["; N$; "] ["; AMT$; "] ["; D$; "]"
300 PRINT
310 REM ===== Test 4: LOC and LOF =====
320 PRINT "Test 4: LOC() and LOF() functions"
330 PRINT "  LOC(1) after GET #1,2 ="; LOC(1)
340 PRINT "  LOF(1) ="; LOF(1); "(bytes)"
350 GET #1, 1
360 PRINT "  LOC(1) after GET #1,1 ="; LOC(1)
370 PRINT
380 REM ===== Test 5: Sequential PUT without record number =====
390 PRINT "Test 5: PUT without explicit record number"
400 LSET N$ = "Carol White"
410 LSET AMT$ = "999"
420 LSET D$ = "Record 3"
430 PUT #1
440 PRINT "  PUT #1 (sequential) - should write to rec"; LOC(1)
450 PRINT
460 REM ===== Test 6: Overwrite existing record =====
470 PRINT "Test 6: Overwriting record 2"
480 GET #1, 2
490 PRINT "  Before: ["; N$; "] ["; AMT$; "]"
500 LSET N$ = "Bob Jones"
510 RSET AMT$ = "54321"
520 PUT #1, 2
530 GET #1, 2
540 PRINT "  After:  ["; N$; "] ["; AMT$; "]"
550 PRINT
560 REM ===== Test 7: Multiple fields of various sizes =====
570 PRINT "Test 7: Various field sizes"
580 OPEN "R", 2, "/tmp/testrand2.dat", 30
590 FIELD #2, 5 AS F1$, 3 AS F2$, 10 AS F3$, 12 AS F4$
600 LSET F1$ = "ABCDE"
610 LSET F2$ = "XY"
620 RSET F3$ = "12"
630 LSET F4$ = "TestData"
640 PUT #2, 1
650 GET #2, 1
660 PRINT "  F1$=["; F1$; "] F2$=["; F2$; "] F3$=["; F3$; "] F4$=["; F4$; "]"
670 PRINT
680 REM ===== Test 8: Field overflow behavior =====
690 PRINT "Test 8: String longer than field (truncation)"
700 FIELD #2, 5 AS S1$, 25 AS S2$
710 LSET S1$ = "ABCDEFGHIJ"
720 LSET S2$ = "This is a very long string"
730 PUT #2, 2
740 GET #2, 2
750 PRINT "  S1$ (5 chars): ["; S1$; "] len="; LEN(S1$)
760 PRINT "  S2$ (25 chars): ["; S2$; "] len="; LEN(S2$)
770 PRINT
780 REM ===== Test 9: GET without record number =====
790 PRINT "Test 9: GET without record number (sequential)"
800 CLOSE #2
810 OPEN "R", 2, "/tmp/testrand2.dat", 30
820 FIELD #2, 5 AS S1$, 25 AS S2$
830 GET #2, 1
840 PRINT "  After GET #2,1: LOC(2)="; LOC(2)
850 GET #2
860 PRINT "  After GET #2:   LOC(2)="; LOC(2); " S1$=["; S1$; "]"
870 PRINT
880 REM ===== Test 10: Empty fields =====
890 PRINT "Test 10: Empty/blank fields"
900 LSET S1$ = ""
910 LSET S2$ = ""
920 PUT #2, 3
930 GET #2, 3
940 PRINT "  Empty S1$=["; S1$; "] len="; LEN(S1$)
950 PRINT "  Empty S2$=["; S2$; "] len="; LEN(S2$)
960 PRINT
970 REM ===== Test 11: Redefine FIELD on same file =====
980 PRINT "Test 11: Redefining FIELD on same file number"
990 FIELD #1, 10 AS X$, 40 AS Y$
1000 GET #1, 1
1010 PRINT "  New field layout: X$=["; X$; "] Y$=["; Y$; "]"
1020 PRINT
1030 REM ===== Test 12: Multiple records with LOF =====
1040 PRINT "Test 12: File size after multiple writes"
1050 PRINT "  File #1 has record size 50"
1060 PRINT "  LOF(1)="; LOF(1); "bytes"
1070 PRINT "  Expected ~150-200 bytes for 3-4 records"
1080 PRINT
1090 REM ===== Cleanup =====
1100 CLOSE #1
1110 CLOSE #2
1120 PRINT "=== All tests complete ==="
1130 END
