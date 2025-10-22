10 :REMARKThis program entered into the public domain on 11 February 1984
20 :REMARKby William van Riper.  It runs on the Osborne EXECUTIVE but may
30 :REMARKbe altered to run on the Osborne 1.  Its use is intended to be
40 :REMARKinstructional and is COPYRIGHTED as such.  Please respect this.
50 :REMARKAny bugs or fixes in this or the accompanying set of programs may
60 :REMARKbe sent to me c/o MBINEX - 617-423-6985 - username VANRYPER.
61 :REMARK
62 :REMARK
69 :REMARKMakes a function to direct-cursor-address the screen:
70 DEF  FNP$(X,Y)=CHR$(27)+"="+CHR$(Y+32)+CHR$(X+32)
80 WIDTH 255
90 PRINT  CHR$(26)
95 :REMARK
100 PRINT  FNP$(5,5);"*** FINDCHAR MENU ***"
110 PRINT  FNP$(5,8);"1. Look at one character at a time"
120 PRINT  FNP$(5,10);"2. Run through characters 0-255"
130 PRINT  FNP$(5,12);"3. Exit to MBASIC"
140 PRINT  FNP$(5,16);"Please enter you selection: ";
150 X$=INKEY$:IF X$=""  THEN 150
160 IF X$="1"  THEN  GOTO 340
170 IF X$="3"  THEN  WIDTH 80:PRINT  CHR$(26):FILES:END
180 IF X$="2"  THEN  GOTO 190 :ELSE  GOTO 150
184 :REMARK
185 :REMARK
186 :REMARKthis runs through the characters sequentially from 1-255
187 :REMARKnote the bank-switching stuff which is needed on the EXEC - the OUT 0,65
188 :REMARKshadows in video memory in bank 7 - the OUT 0,1 shadows it out so the
189 :REMARKsystem won't hang!
190 PRINT  CHR$(26)
200 PRINT  CHR$(27)+CHR$(46)+CHR$(48)::REMARKthis turns off the cursor
204 PRINT  FNP$(5,12);"When poking directly to video memory,"
210 PRINT  FNP$(15,22);"HIT ANY KEY TO CONTINUE, <ESC> FOR MENU...";
220 FOR I=0  TO 255
230 OUT 0,65
240 POKE 1.55591,I
250 OUT 0,1
260 PRINT  FNP$(29,14);I;FNP$(20,14);"ASCII: ";FNP$(35,14);"=";
265 IF I<32  THEN  GOTO 270
266 PRINT  FNP$(10,16);"BUT  PRINT CHR$(";I;") yields: ";:PRINT  CHR$(I);
270 X$=INKEY$:IF X$=""  THEN 270
280 IF  ASC(X$)=27  THEN 320
290 NEXT I
300 PRINT  FNP$(20,14);"                                             "
305 PRINT  FNP$(10,16);"                                                  "
310 GOTO 220
320 PRINT  CHR$(27)+CHR$(46)+CHR$(50)::REMARKthis turns the cursor back on again...
330 GOTO 90
332 :REMARK
333 :REMARK
334 :REMARKthis allows you to check on the character that will be written when
335 :REMARKyou poke it to video memory - it's not always what you might think -
336 :REMARKthis is because you have a choice of graphics and standard characters
337 :REMARKin both normal and reverse video
338 :REMARK
340 PRINT  CHR$(26):PRINT:PRINT:PRINT:PRINT
350 PRINT  FNP$(5,5);:INPUT "Enter ASCII value desired: ",X
360 PRINT  FNP$(20,14);"                                    "
370 OUT 0,65
380 POKE 1.55591,X
390 OUT 0,1
400 PRINT  FNP$(19,12);"ASCII VALUE"
410 PRINT  FNP$(36,12);"CHARACTER"
420 PRINT  FNP$(22,14);X;
430 PRINT  FNP$(5,22);"HIT ANY KEY TO CONTINUE, <ESC> FOR MENU....";
440 X$=INKEY$:IF X$=""  THEN 440
450 PRINT  FNP$(30,5);"            "
460 IF  ASC(X$)=27  THEN  GOTO 90
470 GOTO 350
480 END
6682 ONTINUE, <ESC> FOR MENU....";
440 X$=INKEY$:IF X$
