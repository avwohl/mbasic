10 PRINT
20 PRINT "Please wait while I 'Clean House' on Array Set-up..."
30 PRINT
40 CLEAR 3000
50 D=2500
60 S=0
70 DIM B$(2550)
80 DIM C(D)
90 DIM L$(D)
100 FOR N=0 TO D
110 L$(N)="%"
120 NEXT N
130 PRINT "Enter Analysis Text, and terminate with '%'"
140 PRINT
150 FOR N=0 TO 10
160 INPUT B$(N)
170 IF B$(N)="%" GOTO 190
180 NEXT N
190 PRINT "Working...and this will take some time!"
200 F=N-1
210 FOR N=O TO F
220 L=LEN(B$(N))
230 FOR K=1 TO L
240 A$=MID$(B$(N),K,1)
250 FOR J=0 TO D
260 IF L$(J)=A$ GOTO 330
270 NEXT J
280 L$(S)=A$
290 C(S)=C(S)+1
300 T=T+1
310 S=S+1
320 GOTO 350
330 C(J)=C(J)+1
340 T=T+1
350 NEXT K
360 NEXT N
370 M=1
380 FOR K=1 TO S-2
390 FOR N=1 TO S-M
400 IF C(N-1)=C(N) GOTO 470
410 T$=L$(N-1)
420 U=C(N-1)
430 L$(N-1)=L$(N)
440 C(N-1)=C(N)
450 L$(N)=T$
460 C(N)=U
470 NEXT N
480 M=M+1
490 NEXT K
500 PRINT
510 PRINT "       Character Frequency Analysis"
520 PRINT "       ============================"
530 PRINT
540 PRINT "Total Characters Entered = ",T
550 PRINT
560 PRINT "Character","Occurrence","Probablity (%)"
570 PRINT "------------------------------------------"
580 PRINT
590 FOR N=0 TO D
600 PRINT L$(N),C(N),100*(C(N)/T)
610 IF L$(N)="%" GOTO 630
620 NEXT N
630 PRINT "------------- End of Analysis ------------":END
