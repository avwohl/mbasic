10 REM EPSON MX-80 PRINTER CONFIG. PROGRAM
20 REM
30 REM THIS PROG. IS NOT TO BE USED IN A COMMERCIAL ENVIRONMENT
40 REM WITHOUT PROPER AUTHORIZATION.
50 REM
60 REM COPYRIGHT (c) RODERICK WAYNE HART WA3MEZ
70 REM JUNE 21, 1981
80 REM
90 REM system equates
100 CLR = 11		'clear screen command
110 BEL = 7		'bell command
120 ESC = 27		'escape command
130 D = 500		'delay constant
140 DPORT = 33		'console data port
150 REM
160 REM print sign-on message
170 GOSUB 2600
180 GOSUB 2710
190 GOSUB 2610
200 PRINT TAB(5);
210 PRINT "be sure to turn off the printer and turn it back on to"
220 PRINT TAB(5);
230 PRINT "initialize the printer memory before executing this prog-"
240 PRINT TAB(5);
250 PRINT "ram. type RETURN when you are ready."
260 PRINT:PRINT
270 PRINT TAB(4);
280 INPUT " ";S
290 REM
300 REM print menu
310 GOSUB 2600
320 GOSUB 2710
330 GOSUB 2610
340 PRINT TAB(5);"1. select character print mode"
350 PRINT TAB(5);"2. set line spacing"
360 PRINT TAB(5);"3. set vertical tabs"
370 PRINT TAB(5);"4. set horizontal tabs"
380 PRINT TAB(5);"5. set page length"
390 PRINT TAB(5);"6. set characters per line"
400 PRINT TAB(5);"7. execute printer test"
410 PRINT TAB(5);"8. return to CP/M"
420 GOSUB 2610
430 PRINT TAB(4);
440 INPUT " ";S
450 IF S = 1 THEN 560
460 IF S = 2 THEN 830
470 IF S = 3 THEN 1160
480 IF S = 4 THEN 1460
490 IF S = 5 THEN 1760
500 IF S = 6 THEN 1910
510 IF S = 7 THEN 2230
520 IF S = 8 THEN SYSTEM
530 GOSUB 2450
540 GOTO 310
550 REM
560 GOSUB 2600
570 PRINT TAB(22);"character print mode"
580 PRINT TAB(22);"--------------------"
590 GOSUB 2610
600 PRINT TAB(5);"1. double strike"
610 PRINT TAB(5);"2. emphasized"
620 PRINT TAB(5);"3. compressed"
630 PRINT TAB(5);"4. return to main menu"
640 GOSUB 2610
650 PRINT TAB(4);
660 INPUT " ";S
670 IF S = 1 THEN 740
680 IF S = 2 THEN 770
690 IF S = 3 THEN 800
700 IF S = 4 THEN 300
710 GOSUB 2450
720 GOTO 560
730 REM double strike
740 LPRINT CHR$(ESC)+"G";
750 GOTO 560
760 REM emphasize
770 LPRINT CHR$(ESC)+"E";
780 GOTO 560
790 REM compress
800 LPRINT CHR$(15);
810 GOTO 560
820 REM
830 GOSUB 2600
840 PRINT TAB(26);"line spacing"
850 PRINT TAB(26);"------------"
860 GOSUB 2610
870 PRINT TAB(5);"1. 1/6 inch"
880 PRINT TAB(5);"2. 1/8 inch"
890 PRINT TAB(5);"3. 7/72 inch"
900 PRINT TAB(5);"4. return to main menu"
910 GOSUB 2610
920 PRINT TAB(4);
930 INPUT " ";S
940 IF S = 1 THEN 1010
950 IF S = 2 THEN 1060
960 IF S = 3 THEN 1110
970 IF S = 4 THEN 310
980 GOSUB 2450
990 GOTO 830
1000 REM 1/6 inch line spacing
1010 LPRINT CHR$(ESC)+"A";CHR$(140);CHR$(ESC)+"2";
1020 PRINT TAB(5);
1030 PRINT "line spacing set to 1/6 inch"
1040 GOTO 2340
1050 REM 1/8 inch line spacing
1060 LPRINT CHR$(ESC)+"A";CHR$(137);CHR$(ESC)+"0";
1070 PRINT TAB(5);
1080 PRINT "line spacing set to 1/8 inch"
1090 GOTO 2340
1100 REM 7/72 inch line spacing
1110 LPRINT CHR$(ESC)+"A";CHR$(135);CHR$(ESC)+"1";
1120 PRINT TAB(5);
1130 PRINT "line spacing set to 7/72 inch"
1140 GOTO 2340
1150 REM
1160 GOSUB 2600
1170 PRINT TAB(26);"vertical tabs"
1180 PRINT TAB(26);"-------------"
1190 T=0:T1=0:VTAB=0
1200 GOSUB 2610
1210 PRINT TAB(5);
1220 INPUT "how many vertical tabs do you wish to set ";VTAB
1230 IF VTAB = 0 GOTO 310
1240 PRINT
1250 PRINT TAB(5);
1260 PRINT "input the desired tab locations after the prompt"
1270 REM began sequence
1280 LPRINT CHR$(ESC)+"B";
1290 FOR X = 1 TO VTAB
1300 GOSUB 2520
1310 IF T => 64 AND X < VTAB GOTO 2640
1320 IF T =< T1 GOTO 2390
1330 IF T => 64 GOTO 2390
1340 T1 = T
1350 REM send tab to printer
1360 LPRINT CHR$(T+128);
1370 NEXT X
1380 REM end sequence
1390 LPRINT CHR$(128);
1400 GOSUB 2610
1410 PRINT TAB(5);
1420 REM tell the human how many tabs we have processed
1430 PRINT VTAB;" vertical tabs set"
1440 GOTO 2340
1450 REM
1460 GOSUB 2600
1470 PRINT TAB(26);"horizontal tabs"
1480 PRINT TAB(26);"---------------"
1490 T=0:T1=0:HTAB=0
1500 GOSUB 2610
1510 PRINT TAB(5);
1520 INPUT "how many horizontal tabs do you wish to set ";HTAB
1530 IF HTAB = 0 GOTO 310
1540 PRINT
1550 PRINT TAB(5);
1560 PRINT "input the desired tab locations after the prompt"
1570 REM began sequence
1580 LPRINT CHR$(ESC)+"D";
1590 FOR X = 1 TO HTAB
1600 GOSUB 2560
1610 IF T => 112 AND X < HTAB GOTO 2640
1620 IF T =< T1 GOTO 2390
1630 IF T => 112 GOTO 2390
1640 T1 = T
1650 REM send tab to printer
1660 LPRINT CHR$(T+128);
1670 NEXT X
1680 REM end sequence
1690 LPRINT CHR$(128);
1700 GOSUB 2610
1710 PRINT TAB(5);
1720 REM tell the human how many tabs we have processed
1730 PRINT HTAB;" horizontal tabs set"
1740 GOTO 2340
1750 REM
1760 GOSUB 2600
1770 PRINT TAB(27);"page length"
1780 PRINT TAB(27);"-----------"
1790 GOSUB 2610
1800 PRINT TAB(5);
1810 INPUT "page length --> ";L
1820 IF L > 66 GOTO 2420
1830 GOSUB 2610
1840 PRINT TAB(5);
1850 REM tell the human what we have done
1860 PRINT "page length set at ";L;" lines"
1870 REM tell printer page length
1880 LPRINT CHR$(ESC)+"C";L;
1890 GOTO 2340
1900 REM
1910 GOSUB 2600
1920 PRINT TAB(23);"characters per line"
1930 PRINT TAB(23);"-------------------"
1940 GOSUB 2610
1950 PRINT TAB(5);"1. 132 characters per line"
1960 PRINT TAB(5);"2. 80 characters per line"
1970 PRINT TAB(5);"3. 40 characters per line"
1980 PRINT TAB(5);"4. return to main menu"
1990 PRINT TAB(4);
2000 INPUT " ";S
2010 IF S = 1 THEN 2070
2020 IF S = 2 THEN 2120
2030 IF S = 3 THEN 2170
2040 IF S = 4 THEN 310
2050 GOSUB 2450
2060 GOTO 1910
2070 PRINT TAB(5);
2080 PRINT "printer set for 132 characters per line"
2090 REM setup for 132 cpl
2100 LPRINT CHR$(29);
2110 GOTO 2340
2120 PRINT TAB(5);
2130 PRINT "printer set for 80 characters per line"
2140 REM setup 80 cpl
2150 LPRINT CHR$(30);
2160 GOTO 2340
2170 PRINT TAB(5);
2180 PRINT "printer set for 40 characters per line"
2190 REM setup 40 cpl
2200 LPRINT CHR$(31);
2210 GOTO 2340
2220 REM terminal test routine
2230 GOSUB 2600
2240 PRINT:PRINT TAB(10);
2250 PRINT "type any ascii character to stop test ";
2260 LPRINT CHR$(140);		'form feed
2270 FOR X = 32 TO 127
2280 A = INP(DPORT)		'check for abort
2290 IF A <> 13 THEN 310
2300 LPRINT CHR$(X);
2310 NEXT X
2320 GOTO 2270
2330 REM subroutine
2340 GOSUB 2610
2350 PRINT TAB(5);
2360 INPUT "type return to continue";S
2370 GOTO 300
2380 REM subroutine
2390 GOSUB 2450
2400 GOTO 1300
2410 REM subroutine
2420 GOSUB 2450
2430 GOTO 1760
2440 REM error subroutine
2450 PRINT CHR$(CLR)
2460 PRINT CHR$(BEL);CHR$(BEL)
2470 PRINT TAB(14);"invalid selection, please try again !"
2480 FOR S = 1 TO D		'set up delay
2490 NEXT S
2500 RETURN
2510 REM subroutine
2520 PRINT:PRINT TAB(10);
2530 INPUT "vertical tab --> ";T
2540 RETURN
2550 REM subroutine
2560 PRINT:PRINT TAB(10);
2570 INPUT "horizontal tab --> ";T
2580 RETURN
2590 REM clear screen subroutine
2600 PRINT CHR$(CLR)
2610 PRINT:PRINT
2620 RETURN
2630 REM fatal error subroutine
2640 GOSUB 2600
2650 PRINT TAB(5);"FATAL ERROR, TURN OFF PRINTER AND START OVER !"
2660 PRINT:PRINT
2670 FOR X = 1 TO D
2680 NEXT X
2690 GOTO 310
2700 REM program title print subroutine
2710 PRINT TAB(15);"EPSON MX-80 PRINTER CONFIG. PROGRAM"
2720 PRINT TAB(15);"-----------------------------------"
2730 RETURN
2740 END
AB(15);"EPSON MX-80 PRINTER CONFIG. PROGRAM"
2720 PRINT TAB(15);"-----------------