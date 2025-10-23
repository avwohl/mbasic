10 REM Comprehensive sequential file I/O test
20 PRINT "=== Sequential File I/O Tests ==="
30 PRINT
40 REM ===== Test 1: Writing sequential output =====
50 PRINT "Test 1: Writing to sequential output file"
60 OPEN "O", 1, "SEQOUT.DAT"
70 PRINT #1, "Line 1: Hello World"
80 PRINT #1, "Line 2: MBASIC Test"
90 PRINT #1, 123
100 PRINT #1, 45.67
110 PRINT #1, "Line 5: Mixed"; 999; "data"
115 PRINT "  Before CLOSE: LOC(1)="; LOC(1); " LOF(1)="; LOF(1)
120 CLOSE #1
130 PRINT "  Wrote 5 lines to SEQOUT.DAT"
150 PRINT
160 REM ===== Test 2: Reading sequential input =====
170 PRINT "Test 2: Reading from sequential input file"
180 OPEN "I", 1, "SEQOUT.DAT"
190 PRINT "  After OPEN: LOC(1)="; LOC(1); " LOF(1)="; LOF(1)
200 INPUT #1, A$
210 PRINT "  Read: ["; A$; "]"
220 PRINT "  After INPUT: LOC(1)="; LOC(1); " LOF(1)="; LOF(1)
230 INPUT #1, B$
240 PRINT "  Read: ["; B$; "]"
250 INPUT #1, N
260 PRINT "  Read number:"; N
270 INPUT #1, F
280 PRINT "  Read float:"; F
290 PRINT "  After 4 INPUTs: LOC(1)="; LOC(1); " LOF(1)="; LOF(1)
300 CLOSE #1
310 PRINT
320 REM ===== Test 3: LINE INPUT# =====
330 PRINT "Test 3: LINE INPUT# (read entire lines)"
340 OPEN "I", 1, "SEQOUT.DAT"
350 LINE INPUT #1, L$
360 PRINT "  Line 1: ["; L$; "]"
370 LINE INPUT #1, L$
380 PRINT "  Line 2: ["; L$; "]"
390 PRINT "  LOC(1)="; LOC(1); " LOF(1)="; LOF(1)
400 CLOSE #1
410 PRINT
420 REM ===== Test 4: EOF() function =====
430 PRINT "Test 4: EOF() end-of-file detection"
440 OPEN "I", 1, "SEQOUT.DAT"
450 C = 0
460 IF EOF(1) THEN PRINT "  ERROR: EOF true at start!" : GOTO 530
470 WHILE NOT EOF(1)
480 LINE INPUT #1, L$
490 C = C + 1
500 WEND
510 PRINT "  Read"; C; "lines until EOF"
520 PRINT "  EOF(1)="; EOF(1); " (should be -1/true)"
530 CLOSE #1
540 PRINT
550 REM ===== Test 5: PRINT# with separators =====
560 PRINT "Test 5: PRINT# with comma and semicolon"
570 OPEN "O", 1, "SEQ2.DAT"
580 PRINT #1, "A", "B", "C"
590 PRINT #1, "X"; "Y"; "Z"
600 PRINT #1, 100, 200, 300
610 PRINT #1, 1; 2; 3
620 CLOSE #1
630 OPEN "I", 1, "SEQ2.DAT"
640 LINE INPUT #1, L$
650 PRINT "  Comma separated: ["; L$; "]"
660 LINE INPUT #1, L$
670 PRINT "  Semicolon: ["; L$; "]"
680 LINE INPUT #1, L$
690 PRINT "  Numbers comma: ["; L$; "]"
700 LINE INPUT #1, L$
710 PRINT "  Numbers semi: ["; L$; "]"
720 CLOSE #1
730 PRINT
740 REM ===== Test 6: Append mode =====
750 PRINT "Test 6: Append mode (OPEN A)"
760 OPEN "A", 1, "SEQOUT.DAT"
770 PRINT "  After OPEN A: LOC(1)="; LOC(1); " LOF(1)="; LOF(1)
780 PRINT #1, "Appended line 6"
790 PRINT #1, "Appended line 7"
800 CLOSE #1
810 PRINT "  Appended 2 lines"
820 OPEN "I", 1, "SEQOUT.DAT"
830 C = 0
840 WHILE NOT EOF(1)
850 LINE INPUT #1, L$
860 C = C + 1
870 IF C > 5 THEN PRINT "  Line"; C; ": ["; L$; "]"
880 WEND
890 PRINT "  Total lines now:"; C
900 CLOSE #1
910 PRINT
920 REM ===== Test 7: Write empty lines =====
930 PRINT "Test 7: Writing and reading empty lines"
940 OPEN "O", 1, "EMPTY.DAT"
950 PRINT #1, ""
960 PRINT #1, "Not empty"
970 PRINT #1, ""
980 CLOSE #1
990 OPEN "I", 1, "EMPTY.DAT"
1000 LINE INPUT #1, L$
1010 PRINT "  Line 1 len="; LEN(L$); " ["; L$; "]"
1020 LINE INPUT #1, L$
1030 PRINT "  Line 2 len="; LEN(L$); " ["; L$; "]"
1040 LINE INPUT #1, L$
1050 PRINT "  Line 3 len="; LEN(L$); " ["; L$; "]"
1060 CLOSE #1
1070 PRINT
1080 REM ===== Test 8: LOC changes during read/write =====
1090 PRINT "Test 8: LOC() during sequential operations"
1100 OPEN "O", 1, "LOCTEST.DAT"
1110 PRINT "  After OPEN O: LOC(1)="; LOC(1)
1120 PRINT #1, "First"
1130 PRINT "  After 1 PRINT#: LOC(1)="; LOC(1)
1140 PRINT #1, "Second"
1150 PRINT "  After 2 PRINT#: LOC(1)="; LOC(1)
1160 PRINT #1, "Third"
1170 PRINT "  After 3 PRINT#: LOC(1)="; LOC(1)
1180 CLOSE #1
1190 OPEN "I", 1, "LOCTEST.DAT"
1200 PRINT "  After OPEN I: LOC(1)="; LOC(1)
1210 LINE INPUT #1, L$
1220 PRINT "  After 1 read: LOC(1)="; LOC(1)
1230 LINE INPUT #1, L$
1240 PRINT "  After 2 reads: LOC(1)="; LOC(1)
1250 LINE INPUT #1, L$
1260 PRINT "  After 3 reads: LOC(1)="; LOC(1)
1270 CLOSE #1
1280 PRINT
1290 PRINT "=== All sequential I/O tests complete ==="
1300 END
