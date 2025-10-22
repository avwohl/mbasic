10 :REMARK \t\tTANKS.BAS\t\tVersion 05.02.81
20 :REMARK 
30 :REMARK Description --> A video game of tank warfare on the H19 terminal.
40 :REMARK 
50 :REMARK Author:\tTerry L. Perrino\tClaremont High School
60 :REMARK 
70 :REMARK \t\tModifications by H.U.G.
80 CLEAR 3000:WIDTH 255:DEFINT A-Z:GOSUB 1150
90 E$=CHR$(27):E1$=E$+"E":Y$=E$+"Y":F$=E$+"F":G$=E$+"G":P$=E$+"p":Q$=E$+"q"
100 Y5$=E$+"y5":X5$=E$+"x5"
110 DIM B$(80,24),P$(24),TD(2),X(4),Y(4),TX(2),TY(2),T$(4),S(2)
120 FOR R=1 TO 23:READ P$(R):NEXT R
130 CS$=E1$:H$=E$+"H":M$=Y$
140 GOSUB 990
150 PRINT E1$Y$"+?Initializing"X5$
160 TX(1)=6:TX(2)=75:TY(1)=12:TY(2)=12:S(1)=0:S(2)=0
170 OX(1)=6:OX(2)=75:OY(1)=12:OY(2)=12:OD(1)=1:OD(2)=3
180 X(1)=1:Y(2)=1:X(3)=-1:Y(4)=-1
190 T$(1)="v":T$(2)="s":T$(3)="t":T$(4)="u"
200 TD(1)=1:TD(2)=3
210 PRINT E1$Y$"+3Type any character to start warfare"Y5$;:A$=INPUT$(1)
220 PRINT X5$E1$"Tank #1:"S(1)Y$" bTank #2:";S(2)F$
230 FOR A=1 TO 22:PRINT P$(A):NEXT A:PRINT P$(23);
240 FOR T=1 TO 2:PRINT Y$CHR$(TY(T)+32)CHR$(TX(T)+31)T$(TD(T));:NEXT T
250 :REMARK \t\tSTART OF GAME INPUT AND GENERAL PLAY
260 T=T+1:IF T>2 THEN T=1\t:REMARK  EXCHANGE TANKS TO MOVE NEXT
270 IF TM(T)=1 THEN 370
280 C$=MID$(P$(TY(T)+Y(TD(T))),TX(T)+X(TD(T)),1)
290 IF C$="T" OR C$="i" THEN 370
300 PRINT Y$CHR$(TY(T)+32)CHR$(TX(T)+31)" ";
310 MID$(P$(TY(T)),TX(T),1)=" "
320 TX(T)=TX(T)+X(TD(T)):TY(T)=TY(T)+Y(TD(T))
330 IF C$="+" THEN 700
340 MID$(P$(TY(T)),TX(T),1)="T"
350 PRINT Y$CHR$(TY(T)+32)CHR$(TX(T)+31)T$(TD(T));
360 :REMARK \t\t\tACCEPT INPUT AND EXECUTE ACCORDINGLY
370 DEF USR0=VARPTR(U0(0)):X=USR0(0):IF X>96 AND X<123 THEN X=X-32
380 IF X=54 THEN TD(2)=TD(2)+1:T=2:IF TD(2)>4 THEN TD(2)=1:GOTO 500::ELSE GOTO 500
390 IF X=52 THEN TD(2)=TD(2)-1:T=2:IF TD(2)<1 THEN TD(2)=4:GOTO 500::ELSE GOTO 500
400 IF X=56 THEN TM(2)=0:GOTO 250
410 IF X=50 THEN TM(2)=1:GOTO 250
420 IF X=53 THEN T=2:GOTO 530\t:REMARK  *** GO TO SHOOT BOMB ***
430 IF X=83 THEN TD(1)=TD(1)+1:T=1:IF TD(1)>4 THEN TD(1)=1:GOTO 500::ELSE GOTO 500
440 IF X=65 THEN TD(1)=TD(1)-1:T=1:IF TD(1)<1 THEN TD(1)=4:GOTO 500::ELSE GOTO 500
450 IF X=87 THEN TM(1)=0:GOTO 250
460 IF X=90 THEN TM(1)=1:GOTO 250
470 IF X=32 THEN T=1:GOTO 530::REMARK \t\tGO SHOOT BOMB
480 IF X<>69 THEN 250
490 PRINT E1$G$Y$"+?* End of session *"Y5$;:GOSUB 1160:RUN "MENU"
500 :REMARK \t\tTURN TANK #T AROUND WHILE TANK ISN'T MOVING
510 PRINT Y$CHR$(TY(T)+32)CHR$(TX(T)+31)T$(TD(T));
520 GOTO 250
530 :REMARK \t\tSHOOT BOMB
540 IF MID$(P$(TY(T)+Y(TD(T))),TX(T)+X(TD(T)),1)="i" THEN 250
550 IF TD(T)=1 OR TD(T)=3 THEN 630
560 FOR Y=TY(T)+Y(TD(T)) TO TY(T)+Y(TD(T))*5 STEP Y(TD(T))
570 IF MID$(P$(Y),TX(T),1)="i" THEN 250
580 IF MID$(P$(Y),TX(T),1)="+" THEN 610
590 IF MID$(P$(Y),TX(T),1)="T" THEN S(T)=S(T)+1:GOTO 710
600 PRINT Y$CHR$(Y+32)CHR$(TX(T)+31)"^"CHR$(8)" ";
610 NEXT Y
620 GOTO 250
630 FOR X1=TX(T)+X(TD(T)) TO TX(T)+X(TD(T))*5 STEP X(TD(T))
640 IF MID$(P$(TY(T)),X1,1)="i" THEN 250
650 IF MID$(P$(TY(T)),X1,1)="+" THEN 680
660 IF MID$(P$(TY(T)),X1,1)="T" THEN S(T)=S(T)+1:GOTO 710
670 PRINT Y$CHR$(TY(T)+32)CHR$(X1+31)"^"CHR$(8)" ";
680 NEXT X1
690 GOTO 250
700 T=T+1:IF T>2 THEN T=1:S(T)=S(T)+1::ELSE S(T)=S(T)+1
710 T=T+1:IF T>2 THEN T=1
720 MID$(P$(TY(T)),TX(T),1)=" "
730 PRINT Y$CHR$(TY(T)+32)CHR$(TX(T)+31)" \a";:\n\tTX(T)=OX(T):TY(T)=OY(T):TD(T)=OD(T)
740 PRINT Y$CHR$(TY(T)+32)CHR$(TX(T)+31)T$(TD(T));
750 PRINT Y$" ("S(1)Y$" j"S(2);:GOTO 250
760 DATA "iiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii"
770 DATA "i                                                                              i"
780 DATA "i    iiiii                    iiiiiiiiiiiiiiiiiiii                    iiiii    i"
790 DATA "i      i                      i                  i                      i      i"
800 DATA "i    iiiii                         iiiiiiiiii                         iiiii    i"
810 DATA "i                                     i  i                                     i"
820 DATA "i                   iii      +      +      +      +      iii                   i"
830 DATA "i                   iii                                  iii                   i"
840 DATA "i      iii                   +      +      +      +                   iii      i"
850 DATA "i        iii                                                        iii        i"
860 DATA "i   iii                      +      +      +      +                      iii   i"
870 DATA "i     i                                                                  i     i"
880 DATA "i   iii                      +      +      +      +                      iii   i"
890 DATA "i        iii                                                        iii        i"
900 DATA "i      iii                   +      +      +      +                   iii      i"
910 DATA "i                   iii                                  iii                   i"
920 DATA "i                   iii      +      +      +      +      iii                   i"
930 DATA "i                                     i  i                                     i"
940 DATA "i    iiiii                         iiiiiiiiii                         iiiii    i"
950 DATA "i      i                      i                  i                      i      i"
960 DATA "i    iiiii                    iiiiiiiiiiiiiiiiiiii                    iiiii    i"
970 DATA "i                                                                              i"
980 DATA "iiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii"
990 PRINTE1$Y$" 9* Tanks *"
1000 PRINT Y$"##The game of tanks is played on a 78x22 matrix.  The object of"
1010 PRINT "the game is to make as many points possible by hitting the other"
1020 PRINT "player with your bullets or running him into a mine."
1030 PRINT Y$"' The controls for each tanks are as follows:"
1040 PRINT Y$"*0Tanks #1"Y$"*HTanks #2"
1050 PRINT Y$"+0========"Y$"+H========"
1060 PRINT Y$",0A --> LEFT"Y$",H4 --> LEFT"
1070 PRINT Y$"-0S --> RIGHT"Y$"-H6 --> RIGHT"
1080 PRINT Y$".0W --> FORWARD"Y$".H8 --> FORWARD"
1090 PRINT Y$"/0Z --> STOP"Y$"/H2 --> STOP"
1100 PRINT Y$"00SPACE --> FIRE"Y$"0H5 --> FIRE"
1110 PRINT Y$"2 The bullets fly to a maximum of 5 locations.  To exit the game,"
1120 PRINT "type 'E'.  Let the war begin!"
1130 PRINT Y$"60Hit any key to continue "Y5$;:A$=INPUT$(1):RETURN
1140 :REMARK \t\tReal Time Function for MBASIC
1150 DIM U0(3):U0(0)=&H36:U0(1)=&H1FF:U0(2)=&H77D8:U0(3)=&HC9
1160 DEF USR0=VARPTR(U0(0))::REMARK \t\tClear Buffer
1170 IF USR0(0)<>0 THEN 1170
1180 RETURN
