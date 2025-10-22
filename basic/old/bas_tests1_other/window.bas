4  :REMARKprogram name WINDOW for the Osborne EXECUTIVE - probably will not work
5  :REMARKat all on other terminals unless they have windowing capabilities -
6  :REMARK11 February 1984 by W. van Riper
7  :REMARK
10 PRINT  CHR$(26):PRINT:PRINT
12 DEF  FNP$(X,Y)=CHR$(27)+"="+CHR$(32+Y)+CHR$(32+X)::REMARKdirect cursor addressing
15 U=0:YS=0::REMARKflags test from later on in the program
16 :REMARK
17 :REMARK
20 PRINT:PRINT  TAB(10);"DEFINE AND SET WINDOWS"
30 PRINT:PRINT
40 INPUT "NUMBER OF WINDOW FOR FUTURE REFERENCE: ",N
70 PRINT
80 INPUT "X VALUES OF WIDTH (LEFT,RIGHT): ",LX,RX
90 PRINT
100 INPUT "Y VALUES OF HEIGHT (UPPER,LOWER): ",UY,LY
110 PRINT
120 PRINT "WINDOW NUMBER ";N
130 PRINT LX;" TO ";RX;" WIDE"
140 PRINT UY;" TO ";LY;" HIGH"
150 PRINT
160 PRINT "IS THIS CORRECT? ";
170 X$=INKEY$:IF X$=""  THEN 170
180 IF X$="N"  OR X$="n"  THEN  GOTO 10
181 :REMARK                                                                                  
182 PRINT  CHR$(26)
185 PRINT  FNP$(10,22);"Hit any key to examine window just created...";
187 X$=INKEY$:IF X$=""  THEN 187
190 PRINT
192 :REMARK
193 :REMARK
195 :REMARKthe following is the function that sets the window - N is the number
196 :REMARKof the window for future reference - the lines afterward fill the 
197 :REMARKwindow with a character so you can examine it
198 :REMARK
199 :REMARK
200 DEF  FNW$(N,UY,LX,LY,RX)=CHR$(27)+CHR$(122)+CHR$(N)+CHR$(32+UY)+CHR$(32+LX)+CHR$(32+LY)+CHR$(32+RX)
205 PRINT  CHR$(26)
210 DEF  FNP(X,Y)=((X+Y*128)+1.5)
220 PRINT  FNW$(N,UY,LX,LY,RX)
230 PRINT  CHR$(26)
240 FOR Y=UY  TO LY
250 FOR X=LX  TO RX
260 OUT 0,65
270 POKE (FNP(X,Y)),141
280 OUT 0,1
290 NEXT X
300 NEXT Y
305 GOSUB 600
310 X$=INKEY$:IF X$=""  THEN  GOTO 310
320 FOR I=1  TO 40:OUT 0,65:POKE 1.59015+I,32:OUT 0,1:NEXT I::REMARKmystery line
322 :REMARK
323 :REMARKthis gives you a chance to undo what you've just done before you go into
324 :REMARKthe save routine in line 331:
325 :REMARK
330 IF X$="U"  OR X$="u"  THEN U=1:GOTO 550
331 PRINT  CHR$(26):INPUT "NAME OF FILE TO SAVE UNDER: ",R$
340 OPEN "O",#1,R$+".BAS"
342 Z$="10000 REM THIS IS "+STR$(LX)+" TO "+STR$(RX)+" WIDE AND "+STR$(UY)+" TO "+STR$(LY)+" HIGH"
350 A$="10050 DEF FNW$(N,UY,LX,LY,RX)=CHR$(27)+CHR$(122)+"
360 B$=STR$(N+48):C$=STR$(UY):D$=STR$(LY):E$=STR$(RX):F$=STR$(LX)
370 G$="CHR$(32+"
380 T$="CHR$("+B$+")"+G$+C$+")"+G$+F$+")"+G$+D$+")"+G$+E$+")"
390 U$=A$+T$
395 PRINT#1,Z$
400 PRINT#1,U$
410 PRINT#1,"10100 RETURN"
420 CLOSE
450 :REMARK
460 :REMARKgives you a choice of either going back to the top to start another
470 :REMARKwindow or exit to MBASIC - if you go back to the top, make sure that
480 :REMARKyou give the next window another number and the file a new name, 
490 :REMARKunless you want to overwrite a previous file - the screen is restored
492 :REMARKhere whether you exit or not - I hate responding to those prompts
494 :REMARKin a tiny 2 by 25 window! - note that this is where those flags
496 :REMARKat the beginning of the program come from...
497 :REMARK
500 PRINT  CHR$(26)
510 PRINT "Another window (y/n)? ";
520 X$=INKEY$:IF X$=""  THEN 520
530 IF X$="Y"  OR X$="y"  THEN YS=1:GOTO 550
540 IF X$="N"  OR X$="n"  THEN  GOTO 550 :ELSE 520
550 PRINT  CHR$(27)+CHR$(122)+CHR$(49)+CHR$(32)+CHR$(32)+CHR$(55)+CHR$(112)
555 IF U=1  OR YS=1  THEN  GOTO 10
560 PRINT  CHR$(26):FILES:END
590 :REMARK
592 :REMARKthis is just a cosmetic subroutine but it illustrates how to poke
594 :REMARKa string of characters to video memory - mystery line 320 wipes it
595 :REMARKout again when no longer needed
596 :REMARK
600 S$="Hit any key to continue or U to undo..."
610 FOR I=1  TO  LEN(S$)
620 S=ASC(MID$(S$,I,1))
630 OUT 0,65
640 POKE 1.59015+I,S
650 OUT 0,1
660 NEXT I
670 RETURN
6682 key to continue or U to undo..."
610 FOR I=1  TO  LEN(S$)
620 S=ASC(MID$(S$,I,1))
630 OUT 0,65
640 POKE 1.59015+I,S
650 OUT 0,1
660 NEXT I
