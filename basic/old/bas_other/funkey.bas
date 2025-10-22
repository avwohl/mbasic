10 REM *************FUNKEY.BAS 9/17/86********************************
20 REM WRITTEN IN MICROSOFT BASIC
30 REM AL BRENDEL... 9/20/86
40 REM TERMINAL FUNCTION KEY PROGRAMMER AND LABELER
50 REM WORKS WITH EITHER WYSE OR TELEVIDEO..MAYBE OTHERS
60 REM COULD BE CONVERTED TO .COM PROGRAM BUT I CHANGE MY MIND SO OFTEN I WANTED
70 REM SOMETHING EASY TO CHANGE..
80 REM COULD BE USED FOR ALL 32 FUNCTION KEYS BUT ONLY THOSE CAPABLE OF BEING
90 REM DISPLAYED WERE USED.
100 REM TO USE..CHANGE FUNCTIONS AND LABELS TO SUIT,SAVE,REMOVE STATEMENT 500
110 REM AND THEN TYPE...... MBASIC FUNKEY
120 REM **************** DEFINITIONS *****************************
130 DIM M$(16),C$(16)
140 CLR$=CHR$(26)		'CLEAR SCREEN
150 CR$=CHR$(13)			'CARRIAGE RETURN
160 ESC$=CHR$(27)		'ESCAPE
170 DEL$=CHR$(127)		'DELETE
180 DEF FNWYSE$=ESC$+"A"+"1"+"4"		'REVERSE FUNCTION MESSAGE--WYSE ONLY
190 DEF FNTVI$=ESC$+"\"+"1"+"4"		'REVERSE FUNCTION MESSAGE--TVI-920 ONLY
200 DEF FNHEAD$(MSG$)=ESC$+"F"+MSG$+CR$	'HEADER MESSAGE
210 DEF FNMSG$(N,MSG$)=ESC$+"z"+CHR$(N)+MSG$+CR$	'FUNCTION KEY FIELD MSG.
220 DEF FNFUN$(V,SEQ$)=ESC$+"z"+CHR$(V)+SEQ$+DEL$	'FUNCTION KEY FUNCTION
230 REM ******************PROGRAM *******************************
240 PRINT FNWYSE$;FNTVI$;
250 PRINT CLR$;
260 PRINT"	FUNCTION KEY PROGRAMMER AND LABELER PROGRAM":PRINT:PRINT
270 PRINT"PROGRAM WILL PROGRAM AND LABEL F1 THRU F8 AND (SHIFT)F1 THRU (SHIFT)F8"
280 PRINT:PRINT
290 PRINT"FUNCTIONS AVAILABLE:":PRINT:PRINT
300 PRINT"1.....NO FUNCTIONS"
310 PRINT"2.....TURBODOS"
320 PRINT"3.....WORDSTAR"
330 PRINT"4.....BASIC"
340 PRINT"5.....MEX"
350 PRINT"6.....DBASE II"
360 PRINT"7.....ADVENTURE"
370 PRINT "INPUT CHOICE";
380 N=ASC(INPUT$(1))-48
390 IF N<0 OR N>7 THEN 380
400 IF N=1 THEN PRINT ESC$+"A"+"1"+"1":PRINT ESC$+"\"+"1"+"1"
410 ON N GOSUB 560,750,940,1130,1320,1510,1700
420 PRINT FNHEAD$(HEAD$)"
430 FOR X=1 TO 8
440 PRINT FNMSG$(47+X,M$(X));FNFUN$(63+X,C$(X));
450 NEXT X
460 FOR X=9 TO 16
470 PRINT FNMSG$(71+X,M$(X));FNFUN$(87+X,C$(X));
480 NEXT X
490 PRINT CLR$
500 END	'REMOVE THIS STATEMENT AFTER CHECKING AND SAVING YOUR VERSION****
510 SYSTEM
520 REM******************DATA***********************************
530 REM DATA FORMAT:   M$(N)="MSG DISPLAYED AT SCREEN BOTTOM" (8 CHARACTERS)
540 REM                C$(N)=COMMAND STRING STORED UNDER F(N) KEY (8 CHARACTERS)
550 REM                HEAD$="MSG DISPLAYED AT TOP OF SCREEN"(46 CHARACTERS)
560 REM***********NO FUNCTIONS**************
570 HEAD$=""
580 M$(1)="        ":C$(1)=""
590 M$(2)="        ":C$(2)=""
600 M$(3)="        ":C$(3)=""
610 M$(4)="        ":C$(4)=""
620 M$(5)="        ":C$(5)=""
630 M$(6)="        ":C$(6)=""
640 M$(7)="        ":C$(7)=""
650 M$(8)="        ":C$(8)=""
660 M$(9)="        ":C$(9)=""
670 M$(10)="        ":C$(10)=""
680 M$(11)="        ":C$(11)=""
690 M$(12)="        ":C$(12)=""
700 M$(13)="        ":C$(13)=""
710 M$(14)="        ":C$(14)=""
720 M$(15)="        ":C$(15)=""
730 M$(16)="        ":C$(16)=""
740 RETURN
750 REM***********TURBODOS******************
760 HEAD$="                            TURBODOS FUNCTIONS"
770 M$(1)="  DIR   ":C$(1)="DIR"+CR$
780 M$(2)=" BISHOW ":C$(2)="BISHOW "
790 M$(3)=" NSWPT  ":C$(3)="NSWPT"+CR$
800 M$(4)="WORDSTAR":C$(4)="WS"+CR$
810 M$(5)="FAST-WS ":C$(5)="FWS"+CR$
820 M$(6)=" HELP   ":C$(6)="HELP"+CR$
830 M$(7)="MBASIC  ":C$(7)="MBASIC"+CR$
840 M$(8)="SYSTEM  ":C$(8)="SYSTEM"+CR$
850 M$(9)="  0A:   ":C$(9)="0A:"+CR$
860 M$(10)="  2A:   ":C$(10)="2A:"+CR$
870 M$(11)="  6A:   ":C$(11)="6A:"+CR$
880 M$(12)="  10A:  ":C$(12)="10A:"+CR$
890 M$(13)="  30A:  ":C$(13)="30A:"+CR$
900 M$(14)="        ":C$(14)=""
910 M$(15)="        ":C$(15)=""
920 M$(16)="        ":C$(16)=""
930 RETURN
940 REM***********WORDSTAR******************
950 HEAD$="                            WORDSTAR FUNCTIONS"
960 M$(1)=" DONE   ":C$(1)=CHR$(11)+"D"
970 M$(2)="SAV&CONT":C$(2)=CHR$(11)+"S"
980 M$(3)="ABANDON ":C$(3)=CHR$(11)+"Q"
990 M$(4)="READFILE":C$(4)=CHR$(11)+"R"
1000 M$(5)="PAGE UP ":C$(5)=CHR$(17)+"R"
1010 M$(6)="PAGE DN ":C$(6)=CHR$(17)+"C"
1020 M$(7)=" FIND   ":C$(7)=CHR$(17)+"F"
1030 M$(8)=" TAB    ":C$(8)=CHR$(15)+"G"
1040 M$(9)="        ":C$(9)=""
1050 M$(10)="        ":C$(10)=""
1060 M$(11)="        ":C$(11)=""
1070 M$(12)="        ":C$(12)=""
1080 M$(13)="        ":C$(13)=""
1090 M$(14)="        ":C$(14)=""
1100 M$(15)="        ":C$(15)=""
1110 M$(16)="        ":C$(16)=""
1120 RETURN
1130 REM***********BASIC*********************
1140 HEAD$="                              MBASIC FUNCTIONS"
1150 M$(1)=" LIST   ":C$(1)="LIST"+CR$
1160 M$(2)=" LLIST  ":C$(2)="LLIST"+CR$
1170 M$(3)="  AUTO  ":C$(3)="AUTO"+CR$
1180 M$(4)=" FILES  ":C$(4)="FILES"+CR$
1190 M$(5)="  RUN   ":C$(5)="RUN"+CR$
1200 M$(6)=" RENUM  ":C$(6)="RENUM"+CR$
1210 M$(7)=" MBASIC ":C$(7)="MBASIC"+CR$
1220 M$(8)=" SYSTEM ":C$(8)="SYSTEM"+CR$
1230 M$(9)="        ":C$(9)=""
1240 M$(10)="        ":C$(10)=""
1250 M$(11)="        ":C$(11)=""
1260 M$(12)="        ":C$(12)=""
1270 M$(13)="        ":C$(13)=""
1280 M$(14)="        ":C$(14)=""
1290 M$(15)="        ":C$(15)=""
1300 M$(16)="        ":C$(16)=""
1310 RETURN
1320 REM***********MEX***********************
1330 HEAD$="                                 MEX FUNCTIONS"
1340 M$(1)="CMD LEVL":C$(1)=CHR$(10)+"E"
1350 M$(2)="COPY TXT":C$(2)=CHR$(10)+"S"
1360 M$(3)="NO COPY ":C$(3)=CHR$(10)+"U"
1370 M$(4)="  HELP  ":C$(4)=CHR$(10)+"?"
1380 M$(5)="PRT TOGL":C$(5)=CHR$(10)+"P"
1390 M$(6)="XMITFILE":C$(6)=CHR$(10)+"T"
1400 M$(7)="XMODEM _":C$(7)="XMODEM "
1410 M$(8)="TURBODOS":C$(8)="CPM"+CR$
1420 M$(9)="ALBERT  ":C$(9)=CHR$(10)+"A"
1430 M$(10)="BRENDEL ":C$(10)=CHR$(10)+"B"
1440 M$(11)="PASSWORD":C$(11)=CHR$(10)+"C"
1450 M$(12)="XMODEM S":C$(12)=CHR$(10)+"D"
1460 M$(13)="        ":C$(13)=""
1470 M$(14)="        ":C$(14)=""
1480 M$(15)="        ":C$(15)=""
1490 M$(16)="        ":C$(16)=""
1500 RETURN
1510 REM***********DBASEII*******************
1520 HEAD$=""
1530 M$(1)="        ":C$(1)=""
1540 M$(2)="        ":C$(2)=""
1550 M$(3)="        ":C$(3)=""
1560 M$(4)="        ":C$(4)=""
1570 M$(5)="        ":C$(5)=""
1580 M$(6)="        ":C$(6)=""
1590 M$(7)="        ":C$(7)=""
1600 M$(8)="        ":C$(8)=""
1610 M$(9)="        ":C$(9)=""
1620 M$(10)="        ":C$(10)=""
1630 M$(11)="        ":C$(11)=""
1640 M$(12)="        ":C$(12)=""
1650 M$(13)="        ":C$(13)=""
1660 M$(14)="        ":C$(14)=""
1670 M$(15)="        ":C$(15)=""
1680 M$(16)="        ":C$(16)=""
1690 RETURN
1700 REM***********ADVENTURE*****************
1710 HEAD$="                           ADVENTURE FUNCTIONS"
1720 M$(1)=" LOOK   ":C$(1)="LOOK"+CR$
1730 M$(2)="INVNTORY":C$(2)="INVENT"+CR$
1740 M$(3)="  TAKE  ":C$(3)="TAKE "
1750 M$(4)="  DROP  ":C$(4)="DROP "
1760 M$(5)="  HELP  ":C$(5)="HELP"+CR$
1770 M$(6)="  QUIT  ":C$(6)="QUIT"+CR$
1780 M$(7)="  SAVE  ":C$(7)="SAVE"+CR$
1790 M$(8)="RESTORE ":C$(8)="RESTORE"+CR$
1800 M$(9)="        ":C$(9)=""
1810 M$(10)="        ":C$(10)=""
1820 M$(11)="        ":C$(11)=""
1830 M$(12)="        ":C$(12)=""
1840 M$(13)="        ":C$(13)=""
1850 M$(14)="        ":C$(14)=""
1860 M$(15)="        ":C$(15)=""
1870 M$(16)="        ":C$(16)=""
1880 RETURN
1890 REM***********         *****************
1900 HEAD$=""
1910 M$(1)="        ":C$(1)=""
1920 M$(2)="        ":C$(2)=""
1930 M$(3)="        ":C$(3)=""
1940 M$(4)="        ":C$(4)=""
1950 M$(5)="        ":C$(5)=""
1960 M$(6)="        ":C$(6)=""
1970 M$(7)="        ":C$(7)=""
1980 M$(8)="        ":C$(8)=""
1990 M$(9)="        ":C$(9)=""
2000 M$(10)="        ":C$(10)=""
2010 M$(11)="        ":C$(11)=""
2020 M$(12)="        ":C$(12)=""
2030 M$(13)="        ":C$(13)=""
2040 M$(14)="        ":C$(14)=""
2050 M$(15)="        ":C$(15)=""
2060 M$(16)="        ":C$(16)=""
2070 RETURN
2080 REM***********         *****************
2090 HEAD$=""
2100 M$(1)="        ":C$(1)=""
2110 M$(2)="        ":C$(2)=""
2120 M$(3)="        ":C$(3)=""
2130 M$(4)="        ":C$(4)=""
2140 M$(5)="        ":C$(5)=""
2150 M$(6)="        ":C$(6)=""
2160 M$(7)="        ":C$(7)=""
2170 M$(8)="        ":C$(8)=""
2180 M$(9)="        ":C$(9)=""
2190 M$(10)="        ":C$(10)=""
2200 M$(11)="        ":C$(11)=""
2210 M$(12)="        ":C$(12)=""
2220 M$(13)="        ":C$(13)=""
2230 M$(14)="        ":C$(14)=""
2240 M$(15)="        ":C$(15)=""
2250 M$(16)="        ":C$(16)=""
2260 RETURN
