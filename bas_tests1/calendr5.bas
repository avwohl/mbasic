10 PRINT
20 PRINT "****************************"
30 PRINT "*  THE GREGORIAN CALENDR1  *"
40 PRINT "*                          *"
50 PRINT "****************************"
60 REM
70  REM	  Original program obtained from CP/Mug.
80  REM   Program adapted to read the TP-100 TimEPROMmer card
90  REM   from Optronics Technology, 2990 Atlantic Avenue,
100 REM   Penfield, NY 14526, and to compute astronomical "Julian 
110 REM   Date," by D. Mc Lanahan, Box 17, Marlow, NH 03456.
120 REM   Program computes day-of-week and ignores TP-100 d-o-w.
130 REM
140 DIM M$(12),D$(6),TIME(6)
150 P=40 :  REM: P is the base location of the TimEPROMmer card.
160 P1=P+1
170 DATA January,February,March,April,May,June,July,August
180 DATA September,October,November,December
190 FOR A=1 TO 12:READ M$(A):NEXT A
200 DATA Sunday,Monday,Tuesday,Wednesday,Thursday,Friday,Saturday
210 FOR A=0 TO 6:READ D$(A):NEXT A
220 DEF FND(V)=INT(7*(V/7-INT(V/7))+.05)
230 PRINT:PRINT
240 PRINT "The Routines:":PRINT
250 PRINT "     1.   Print a calendar"
260 PRINT "     2.   Day of the week"
270 PRINT "     3.   Days between dates"
280 PRINT "     4.   Date before or after"
290 PRINT "     5.   Astronomical Julian date"
300 PRINT "     6.   Return to Basic"
310 PRINT "     7.   Return to System" : PRINT
320 INPUT "Enter Routine Number";R
330 PRINT CHR$(12)
340 ON R GOTO 370,660,750,860,1000,1560,1550
350 GOTO 320
360 REM
370 PRINT "This routine will print a calendar for each month"
380 PRINT "starting with the month and year entered and"
390 PRINT "continuing for the number of months specified."
400 REM  PRINT "CALENDARS WILL BE PRINTED ON LINE PRINTER"
410 REM  PRINT "IF SENSE SWITCH 'A15' IS RAISED."
420 GOSUB 1290:DM=1:C=0
430 PRINT:INPUT "Number of months";N:IF (INP(255) AND INP(128))<>0 GOTO 530
440 IF C=N THEN PRINT CHR$(12):GOTO 240
450 PRINT CHR$(12);"******** ";M$(MY);TAB(20);YR;"********"
460 PRINT " SUN  MON  TUE  WED  THU  FRI  SAT"
470 PRINT "***********************************"
480 GOSUB 1220
490 DW=FND(X)
500 PRINT TAB(5*DW);DM;:IF DM=6 THEN PRINT
510 X=X+1:GOSUB 1160:IF DM=1 THEN C=C+1:GOTO 440
520 GOTO 490
530 IF C=N THEN PRINT:PRINT CHR$(12):GOTO 240
540 PRINT:PRINT:PRINT
550 PRINT "******** "M$(MY);TAB(20);YR;"********"
560 PRINT " SUN  MON  TUE  WED  THU  FRI  SAT"
570 FOR I=1 TO 34:PRINT "*";:NEXT I:PRINT
580 GOSUB 1220
590 DW=FND(X)
600 PRINT TAB(5*DW);DM;:IF DW=6 THEN PRINT
610 X=X+1:GOSUB 1160:IF DM=1 THEN C=C+1:GOTO 530
620 GOTO 590
630 REM
640 REM ***DAY OF WEEK***
650 REM
660 PRINT "This routine will determine the day of the week"
670 PRINT "For any Gregorian date after December 31, 1582."
680 GOSUB 1130
690 DW=FND(X)
700 PRINT:PRINT M$(MY);" ";STR$(DM);",";YR;" is a ";D$(DW)
710 GOTO 230
720 REM
730 REM ***NUMBER OF DAYS***
740 REM
750 PRINT "This routine will determine the number of days"
760 PRINT "between two Gregorian dates after December 31, 1582."
770 GOSUB 1130:D2=D1:M2=M1:Y2=Y1:X2=X:GOSUB 1130
780 PRINT M$(M2);" ";STR$(D2);",";Y2;"is";ABS(X2-X);"day";
790 IF ABS(X2-X<>1) THEN PRINT "s";
800 IF X2>X THEN PRINT " after ":GOTO 820
810 PRINT " before "
820 PRINT M$(MY);" ";STR$(DM);","YR:GOTO 230
830 REM
840 REM ***DATE***
850 REM
860 PRINT "This routine will determine the Gregorian date for a"
870 PRINT "given number of days before (-) or after a specified date."
880 GOSUB 1130:INPUT "Number of days before (-) or after date";Z
890 X=X+Z:IF X>139753! GOTO 920
900 PRINT:PRINT "The date is prior to the adoption of the Gregorian Calendar."
910 GOTO 880
920 GOSUB 1160:PRINT:PRINT ABS(Z);"day";:IF ABS(Z)<>1 THEN PRINT "s"
930 IF Z<0 THEN PRINT " before ";:GOTO 950
940 PRINT " after ";
950 PRINT M$(M1);" ";STR$(D1);",";Y1
960 PRINT " is ";M$(MY);" ";STR$(DM);",";YR:GOTO 230
970 REM
980 REM ***JULIAN DATE***
990 REM
1000 PRINT "This routine will determine the Julian Date"
1010 PRINT "for a Gregorian date after 31 December 1582"
1020 GOSUB 1030
1030 GOSUB 1130
1040 OFFSET#=2159407.5#
1050 PRINT M$(MY);" ";STR$(DM);",";YR;"is Julian Day  ";
1060 PRINT USING "########,.#";(X+OFFSET#)
1070 PRINT "Before noon UT (GMT), ignore the decimal."
1080 PRINT "After noon UT, add 0.5.":GOTO 230
1090 STOP
1100 REM
1110 REM ***SUBROUTINES***
1120 REM
1130 GOSUB 1260:GOSUB 1220:D1=DM:M1=MY:Y1=YR:GOSUB 1160:REM***TEST DATE***
1140 IF D1<>DM OR M1<>MY OR Y1<>YR THEN PRINT:PRINT "INVALID DATE":GOTO 1130
1150 RETURN
1160 Y=INT((X+60)/365.25):REM ***NUMBER TO DATE***
1170 I=X-INT(Y*365.25)+120+INT(Y/100)-INT(Y/400)
1180 M=INT((I-.1)/30.6):IF M<4 THEN M=M+12:Y=Y-1:GOTO 1170
1190 I=I-INT(M*30.6):IF M>13 THEN M=M-12:Y=Y+1
1200 YR=Y+1200:MY=M-1:DM=I
1210 RETURN
1220 D=DM:M=MY:Y=YR-1200:REM ***DATE TO NUMBER***
1230 M=M+1:IF M<=3 THEN Y=Y-1:M=M+12
1240 X=INT(365.25*Y)+INT(30.6*M)+D-120-INT(Y/100)+INT(Y/400)
1250 RETURN
1260 PRINT : PRINT "Day of the month-"
1270 INPUT "(for today, enter 0)",DM:IF DM=0 GOTO 1350 : REM***ENTER DATE***
1280 GOTO 1320
1290 PRINT : PRINT "Starting Month (1-12)---?";
1300 PRINT:INPUT "(for this month, enter 0)",MY:IF MY=0 GOTO 1350 : IF MY<1 OR MY>12 GOTO 1290
1310 GOTO 1330
1320 PRINT : INPUT "Enter month";MY:IF MY<1 OR MY>12 GOTO 1320
1330 PRINT:INPUT "YEAR (>1582)";YR:IF YR<1583 GOTO 1330
1340 PRINT:RETURN
1350 REM
1360 REM ****** READ TP-100 (CALENDAR BOARD) DATA ****** 
1370 REM
1380 REM ....OUTPUT HOLD BIT
1390 OUT P,16
1400 REM ....OUTPUT HOLD + READ BITS
1410 OUT P,48
1420 REM ....OUTPUT ADDRESS AND INPUT DATA FOR RANGE
1430 FOR X=1 TO 6
1440 OUT P,61-X
1450 TIME(X)=(INP(P1) AND 15): NEXT X
1460 REM ....REMOVE HOLD RESUME CLOCK FUNCTIONS
1470 OUT P,0
1480 REM
1490 REM ****** FORMAT DATA ******
1500 REM
1510 YR=(TIME(1)*10+TIME(2)+1900)
1520 MY=(TIME(3) AND 1)*10+TIME(4)
1530 DM=(TIME(5) AND 3)*10+TIME(6)
1540 RETURN
1550 SYSTEM
1560 END
