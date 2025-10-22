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
140 E$=CHR$(27):'                Escape Character
150 CLS$=CHR$(26):'              Clear Screen
160 DC$=E$+"=":'                 Direct Cursor Addressing
170 GY$=E$+"g":'                 Graphics On
180 GN$=E$+"G":'                 Graphics Off
190 HO$=E$+CHR$(1):'             Cursor Home
200 EP$=E$+"T":'                Erase to End of Line
210 DY$=E$+")":'                DIM Display On
220 DN$=E$+"(":'                DIM Display Off
230 UY$=E$+"l":'                Start Underlining
240 UN$=E$+"m":'                End Underlining
250 'NOTE: The Osborne I uses the following scheme for direct cursor addressing:
260 '      Location= (CHR$(Line number+32));(CHR$(Column number+32))
270 PRINT CLS$
280 PRINT"          The Wizard of OsZ - 'GOLDMINE'"
290 PRINT
300 L=W=S=0:C=10:M=4 ' reset variables
310 PRINT:PRINT:PRINT TAB(18);GY$;CHR$(13);GN$;" = Gold"
320 PRINT:PRINT TAB(18);GY$;CHR$(0);GN$;" = Miner"
330 PRINT:PRINT TAB(18);"* = Dead Miner":PRINT
340 PRINT TAB(18);CHR$(127);" = Tunnel Wall":PRINT
350 PRINT TAB(18);GY$;CHR$(12);GN$;" = Assay Office":PRINT
360 PRINT TAB(8);"Use ";UY$;"ARROW";UN$;" keys for direction control":PRINT
370 PRINT TAB(12);"Use ";UY$;"RETURN";UN$;" or ";UY$;"ENTER";UN$;" to blast"
380 PRINT DC$+CHR$(54)+CHR$(32);EP$ ' clear message line
390 FOR N=1 TO 100:NEXT N ' ring bell and flash message on screen
400 PRINT DC$+CHR$(54)+CHR$(47);DY$;"Press any key to play";DN$;
410 FOR N=1 TO 100:NEXT N ' hold message on screen for this delay time
420 IF INKEY$="" THEN RC=RC+1:GOTO 380 ' wait for response, bump random count
430 RANDOMIZE RC ' generate random number based on inkey loop count
440 PRINT CLS$:GOSUB 710 ' display cave structure and gold
450 XX=24:YY=22:T=250
460 POKE -(1152-XX+128*YY),32 ' clear display coordinate position
470 A$=INKEY$ ' get keyboard input
480 IF A$="" THEN 650 ' if no key, flash current miner position
490 A=ASC(A$) ' got a character, is it one of the arrow keys?
500 IF A=50 OR A=10 THEN YY=YY-1:GOSUB 1640:IF MC=127 THEN YY=YY+1
510 IF YY<3 THEN YY=YY+1
520 IF A=52 OR A=8 THEN XX=XX-1:GOSUB 1640:IF MC=127 OR MC=22 THEN XX=XX+1
530 IF XX<1 THEN XX=XX+1
540 IF A=56 OR A=11 THEN YY=YY+1:GOSUB 1640:IF MC=127 THEN YY=YY-1
550 IF YY>20 AND XX<>24 THEN YY=YY-1
560 IF YY>22 THEN YY=YY-1
570 IF A=54 OR A=12 THEN XX=XX+1:GOSUB 1640:IF MC=127 OR MC=22 THEN XX=XX-1
580 IF XX>48 THEN XX=XX-1
590 IF MC=13 THEN S=S+1 ' if gold found, add one to tally
600 IF MC=12 THEN GOSUB 970 ' if back at assay office, display new tally
610 IF MC=42 THEN GOSUB 960 ' if dead miner found, ring bell
620 IF A=13 AND YY>21 THEN 640
630 IF A=13 THEN GOSUB 1080:GOSUB 1400 ' if enter or return, explode a charge
640 GOSUB 860 ' display total amount of gold and charges
650 POKE -(1152-XX+128*YY),0 ' display miner
660 IF C<=0 THEN GOSUB 1550
670 GOSUB 1290
680 FOR N=1 TO 25:NEXT N
690 A$=""
700 GOTO 460 ' repeat this (humungous) loop...
710 PRINT TAB(24);GY$;CHR$(22);GN$;" ";GY$;CHR$(12);GN$;" ";GY$;CHR$(22);GN$
720 PRINT GY$;STRING$(24,CHR$(22));" ";STRING$(25,CHR$(22));GN$
730 FOR I=1 TO 18:PRINT GY$;CHR$(22);SPC(48);CHR$(22);GN$:NEXT
740 PRINT GY$;STRING$(50,CHR$(22));GN$
750 X=4:Y=22:GOSUB 1630:PRINT"Please wait for the GOLDMINE to be built..."
760 FOR I=1 TO 400
770 XX=INT(RND*48)+1:YY=INT(RND*18)+3
780 IF PEEK(-(1152-INT(XX)+128*INT(YY)))=127 THEN 770
790 POKE -(1152-XX+128*YY),127
800 NEXT
810 FOR YY=20 TO 3 STEP-1
820 FOR XX=1 TO 48
830 IF PEEK(-(1152-XX+128*YY))<>127 THEN POKE -(1152-XX+128*YY),13
840 NEXT XX,YY
850 GOSUB 880 ' display new miner, ten new charges, no gold
860 X=1:Y=22:GOSUB 1630:PRINT"Gold =";S;EP$;TAB(42);"Charges =";C
870 RETURN
880 Y=22 
890 IF M<0 THEN 1590 ' if all miners have died, time to quit
900 PRINT CHR$(30);"          ":PRINT "          "
910 FOR X=1 TO M*2-1 STEP 2 ' display miners
920 POKE -(1152-X+128*Y),0 ' and will a new miner sign-in please... 
930 NEXT X
940 C=10:S=0 ' make ten new charges, set recovered gold to zero for new miner
950 RETURN
960 S=S+S1:PRINT CHR$(7);:RETURN ' found dead miner, ring the bell
970 C1=C:IF C1=0 THEN C1=1 ' tally gold
980 W=S*C1+W
990 FOR I=1 TO 3 ' ring bell with three beeps
1000 PRINT CHR$(7);
1010 FOR J=1 TO 500:NEXT
1020 NEXT I
1030 X=39:Y=1:GOSUB 1630:PRINT USING "$##,###.##";W
1040 M=M-1 ' one less miner to worry about...
1050 XX=XX-1
1060 GOSUB 880 ' display new miner, ten new charges, no gold
1070 RETURN
1080 IF C<=0 THEN 1550 ' exploding charge
1090 X=XX-1:Y=YY:GOSUB 1650:IF SC=22 THEN 1110
1100 GOSUB 1660
1110 X=XX+1:Y=YY:GOSUB 1650:IF SC=22 THEN 1130
1120 GOSUB 1660
1130 X=XX:Y=YY+1:GOSUB 1650:IF SC=22 THEN 1150
1140 GOSUB 1660
1150 X=XX:Y=YY-1:GOSUB 1650:IF SC=22 THEN 1170
1160 GOSUB 1660
1170 PRINT CHR$(7);
1180 FOR N=1 TO 500:NEXT
1190 PRINT CHR$(7);
1200 X=XX-1:Y=YY:GOSUB 1650:IF SC=22 THEN 1220
1210 GOSUB 1670
1220 X=XX+1:Y=YY:GOSUB 1650:IF SC=22 THEN 1240
1230 GOSUB 1670
1240 X=XX:Y=YY+1:GOSUB 1650:IF SC=22 THEN 1260
1250 GOSUB 1670
1260 X=XX:Y=YY-1:GOSUB 1650:IF SC=22 THEN 1280
1270 GOSUB 1670
1280 C=C-1:RETURN
1290 ' random cave-in during digging, more when going deeper!
1300 IF YY>21 THEN RETURN
1310 IF RND>.5 THEN RETURN
1320 IF YY<10 THEN F=2 ELSE F=1
1330 FOR I=1 TO F
1340 X=INT(RND*48)+1:Y=INT(RND*18)+3
1350 GOSUB 1650
1360 IF SC=32 THEN POKE -(1152-X+128*Y),127
1370 IF X=XX AND Y=YY THEN GOSUB 1500:RETURN
1380 NEXT I
1390 RETURN
1400 ' cause random cave-in
1410 K=INT(RND*10)+10
1420 FOR I=1 TO K
1430 X=INT(RND*48)+1:Y=INT(RND*18)+3
1440 GOSUB 1650
1450 IF SC=22 OR SC=13 THEN 1430
1460 IF SC=0 THEN GOSUB 1500:RETURN
1470 POKE -(1152-X+128*Y),127
1480 NEXT I
1490 RETURN
1500 PRINT CHR$(7); ' crush miner (yucch!)
1510 M=M-1 ' miner eats dirt, one less to crush (I think I will get sick...)
1520 POKE -(1152-X+128*Y),42 ' display dead miner
1530 S1=S
1540 GOSUB 880:XX=24:YY=22:RETURN ' setup new miner
1550 IF T<=0 THEN X=XX:Y=YY:GOSUB 1670:GOSUB 880:T=250:
                  X=1:Y=22:GOSUB 1630:PRINT"Gold =";EP$;TAB(42);"Charges =";C:
                  XX=24:YY=22:RETURN
1560 X=15:Y=22:GOSUB 1630:PRINT CHR$(7);"Time to get out!"
1570 T=T-5
1580 RETURN
1590 X=0:Y=22:GOSUB 1630:PRINT EP$;TAB(16):"Want to play again (Y or N)";
1600 A$=INPUT$(1)
1610 IF A$="Y" OR A$="y" THEN GOTO 270 ' setup new mine display, if yes
1620 SYSTEM
1630 CP$=DC$+CHR$(Y+32)+CHR$(X+32):PRINT CP$;:RETURN ' position cursor
1640 MC=PEEK(-(1152-XX+128*YY)):RETURN
1650 SC=PEEK(-(1152-X+128*Y)):RETURN
1660 POKE -(1152-X+128*Y),43:RETURN ' display plus (+) character
1670 POKE -(1152-X+128*Y),32:RETURN ' display space character
