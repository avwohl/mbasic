10 :REMARK \t\tLUNAR.BAS\t\tDEMO Version
20 CLEAR 500:DEFINT E-Z:WIDTH 255
30 E$=CHR$(27):E1$=E$+"E":F$=E$+"F":G$=E$+"G":P$=E$+"p":Q$=E$+"q":Y$=E$+"Y"
40 Y5$=E$+"y5":X5$=E$+"x5":K$=E$+"K":J$=E$+"J":B$=E$+"B":D$=E$+"D":U$=CHR$(95)
50 Q1$=CHR$(34)
60 DIM U0(3):U0(0)=&H36 : U0(1)=&H1FF : U0(2)=&H77D8 : U0(3)=&HC9 
70 T=0:SF=0:Z9=0: 
80 PRINT E1$G$Q$X5$:GOSUB 2020
90 D6=L9*L9*L9*L9*L9*L9*L9*L9*L9
100 IF D6>1000 THEN D6=1000
110 B1$=Y$+"8 "
120 T5$=F$+"`"+P$+D$+D$+B$+"rU"+U$+D$+D$+D$+B$+" S "+D$+D$+D$+B$+" A "+Q$
130 T6$=B$+D$+D$+D$+D$+D$+"{x i y{"
140 T7$=T5$+T6$
150 W1$=Q$+" "+D$+D$+B$+"   "+D$+D$+D$+B$+"   "+D$+D$+D$+B$+"   "
160 W2$=B$+D$+D$+D$+D$+D$+"          "
170 W$=W1$+W2$
180 PRINT X5$E1$E$"x1"P$F$
190 GOSUB 1920
200 IF L$="L" OR L$="l" THEN 1320
210 PRINT E$"H"
220 A=10000
230 B=2000:GOSUB 410::REMARK \t\tPrint the calibration scale
240 A=10000
250 DEF USR0=VARPTR(U0(0))
260 IF USR0(0)<>0 THEN 260
270 GOTO 330
280 PRINT Q$G$Y$"#$f1 - Increase Fuel Burn"
290 PRINT Y$"$$f2 - Decrease Fuel Burn"
300 PRINT Y$"%$f3 - Maintain Fuel Burn"
310 PRINT Y$"&$f4 - Cut Fuel Burn to zero"F$:RETURN
320 :REMARK \t\t\t\t Print the rocket at the top
330 W=32::REMARK PRINT Q$Y$" a"T7$:W=32
340 L=32
350 GOSUB 490
360 :REMARK \t\t\t\tPrint the rocket coming down
370 PRINT Y$CHR$(W)"a"W$;:L=L+1:
380 PRINT Y$CHR$(L)"a"T7$Q$:W=L
390 IF Z9=1 GOTO 1210
400 GOTO 580
410 L=33
420 GOSUB 280
430 PRINT Q$Y$" Pc";
440 PRINT B$D$"`"B$D$"`"B$D$"`";
450 X$=STR$(A):PRINT B$;:FOR X=81TO 80-LEN(X$)STEP -1:PRINT CHR$(8);:NEXT X
460 PRINT A"t";:A=A-B
470 L=L+4:IF L>=52 THEN RETURN 
480 GOTO 440
490 :REMARK \t\t\t\t\tInput Output program
500 H=9400::REMARK \t\t\t\tH = Height of rocket
510 V=500: :REMARK \t\t\t\tV = Rate the rocket is falling
520 F=900:IF L9=1 THEN F=658
530 :REMARK \t\t\t\t\tF = Amount of fuel on board
540 GOSUB 800:RETURN::REMARK \t\t\tGo to print out sub-routine
550 PRINT E1$E$"H"Q$
560 PRINT B1$G$:PRINT F$
570 DEF USR0=VARPTR(U0(0)):J=USR0(0)
580 FOR X0=1 TO D6/50:PRINT Y$CHR$(W+4)"ai";:PRINT D$" "D$"i":NEXT X0
590 LX=J:DEF USR0=VARPTR(U0(0)):J=USR0(0)
600 IF J=27 THEN 580
610 IF J=0 THEN J=LX
620 PRINT Y$CHR$(W+4)"ai"
630 IF J<83 GOTO 780
640 IF J=86 GOTO 780
650 ON J-82 GOTO 700,730,660
660 V=V+5-R1
670 F=F-R1:IF F<=0THEN R1=0
680 H=H-(V+V+5)/2
690 GOTO 820
700 R1=R1+4:F=F-R1:IF F<0 THEN R1=0
710 V=V+5-R1
720 H=H-(V+V+5)/2:GOTO 820
730 R1=R1-4
740 IF R1<0 THEN R1=0
750 V=V+5-R1
760 F=F-1:IF F<0 THEN R1=0
770 H=H-(V+V+5)/2:GOTO 820
780 V=V+5-INT(R1/2):R1=0
790 H=H-V:F=F-INT(R1/2):GOTO 830
800 PRINT P$Y$"7   ALTITUDE   RATE OF DECENT   ELAPSED TIME   FUEL REMAINING";
810 PRINT "   RATE OF BURN";:RETURN 
820 REM
830 T=T+1
840 IF F<0 THEN F=0
850 H=INT(H)
860 GOSUB 2330
870 D=A/22
880 N=INT(H/D+0.5)
890 N=21-N
900 N=N+31
910 IF L9=1 THEN IF T=38 GOTO 1490
920 IF L9=2 THEN IF T=60 GOTO 1490
930 IF N<32 GOTO 1850
940 IF N=L GOTO 580
950 L=N-1
960 IF A=10000 AND H<2000 GOTO 1030
970 IF A=2000 AND H<400 GOTO 1070
980 IF H<0 GOTO 1490
990 IF A=400 AND H<80 GOTO 1110
1000 IF A=100 AND H<16 GOTO 1150
1010 IF H<8 AND V<8 GOTO 1190
1020 GOTO 370
1030 A=2000:B=400
1040 GOSUB 410
1050 A=2000
1060 L=32:GOTO 370
1070 A=400:B=80
1080 GOSUB 410
1090 A=400
1100 L=32:GOTO 370
1110 A=100:B=20
1120 GOSUB 410
1130 A=100
1140 L=32:GOTO 370
1150 A=16:B=4
1160 GOSUB 410
1170 A=16
1180 L=32:GOTO 370
1190 Z9=1:L=48
1200 GOTO 370
1210 PRINT Y$"1`"E$"b"D$D$B$E$"o"Y$"3P "Y$"4K      "E$"H"P$G$
1220 PRINT Y$"7 "STRING$(75,32)E$"H"Q$E$"y1":PRINT E$"x1"Q$
1230 A$="Houston . . . Tranquility Base Here . . . The Eagle has landed . ."
1240 A$=A$+" . . . .  "
1250 PRINT Y$"8o";
1260 FOR X=1 TO LEN(A$)
1270 PRINT MID$(A$,X,1)
1280 PRINT E$"N"
1290 PRINT Y$"8o";
1300 FOR X0=1 TO 100:NEXT X0
1310 NEXT X
1320 PRINT Q$Y$")>COUNTDOWN"P$
1330 PRINT Q$Y$"1a"T7$Y$"5a "
1340 PRINT P$Y$"*:                 "Y$"+:                 "Y$",:                 "
1350 FOR X=10 TO 0 STEP -1 
1360 IF X<3 THEN FOR X0=1 TO 25:PRINT Q$Y$"5ai"D$" "P$:GOTO 1380
1370 FOR X0=1 TO 150
1380 NEXT X0
1390 IF X=0 THEN PRINT Q$Y$"5"U$"|   }"P$Y$"6`"U$Q$" "P$"r"
1400 PRINT Y$"+A\a"X:NEXT X
1410 PRINT Y$"+=BLASTOFF!!!!\a"
1420 FOR Q=49 TO 32 STEP -1
1430 PRINT Q$Y$CHR$(Q)"a"T5$Y$CHR$(Q+4)"ai"
1440 IF Q=32 THEN 1460
1450 PRINT Y$CHR$(Q)"a"W1$Y$CHR$(Q+4)"a "
1460 NEXT Q
1470 PRINT G$Q$
1480 PRINT E$"y1":FOR Q=1 TO 150:NEXT Q:GOTO 2380
1490 PRINT Y$"  "E1$P$G$:PRINT E$;"y1":PRINT Y$" 1";
1500 FOR X=32 TO 56
1510 PRINT "    ";
1520 PRINT D$D$D$D$B$;
1530 NEXT X
1540 PRINT Y$"( "STRING$(38,32)
1550 PRINT STRING$(38,32)Q$
1560 L=43
1570 GOSUB 1840
1580 PRINT "This is all that marks the spot where"
1590 L=44
1600 GOSUB 1840
1610 PRINT "your Space Cruiser smashed into the"
1620 L=45
1630 GOSUB 1840
1640 PRINT "Lunar Surface.  Amazingly, noone was"
1650 L=46
1660 GOSUB 1840
1670 PRINT "hurt.  After 2 years in the hospital,"
1680 L=47
1690 GOSUB 1840
1700 PRINT "the president gave you command of the"
1710 L=48
1720 GOSUB 1840
1730 PRINT "Galactic Garbage Ship, U.S.S. Hefty."
1740 L=49
1750 GOSUB 1840
1760 PRINT "However, you may be banned from ever "
1770 L=50
1780 GOSUB 1840
1790 PRINT "landing on the moon again."
1800 DEF USR0=VARPTR(U0(0))
1810 IF USR0(0)<>0 THEN 1810
1820 PRINT Y$"68Depress RETURN for your landing statistics."Y5$;:C$=INPUT$(1)
1830 GOTO 2410
1840 PRINT Y$CHR$(L)"=";:RETURN 
1850 IF H>16 AND A=16 GOTO 1110
1860 IF H>100 AND A=100 GOTO 1070
1870 IF H>400 AND A=400 GOTO 1030
1880 A=10000:B=2000
1890 GOSUB 410
1900 A=10000:L=32:GOTO 370
1910 RETURN
1920 PRINT Y$"3Ir"Q$TAB(37)P$"r"
1930 PRINT Y$"4*r y"U$Y$"47r"U$;
1940 PRINT Y$"4Hrx"Y$"4Rr "U$;
1950 PRINT Y$"4Vr"U$Y$"4ir " Y$"5#r"U$Y$"5)r    x"
1960 PRINT Y$"52rx"U$Y$"56r  x"Y$"5"CHR$(64)"rq";
1970 PRINT Y$"5Er"U$"ry "Y$"5Nrx"U$"ry x y  y"U$
1980 PRINT Y$"5hry "Y$"6 ry  x"U$Y$"6'r y     x";
1990 PRINT Y$"62y   y   "U$Y$"6<nor   "U$"rpy    ";
2000 PRINT Y$"6Lr             x  x  y   y  x   "Y$"7 "STRING$(75,32);
2010 RETURN
2020 PRINT Y$" *The object of your mission, Captain, is to safely land"
2030 PRINT Y$"!%your ship at 3 ft/sec on the surface of Jupiter's ninth moon."
2040 PRINT Y$Q1$"%Due to the complexity of your cargo and unpredictabity of"
2050 PRINT Y$"#%the lunar gravitational pressure, you must understand, Sir,"
2060 PRINT Y$"$%that your cargo may react violently with the gravitational"
2070 PRINT Y$"%%pressure causing self-destruction of cargo and ship."
2080 PRINT Y$"'*To command and land your ship; depress the following keys
2090 PRINT Y$"(%to do said operation:"
2100 PRINT Y$"+0f1 ==> Increase Fuel Burn by four (4) units/sec"
2110 PRINT Y$"-0f2 ==> Decrease Fuel Burn by four (4) units/sec"
2120 PRINT Y$"/0f3 ==> Maintain Fuel Burn at present level of units/sec"
2130 PRINT Y$"10f4 ==> Cut Fuel Burn to zero (0) units/sec"
2140 PRINTY$"3%Are you ready to proceed, Sir? . . . If so, depress RETURN. "Y5$;
2150 C$=INPUT$(1):GOTO 2160
2160 PRINT E1$
2170 PRINT X5$Y$"!.Our Primary Data Station indicates three possible landing"
2180 PRINT Y$Q1$".levels, based on your projected limited fuel and possible"
2190 PRINT Y$"#.limited time period, before your complete destruction."
2200 PRINT Y$"$.The levels are as follows:"
2210 PRINT Y$"&.Level 3 ==>  900 units of fuel remain"
2220 PRINT Y$"';no time limit exists"
2230 PRINT Y$").Level 2 ==>  CAUTION !!!"
2240 PRINT Y$"*;900 units of fuel remain"
2250 PRINT Y$"+;60 seconds remain before self-destruction!"
2260 PRINT Y$"-.Level 1 ==>  EMERGENCY !!!
2270 PRINT Y$".;Only 658 units of fuel remain"
2280 PRINT Y$"/;only 38 seconds remain before complete devastation!"
2290 PRINT Y$"2.ENTER LEVEL (3,2 or 1) <1> ? "Y5$;:L$=INPUT$(1):\n\tIF L$=CHR$(13) THEN L$="1"
2300 IF L$="l" OR L$="L" THEN RETURN
2310 L9=INT(VAL(L$)):IF VAL(L$)<1 OR VAL(L$)>3 THEN 2290
2320 RETURN
2330 PRINT Y$"8 "G$USING "###### ft";H;
2340 PRINT USING "########## ft/sec";V;
2350 PRINT USING "######### sec";T;
2360 PRINT USING "############ units";F;
2370 PRINT USING "####### units/sec";R1;:PRINT F$;:RETURN
2380 DEF USR0=VARPTR(U0(0))
2390 IF USR0(0)<>0 THEN 2390
2400 SF=5
2410 PRINT E1$X5$Y$" .The following list is your landing statistics:"
2420 PRINT Y$Q1$".Amount of time used:"USING"############# sec";T
2430 IF L9=2 THEN T2=60-T :ELSE IF L9=1 THEN T2=38-T :ELSE GOTO 2450
2440 PRINT Y$"$.Amount of time remaining:"USING"######### sec";T2
2450 IF L9=1 THEN F9=658-F :ELSE F9=900-F
2460 PRINT Y$"&.Amount of fuel used:"USING"############## gal";F9
2470 PRINT Y$"(.Amount of fuel remaining:"USING"######### gal";F
2480 IF SF=5 THEN 2490 :ELSE 2500
2490 IF V>3 THEN V=3:IF V<=3 THEN 2530 
2500 IF (L9=1 AND T<38) OR (L9=2 AND T<60) THEN 2530
2510 IF L9=3 THEN GOTO 2530 :ELSE IF H<0 THEN H=0
2520 PRINT Y$"*.Altitude at time expiration:"USING"###### ft";H
2530 PRINT Y$",.Rate of Descent at finish:"USING"######## ft/sec";V
2540 PRINT Y$"5+Do you wish to attempt the mission again? Y or N <Y>? "Y5$;
2550 C$=INPUT$(1):IF C$="N" OR C$="n" THEN 2560 :ELSE 20
2560 PRINT Y5$E1$:RUN"MENU":END
