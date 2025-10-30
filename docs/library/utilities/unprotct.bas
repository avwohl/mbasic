10 REM  This program is written for MBASIC ver 5.21.
20 REM  To check it out, save it with the ,P option,
30 REM  then LOAD it, try to list it (fails), RUN it
40 REM  and try LIST again (works).
50 REM
60 PRINT"This is an UNPROTECT-program..."
70 PRINT"It will, when run, unprotect itself."
80 PRINT"Presently, it will run only on MBASIC 5.21"
90 PRINT
100 PRINT"Enter a decimal address where you know are at least 11 bytes"
110 INPUT "free for temporary storage : ";A
120 PRINT
130 REM   this is the code to UNprotect a loaded file:
140 REM
150 REM  mvi a,31h
160 REM  sta 803h  <= may be different in other versions
170 REM  xra a
180 REM  sta 0bech <=  "   "     "      "   "       "
190 REM  ret
200 REM
210 REM  call the above routine wherever you loaded it
220 REM  by 1) setting a variable to the address and
230 REM     2) calling it with CALL <variable>.
240 REM  you can UNprotect lots of files this way; you
250 REM  don't have to enter the routine or reload MBASIC.
260 REM
270 FOR I=0 TO 9
280 READ N
290 POKE A+I,N
300 NEXT
310 CALL A
320 PRINT:PRINT
330 PRINT"The file is now UNprotected - try it by LISTing..."
340 END
350 DATA &H3E,&H31,&H32,3,8,&HAF,&H32,&HEC,&H0B,&HC9
