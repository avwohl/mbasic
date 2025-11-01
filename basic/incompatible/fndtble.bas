100 REM Find SINCON and ATNCON Tables (FNDTBLE.BAS)
110 REM by Jim McClanahan, W4JBM (Sept. 2020)
120 REM
130 REM This program searches for the tables that ultimately create the
140 REM tables found by van den Assem and van Elk in their program KRAKINST.BAS.
150 REM
160 REM This program is not at all elegant.
170 REM This program takes a long time to run.
180 REM To make it a bit less painful, this program does "assume"
190 REM      some pre-knowledge that the tables we are searching for are
200 REM      only about 250 bytes apart. Without that assumption, the time
210 REM      it takes to yield results is even longer.
220 REM
230 FOR A%=255 TO 30000
240 FOR B%=A%-250 TO A%+250
250 IF (PEEK(A%) XOR PEEK(B%)) <> 206 THEN 300
260 IF (PEEK(A%-1) XOR PEEK(B%-1)) <> 70 THEN 300
270 IF (PEEK(A%-2) XOR PEEK(B%-2)) <> 221 THEN 300
280 IF (PEEK(A%-3) XOR PEEK(B%-3)) <> 79 THEN 300
290 PRINT A%,B%
300 NEXT B%
310 NEXT A%
