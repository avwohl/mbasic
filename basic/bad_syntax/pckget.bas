5  ' Run this program on the PC in conjunction with a Fortran program on the
6  ' mainframe to get Kermit to the PC
7  ' Daphne Tzoar , January 1983
8  ' Columbia University Center for Computing Activities
9  '
10 OPEN "com1:4800,n,8,1" AS #1        ' Clear the port status.
20 CLOSE #1
30 OPEN "com1:4800,n,8,1,cs,ds,cd" AS #1
40 OPEN "KERMIT.EXE" FOR OUTPUT AS #2
50 OK$ = "ok"
60 PRINT#1,OK$		   ' Tell host we're ready for data
70 X$=INPUT$(65,#1)        ' Data plus semi-colon
80 VALUE$ = LEFT$(X$,1)      'First char of input
90 VALUE = ASC(VALUE$)
100 IF VALUE = 64 OR VALUE = 192 GOTO 430    ' @ means we're done
110 IF VALUE >= 160 AND VALUE <= 175 THEN GOTO 140   ' Kill all illegal chars
120 IF VALUE >= 32 AND VALUE <= 47 THEN GOTO 140
130 X$ = MID$(X$,2) : GOTO 80
140 IF VALUE <> 174 GOTO 210     ' Not a dot (for read) - don't worry
150 TWO$ = MID$(X$,2,1)          ' Look at char after the dot.
160 TWO = ASC(TWO$)
170 IF TWO >= 160 AND TWO <= 175 THEN GOTO 210    ' It's ok.
180 IF TWO >= 32 AND TWO <= 47 THEN GOTO 210
190 X$ = MID$(X$,3)	    ' Kill the char
200 GOTO 80
210 SIZ = LEN(X$)           ' How much input was actual data
220 READIN = 65 - SIZ
230 XTWO$=INPUT$(READIN,#1)     ' Get rest of data
240 X$ = X$ + XTWO$ : X$ = LEFT$(X$,64)
250 PRINT X$         ' Optional - use this line to follow the transmission
260 GOSUB 290
270 PRINT#2,X$;      ' Put data to the file.
280 GOTO 60
290 ' GET TWO CHARS, SUBTRACT SPACE (20 HEX) FROM EACH, AND COMBINE
300 ' TO ONE DIGIT.
310 FOR A = 1 TO 32
320 Y$ = MID$(X$,A,1)
330 Z$ = MID$(X$,A+1,1)
340 YNUM = ASC(Y$) : ZNUM = ASC(Z$)
350 IF YNUM > 127 THEN YNUM = YNUM - 128    ' Turn off hi bit if on
360 IF ZNUM > 127 THEN ZNUM = ZNUM - 128
370 YNUM = YNUM -32 : ZNUM = ZNUM -32       ' Subtract the space
380 XNUM = (16 * YNUM) +ZNUM
390 NEWCHR$ = CHR$(XNUM)
400 X$ = MID$(X$,1,A-1) + NEWCHR$ + MID$(X$,A+2)
410 NEXT A
420 RETURN
430 PRINT  " [All done.]"
440 CLOSE #1,#2                            ' Clean up.
450 END
