10 '  EXITRBBS.BAS, version 1.1
20 '  Routine to allow users to leave comments before logging off
30 '  Original by Brian Kantor & Skip Hansen 09/81 (?)
40 '  Minor text changes, bye call, and time-on-system stuff added
50 '            by Ben Bronson, 10/11/81
60 '     Note that this is meant to be compiled and called "BYE.COM", while
70 '     the real assembly-language BYE.COM (which is still needed) is
80 '     given another name (here, 'BYEX.COM').  The easiest way to handle
90 '     this is to use Macro-80 to assemble a dummy file like the following:
91 '            ENTRY	BYEX
92 '            BYEX 	EQU	0F800H
93 '            	RET
94 '     where '0F800H' is the address at which the real BYE runs.  Then you
95 '     just include BYEX.REL when using L80 to load the BYE.REL file pro-
96 '     duced by BASCOMing BYE.BAS:  'L80 BYE,BYEX,BYE/N/E'
97 '  
100 '  Main routine for users to leave comments before logging off
120 '
130 DEFINT A-Z
140 DIM H(6),HT(6),HD(6)
150 ERS$=CHR$(8)+" "+CHR$(8)
165 OPEN "I",1,"A:LASTCALR":INPUT #1,N$,O$,F$,DT$:CLOSE
170 PRINT
180 PRINT "Want to leave any comments (Y/N)? ";:C=1:GOSUB 400:C=0
190 IF LEFT$(B$,1)="N" OR LEFT$(B$,1)="n" THEN 360
200 IF LEFT$(B$,1)<>"Y" AND LEFT$(B$,1)<>"y" THEN 180
210 PRINT
230 OPEN "R",1,"A:COMMENTS",65:FIELD#1,65 AS RR$
240 GET#1,1:RE=VAL(RR$)+1:RL=65
250 IF RE=1 THEN RE=2
260 S$="From: "+N$+" "+O$+" "+DT$:GOSUB 510   'This assumes you have the date in LASTCALR as "DT$"
270 PUT#1,RE
280 PRINT "Enter comments, <return> to end, (16 lines max)"
290 PRINT
300 PRINT "*";
310 GOSUB 400
320 IF B$="" THEN 350 
330 RE=RE+1:S$=B$:RL=65:GOSUB 510:PUT#1,RE 
340 GOTO 300
350 S$=STR$(RE):RL=65:GOSUB 510:PUT#1,1:CLOSE
360 GOSUB 44000
370 PRINT "Please call again"
390 CALL BYEX   'Calling the dummy file that points to the real BYE
395 END
400 '
410 '  Accept string into B$ from console
420 '
430 GOSUB 560
440 B$=SAV$
450 IF LEN(B$)=0 THEN RETURN
460 IF C=0 THEN 500
470 FOR ZZ=1 TO LEN(B$)
480    MID$(B$,ZZ,1)=CHR$(ASC(MID$(B$,ZZ,1))+32*(ASC(MID$(B$,ZZ,1))>96))
490 NEXT ZZ
500 RETURN
510 '
520 '  Fill and store disk record
530 '
540 LSET RR$=LEFT$(S$+SPACE$(RL-2),RL-2)+CHR$(13)+CHR$(10)
550 RETURN
560 CHC=0: SAV$=""
570 NCH=ASC(INPUT$(1))
580 IF NCH=127 THEN 640
590 IF NCH<32 THEN 670
600 IF CHC>=62 THEN PRINT CHR$(7);:GOTO 570
610 SAV$=SAV$+CHR$(NCH): CHC=CHC+1: PRINT CHR$(NCH);
620 IF CHC=55 THEN PRINT CHR$(7);
630 GOTO 570
640 IF CHC=0 THEN 570 ELSE PRINT RIGHT$(SAV$,1);: GOTO 660
650 IF CHC=0 THEN 570 ELSE PRINT ERS$;
660 CHC=CHC-1: SAV$=LEFT$(SAV$,CHC): GOTO 570
670 IF NCH=8 THEN 650
680 IF NCH=13 THEN PRINT: RETURN
690 IF NCH=21 THEN PRINT " #": GOTO 560
700 IF NCH<>24 OR CHC=0 THEN 570
710 FOR BCC=1 TO CHC: PRINT ERS$;: NEXT BCC: GOTO 560
44000 ' Clock routine from Hank Szyszka, modified
44010 ' Print present time first
44210 C=32 : ' C=CLOCK PORT (20H)
44220 ' Note that this is a Mountain Hardware 100,000 DAY Clock 
44230 H(1)=INP(C+9) AND 15:H(2)=INP(C+8) AND 15
44240 H(3)=INP(C+7) AND 15:H(4)=INP(C+6) AND 15
44250 H(5)=INP(C+5) AND 15:H(6)=INP(C+4) AND 15
44260 REM
44270 PRINT:PRINT N$+" "+O$+" logged off at ";
44280 TF$="#"
44290 FOR I=1 TO 6
44300 PRINT USING TF$;H(I);
44310 IF I=2 THEN PRINT ":";
44320 IF I=4 THEN PRINT ":";
44330 NEXT I
44340 PRINT
44700 '  Now get hh/mm/ss stored by enterbbs prog (not yet released as of 10/11/81)
44710 HT(1)=PEEK(74):HT(2)=PEEK(75):HT(3)=PEEK(76)
44720 HT(4)=PEEK(77):HT(5)=PEEK(78):HT(6)=PEEK(79)
44730 '  And calculate the difference...
44740 IF H(6)<HT(6) THEN H(6)=H(6)+10:H(5)=H(5)-1
44750 IF H(5)<HT(5) THEN H(5)=H(5)+6:H(4)=H(4)-1
44760 IF H(4)<HT(4) THEN H(4)=H(4)+10:H(3)=H(3)-1
44770 IF H(3)<HT(3) THEN H(3)=H(3)+6:H(2)=H(2)-1
44780 IF H(2)<HT(2) THEN H(2)=H(2)+10:H(1)=H(1)-1
44790 HD(6)=H(6)-HT(6):HD(5)=H(5)-HT(5):HD(4)=H(4)-HT(4)
44800 HD(3)=H(3)-HT(3):HD(2)=H(2)-HT(2):HD(1)=H(1)-HT(1)
44810 PRINT "You were on the system for ";
44820 TF$="#"
44830 FOR I=1 TO 6
44840 PRINT USING TF$;HD(I);
44850 IF I=2 THEN PRINT ":";
45860 IF I=4 THEN PRINT ":";
45870 NEXT I
45880 PRINT " (hrs/mins/secs)":PRINT
45890 RETURN
