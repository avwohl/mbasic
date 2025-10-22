10 :REMARK \t\tSCENECAR.BAS
20 :REMARK 
30 :REMARK Descritpion -->\tA video game of car driving on the H19 terminal.
40 :REMARK 
50 :REMARK Author:\tTerry L. Perrino\tClaremont High School
60 :REMARK 
70 :REMARK \t\tModifications by H.U.G.
80 CLEAR 5000:WIDTH 255:DEFINT A-Z:GOSUB 1030
90 E$=CHR$(27):E1$=E$+"E":Y$=E$+"Y":F$=E$+"F":G$=E$+"G":P$=E$+"p":Q$=E$+"q"
100 Y5$=E$+"y5":X5$=E$+"x5":H$=E$+"H":I$=E$+"L":R$=E$+CHR$(64)+" "+E$+"O"
110 L$=E$+"N":C$=Y$+"8 "
120 GOSUB 830
130 PRINT E1$Y$" 5* Scenic-Driving *"
140 PRINT Y$"%0What's your rating? (N)ovice, (E)xpert, or (P)ro <N>"Y5$;:
150 A$=INPUT$(1):IF ASC(A$)>96 AND ASC(A$)<123 THEN A$=CHR$(ASC(A$)-32)
170 IF A$="E" THEN R=2:GOTO 200
180 IF A$="P" THEN R=3:GOTO 200
190 R=1
200 PRINT E1$
210 PRINT Y$"+3Type any character to begin your drive. ";:A$=INPUT$(1)
220 PRINT E1$X5$
230 DIM P(25)
240 FOR P=1 TO 24:P(P)=40:NEXT P
250 PRINT F$E$"x1"
260 X=40
270 X1=40
280 X2=40
290 R1$(0)="GRANNY"
300 R1$(1)="SUNDAY DRIVER"
310 R1$(2)="ROAD HOG"
320 R1$(3)="BEGINNER"
330 R1$(4)="FAIR"
340 R1$(5)="GOOD"
350 R1$(6)="ELITE"
360 R$(0)=" y     y"
370 R$(1)="}     } "
380 R$(2)="x     x "
390 O$(0)="       xy     "
400 O$(1)="      xcfy    "
410 O$(2)="   xzzzyzzy   "
420 O$(3)="xzz  xzzzzzzy "
430 O$(4)="   xzzy       "
440 O$(5)=" xzzzy zzzy   "
450 FOR N=1 TO 24:PRINT TAB(X-6);R$(1):NEXT N
460 PRINT C$E1$SPACE$(X2-3)"nuo"H$;
470 X1=X2
480 :REMARK \t\t\tSTART OF PROGRAM
490 IF X1-X2<=1 AND X1-X2>=-2 THEN 580
500 PRINT C$E1$SPACE$(X1-2)"\a*BOOM*"H$;:D=D+1
510 IF D<=5 THEN 460
520 PRINT C$E1$H$E1$G$
530 PRINT "You scored"M"miles in"D"crashes."
540 IF D=0 THEN D=1
550 IF INT(M/D)>6 THEN M=D*6
560 PRINT:PRINT "Your rank ---> ";R1$(INT(M/D))
570 PRINT:GOSUB 1040:PRINT "Would you like to play again? "Y5$;:A$=INPUT$(1):\n\tIF A$="N" OR A$="n" THEN RUN "MENU"::ELSE 80
580 IF INT(RND(1)*R)+1=1 THEN A=INT(RND(1)*3)-1
590 IF X+A<6 OR X+A>74 THEN 490
600 X=X+A
610 IF S=1 THEN 690
620 IF INT(RND(1)*10)+1<>7 THEN 740
630 S=1:S1$=SPACE$(79):S2$=SPACE$(79)
640 S2=INT(RND(1)*3)
650 S3=INT(RND(1)*65)+1
660 S0$=SPACE$(S3)+O$(S2*2+1)+SPACE$(79-S3-14)
670 S1$=SPACE$(S3)+O$(S2*2)+SPACE$(79-S3-14)
680 GOTO 720
690 PRINT I$;H$;LEFT$(S1$,X-6);R$(A+1);MID$(S1$,X);
700 S=0
710 GOTO 750
720 PRINT I$;H$;LEFT$(S0$,X-6);R$(A+1);MID$(S0$,X);
730 GOTO 750
740 PRINT I$;H$;SPACE$(X-6);R$(A+1);
750 P=P+1:IF P>24 THEN P=1:M=M+1
760 P(P)=X
770 X2=P(P+1):IF P+1>24 THEN X2=P(1)
780 DEF USR0=VARPTR(U0(0)):G=USR0(0)
790 IF G=52 THEN X1=X1-1:PRINT C$;L$;H$;:GOTO 490
800 IF G=54 THEN X1=X1+1:PRINT C$;R$;H$;:GOTO 490
810 IF G=69 OR G=101 THEN 520 :ELSE 490
820 :REMARK \t\t\t\tINSTRUCTIONS
830 PRINT X5$E1$Y$" 5* Scenic Driving *"
840 PRINT
850 PRINT "\tThe object to the game is to drive your car on a curving road"
860 PRINT "without running off the road.  There are various trees and mountains"
870 PRINT "to give the illusion of scenic driving."
880 PRINT "\tYour car will appear on the bottom of the screen.  The road"
890 PRINT "will move down the screen toward your car.  You have to keep your"
900 PRINT "car between the boundries of the road.  Once you run off the road,"
910 PRINT "your car explodes and you receive another car in the middle of the"
920 PRINT "road.  After six crashes, the game is over."
930 PRINT "\tYou manipulate the car by using the left and right arrows on the"
940 PRINT "right keypad of the H89.  For every time you hit the arrow, the car"
950 PRINT "moves once in that direction.  DO NOT overload the input buffer by"
960 PRINT "typing faster than the car will go, otherwise the computer will "
970 PRINT "remember these moves and do them when you may not want to."
980 PRINT Y$"4%If you want to exit the program before the game is over, type"
990 PRINT "'E'.  HAPPY DRIVING!"
1000 PRINTY$"60Hit any key to start. "Y5$;:A$=INPUT$(1):PRINT X5$
1010 RETURN
1020 :REMARK \t\tReal Time Function for MBASIC
1030 DIM U0(3):U0(0)=&H36:U0(1)=&H1FF:U0(2)=&H77D8:U0(3)=&HC9
1040 DEF USR0=VARPTR(U0(0))::REMARK \t\tClear Buffer
1050 IF USR0(0)<>0 THEN 1050
1060 RETURN
