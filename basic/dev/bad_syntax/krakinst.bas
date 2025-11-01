10 REM  line with line number 10
100 REM ********************************
110 REM *                              *
120 REM *  KRAKINST.BAS                *
122 REM *                              *
124 REM *  From Computers & Security   *
126 REM *  Vol. 5, Iss. 1, March 1986  *
128 REM *  Pages 36-45                 *
130 REM *                              *
140 REM *  This program computes the   *
150 REM *  143 byte long Q-key and     *
160 REM *  the number of zeroes (00-   *
170 REM *  bytes) at the end of a      *
180 REM *  program. These data are     *
190 REM *  stored in the file named    *
200 REM *  "KRAKINFO.DAT".             *
210 REM *                              *
220 REM *  Note that the first line    *
230 REM *  of this program must have   *
240 REM *  line number 10.             *
250 REM *                              *
260 REM *  Delft, 85.06.13             *
270 REM *                              *
280 REM *  R. van den Assem            *
290 REM *  W.J. van Elk                *
320 REM *                              *
330 REM ********************************
340 REM ---------------------
350 REM create and open files
360 REM ---------------------
370 SAVE "TEMPTOK.$$$"
380 SAVE "TEMPCODE.$$$",p
390 OPEN "R", #1, "TEMPTOK.$$$",1
400 FIELD #1, 1 AS PLAIN$
410 OPEN "R", #2, "TEMPCODE.$$$",1
420 FIELD #2, 1 AS CODE$
430 OPEN "O", #3, "KRAKINFO.DAT"
440 REM ----------
450 REM initialize
460 REM ----------
470 GET #1 :  GET #2
480 A%=13 : B%=11
490 REM -------------
500 REM compute Q-key
510 REM -------------
520 FOR I%=1 TO 143
530 GET #1 : GET #2
540 PLAIN% = ASC(PLAIN$)
550 CODE% = ASC(CODE$)
560 Q1% = (CODE% - B% + 256) MOD 256
570 Q2% = (PLAIN% - A% + 256) MOD 256
580 Q% = Q1% XOR Q2%
590 A% = A%-1 : IF A%=0 THEN A%=13
600 B% = B%-1 : IF B%=0 THEN B%=11
610 PRINT #3, Q%
620 NEXT I%
630 CLOSE #1, #2
640 REM ---------------------------
650 REM computer number of zeros at
660 REM the end of a program
670 REM ---------------------------
680 OPEN "R", #1, "TEMPTOK.$$$", 1
690 FIELD #1, 1 AS PLAIN$
700 FOR I%=1 TO 5: GET #1 : NEXT I%
710 IF ASC(PLAIN$) = 10 THEN NNUL%=4
720 IF ASC(PLAIN$) <> 10 THEN NNUL%=3
730 PRINT #3, NNUL%
740 CLOSE #1
750 REM --------------
760 REM end of program
770 REM --------------
780 CLOSE #3
790 KILL "TEMPTOK.$$$"
800 KILL "TEMPCODE.$$$"
810 END
820 REM ********************************

