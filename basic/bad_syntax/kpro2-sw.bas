10 ' SPACEWAR - Complements of the Wizard of OsZ, and Kelly Smith CP/M-Net
20 ' ------------------ Kaypro II Terminal Commands ----------------------
30 '
40 E$=CHR$(27):'                Escape Character
50 CLS$=CHR$(26):'              Clear Screen
60 DC$=E$+"=":'                 Direct Cursor Addressing
70 EP$=E$+"T":'                Erase to End of Line
80 'NOTE: The Kaypro II uses the following scheme for direct cursor addressing:
90 '       Location= (CHR$(Line number+32));(CHR$(Column number+32))
100 'It appears that the Kaypro II looks very much like an ADM-3A Terminal !!!
110 '
120 PRINT CLS$
130 PRINT"           The Wizard of OsZ - 'SPACEWAR'"
140 PRINT
150 PRINT:PRINT "Do you require instructions (Y or N) ?";
160 A$=INKEY$:IF LEN(A$)=0 THEN GOTO 160 ' get keyboard input
170 IF A$="N" OR A$="n" THEN PRINT CLS$:GOTO 480
180 PRINT CLS$ ' clear screen
190 PRINT "You  are  about to go on a mission to  destroy  five" 
200 PRINT "alien  space  craft  that threaten  the  galaxy...In" 
210 PRINT "order  to  destroy an alien space  craft,  you  must" 
220 PRINT "position it such that it appears in the exact center" 
230 PRINT "of your target sight.   To do that,  use the numeric" 
240 PRINT "keypad  to position the alien craft in the following" 
250 PRINT "four directions:"
260 PRINT
270 FOR I=1 TO 10:PRINT DC$+CHR$(41)+CHR$(32);EP$
280 FOR N=1 TO 10:NEXT N ' ring bell and flash message on screen
290 PRINT CHR$(7);DC$+CHR$(41)+CHR$(32);
    "        8 - Up, 2 - Down, 4 - Left, 6 - Right";
300 FOR N=1 TO 10:NEXT N
310 NEXT I
320 FOR N=1 TO 2000:NEXT N:PRINT:PRINT
330 FOR I=1 TO 10:PRINT DC$+CHR$(43)+CHR$(32);EP$
340 FOR N=1 TO 10:NEXT N ' ring bell and flash message on screen
350 PRINT CHR$(7);DC$+CHR$(43)+CHR$(32);
    "Then  to fire on the alien space craft,  enter  '5'.";
360 FOR N=1 TO 10:NEXT N
370 NEXT I
380 FOR N=1 TO 2000:NEXT N:PRINT:PRINT
390 PRINT DY$"Also,   time   is  an  important  factor   on   your" 
400 PRINT "mission...Alien  return  fire degrades  your  target" 
410 PRINT "aiming ability, so don't delay!  Your performance is" 
420 PRINT "based  on the number of alien space craft  destroyed" 
430 PRINT "to  the number of misses...";"Enter '0' at any time  to" 
440 PRINT "quit";".   Please  enter  you  current  rating  now  as" 
450 PRINT "follows:"
460 PRINT DN$
470 FOR N=1 TO 2000:NEXT N
480 FOR I=1 TO 10:PRINT DC$+CHR$(53)+CHR$(32);EP$
490 FOR N=1 TO 10:NEXT N ' ring bell and flash message on screen
500 PRINT CHR$(7);DC$+CHR$(53)+CHR$(35);
    "N - Novice, H - Hotshot, E - Expert, A - Ace ?";
