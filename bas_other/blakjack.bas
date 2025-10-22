10 '         *+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*
20 '         *+                                             +*
30 '         *+  Graphics Games for the Osborne I Computer  +*
40 '         *+      Courtesy of Kelly Smith, CP/M-Net      +* 
50 '         *+              (805) 527-9321                 +*
60 '         *+                   and                       +*
70 '         *+       Wizard of OsZ, (213) 341-9399         +*
80 '         *+                                             +*
90 '         *+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*
100 '
110 ' Wizard of OsZ, P.O. Box 964, Chatsworth, CA 91311 (213) 341-9399
120 '
130 ' ---------------- Osborne I Terminal Commands -------------------
140 '
150 '
160 E$=CHR$(27): '                Escape Character
170 CLS$=CHR$(26): '              Clear Screen
180 DC$=E$+"=": '                 Direct Cursor Addressing
190 GY$=E$+"g": '                 Graphics On
200 GN$=E$+"G": '                 Graphics Off
210 HO$=E$+CHR$(1): '             Cursor Home
220 EP$=E$+"T": '                Erase to End of Line
230 DY$=E$+")": '                DIM Display On
240 DN$=E$+"(": '                DIM Display Off
250 UY$=E$+"l": '                Start Underlining
260 UN$=E$+"m": '                End Underlining
270 'NOTE: The Osborne I uses the following scheme for direct cursor addressing:
280 '      Location= (CHR$(Line number+32));(CHR$(Column number+32))
290 PRINT CLS$
300 PRINT"          The Wizard of OsZ - 'Black-Jack'"
310 PRINT
320 PRINT:PRINT"Do you require instructions (Y or N) ?";
330 A$=INKEY$:IF LEN(A$)=0 THEN GOTO 330 ' get keyboard input
340 IF A$="N" OR A$="n" THEN PRINT CLS$:GOTO 430
350 PRINT CLS$;UY$;"  The Wizard of OsZ Casino house limit is $10,000   ";UN$;:PRINT
360 PRINT:PRINT "Your choices to the question HIT are as follows:":PRINT
370 PRINT "0 <-- NO HIT";DY$;" on this hand";DN$
380 PRINT "1 <-- HIT";DY$;" on this hand";DN$
390 PRINT "2 <-- DOUBLE BET";DY$;" after seeing cards 1 and 2 and HIT";DN$
400 PRINT "3 <-- SPLIT";DY$;" the hand, for two pairs";DN$
410 PRINT:PRINT "To stop the game, enter a ";UY$;"0";UN$;" for your wager.":PRINT
420 DIM W[10]
430 K=K1=W1=C2=0
440 NB$=STRING$(6,127)
450 MD$=STRING$(1,127)+STRING$(4,32)+STRING$(1,127)
460 DIM Q[52]:DIM D[52]
470 PRINT:PRINT TAB(15);"Press any key to begin play...";
480 IF INKEY$="" THEN RS=RS+1:GOTO 480
490 RANDOMIZE RS
500 PRINT CLS$
510 FOR I=1 TO N/2
520	X=INT(RND*100):IF X>51 THEN GOTO 520
530 NEXT I
540 FOR A=1 TO 52
550   D[A]=0
560 NEXT A
570 FOR A=0 TO 39 STEP 13
580   FOR C=1 TO 13
590     Q[A+C]=C
600   NEXT C
610 NEXT A
620 PRINT 
630 K=K+1
640 FOR P=1 TO 5
650   E[P]=0
660   V[P]=0
670   T[P]=0
680 NEXT P
690 V[3]=1
700 ' ask for wager entry, clearing any overflow digits from screen
710 PRINT DC$+CHR$(53)+CHR$(32);"Enter your wager";EP$
720 PRINT DC$+CHR$(53)+CHR$(48); ' reposition for new wager entry                  
730 P=1
740 INPUT W2
750 PRINT
760 W[2]=W2
770 IF W2<=0 THEN GOTO 3490
780 IF W2<=10000 THEN GOTO 840
790 FOR I = 1 TO 50
800	PRINT DC$+CHR$(1)+CHR$(34);"That's too much...the casino limit is $10,000!";
810	FOR X=1 TO 20:NEXT X:PRINT DC$+CHR$(1)+CHR$(32);EP$
820 NEXT I
830 GOTO 710
840 PRINT DC$+CHR$(1)+CHR$(33);
850 FOR TPT=1 TO 20
860   PRINT DC$+CHR$(TPT+32)+CHR$(32);EP$
870 NEXT TPT
880 PRINT DC$+CHR$(1)+CHR$(33);"Dealers hand";DC$+CHR$(12)+CHR$(33);"Your hand"
890 CLM=3
900 LN=2
910 PRINT HO$; ' home cursor
920 FOR HH=1 TO 9:PRINT EP$+CHR$(10);:NEXT HH ' sanitize screen
930 PRINT EP$
940 GOSUB 2180 : ' deal the cards
950 GOSUB 3530:PRINT DY$; ' begin half intensity
960 FOR TPT=1 TO 3 ' dealers card down (and dirty!)
970   PRINT DC$+CHR$(LN+TPT)+CHR$(CLM+33);"****":NEXT TPT
980 PRINT DN$ ' end half intensity
990 IF E[1]=0 THEN GOTO 1010
1000 V[4]=1
1010 V[5]=1
1020 GOSUB 2180 : ' deal the cards
1030 M=X
1040 P=2
1050 LN=10
1060 CLM=3
1070 GOSUB 2180 : ' deal the cards
1080 G=X
1090 ' next card up
1100 GOSUB 2180 : ' deal the cards
1110 IF V[2]>0 THEN GOTO 1540
1120 S=X
1130 IF V[3]<>1 THEN GOTO 1540
1140 IF T[P]<>21 THEN GOTO 1260
1150 FOR I=1 TO 50 ' flash opponent blackjack win and ring bell
1160	PRINT DC$+CHR$(15)+CHR$(32);"         >>>BLACKJACK<<<";CHR$(7);
1170	FOR X=1 TO 20:NEXT X:PRINT DC$+CHR$(15)+CHR$(41);EP$
1180 NEXT I
1190 PRINT DC$+CHR$(8)+CHR$(32);"My hole card was ",
1200 X=M
1210 CLM=10
1220 LN=2
1230 GOSUB 2550 : ' print card
1240 W1=W1+W2*2
1250 GOTO 3130
1260 IF V[4]=0 THEN GOTO 1450
1270 PRINT DC$+CHR$(7)+CHR$(32);"Do you want to buy insurance (Y for YES, N for NO)";EP$
1280 PRINT "If YES and I have BLACKJACK, you ";UY$;"win $";W2;UN$
1290 PRINT "If not, you ";UY$;"lose $";W2/2;UN$;" to the Wizard of OsZ Casino";EP$
1300 INPUT X$
1310 PRINT 
1320 IF LEFT$(X$,1)="N" OR LEFT$(X$,1)="n" THEN GOTO 1400
1330 IF T[1]<>21 THEN GOTO 1400
1340 W1=W1+W2
1350 FOR I=1 TO 50 ' flash "you win on insurance"
1360	PRINT DC$+CHR$(1)+CHR$(32);"   You win $";W2;" on your insurance bet";
1370	FOR X=1 TO 20:NEXT X:PRINT DC$+CHR$(1)+CHR$(32);EP$
1380 NEXT I
1390 GOTO 1450
1400 W1=W1-W2/2
1410 FOR I=1 TO 50 ' flash "You lost on insurance"
1420	PRINT DC$+CHR$(1)+CHR$(32);"   You lost $";W2/2;" on your insurance bet";
1430	FOR X=1 TO 20:NEXT X:PRINT DC$+CHR$(1)+CHR$(32);EP$
1440 NEXT I
1450 IF T[1]<>21 THEN GOTO 1540
1460 FOR I=1 TO 50 ' flash dealer blackjack win and ring bell
1470	PRINT DC$+CHR$(7)+CHR$(32);"         >>>BLACKJACK<<<";CHR$(7);
1480	FOR X=1 TO 20:NEXT X:PRINT DC$+CHR$(7)+CHR$(41);EP$
1490 NEXT I
1500 X=M
1510 LN=2:CLM=10
1520 GOSUB 2550 : ' print card
1530 GOTO 3110
1540 IF T[P]<=21 THEN GOTO 1650
1550 IF E[P]>0 THEN GOTO 1630
1560 PRINT DC$+CHR$(16)+CHR$(32);"You busted!  ";
1570 PRINT "Your total was";T[P];EP$;
1580 FOR I=1 TO 500:NEXT I ' delay for readability
1590 IF V[2]=1 THEN GOTO 1950
1600 CLM=9
1610 LN=2
1620 GOTO 2890 : ' dealer plays
1630 E[P]=E[P]-1
1640 T[P]=T[P]-10
1650 IF V[1]=2 THEN GOTO 1570
1660 V[3]=V[3]+1
1670 FOR I=1 TO 10:PRINT DC$+CHR$(15)+CHR$(32);EP$
1680 FOR X=1 TO 10:NEXT X ' flash hit request on screen
1690	PRINT CHR$(7);DC$+CHR$(15)+CHR$(32);"Hit";
1700 FOR X=1 TO 10:NEXT X
1710 NEXT I
1720 INPUT X:V[1]=X
1730 IF V[1]<>3 THEN GOTO 2090
1740 IF V[2]>0 THEN GOTO 2070
1750 IF V[3]<>2 THEN GOTO 2070
1760 IF Q[G]=Q[S] THEN GOTO 1790
1770 PRINT "Now really, does that look like a PAIR?";EP$
1780 GOTO 1670
1790 V[2]=1
1800 IF Q[G]<>1 THEN GOTO 1820
1810 V[1]=2
1820 P=3
1830 PRINT DC$+CHR$(21)+CHR$(32);"Playing ";UY$;"HAND ONE";UN$;" now";EP$
1840 ' 1st card
1850 CLM=3
1860 W[3]=W2
1870 X=G
1880 GOSUB 1900
1890 GOTO 1090 : ' next card
1900 GOSUB 2460
1910 GOSUB 2550 : ' print card
1920 V[3]=1
1930 T[P]=C
1940 RETURN 
1950 P=2
1960 V[2]=2
1970 PRINT DC$+CHR$(21)+CHR$(32);"Playing ";UY$;"HAND TWO";UN$;" now"
1980 PRINT DC$+CHR$(42)+CHR$(32); ' boogie back to last hand position and...
1990 FOR HH=1 TO 5:PRINT EP$+CHR$(10);:NEXT HH ' clear last hand delt
2000 X=S
2010 LN=10
2020 CLM=3
2030 GOSUB 1900
2040 IF Q[G]=1 THEN GOTO 2060
2050 V[1]=0
2060 GOTO 1090 : ' next card
2070 PRINT "No splits now, try again..."
2080 GOTO 1670
2090 IF V[1]<>2 THEN GOTO 2140
2100 IF V[3]=2 THEN GOTO 2130
2110 PRINT "Too late to double!";EP$
2120 GOTO 1670
2130 W[P]=2*W[P]
2140 IF V[1]>0 THEN GOTO 1090 : ' next card
2150 CLM=10
2160 LN=10
2170 GOTO 1570
2180 ' subroutine to deal the cards
2190 GOSUB 2290
2200 T[P]=T[P]+C
2210 IF V[5]=0 THEN GOTO 2270
2220 V[5]=0
2230 IF P<>2 THEN RETURN 
2240 PRINT DC$+CHR$(16)+CHR$(32);
2250 PRINT USING "'Your total is  ',D3.0,'  '",T[P];EP$
2260 RETURN 
2270 GOSUB 2550 : ' print a card
2280 RETURN 
2290 N=INT(RND*100):IF N>14 THEN GOTO 2290
2300 FOR A=1 TO N
2310	X=INT(RND*100):IF X>52 THEN 2310
2320   IF X=0 THEN GOTO 2310
2330 NEXT A
2340 IF D[X]=0 THEN GOTO 2440
2350 R=R+1
2360 IF R<50 THEN GOTO 2290
2370 FOR A=1 TO 52
2380   IF D[A]=K THEN GOTO 2400
2390   D[A]=0
2400 NEXT A
2410 R=0
2420 PRINT DC$+CHR$(8)+CHR$(32);"I reshuffled the deck...";EP$
2430 GOTO 2290
2440 R=0
2450 D[X]=K
2460 IF Q[X]<>1 THEN GOTO 2500
2470 C=11 ' be sure that ace counts as 11
2480 E[P]=E[P]+1
2490 RETURN 
2500 IF Q[X]>10 THEN GOTO 2530
2510 C=Q[X]
2520 RETURN 
2530 C=10
2540 RETURN 
2550 ' subroutine to print a card
2560 GOSUB 2590
2570 GOSUB 2730 : ' print suit
2580 RETURN 
2590 IF Q[X]<>1 THEN GOTO 2620
2600 NMB$="A" ' ace
2610 RETURN 
2620 IF Q[X]>10 THEN GOTO 2650
2630 X$=STR$(Q[X]):NMB$=MID$(X$,2,2)
2640 RETURN 
2650 IF Q[X]>11 THEN GOTO 2680
2660 NMB$="J" ' jack
2670 RETURN 
2680 IF Q[X]>12 THEN GOTO 2710
2690 NMB$="Q" ' queen
2700 RETURN 
2710 NMB$="K" ' king
2720 RETURN 
2730 ' subroutine to print suit
2740 IF X>39 THEN GOTO 2800
2750 IF X>26 THEN GOTO 2830
2760 IF X>13 THEN GOTO 2860
2770 SUT$="S" ' spade
2780 GOSUB 3610 : ' print cards
2790 RETURN 
2800 SUT$="C" ' club
2810 GOSUB 3610 : ' print cards
2820 RETURN 
2830 SUT$="H" ' heart
2840 GOSUB 3610 : ' print cards
2850 RETURN 
2860 SUT$="D" ' diamond
2870 GOSUB 3610 : ' print cards
2880 RETURN 
2890 ' subroutine for dealer play
2900 P=2
2910 PRINT DC$+CHR$(7)+CHR$(32);
2920 X=M
2930 LN=2
2940 CLM=10
2950 GOSUB 2550 : ' print card
2960 IF T[2]<22 THEN GOTO 2990
2970 IF V[2]=0 THEN GOTO 3110
2980 IF T[3]>21 THEN GOTO 3110
2990 P=1
3000 IF T[1]<17 THEN GOTO 3180
3010 IF T[1]>17 THEN GOTO 3030
3020 IF E[1]>0 THEN GOTO 3180
3030 IF T[1]>21 THEN GOTO 3210
3040 P=2
3050 IF T[P]>21 THEN GOTO 3110
3060 IF T[1]>21 THEN GOTO 3090
3070 IF T[1]>T[P] THEN GOTO 3110
3080 IF T[1]=T[P] THEN GOTO 3120
3090 W1=W1+W[P]
3100 GOTO 3120
3110 W1=W1-W[P]
3120 IF V[2]>0 THEN GOTO 3150
3130 GOSUB 3270
3140 GOTO 630
3150 P=3
3160 V[2]=0
3170 GOTO 3050
3180 PRINT DC$+CHR$(6)+CHR$(32);"I Draw..."
3190 GOSUB 2180 : ' deal
3200 GOTO 2990
3210 IF E[1]=0 THEN GOTO 3250
3220 E[1]=E[1]-1
3230 T[1]=T[1]-10
3240 GOTO 2990
3250 PRINT DC$+CHR$(7)+CHR$(32);"I busted!";EP$;
3260 GOTO 3040
3270 PRINT DC$+CHR$(8)+CHR$(32);"My total was ";T[1];EP$
3280 PRINT EP$ ' flush next entry on comment line
3290 IF W1<0 THEN GOTO 3370
3300 IF W1=0 THEN GOTO 3430
3310 FOR I=1 TO 10 ' slowly flash current financial status
3320	FOR X=1 TO 50:NEXT X:PRINT DC$+CHR$(21)+CHR$(60);EP$
3330	PRINT DC$+CHR$(21)+CHR$(60);"You're ";UY$;"ahead $";W1;UN$;EP$
3340	FOR X=1 TO 50:NEXT X:PRINT DC$+CHR$(21)+CHR$(60);EP$
3350 NEXT I
3360 RETURN 
3370 FOR I=1 TO 10 ' slowly flash current financial status
3380	FOR X=1 TO 50:NEXT X:PRINT DC$+CHR$(21)+CHR$(60);EP$
3390	PRINT DC$+CHR$(21)+CHR$(60);"You're "UY$;"behind $";-W1;UN$;EP$
3400	FOR X=1 TO 50:NEXT X:PRINT DC$+CHR$(21)+CHR$(60);EP$
3410 NEXT I
3420 RETURN 
3430 FOR I=1 TO 10 ' slowly flash current financial status
3440	FOR X=1 TO 50:NEXT X:PRINT DC$+CHR$(21)+CHR$(60);EP$
3450	PRINT DC$+CHR$(21)+CHR$(60);"You're ";UY$;"EVEN!";UN$;EP$
3460	FOR X=1 TO 50:NEXT X:PRINT DC$+CHR$(21)+CHR$(60);EP$
3470 NEXT I
3480 RETURN 
3490 PRINT CLS$:INPUT"Do you really want to quit (Y or N)";X$
3500 IF LEFT$(X$,1)="N" OR LEFT$(X$,1)="n" THEN GOTO 500
3510 PRINT CLS$
3520 SYSTEM
3530 ' print blank card
3540 CLM=CLM+7
3550 PRINT DC$+CHR$(LN)+CHR$(32+CLM);NB$
3560 PRINT DC$+CHR$(LN+1)+CHR$(32+CLM);MD$
3570 PRINT DC$+CHR$(LN+2)+CHR$(32+CLM);MD$
3580 PRINT DC$+CHR$(LN+3)+CHR$(32+CLM);MD$
3590 PRINT DC$+CHR$(LN+4)+CHR$(32+CLM);NB$
3600 RETURN 
3610 ' print cards
3620 GOSUB 3530
3630 PRINT DY$
3640 PRINT DC$+CHR$(LN+1)+CHR$(CLM+33);NMB$;SUT$
3650 PRINT DC$+CHR$(LN+3)+CHR$(CLM+32+(4-LEN(NMB$)));NMB$;SUT$
3660 PRINT DC$+CHR$(16)+CHR$(32);
3670 PRINT DN$;
3680 IF P=2 THEN PRINT "Your total is ";T[P];EP$
3690 RETURN
