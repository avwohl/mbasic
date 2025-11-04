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
150 E$=CHR$(27):'                Escape Character
160 CLS$=CHR$(26):'              Clear Screen
170 DC$=E$+"=":'                 Direct Cursor Addressing
180 GY$=E$+"g":'                 Graphics On
190 GN$=E$+"G":'                 Graphics Off
200 HO$=E$+CHR$(1):'            Cursor Home
210 EP$=E$+"T":'                Erase to End of Line
220 DY$=E$+")":'                DIM Display On
230 DN$=E$+"(":'                DIM Display Off
240 UY$=E$+"l":'                Start Underlining
250 UN$=E$+"m":'                End Underlining
260 'NOTE:  The Osborne I uses the following scheme for direct cursor addressing:
270 '       Location= (CHR$(Line number+32));(CHR$(Column number+32))
280 PRINT CLS$
290 PRINT"           The Wizard of OsZ - 'SPACEWAR'"
300 PRINT
310 PRINT:PRINT "Do you require instructions (Y or N) ?";
320 A$=INKEY$:IF LEN(A$)=0 THEN GOTO 320 ' get keyboard input
330 IF A$="N" OR A$="n" THEN PRINT CLS$:GOTO 640
340 PRINT CLS$ ' clear screen
350 PRINT DY$;"You  are  about to go on a mission to  destroy  five" 
360 PRINT "alien  space  craft  that threaten  the  galaxy...In" 
370 PRINT "order  to  destroy an alien space  craft,  you  must" 
380 PRINT "position it such that it appears in the exact center" 
390 PRINT "of your target sight.   To do that,  use the numeric" 
400 PRINT "keypad  to position the alien craft in the following" 
410 PRINT "four directions:"
420 PRINT DN$
430 FOR I=1 TO 10:PRINT DC$+CHR$(41)+CHR$(32);EP$
440 FOR N=1 TO 10:NEXT N ' ring bell and flash message on screen
450 PRINT CHR$(7);DC$+CHR$(41)+CHR$(32);
    "        8 - Up, 2 - Down, 4 - Left, 6 - Right";
460 FOR N=1 TO 10:NEXT N
470 NEXT I
480 FOR N=1 TO 2000:NEXT N:PRINT:PRINT
490 FOR I=1 TO 10:PRINT DC$+CHR$(43)+CHR$(32);EP$
500 FOR N=1 TO 10:NEXT N ' ring bell and flash message on screen
510 PRINT CHR$(7);DC$+CHR$(43)+CHR$(32);
    "Then  to fire on the alien space craft,  enter  '5'.";
520 FOR N=1 TO 10:NEXT N
530 NEXT I
540 FOR N=1 TO 2000:NEXT N:PRINT:PRINT
550 PRINT DY$"Also,   time   is  an  important  factor   on   your" 
560 PRINT "mission...Alien  return  fire degrades  your  target" 
570 PRINT "aiming ability, so don't delay!  Your performance is" 
580 PRINT "based  on the number of alien space craft  destroyed" 
590 PRINT "to  the number of misses...";DN$;"Enter '0' at any time  to" 
600 PRINT "quit";DY$;".   Please  enter  you  current  rating  now  as" 
610 PRINT "follows:"
620 PRINT DN$
630 FOR N=1 TO 2000:NEXT N
640 FOR I=1 TO 10:PRINT DC$+CHR$(53)+CHR$(32);EP$
650 FOR N=1 TO 10:NEXT N ' ring bell and flash message on screen
660 PRINT CHR$(7);DC$+CHR$(53)+CHR$(35);
    "N - Novice, H - Hotshot, E - Expert, A - Ace ?";
