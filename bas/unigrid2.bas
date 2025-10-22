10 CLS$=CHR$(26):' character to clear screen, set for your terminal 
20 ' =======================================================================
30 ' Version 2, 3 may 87 by Jim Lill, WA2ZKD
40 ' - optimized for CP/M, MBASIC 5.0
50 ' - changed text to upper and lower case for easier reading.
60 ' - added a inkey$ sub-routine for improved user interface
70 ' =======================================================================
80 ' worldwide QTH locator, contest scoring and map program by N6NB.
90 ' *a public domain program for use on apple, commodore, ibm, trs-80
100 '    and other microcomputers with basic and at least 32k of ram.
110 ' *this program converts Lat-Long to 4 and 6-digit locators, calculates
120 '    beam headings and distance between locators, tallies locator-based
130 '    contest scores, and provides map-to-locator translations.
140 ' *thanks to WA1JXN, W3RUU, KC6A and SM5AGM for their suggestions.
150 ' *note:  enter Minus sign ('-') for east Longitude or south latitude.
160 '  --if 0 Degrees east or south, use Minus sign ('-') with Minutes.
170 '   (examples:  -31 Degr, 10.1 Mins or 0 Degr, -10.1 Mins).
180 PI=3.14159:RA=57.2958:DEF FNA(X)=INT(X*100+.5)/100:PT=0:NR=5:C1=0
190 M(1)=50:M(2)=100:M(3)=150:M(4)=250:F(1)=1:F(2)=2:F(3)=3:F(4)=4:F(5)=5
200 U(1)=82:U(2)=82:U(3)=57:U(4)=57:U(5)=88:U(6)=88
210 L(1)=65:L(2)=65:L(3)=48:L(4)=48:L(5)=65:L(6)=65
220 SX(1)=.06336:SX(2)=.12672:SX(3)=.25344:SX(4)=1.01376:SX(5)=2.64
230 SY(1)=13.7149:SY(2)=6.85747:SY(3)=3.42873:SY(4)=.857184:SY(5)=.329159
240 S$(1)="1:1,000,000 scale":S$(2)="1:500,000 scale":ML$=" Mi"
250 S$(3)="1:250,000 scale":S$(4)="1:62,500 scale":S$(5)="1:24,000 scale"
260 PRINT CLS$
270 PRINT:PRINT:PRINT "  QTH Locator Program Startup Menu"
280 PRINT:PRINT "1 - Convert locators to coordinates"
290 PRINT "2 - Convert coordinates to locators"
300 PRINT "3 - Obtain locator of a point on map"
310 PRINT "4 - Pinpoint a known locator on map"
320 PRINT "5 - Compute DX and contest scores"
330 PRINT "6 - Change contest scoring system"
340 PRINT "7 - Exit"
350 PRINT:PRINT "Enter 1,2,3,4,5,6 or 7 ==>  ";:' get CN
360 K$=INKEY$
370 IF K$="" THEN 360
380 CN = ASC(K$) - 48
390 ON CN GOTO 430,580,1810,2160,780,1260,1690
400 PRINT "invalid choice.":GOTO 270
410 ' locator-to-coordinate conversion routine; 4 and 6-digit locators ok.
420 ' if 4 digits, approximate center of area is assumed.
430 PRINT CLS$: PRINT "Enter locator to convert:":GOSUB 440:GOTO 270
440 INPUT G1$
450 IF LEN(G1$)=4 THEN G1$=G1$+"MM"
460 IF LEN(G1$)<>6 THEN 1470
470 FOR K=1 TO 6:A(K)=ASC(MID$(G1$,K,1))
480 IF A(K)>U(K) OR A(K)<L(K) THEN 1470
490 NEXT K
500 LO=180-(A(1)-65)*20-(A(3)-48)*2-(A(5)-64.5)/12
510 LA=-90+(A(2)-65)*10+A(4)-48+(A(6)-64.5)/24
520 XO$="W Long":LX=ABS(LO):IF LO<0 THEN XO$="E Long"
530 XA$="n Lat":LY=ABS(LA):IF LA<0 THEN XA$="s Lat"
540 OM=(LX-INT(LX))*60:AM=(LY-INT(LY))*60
550 PRINT:PRINT G1$;" = ";INT(LX);"Deg ";FNA(OM);"Min ";XO$
560 PRINT TAB(10)INT(LY);"Deg ";FNA(AM);"Min ";XA$:RETURN
570 ' coordinate-to-locator conversion routine
580 PRINT CLS$:GOSUB 590:GOSUB 710:GOTO 270
590 PRINT:PRINT "use (-) for East Long, South Lat"
600 PRINT "Enter the Longitude (Degrees,Mins)":INPUT LO,OM
610 L2=ABS(OM):IF LO<0 THEN OM=-L2
620 L1=ABS(LO):LO=LO+OM/60:XO$="W Long":IF LO<0 THEN XO$="E Long"
630 IF L1>179 THEN 1440
640 IF L2>59.99 THEN 1440
650 PRINT "Enter the Latitude (Degs,Mins)":INPUT LA,AM
660 L4=ABS(AM):IF LA<0 THEN AM=-L4
670 L3=ABS(LA):LA=LA+AM/60:XA$="n Lat":IF LA<0 THEN XA$="s Lat"
680 IF L3>89 THEN 1440
690 IF L4>59.99 THEN 1440
700 QA=LA:QO=LO:RETURN
710 QP=(180-QO)/20:C=INT(QP):B$=CHR$(C+65):R=(QP-C)*10:C=INT(R):D$=CHR$(C+48)
720 M=(R-C)*24:C=INT(M):F$=CHR$(C+65):QB=(QA+90)/10:C=INT(QB):C$=CHR$(C+65)
730 R=(QB-C)*10:C=INT(R):E$=CHR$(C+48):M=(R-C)*24:C=INT(M):G$=CHR$(C+65)
740 A$=B$+C$+D$+E$+F$+G$
750 PRINT:PRINT "at ";INT(L1);"/";FNA(L2);XO$;" - ";INT(L3);"/";FNA(L4);XA$
760 PRINT "The Gridlocator is ";A$:RETURN
770 ' contest scoring routine--computes DX, beam headings and point totals.
780 PRINT CLS$:PRINT  "Enter your own QTH locator:":GOSUB 440
790 HO=LO/RA:HA=LA/RA:H$=G1$:XX=0
800 PRINT:INPUT "Locator or Command ('?' for menu) ";G1$
810 IF G1$="QRT" THEN PRINT:GOTO 1200
820 IF G1$="X" THEN 1480
830 IF G1$="?" THEN 1500
840 IF G1$="+" THEN 1580
850 IF G1$="-" THEN 1640
860 IF G1$="C" THEN GOSUB 590:GOSUB 710:PRINT:GOTO 800
870 IF G1$="M" THEN GOSUB 1730:PRINT:GOTO 800
880 IF LEN(G1$)>3 THEN GOSUB 450:GOSUB 900:GOTO 1190
890 PRINT "Invalid Entry.  Please try again!":GOTO 800
900 LO=LO/RA:LA=LA/RA:ZL=LA
910 L=HO-LO:IF L<>0 THEN 940
920 IF HA>ZL THEN AZ=180:GOTO 1040
930 IF HA<=ZL THEN AZ=0:GOTO 1040
940 IF L>PI THEN L=L-2*PI
950 IF L<-PI THEN L=L+2*PI
960 IF SIN(LA)=0 THEN AA=PI/2:GOTO 980
970 AA=COS(L)*(COS(LA)/SIN(LA)):AA=ATN(AA)
980 IF SIN(AA)=0 THEN AZ=0:GOTO 1000
990 AZ=((COS(L)/SIN(L))*COS(HA+AA))/SIN(AA):IF AZ<>0 THEN AZ=ATN(1/AZ)
1000 AZ=AZ*RA:L=L*RA
1010 IF L>0 AND AZ<0 THEN AZ=AZ+180
1020 IF L<0 AND AZ>0 THEN AZ=AZ+180
1030 IF L<0 AND AZ<0 THEN AZ=AZ+360
1040 AZ=INT(AZ+.5):DX=(SIN(HA)*SIN(LA))+(COS(HA)*COS(LA)*COS(HO-LO))
1050 IF DX>1 THEN DX=1
1060 IF DX<=-1 THEN DX=180:GOTO 1130
1070 DX=SQR(1-(DX*DX))/DX
1080 IF HO<>LO THEN 1110
1090 IF HA=>ZL THEN DX=HA-LA:GOTO 1120
1100 IF HA<ZL THEN DX=LA-HA:GOTO 1120
1110 DX=ATN(DX)
1120 DX=DX*RA:IF DX<0 AND DX>-90 THEN DX=DX+180
1130 DX=DX*69.0468:KM=DX/.6215:DX=FNA(DX):KM=FNA(KM):PX=F(1)
1140 PRINT "DX from center of ";H$;" to ";G1$;":"
1150 PRINT TAB(6)DX;" Mi";" and ";KM;" KM":IF ML$=" Mi" THEN KM=DX
1160 PRINT TAB(6)AZ;" Degrees Azimuth"
1170 FOR J=1 TO NR-1:IF KM=>M(J) THEN PX=F(J+1)
1180 NEXT J:RETURN
1190 PRINT TAB(6)PX;" Pt(s) for this QSO":PT=PT+PX:D9=D9+KM:QS=QS+1:XX=1
1200 PRINT:PRINT TAB(6)"----------------------"
1210 PRINT TAB(6)PT;" Total Pts"
1220 PRINT TAB(6)D9;" ";ML$;" Total DX"
1230 PRINT TAB(6)QS;" QSOs Entered":IF G1$="QRT" THEN 1690
1240 GOTO 800
1250 ' routine to modify scoring system.
1260 PRINT CLS$:PRINT  "Unless you change the values here,"
1270 PRINT "This scoring system will apply:":PRINT
1280 PRINT F(1);" Pt(s) per QSO if DX < ";M(1);ML$:IF NR<=2 THEN 1320
1290 FOR J=2 TO NR-1
1300 PRINT F(J);" Pts if DX = ";M(J-1);" to ";M(J);ML$
1310 NEXT J
1320 PRINT F(NR);" Pts if DX => ";M(NR-1);ML$:PRINT
1330 INPUT "Are these values correct (y/n)";OK$
1340 IF OK$="Y" OR OK$="y" THEN 270
1350 PRINT:INPUT "Use miles (Mi) or Kilometers (KM)";ML$:ML$=" "+ML$
1360 PRINT:INPUT "Enter the lowest Pt value";F(1):NR=2
1370 PRINT "Enter maximum DX for ";F(1);" Pt(s)";:INPUT M(1)
1380 PRINT:INPUT "Enter the next point value";F(NR)
1390 PRINT "Enter maximum DX for "F(NR);" Pts"
1400 INPUT "(if no higher limit exists, enter 0)";M(NR)
1410 IF M(NR)=0 THEN 1250
1420 NR=NR+1:GOTO 1380
1430 ' operator messages and editing functions
1440 PRINT "Entry incorrect.  Maximum Coordinates:"
1450 PRINT "89 Deg latitude, 179 Deg Longitude,"
1460 PRINT "and 59.99 Minutes":GOTO 590
1470 PRINT "Invalid Entry Format.  Please Try Again.":GOTO 440
1480 IF XX=0 THEN PRINT "Can't delete":GOTO 800
1490 XX=0:QS=QS-1:PT=PT-PX:D9=D9-KM:PRINT "--last entry deleted--":GOTO 1200
1500 PRINT:PRINT:PRINT TAB(12)"Data Entry Menu":PRINT
1510 PRINT "You may enter a station's locator, or--"
1520 PRINT:PRINT "'X' to delete the last entry"
1530 PRINT "'+' to add prior qsos to totals"
1540 PRINT "'-' to delete any previous qso"
1550 PRINT "'c' to convert coordinates to locator"
1560 PRINT "'m' to perform map operations"
1570 PRINT "'QRT' to end session":PRINT:GOTO 800
1580 PRINT:PRINT:PRINT "this option allows you to add QSOs,"
1590 PRINT "DX, and contest points from"
1600 PRINT "a previous session to your totals.":PRINT
1610 PRINT "how many QSOs to add?":INPUT Q1:QS=QS+Q1
1620 PRINT "how many total miles (or KM) to add?":INPUT D1:D9=D9+D1
1630 PRINT "how many points to add?":INPUT P1:PT=PT+P1:GOTO 1200
1640 PRINT:PRINT:PRINT "this option allows you to delete"
1650 PRINT "any previous QSO from the totals"
1660 PRINT "by entering its locator.":PRINT
1670 INPUT "locator to delete";G1$:GOSUB 450:GOSUB 900
1680 QS=QS-1:PT=PT-PX:D9=D9-KM:XX=0:GOTO 1200
1690 PRINT CLS$:PRINT "note:   you have exited the program."
1700 PRINT "be sure to write down your data"
1710 PRINT "before turning off your computer!":END
1720 ' map conversion routines 
1730 PRINT:PRINT "map operations.  choose either--"
1740 PRINT "1 - obtain locator of a point on map"
1750 PRINT "2 - pinpoint a known locator on map"
1760 PRINT "enter 1 or 2";:INPUT M9
1770 IF M9=1 THEN GOSUB 1820:GOTO 800
1780 IF M9=2 THEN GOSUB 2170:GOTO 800
1790 PRINT "invalid choice--try again":GOTO 1730
1800 ' routines to obtain QTH locator of a point on a map
1810 PRINT CLS$:GOSUB 1820:GOTO 270
1820 GOSUB 2300:PRINT:PRINT "measure the vertical and horizontal"
1830 PRINT "distance from the reference point"
1840 PRINT "to the point for which you need"
1850 PRINT "a QTH locator.":PRINT
1860 PRINT "note: use Minus ('-') to indicate a"
1870 PRINT "distance south or east of reference pt.":PRINT
1880 INPUT "# inches vertically from ref pt.";V
1890 INPUT "# inches horizontally from ref. pt.";H
1900 IF ABS(M3+(V*S2/50))<90 THEN 1920
1910 PRINT "error: entry >90 Degr Lat":GOTO 1880
1920 C2=4:IF H=>0 AND V<0 THEN C2=1
1930 IF V=>0 AND H=>0 THEN C2=2
1940 IF V=>0 AND H<0 THEN C2=3
1950 V3=ABS(V)*S2:H3=ABS(H)*S2
1960 IF V3=0 THEN A3=90:GOTO 1980
1970 A3=(ATN(H3/V3))*RA
1980 R3=(H3^2+V3^2)^.5
1990 IF C2=1 THEN T3=A3+180
2000 IF C2=2 THEN T3=360-A3
2010 IF C2=3 THEN T3=A3
2020 IF C2=4 THEN T3=180-A3
2030 NA=(R3*(COS(T3/RA))/60)+M3:XA$="n Lat":IF NA<0 THEN XA$="s Lat"
2040 IF T3=90 THEN 2090
2050 IF T3=270 THEN 2090
2060 X=LOG(TAN((45+(M3/2))/RA)):X1=LOG(TAN((45+(NA/2))/RA))
2070 NO=M4+RA*(TAN(T3/RA))*(X-X1)
2080 GOTO 2100
2090 NO=M4-(R3*SIN(T3/RA))/(60*COS(M3/RA))
2100 IF NO=>180 THEN NO=NO-360
2110 IF NO=<-180 THEN NO=360+NO
2120 XO$="W Long":IF NO<0 THEN XO$="E Long"
2130 QA=NA:NA=ABS(NA):L3=INT(NA):L4=(NA-INT(NA))*60
2140 QO=NO:NO=ABS(NO):L1=INT(NO):L2=(NO-INT(NO))*60:GOTO 710
2150 ' routines to pinpoint a known QTH locator on a map
2160 PRINT CLS$:GOSUB 2170:GOTO 270
2170 GOSUB 2300:PRINT:PRINT "Enter the Gridlocator that you"
2180 PRINT "wish to pinpoint on your map":GOSUB 440
2190 NA=LA:NO=LO:A4=ABS((M3+NA)/2):D4=ABS(M3-NA):D5=ABS(M4-NO)
2200 D6=69.0541-.351726*COS((2*A4)/RA)
2210 D7=69.23*COS(A4/RA)-.05875*COS((3*A4)/RA)
2220 V4=D6*D4*S3:G4=D7*D5*S3
2230 X7$=" north":IF LA<M3 THEN X7$=" south"
2240 X8$=" west":IF LO<M4 THEN X8$=" east"
2250 PRINT:PRINT "the center of ";G1$;" is"
2260 PRINT FNA(V4);" inches ";X7$
2270 PRINT "from the reference point and"
2280 PRINT FNA(G4);" inches ";X8$
2290 PRINT "from the reference point":RETURN
2300 IF C1=0 THEN 2370
2310 PRINT:PRINT "current map parameters:"
2320 PRINT:PRINT "reference point is"
2330 PRINT INT(L5);"/";FNA(L6);X1$;" - ";INT(L7);"/";FNA(L8);X2$
2340 IF S1=6 THEN PRINT "map scale: ";MI;" miles/inch":GOTO 2360
2350 PRINT "map uses ";S$(S1) 
2360 INPUT "want to change map parameters (y/n)";CM$:IF CM$<>"y" THEN RETURN
2370 PRINT:PRINT "please describe your map and select"
2380 PRINT "a reference point for measurements"
2390 PRINT "+----------------------------------+"
2400 PRINT "|                :                 |"
2410 PRINT "|     X----------:                 |"
2420 PRINT "|     :          :                 |"
2430 PRINT "|     :          :                 |"
2440 PRINT "|................R.................|"
2450 PRINT "|                :                 |"
2460 PRINT "|                :                 |"
2470 PRINT "|                :                 |"
2480 PRINT "|                :                 |"
2490 PRINT "+----------------------------------+"
2500 PRINT "(R is your reference point on the map,"
2510 PRINT "and X is an unknown point or locator).":C1=1:PRINT
2520 PRINT "for your reference point on the map:"
2530 GOSUB 590:M3=LA:M4=LO:L5=L1:L6=L2:L7=L3:L8=L4:X1$=XO$:X2$=XA$
2540 PRINT:PRINT "now specify the map's scale:"
2550 PRINT:PRINT TAB(7)"1.  ";S$(1):PRINT TAB(7)"2.  ";S$(2)
2560 PRINT TAB(7)"3.  ";S$(3):PRINT TAB(7)"4.  ";S$(4)
2570 PRINT TAB(7)"5.  ";S$(5):PRINT TAB(7)"6.  any # miles/inch"
2580 PRINT:INPUT "Enter 1,2,3,4,5 or 6";S1:IF S1=6 THEN 2610
2590 IF S1>6 THEN PRINT "invalid scale--try again.":GOTO 2540
2600 S2=SY(S1):S3=SX(S1):GOTO 2310
2610 PRINT:INPUT "enter map scale in miles/inch";MI
2620 S2=MI/1.15078:S3=1/MI:GOTO 2310
