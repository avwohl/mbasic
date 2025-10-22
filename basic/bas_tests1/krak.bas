100 REM ********************************
110 REM *                              *
120 REM *  KRAK.BAS                    *
122 REM *                              *
124 REM *  From Computers & Security   *
126 REM *  Vol. 5, Iss. 1, March 1986  *
128 REM *  Pages 36-45                 *
130 REM *                              *
140 REM *  This program encrypts or    *
150 REM *  decrypts the input file     *
160 REM *  and writes the results into *
170 REM *  the output file. Whether    *
180 REM *  the program encrypts or     *
190 REM *  decrypts depends on the     *
200 REM *  first byte of the input     *
210 REM *  file. The program needs     *
220 REM *  the data in the file        *
230 REM *  "KRAKINFO.DATA" which can   *
240 REM *  be created by the program   *
250 REM *  "KRAKINST.BAS".             *
260 REM *                              *
270 REM *  Delft, 85.06.13             *
280 REM *                              *
290 REM *  R. van den Assem            *
300 REM *  W.J. van Elk                *
310 REM *                              *
330 REM ********************************
360 REM -----------------
370 REM read KRAKINFO.DAT
380 REM -----------------
390 DIM Q%(143)
400 OPEN "I", #1,"KRAKINFO.DAT"
410 FOR I%=1 TO 143
420 INPUT #1,Q%(I%)
430 NEXT I%
440 INPUT #1, NNUL%
450 CLOSE #1
460 REM ---------------------
470 REM create and open files
480 REM ---------------------
500 INPUT "Name of input file";NI$
510 OPEN "R",#2,NI$,1
520 FIELD #2, 1 AS I$
530 GET #2
540 IF ASC(I$) > 253 THEN 580
550 PRINT "File does not appear to be tolkenized BASIC."
560 CLOSE #2
570 STOP
580 PRINT
590 PRINT "The first byte of the file indicates the file"
610 PRINT "needs to be ";
620 IF ASC(I$)=254 THEN Z%=0 ELSE Z%=1
630 IF Z%=0 THEN PRINT "decrypted."
640 IF Z%=1 THEN PRINT "encryped."
650 PRINT
660 INPUT "Name of the output file";NU$
670 OPEN "R",#3,NU$,1
680 FIELD #3, 1 AS U$
690 IF Z%=0 THEN LSET U$ = CHR$(255)
700 IF Z%=1 THEN LSET U$ = CHR$(254)
710 PUT #3
720 REM ----------
730 REM initialize
740 REM ----------
750 A%=13 : B%=11
760 T%=0
770 I%=1
780 REM ------------------
790 REM encrypt or decrypt
800 REM ------------------
810 WHILE T% < NNUL%
820 GET #2
830 X%=ASC(I$)
840 IF Z%=1 THEN 900
850 H% = (X% - B% + 256) MOD 256
860 H% = H% XOR Q%(I%)
870 H% = (H% + A%) MOD 256
880 IF H%=0 THEN T%=T%+1 ELSE T%=0
890 GOTO 940
900 H% = (X% - A% + 256) MOD 256
910 H% = H% XOR Q%(I%)
920 H% = (H% + B%) MOD 256
930 IF X%=0 THEN T%=T%+1 ELSE T%=0
940 LSET U$=CHR$(H%)
950 PUT #3
960 A%=A%-1 : IF A%=0 THEN A%=13
970 B%=B%-1 : IF B%=0 THEN B%=11
980 I%=I%+1 : IF I%=144 THEN I%=1
990 WEND
1000 REM --------------
1010 REM end of program
1020 REM --------------
1030 CLOSE #2, #3
1040 END
1050 REM ******************************