670 FOR N=1 TO 10:NEXT N
680 NEXT I
690 V$=INKEY$:IF LEN(V$)=0 THEN GOTO 690 ' get keyboard input and create rating value
700 IF V$="N" OR V$="n" THEN V=100 ' novice rating
710 IF V$="H" OR V$="h" THEN V=50 ' hotshot rating
720 IF V$="E" OR V$="e" THEN V=10 ' expert rating
730 IF V$="A" OR V$="a" THEN V=5 ' ace, and you better be fast on this one!
740 PRINT CLS$ ' clear screen
750 FOR I=1 TO 10:PRINT DC$+CHR$(44)+CHR$(32);EP$
760 FOR N=1 TO 30:NEXT N ' ring bell and flash message on screen
770 PRINT CHR$(7);DC$+CHR$(44)+CHR$(43);"Good luck on your mission !!!";
780 FOR N=1 TO 30:NEXT N
790 NEXT I
800 D=1:D1=1:PRINT CLS$ ' clear screen
810 GOSUB 1930 ' display initial pilot rating
820 Y=6:X=0:GOSUB 1260:GOSUB 1090 ' display cross-hairs
830 Y=2:X=14:GOSUB 1260:PRINT "Target Position: "
840 Y=INT(10*RND(1)+7) ' set y axis random bounds
850 X=INT(20*RND(1)+21) ' set x axis random bounds
860 GOSUB 1260 ' position to xy coordinate
870 GOSUB 1230 ' display target
880 GOSUB 1820 ' advance alien target position
890 P=Y:Q=X:Y=2:X=31:GOSUB 1260 ' save xy position, position next message
900 PRINT "X =";Q-25;"Y =";P-12 ' display alien target coordinates
910 Y=3:X=13:GOSUB 1260:PRINT "Time =";R;:R=R+1 ' display relative run time
920 D2=SQR(((P-12)^2)+((Q-25)^2)) ' compute distance to target
930 Y=3:X=25:GOSUB 1260:PRINT "Distance =";D2;EP$ ' display distance to target
940 Y=P:X=Q ' restore original xy coordinate values
950 A$=INKEY$:IF LEN(A$)=0 THEN GOTO 880 ' check for keyboard input
960 GOSUB 1260 ' position to xy coordinate
970 IF A$="6" OR A$=CHR$(12) THEN X=X+1 ' 6 or RIGHT arrow = move right
980 IF A$="4" OR A$=CHR$(8) THEN X=X-1 ' 4 or LEFT arrow = move left
990 IF A$="2" OR A$=CHR$(10) THEN Y=Y+1 ' 2 or DOWN arrow = move down
1000 IF A$="8" OR A$=CHR$(11) THEN Y=Y-1 ' 8 or UP arrow = move up
1010 IF A$="5" OR A$=CHR$(13) THEN GOTO 1280 ' 5 or RETURN = fire on target
1020 IF A$="0" THEN PRINT CLS$:GOTO 1700 ' 0 = quit (maybe)
1030 IF A$="1" OR A$="3" OR A$="7" OR A$="9" THEN GOSUB 2000 ' re-display '+'
1040 IF A$="." THEN GOSUB 2020 ' momentarily display total score if '.' pressed
1050 GOSUB 1790 ' erase target position
1060 GOSUB 1260 ' position to xy coordinate
1070 GOSUB 1230 ' display target
1080 GOTO 880 ' repeat erase/move/position/display sequence
1090 PRINT DY$;"                 ";UY$;"                     ";UN$ ' cross-hairs
1100 PRINT "                           |"
1110 PRINT "                           |"   
1120 PRINT "                           |"
1130 PRINT "       |                                       |"
1140 PRINT "       |                                       |" 
1150 PRINT "       |";UY$;"          ";UN$;"|        +        |";UY$;"          ";UN$;"|"    
1160 PRINT "       |          |                 |          |"
1170 PRINT "       |                                       |"
1180 PRINT "       |                   |                   |"
1190 PRINT "                           |"
1200 PRINT "                           |"
1210 PRINT "                 ";UY$;"                     ";UN$;DN$
1220 RETURN
1230 PRINT"<-";GY$;CHR$(13);GN$;"->": ' target display
1240 P=Y:Q=X ' save xy position
1250 RETURN
1260 PRINT DC$+CHR$(32+Y)+CHR$(32+X); ' position to xy coordinate
1270 RETURN
1280 IF Y=12 THEN GOTO 1300 ' proper line for hit on target?
1290 GOSUB 1590:GOTO 860 ' no, show total number missed
1300 IF X=25 THEN GOTO 1320 ' proper column for hit on target?
1310 GOSUB 1590:GOTO 860 ' no, show total number missed
1320 Y=12:X=26:GOSUB 1260:PRINT GY$;CHR$(13);"+";CHR$(13);GN$ ' explosion
1330 Y=11:X=27:GOSUB 1260:PRINT GY$;CHR$(13);GN$
1340 Y=13:X=27:GOSUB 1260:PRINT GY$;CHR$(13);GN$ ' a quick puff of smoke...
1350 Y=12:X=25:GOSUB 1260:PRINT "+ + +"
1360 Y=11:X=26:GOSUB 1260:PRINT "+ +"
1370 Y=13:X=26:GOSUB 1260:PRINT "+ +"
1380 Y=10:X=27:GOSUB 1260:PRINT "+"
1390 Y=14:X=27:GOSUB 1260:PRINT "+" ' alien craft coming unglued...
1400 Y=12:X=25:GOSUB 1260:PRINT " "
1410 Y=11:X=28:GOSUB 1260:PRINT " "
1420 Y=10:X=27:GOSUB 1260:PRINT " "
1430 Y=13:X=26:GOSUB 1260:PRINT " "
1440 Y=12:X=29:GOSUB 1260:PRINT " "
1450 Y=13:X=28:GOSUB 1260:PRINT " "
1460 Y=14:X=27:GOSUB 1260:PRINT " "
1470 Y=12:X=27:GOSUB 1260:PRINT " "
1480 Y=11:X=26:GOSUB 1260:PRINT " " ' alien craft destroyed (totally!)
1490 FOR I=1 TO 10:PRINT DC$+CHR$(54)+CHR$(32);EP$
1500 FOR N=1 TO 50:NEXT N ' ring bell and flash message on screen
1510 PRINT CHR$(7);DC$+CHR$(54)+CHR$(37);
     UY$;"M A Y";UN$;"  ";UY$;"T H E";UN$;"  ";UY$;"F O R C E";UN$;"  ";
     UY$;"B E";UN$;"  ";UY$;"W I T H";UN$;"  ";UY$;"Y O U";UN$;