510 FOR N=1 TO 10:NEXT N
520 NEXT I
530 V$=INKEY$:IF LEN(V$)=0 THEN GOTO 530 ' get keyboard input and create rating value
540 IF V$="N" OR V$="n" THEN V=100 ' novice rating
550 IF V$="H" OR V$="h" THEN V=50 ' hotshot rating
560 IF V$="E" OR V$="e" THEN V=10 ' expert rating
570 IF V$="A" OR V$="a" THEN V=5 ' ace, and you better be fast on this one!
580 PRINT CLS$ ' clear screen
590 FOR I=1 TO 10:PRINT DC$+CHR$(44)+CHR$(32);EP$
600 FOR N=1 TO 30:NEXT N ' ring bell and flash message on screen
610 PRINT CHR$(7);DC$+CHR$(44)+CHR$(43);"Good luck on your mission !!!";
620 FOR N=1 TO 30:NEXT N
630 NEXT I
640 D=1:D1=1:PRINT CLS$ ' clear screen
650 GOSUB 1770 ' display initial pilot rating
660 Y=6:X=0:GOSUB 1100:GOSUB 930 ' display cross-hairs
670 Y=2:X=14:GOSUB 1100:PRINT "Target Position: "
680 Y=INT(10*RND(1)+7) ' set y axis random bounds
690 X=INT(20*RND(1)+21) ' set x axis random bounds
700 GOSUB 1100 ' position to xy coordinate
710 GOSUB 1070 ' display target
720 GOSUB 1660 ' advance alien target position
730 P=Y:Q=X:Y=2:X=31:GOSUB 1100 ' save xy position, position next message
740 PRINT "X =";Q-25;"Y =";P-12 ' display alien target coordinates
750 Y=3:X=13:GOSUB 1100:PRINT "Time =";R;:R=R+1 ' display relative run time
760 D2=SQR(((P-12)^2)+((Q-25)^2)) ' compute distance to target
770 Y=3:X=25:GOSUB 1100:PRINT "Distance =";D2;EP$ ' display distance to target
780 Y=P:X=Q ' restore original xy coordinate values
790 A$=INKEY$:IF LEN(A$)=0 THEN GOTO 720 ' check for keyboard input
800 GOSUB 1100 ' position to xy coordinate
810 IF A$="6" OR A$=CHR$(12) THEN X=X+1 ' 6 or RIGHT arrow = move right
820 IF A$="4" OR A$=CHR$(8) THEN X=X-1 ' 4 or LEFT arrow = move left
830 IF A$="2" OR A$=CHR$(10) THEN Y=Y+1 ' 2 or DOWN arrow = move down
840 IF A$="8" OR A$=CHR$(11) THEN Y=Y-1 ' 8 or UP arrow = move up
850 IF A$="5" OR A$="*" THEN GOTO 1120 ' 5 or RETURN = fire on target
860 IF A$="0" THEN PRINT CLS$:GOTO 1540 ' 0 = quit (maybe)
870 IF A$="1" OR A$="3" OR A$="7" OR A$="9" THEN GOSUB 1840 ' re-display '+'
880 IF A$="." THEN GOSUB 1860 ' momentarily display total score if '.' pressed
890 GOSUB 1630 ' erase target position
900 GOSUB 1100 ' position to xy coordinate
910 GOSUB 1070 ' display target
920 GOTO 720 ' repeat erase/move/position/display sequence
930 PRINT "                -----------------------" ' cross-hairs
940 PRINT "                           |"
950 PRINT "                           |"   
960 PRINT "                           |"
970 PRINT " |                                                   |"
980 PRINT " |                |                 |                |" 
990 PRINT " |----------------|        +        |----------------|"    
1000 PRINT " |                |                 |                |"
1010 PRINT " |                                                   |"
1020 PRINT " |                         |                         |"
1030 PRINT "                           |"
1040 PRINT "                           |"
1050 PRINT "                -----------------------"
1060 RETURN
1070 PRINT"<-*->": ' target display
1080 P=Y:Q=X ' save xy position
1090 RETURN
1100 PRINT DC$+CHR$(32+Y)+CHR$(32+X); ' position to xy coordinate
1110 RETURN
1120 IF Y=12 THEN GOTO 1140 ' proper line for hit on target?
1130 GOSUB 1430:GOTO 700 ' no, show total number missed
1140 IF X=25 THEN GOTO 1160 ' proper column for hit on target?
1150 GOSUB 1430:GOTO 700 ' no, show total number missed
1160 Y=12:X=26:GOSUB 1100:PRINT "*";"+";"*" ' explosion
1170 Y=11:X=27:GOSUB 1100:PRINT "*"
1180 Y=13:X=27:GOSUB 1100:PRINT "*" ' a quick puff of smoke...
1190 Y=12:X=25:GOSUB 1100:PRINT "+ + +"
1200 Y=11:X=26:GOSUB 1100:PRINT "+ +"
1210 Y=13:X=26:GOSUB 1100:PRINT "+ +"
1220 Y=10:X=27:GOSUB 1100:PRINT "+"
1230 Y=14:X=27:GOSUB 1100:PRINT "+" ' alien craft coming unglued...
1240 Y=12:X=25:GOSUB 1100:PRINT " "
1250 Y=11:X=28:GOSUB 1100:PRINT " "
1260 Y=10:X=27:GOSUB 1100:PRINT " "
1270 Y=13:X=26:GOSUB 1100:PRINT " "
1280 Y=12:X=29:GOSUB 1100:PRINT " "
1290 Y=13:X=28:GOSUB 1100:PRINT " "
1300 Y=14:X=27:GOSUB 1100:PRINT " "
1310 Y=12:X=27:GOSUB 1100:PRINT " "
1320 Y=11:X=26:GOSUB 1100:PRINT " " ' alien craft destroyed (totally!)
1330 FOR I=1 TO 10:PRINT DC$+CHR$(54)+CHR$(32);EP$
1340 FOR N=1 TO 50:NEXT N ' ring bell and flash message on screen
1350 PRINT CHR$(7);DC$+CHR$(54)+CHR$(37);
     "M A Y  T H E  F O R C E  B E  W I T H  Y O U";
