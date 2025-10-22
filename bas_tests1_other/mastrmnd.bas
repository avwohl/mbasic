10 :REMARK        MASTRMND.BAS
20 :REMARK  Written by Evan J. Callahan
30 :REMARK  Date Completed: June 1981
40 :REMARK
50 :REMARK  E. Callahan     MODIFIED BY P. SWAYNE, HUG
60 :REMARK  2514 169th N.E.
70 :REMARK  Bellevue, WA 98008
80 :REMARK
90 :REMARK  PURPOSE:     This is the popular game of Mastermind by Invicta.  It is a
100 :REMARK         game of logic in which the player tries to guess the hidden code
110 :REMARK         in as few attempts as possible.
120 :REMARK
130 :REMARK     *** GAME BEGINS ***
140 :REMARK
150 :REMARK     Set up board on screen
160 E$=CHR$(27):F$=E$+"F":G$=E$+"G":P$=E$+"p":Q$=E$+"q":Y$=E$+"Y"
170 PRINT E$+"E"
180 PRINT Y$"*=Want instructions? <N> ";:A$=INPUT$(1):PRINT A$
190 PRINT E$"E"E$+"x5"
200 IF A$="Y"  OR A$="y"  THEN  GOSUB 1000
210 PRINT E$+"x1"
220 PRINT P$;F$"        faaaaaaaaaaaac"
230 PRINT P$"  CODE>>` w  w  w  w `"
240 PRINT "faaaaaaabaaaaaaaaaaaat"
250 A$="`^ ^ ^ ^` ^  ^  ^  ^ `"
260 B$="vaaaaaaabaaaaaaaaaaaat"
270 FOR X1=1  TO 9:PRINT A$;Q$;X1;P$:PRINT B$:NEXT X1
280 PRINT A$;Q$;X1;P$
290 PRINT "eaaaaaaauaaaaaaaaaaaad";
300 PRINT Q$;G$
310 PRINT Y$"&F>>MASTER MIND<<";Y$")?R=RED    O=ORANGE   Y=YELLOW"
320 PRINT Y$"*?G=GREEN   B=BLUE    P=PURPLE"
330 PRINT Y$",?Q=QUIT    C=CLEAR (GUESS AGAIN)
340 PRINT Y$".?B=BLACK PEG (RIGHT COLOR, RIGHT PLACE)"
350 PRINT Y$"/?W=WHITE PEG (RIGHT COLOR, WRONG PLACE)"
360 :REMARK
370 :REMARK     Figure out hidden code
380 FOR N=0  TO 3
390 C(N)=INT(6*RND(1)+1)
400 GOSUB 800
410 NEXT N
420 :REMARK
430 :REMARK     Start guessing loop
440 FOR TN=1  TO 10
450 PRINT Y$"8 GUESS NUMBER"TN"? ";
460 :REMARK     Input loop
470 IN$="":PRINT Y$"81                    ";Y$"82";
480 PRINT E$"y5";:FOR X3=0  TO 3
490 I1$=INPUT$(1):IF I1$="Q"  THEN 930 :ELSE  IFI1$="C" THEN 470
500 IF I1$<>"Y" ANDI1$<>"B" ANDI1$<>"G" ANDI1$<>"O" ANDI1$<>"R" ANDI1$<>"P"  THEN 
     PRINT  CHR$(7);:GOTO 490
510 PRINT I1$;" ";:IN$=IN$+I1$:NEXT X3
520 PRINT E$"x5";:FOR X1=0  TO 3:G(X1)=ASC(MID$(IN$,X1+1,1)):NEXT X1
530 L1$=CHR$(TN*2+33)
540 PRINT Y$L1$"*" CHR$(G(0));Y$L1$"-" CHR$(G(1));Y$L1$"0" CHR$(G(2))
550 PRINT Y$L1$"3" CHR$(G(3))
560 PRINT Y$"8 <RETURN> OR 'C' ";:I2$=INPUT$(1)
570 IF I2$="C"  THEN 450 :ELSE  IF I2$<>CHR$(13) THEN 560
580 :REMARK     Figure out black pegs
590 PRINT Y$L1$"!";
600 BL=0
610 FOR K=0  TO 3
620 IF G(K)=C(K)  THEN  PRINT "B";E$+"C";:BL=BL+1
630 NEXT K
640 IF BL=4  THEN 890
650 :REMARK     Figure out white pegs
660 FOR X1=0  TO 3:C1(X1)=0:NEXT X1
670 FOR I=0  TO 3
680 FOR J=0  TO 3
690 IF G(I)<>C(J)  OR C1(J)=1  THEN 740
700 C1(J)=1
710 IF BL<>0  THEN BL=BL-1:GOTO 750
720 PRINT "W";E$+"C";
730 GOTO 750
740 NEXT J
750 NEXT I
760 NEXT TN
770 GOTO 910
780 :REMARK
790 :REMARK     Subroutine - turns numbers into letters for secret code
800 ON C(N) GOTO 810,820,830,840,850,860
810 C(N)=89:RETURN
820 C(N)=82:RETURN
830 C(N)=80:RETURN
840 C(N)=79:RETURN
850 C(N)=71:RETURN
860 C(N)=66:RETURN
870 :REMARK
880 :REMARK     End of game messages
890 PRINT Y$"8 *** YOU WIN! ***         "
900 GOTO 940
910 PRINT Y$"8 *** YOU LOSE! ***        "
920 GOTO 940
930 PRINT Y$"8 *** QUITTER!! ***        "
940 PRINT Y$"!*" CHR$(C(0));Y$"!-" CHR$(C(1));Y$"!0" CHR$(C(2));Y$"!3" CHR$(C(3))
950 FOR X=1  TO 500:NEXT X
960 PRINT Y$"8 DO YOU WISH TO PLAY AGAIN? <Y>";:AG$=INPUT$(1)
970 IF AG$<>"N"  AND AG$<>"n"  THEN  PRINT E$+"E";Y$"  ":GOTO 170
980 PRINT Y$"  ";G$;Q$;E$+"E";E$+"y1";E$+"y5"
990 END
1000 PRINT "                     MASTER MIND INSTRUCTIONS
1010 PRINT "
1020 PRINT "
1030 PRINT " This is the game of Master Mind.  I will think of a secret  code
1040 PRINT " consisting  of four colors in a certain  order.  You will get 10
1050 PRINT " chances  to guess the code.  Each turn you must enter  the first
1060 PRINT " letters  of the four colors  you choose.   After you enter  four
1070 PRINT " letters,  I will display them on the playing  board.  If at this
1080 PRINT " point you are satisfied  with your entry,  hit RETURN.   If not,
1090 PRINT " type C to clear the entry and start  over.   You can also type C
1100 PRINT " to clear before you have typed all 4 colors.
1110 PRINT "
1120 PRINT " To the left of your colors on the board, I will place a B (black
1130 PRINT " peg) for every correct  color  that is in the correct  position,
1140 PRINT " and a W (white  peg) for every color that is correct  but in the
1150 PRINT " wrong position.   Please note that the position  of my pegs does
1160 PRINT " not necessarily  correspond  with the position  of your  correct
1170 PRINT " entries.   For example,  if I put a B in the first position,  it
1180 PRINT " means  that  one of your  colors  is correct  and  in the  right
1190 PRINT " position, but not necessarily the first one.
1200 PRINT "
1210 PRINT " Good luck!   Hit RETURN to continue.";
1220 LINE  INPUT A$:PRINT E$"E";:RETURN