1520 FOR N=1 TO 50:NEXT N
1530 NEXT I:PRINT DC$+CHR$(54)+CHR$(32);EP$ 
1540 S=S+10:GOSUB 2020 ' add 10 to total score, and display total score
1550 Y=20:X=17:GOSUB 1260 ' position cursor for next message
1560 PRINT "Aliens Destroyed =";D1 ' add 1 to alien craft hit
1570 D1=D1+1:IF D1=6 THEN 1640 ' close up shop if all 5 destroyed
1580 GOTO 840 ' continue with next target
1590 S=S-10:GOSUB 2020 ' subtract 10 from total score, and display total score
1600 P=Y:Q=X:Y=21:X=17:GOSUB 1260 ' position cursor for next message
1610 PRINT "Aliens Missed =";D:D=D+1 ' add 1 to alien craft missed
1620 Y=P:X=Q:GOSUB 1260 ' position to xy coordinate
1630 RETURN
1640 Y=20:X=0:GOSUB 1260 ' position to xy coordinate
1650 D=D-1 ' subtract -1 to number missed
1660 PRINT "    Congratulations, You have saved the galaxy !!!"
1670 PRINT "        Your mission record:";INT(5/(5+D)*100);"% performance"
1680 IF 5/(5+D)*100>75 THEN V=V-50
1690 IF 5/(5+D)*100<51 THEN V=V+50
1700 Y=21:X=7:GOSUB 1260
1710 PRINT DC$+CHR$(54)+CHR$(32);EP$
1720 FOR N=1 TO 100:NEXT N ' ring bell and flash message on screen
1730 PRINT DC$+CHR$(54)+CHR$(40);"Do you want another mission (Y or N) ?"
1740 FOR N=1 TO 100:NEXT N
1750 A$=INKEY$:IF LEN(A$)=0 THEN GOTO 1710
1760 PRINT DC$+CHR$(54)+CHR$(32);EP$ 
1770 IF LEFT$(A$,1)="Y" OR LEFT$(A$,1)="y" THEN PRINT CLS$:GOTO 640
1780 PRINT CLS$:SYSTEM
1790 PRINT DC$+CHR$(32+P)+CHR$(32+Q); ' position cursor to target location
1800 PRINT "     " ' erase target location
1810 RETURN
1820 T=T+1.5 ' overall skill level set here (3 is super skill level!)
1830 IF T>V THEN 1850
1840 RETURN
1850 IF X>36 THEN GOTO 1890
1860 IF Y<12 THEN GOTO 1890
1870 X=X+1:Y=Y-1:GOSUB 1790:GOSUB 1260:GOSUB 1230:GOTO 1900
1880 GOTO 1900
1890 X=X+1:Y=Y-1:GOSUB 1790:GOSUB 1260:GOSUB 1230:GOTO 1900
1900 IF X>45 OR X<1 THEN Y=12:X=19:V=V+10:GOSUB 1260:
     PRINT CHR$(7);"You're shot down!":GOSUB 1990:GOTO 1700
1910 IF Y<7 OR Y>18 THEN Y=12:X=19:V=V+10:GOSUB 1260:
     PRINT CHR$(7);"You're destroyed!":GOSUB 1990:GOTO 1700
1920 T=0:RETURN
1930 IF V<=5 THEN Q$="Rating = Ace Pilot":GOTO 1970 ' determine pilot rating
1940 IF V<=10 THEN Q$="Rating = Expert Pilot":GOTO 1970
1950 IF V<=49 THEN Q$="Rating = Hotshot Pilot":GOTO 1970
1960 Q$="Rating = Novice Pilot"
1970 Y=0:X=17:GOSUB 1260 ' set cursor position for pilot rating
1980 PRINT UY$;Q$;UN$:RETURN ' print rating
1990 FOR N=1 TO 300:NEXT N:RETURN ' general purpose delay
2000 P=Y:Q=X:Y=12:X=27:GOSUB 1260:PRINT "+" ' print '+' for digits 1,3,7,9
2010 Y=P:X=Q:RETURN
2020 P=Y:Q=X:Y=12:X=19:GOSUB 1260:PRINT "Total Score =";S ' display total score
2030 GOSUB 1990:GOSUB 1990:GOSUB 1260 ' delay while score is displayed
2040 PRINT "        +        ":Y=P:X=Q:RETURN ' erase score display and return
