5  :REMARKthis is the program VIDEONUM - displays memory locations in bank 7
6  :REMARKof the Osborne EXECUTIVE by W. van Riper 1984
7  :REMARK
10 PRINT  CHR$(26)
15 :REMARK
16 :REMARKdefines direct cursor addressing:
17 :REMARK
20 DEF  FNP$(X,Y)=CHR$(27)+"="+CHR$(Y+32)+CHR$(X+32)
21 :REMARK
22 :REMARKthis is the arithmetic which talks about the memory offset to the 
23 :REMARKfollowing line - a function which allows you to write to a specific
24 :REMARKscreen memory location is like: FNP(X,Y)=(X+(128*Y)+49152), and
25 :REMARKyou would poke to this location, specifying X and Y  just like you would in
26 :REMARKdirect cursor addressing except you have to switch in bank 7 with the OUT
27 :REMARKfunction - see comments in the program FINDCHAR of this series
28 :REMARK
29 DEF  FNV(X,Y)=(X+(128*Y)+1.46948)
30 :REMARK
31 WIDTH 255::REMARK this makes the direct cursor addressing work right...
32 :REMARK
40 FOR Y=0  TO 22
50 PRINT  FNP$(1,Y);(Y*128+1.5);" ";"BEGINS ROW ";Y
60 PRINT  FNP$(50,Y);"WHICH  ENDS AT ";(Y*128+1.50241)
70 NEXT Y
80 X$=INKEY$:IF X$=""  THEN 80
90 PRINT  CHR$(26):WIDTH 80:FILES:END
6682 @ STOP);" ";"BEGINS ROW 
