10 PRINT TAB(26) "ROTATE"
20 DIM B(16), B$(16)
30 PRINT "     In this game the board layout is as follows:"
40 FOR I = 1 TO 16 : B(I) = I : NEXT I
50 PRINT : FOR I = 1 TO 13 STEP 4
60 PRINT TAB(2);B(I);TAB(6);B(I+1);TAB(10);B(I+2);TAB(14);B(I+3)
70 NEXT I : PRINT
80 PRINT "     Board positions are occupied randomly by the letters A to P."
90 PRINT "The object of the game is to order the letters by rotating any"
100 PRINT "four letters clockwise, by 90 degrees. You specify the upper left"
110 PRINT "position of the four you wish to rotate. Valid moves are:"
120 PRINT "	1  2  3  5  6  7  9  10  and  11."
130 PRINT "     You also get one special move per game, which you may or may"
140 PRINT "not need. Input a -1 and you may exchange any two letters in a row."
150 PRINT "     To give up, enter a '0' to the prompt. --- GOOD LUCK!"
160 PRINT : PRINT : PRINT : PRINT : PRINT
170 FOR I = 1 TO 16 : B$(I) = "Z" : NEXT I
180 FOR I = 1 TO 16
190 T$ = CHR$(INT(16*RND(1)+65))
200 FOR J = 1 TO I
210 IF B$(J) = T$ THEN 190
220 NEXT J
230 B$(I) = T$ : NEXT I
240 M = 0 : S = 0 : PRINT "     Here's the starting board......" : GOSUB 400
250 INPUT "Position to rotate"; I : IF I = 0 THEN 160
260 IF I = -1 THEN 440
270 IF I = 4 OR I = 8 OR I >11 THEN PRINT "ILLEGAL!   TRY AGAIN..." : GOTO 250
280 M = M + 1 : T$ = B$(I)
290 B$(I) = B$(I + 4) : B$(I + 4) = B$(I + 5) : B$(I + 5) = B$(I + 1) : B$(I + 1) = T$
300 GOSUB 400
310 FOR I = 1 TO 16
320 IF CHR$(I + 64) <> B$(I) THEN GOTO 250
330 NEXT I
340 PRINT : PRINT : PRINT "     You finished in";M;"moves."
350 M1 = M1 + M : G1 = G1 + 1
360 PRINT CHR$(7) : FOR I = 1 TO 15 : NEXT I
370 PRINT : INPUT "Play again"; A$ : IF LEFT$(A$,1) = "Y" THEN GOTO 160
380 PRINT : PRINT "You played";G1;"games and finished in an average of"
390 PRINT M1/G1"moves per game." : PRINT : GOTO 490
400 PRINT : FOR I = 1 TO 13 STEP 4
410 PRINT B$(I)" "B$(I + 1)" "B$(I + 2)" "B$(I + 3)
420 NEXT I : PRINT
430 PRINT "MOVE";M;"     GAME";G1+1 : PRINT : RETURN
440 INPUT "Exchange which two positions"; X, Y
450 IF X<>Y+1 AND X<>Y-1 THEN PRINT "ILLEGAL!    Try again..." : GOTO 440
460 S = S + 1 : IF S > 1 THEN PRINT "Only ONE special move per game."
470 IF S > 1 THEN GOTO 250
480 T$ = B$(X) : B$(X) = B$(Y) : B$(Y) = T$ : GOTO 310
490 END
