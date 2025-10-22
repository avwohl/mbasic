10 ' Compute Bearings
20 ' For The Tandy Model 100
30 ' adapted from a public domain program
40 ' by Paul Macdonald v1.2 01/27/85
50 ' Epson Geneva version in pcs-19 dl6
60 ' adapted for CP/M by Jim Lill 3 July 87
70 ' also made small format changes
80 CLS$=CHR$(26) : ' change this for your terminal
90 PRINT CLS$
100 PRINT "Compute Bearings Program"
110 PRINT "------------------------":PRINT
120 R=3953*12*5280*.0000254
130 PI=4*ATN(1)
140 K=1
150 KK=2
160 FOR J=K TO KK
170 Z$="Destination"
180 IF J=1 THEN Z$="Source" ELSE PRINT
190 PRINT"";Z$;" Latitude  (Degs, Mins, N or S)";
200 INPUT A(J),X,S$
210 A(J)=PI*((A(J)+X/60)/180)
220 IF A(J)=0 THEN 270
230 S$=LEFT$(S$,1)
240 IF S$="N" OR S$="n" THEN 270
250 IF S$="S" OR S$="s" THEN A(J)=-A(J):GOTO 270
260 GOTO 190
270 PRINT Z$;" Longitude (Degs, Mins, E or W)";
280 INPUT B(J),X,S$
290 B(J)=PI*((B(J)+X/60)/180)
300 IF B(J)=0 OR B(J)=PI THEN 350
310 S$=LEFT$(S$,1)
320 IF S$="E" OR S$="e" THEN 350
330 IF S$="W" OR S$="w" THEN B(J)=-B(J):GOTO 350
340 GOTO 270
350 NEXT J
360 C=COS(A(2))
370 X=C*COS(B(2))
380 C=C*SIN(B(2))
390 D=SIN(A(2))
400 H=SIN(A(1))
410 G=COS(B(1))
420 J=SIN(B(1))
430 K=COS(A(1))
440 W=(G*X)+(J*C)
450 E=(H*W)-(K*D)
460 F=(G*C)-(J*X)
470 G=(K*W)+(H*D)
480 IF ABS(ABS(G)-1)<.00001 THEN 510
490 W=1-G*G
500 IF W>0 THEN H=ATN(G/SQR(W)):GOTO 520
510 H=G*PI/2
520 IF ABS(ABS(G)-1)<=.00001 OR W<=0 THEN PRINT"Any Angle OK ";:GOTO 630
530 IF E>0 THEN X=ATN(F/E):GOTO 590
540 X=PI/2
550 IF F<=0 THEN X=-X
560 IF E>=0 THEN 590
570 X=(ATN(F/E))-PI
580 IF F>=0 THEN X=X+2*PI
590 D=180*(PI-X)/PI
600 C=INT(D+.5)
610 IF C=360 THEN C=0
620 PRINT:PRINT "Heading: "C" Degrees ";
630 PRINT"and "
640 D=R*(.5*PI-H)
650 C=INT(D+.5)
660 PRINT"Range: "C" Kilometers or"
670 PRINT C*.6215" Miles."
680 PRINT:PRINT
690 INPUT"New Source (Y/N)";Y$(1)
700 INPUT"New Destination (Y/N)";Y$(2)
710 IF Y$(1)<>"Y" AND Y$(2)<>"Y" THEN GOTO 730
720 GOTO 740
730 IF Y$(1)<>"y" AND Y$(2)<>"y" THEN 810
740 K=1
750 KK=2
760 IF Y$(1)<>"Y" AND Y$(1)<>"y" THEN K=2
770 IF Y$(2)<>"Y" AND Y$(2)<>"y" THEN KK=1
780 PRINT CLS$:PRINT "Compute Bearings Program"
790 PRINT "------------------------":PRINT
800 GOTO 160
810 PRINT CLS$:PRINT:PRINT "Program Terminated on Request."
820 END
