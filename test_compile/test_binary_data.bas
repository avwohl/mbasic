10 REM Test binary data conversion functions
20 PRINT "=== Binary Data Conversion Test ==="
30 PRINT
40 REM Test MKI$/CVI - Integer conversion
50 PRINT "Integer conversion (MKI$/CVI):"
60 I = 12345
70 B$ = MKI$(I)
80 I2 = CVI(B$)
90 PRINT "Original:"; I; " Converted back:"; I2
100 IF I = I2 THEN PRINT "  PASS" ELSE PRINT "  FAIL"
110 PRINT
120 REM Test with negative integer
130 I = -9876
140 B$ = MKI$(I)
150 I2 = CVI(B$)
160 PRINT "Negative:"; I; " Converted back:"; I2
170 IF I = I2 THEN PRINT "  PASS" ELSE PRINT "  FAIL"
180 PRINT
190 REM Test MKS$/CVS - Single precision conversion
200 PRINT "Single precision conversion (MKS$/CVS):"
210 S = 3.14159
220 B$ = MKS$(S)
230 S2 = CVS(B$)
240 PRINT "Original:"; S; " Converted back:"; S2
250 IF ABS(S - S2) < 0.0001 THEN PRINT "  PASS" ELSE PRINT "  FAIL"
260 PRINT
270 REM Test with negative single
280 S = -123.456
290 B$ = MKS$(S)
300 S2 = CVS(B$)
310 PRINT "Negative:"; S; " Converted back:"; S2
320 IF ABS(S - S2) < 0.001 THEN PRINT "  PASS" ELSE PRINT "  FAIL"
330 PRINT
340 REM Test MKD$/CVD - Double precision conversion
350 PRINT "Double precision conversion (MKD$/CVD):"
360 D = 2.718281828
370 B$ = MKD$(D)
380 D2 = CVD(B$)
390 PRINT "Original:"; D; " Converted back:"; D2
400 IF ABS(D - D2) < 0.00000001 THEN PRINT "  PASS" ELSE PRINT "  FAIL"
410 PRINT
420 REM Test with large double
430 D = 1234567.89
440 B$ = MKD$(D)
450 D2 = CVD(B$)
460 PRINT "Large:"; D; " Converted back:"; D2
470 IF ABS(D - D2) < 0.01 THEN PRINT "  PASS" ELSE PRINT "  FAIL"
480 PRINT
490 REM Test string length
500 PRINT "Binary string lengths:"
510 PRINT "MKI$ creates"; LEN(MKI$(1)); "bytes (should be 2)"
520 PRINT "MKS$ creates"; LEN(MKS$(1.0)); "bytes (should be 4)"
530 PRINT "MKD$ creates"; LEN(MKD$(1.0)); "bytes (should be 8)"
540 PRINT
550 REM Test file I/O with binary data
560 PRINT "Testing binary data in files:"
570 OPEN "O", 1, "bindata.dat"
580 I = 42
590 S = 2.5
600 D = 999.999
610 PRINT #1, MKI$(I); MKS$(S); MKD$(D)
620 CLOSE 1
630 OPEN "I", 1, "bindata.dat"
640 LINE INPUT #1, L$
650 CLOSE 1
660 KILL "bindata.dat"
670 I2 = CVI(LEFT$(L$, 2))
680 S2 = CVS(MID$(L$, 3, 4))
690 D2 = CVD(MID$(L$, 7, 8))
700 PRINT "Wrote: I="; I; " S="; S; " D="; D
710 PRINT "Read:  I="; I2; " S="; S2; " D="; D2
720 IF I = I2 AND ABS(S - S2) < 0.001 AND ABS(D - D2) < 0.001 THEN PRINT "  PASS" ELSE PRINT "  FAIL"
730 PRINT
740 PRINT "=== All tests complete ==="
750 END