1360 FOR N=1 TO 50:NEXT N
1370 NEXT I:PRINT DC$+CHR$(54)+CHR$(32);EP$ 
1380 S=S+10:GOSUB 1860 ' add 10 to total score, and display total score
1390 Y=20:X=17:GOSUB 1100 ' position cursor for next message
1400 PRINT "Aliens Destroyed =";D1 ' add 1 to alien craft hit
1410 D1=D1+1:IF D1=6 THEN 1480 ' close up shop if all 5 destroyed
1420 GOTO 680 ' continue with next target
1430 S=S-10:GOSUB 1860 ' subtract 10 from total score, and display total score
1440 P=Y:Q=X:Y=21:X=17:GOSUB 1100 ' position cursor for next message
1450 PRINT "Aliens Missed =";D:D=D+1 ' add 1 to alien craft missed
1460 Y=P:X=Q:GOSUB 1100 ' position to xy coordinate
1470 RETURN
1480 Y=20:X=0:GOSUB 1100 ' position to xy coordinate
1490 D=D-1 ' subtract -1 to number missed
1500 PRINT "    Congratulations, You have saved the galaxy !!!"
1510 PRINT "        Your mission record:";INT(5/(5+D)*100);"% performance"
1520 IF 5/(5+D)*100>75 THEN V=V-50
1530 IF 5/(5+D)*100<51 THEN V=V+50
1540 Y=21:X=7:GOSUB 1100
1550 PRINT DC$+CHR$(54)+CHR$(32);EP$
1560 FOR N=1 TO 100:NEXT N ' ring bell and flash message on screen
1570 PRINT CLS$;DC$+CHR$(54)+CHR$(40);"Do you want another mission (Y or N) ?"
1580 FOR N=1 TO 100:NEXT N
1590 A$=INKEY$:IF LEN(A$)=0 THEN GOTO 1550
1600 PRINT DC$+CHR$(54)+CHR$(32);EP$ 
1610 IF LEFT$(A$,1)="Y" OR LEFT$(A$,1)="y" THEN PRINT CLS$:GOTO 480
1620 PRINT CLS$:SYSTEM
1630 PRINT DC$+CHR$(32+P)+CHR$(32+Q); ' position cursor to target location
1640 PRINT "     " ' erase target location
1650 RETURN
1660 T=T+1.5 ' overall skill level set here (3 is super skill level!)
1670 IF T>V THEN 1690
1680 RETURN
1690 IF X>36 THEN GOTO 1730
1700 IF Y<12 THEN GOTO 1730
1710 X=X+1:Y=Y-1:GOSUB 1630:GOSUB 1100:GOSUB 1070:GOTO 1740
1720 GOTO 1740
1730 X=X+1:Y=Y-1:GOSUB 1630:GOSUB 1100:GOSUB 1070:GOTO 1740
1740 IF X>45 OR X<1 THEN Y=12:X=19:V=V+10:GOSUB 1100:
     PRINT CHR$(7);"You're shot down!":GOSUB 1830:GOTO 1540
1750 IF Y<7 OR Y>18 THEN Y=12:X=19:V=V+10:GOSUB 1100:
     PRINT CHR$(7);"You're destroyed!":GOSUB 1830:GOTO 1540
1760 T=0:RETURN
1770 IF V<=5 THEN Q$="Rating = Ace Pilot":GOTO 1810 ' determine pilot rating
1780 IF V<=10 THEN Q$="Rating = Expert Pilot":GOTO 1810
1790 IF V<=49 THEN Q$="Rating = Hotshot Pilot":GOTO 1810
1800 Q$="Rating = Novice Pilot"
1810 Y=0:X=17:GOSUB 1100 ' set cursor position for pilot rating
1820 PRINT Q$:RETURN ' print rating
1830 FOR N=1 TO 300:NEXT N:RETURN ' general purpose delay
1840 P=Y:Q=X:Y=12:X=27:GOSUB 1100:PRINT "+" ' print '+' for digits 1,3,7,9
1850 Y=P:X=Q:RETURN
1860 P=Y:Q=X:Y=12:X=19:GOSUB 1100:PRINT "Total Score =";S ' display total score
1870 GOSUB 1830:GOSUB 1830:GOSUB 1100 ' delay while score is displayed
1880 PRINT "        +        ":Y=P:X=Q:RETURN ' erase score display and return
