10 :REMARK \t\tSURROUND.BAS\t\tVersion 05.02.81
20 :REMARK Description -->  A video game of wall building on the H19 Terminal.
30 :REMARK 
40 :REMARK Source -->\tTERRY L. PERRINO
50 :REMARK \t\tCLAREMONT HIGH SCHOOL
60 :REMARK 
70 :REMARK \t\tModifications by H.U.G.
80 :REMARK 
90 CLEAR 5000:WIDTH 255:DEFINT A-Z:GOSUB 630
100 E$=CHR$(27):E1$=E$+"E":Y$=E$+"Y":F$=E$+"F":G$=E$+"G":P$=E$+"p":Q$=E$+"q"
110 Y5$=E$+"y5":X5$=E$+"x5":H$=E$+"H"
120 GOSUB 470
130 PRINT E1$Y$"+? Initializing"X5$
140 X(1)=1:Y(2)=1:X(3)=-1:Y(4)=-1
150 P$(1)=" ":P$(2)="i"
160 DIM B$(80,24)
170 FOR S=1 TO 80:B$(S,1)="O":B$(S,24)="O":NEXT S
180 FOR S=2 TO 23:B$(1,S)="O":B$(80,S)="O":NEXT S
190 PRINT E1$Y$"+6Type any character to start game";:A$=INPUT$(1)
200 PRINT X5$E1$P$SPACE$(80);
210 FOR S=2 TO 23:PRINT Y$CHR$(S+31)"  "Y$CHR$(S+31)"o ";:NEXT S
220 PRINT Y$"7 "SPACE$(80)Q$;
230 PRINT Y$" %Score #1:"S1;Y$" a";
240 PRINT "Score #2:"S2;H$P$F$;
250 PX(1)=5:PX(2)=75:PY(1)=12:PY(2)=12:D(1)=1:D(2)=3
260 :REMARK \t\t\tMOVE PLAYERS
270 W=W+1:IF W>2 THEN W=1
280 IF B$(PX(W)+X(D(W)),PY(W)+Y(D(W)))="O" THEN 440
290 PX(W)=PX(W)+X(D(W)):PY(W)=PY(W)+Y(D(W)):B$(PX(W),PY(W))="O"
300 PRINT Y$CHR$(PY(W)+31)CHR$(PX(W)+31)P$(W);
310 DEF USR0=VARPTR(U0(0)):X=USR0(0)
320 IF X>96 AND X<123 THEN X=X-32
330 I$=CHR$(X)
340 IF I$="W" THEN D(1)=4:GOTO 270
350 IF I$="8" THEN D(2)=4:GOTO 270
360 IF I$="S" THEN D(1)=1:GOTO 270
370 IF I$="6" THEN D(2)=1:GOTO 270
380 IF I$="Z" THEN D(1)=2:GOTO 270
390 IF I$="2" THEN D(2)=2:GOTO 270
400 IF I$="A" THEN D(1)=3:GOTO 270
410 IF I$="4" THEN D(2)=3:GOTO 270
420 IF I$<>"E" THEN 270
430 PRINT Q$G$E1$Y5$Y$"+=* End of session *":GOSUB 640:RUN "MENU"
440 PRINT Y$CHR$(PY(W)+31)CHR$(PX(W)+31);
450 IF W=1 THEN S2=S2+1:PRINT "\a1";::ELSE S1=S1+1:PRINT "\a2";
460 ERASE B$:PRINT Q$G$;:GOTO 160
470 :REMARK \t\t\tInstructions
480 PRINT E1$X5$Y$" 9* Surround *"
490 PRINT Y$"#'Surround is played on a 22x78 grid.  The object of the game"
500 PRINT "is to make your apponent crash into a wall by surrounding him.  The"
510 PRINT "game starts off with both players building walls toward each other."
520 PRINT "The players can then manipulate their wall-builders to their advantage."
530 PRINT Y$"( The players are moved as follows:"
540 PRINT Y$"*%Player #1:    W ===> UP"Y$"*LPlayer #2:    8 ===> UP"
550 PRINT Y$"+3Z ===> DOWN"Y$"+Z2 ===> DOWN"
560 PRINT Y$",3A ===> LEFT"Y$",Z4 ===> LEFT"
570 PRINT Y$"-3S ===> RIGHT"Y$"-Z6 ===> RIGHT"
580 PRINT Y$"/ Note:  Player #2's directions are the same as the arrows"\n\t" on the right"
590 PRINT Y$"0'keyboard on the H89."
600 PRINT Y$"2'To exit the game at any time, type 'E'.  HAVE FUN!"
610 PRINT Y$"50Hit any key to continue. "Y5$;:A$=INPUT$(1):RETURN
620 :REMARK \t\tReal Time Function for MBASIC
630 DIM U0(3):U0(0)=&H36:U0(1)=&H1FF:U0(2)=&H77D8:U0(3)=&HC9
640 DEF USR0=VARPTR(U0(0))::REMARK \t\tClear Buffer
650 IF USR0(0)<>0 THEN 650
660 RETURN
