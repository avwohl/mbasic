10 ' CPM-PERT Program from Interface Age, Feb 1981
20 ' Written by Richard Parry
30 ' Adapted to Microsoft BASIC by Charles H Strom
40 ' Dressed up & Adapted to Freedom 100 and Decision I 10 Apr 84 [Toad hall]
50 ' Added COUT and LIST location from CP/M and BIOS jump table to alleviate
60 ' problems with reserved locations in Page 0, problems with RST 1 and 3
70 ' (my CP/M didn't have them), having to run any special programs, etc.
80 ' Also changed location in MBASIC of CONOUT routine (different in V5.1).
90 ' David Kirschbaum, Toad Hall
100 ' 7573 Jennings Lane, Fayetteville NC 28303  (919)868-3471/396-6862
110 ' ARPANet ABN.ISCAMS@USC-ISID
120 '
130 '== Locate COUT (conout) and LIST in CP/M BIOS Jump Table ==
140 '
150 ' Location of warm boot in BIOS jump table can be found at bytes 0001
160 ' (Least Significant Byte, LSB), and 0002 (Most Significant Byte, MSB).
170 '
180 COUT1%=PEEK(1) : COUT2%=PEEK(2)	'get LSB and MSB of warm boot jump
190 COUT1%=COUT1%+9	'bump up 9 bytes from warm boot to COUT
200   IF COUT1%<256 THEN 220		'no need to increase MSB
210 COUT2%=COUT2%+256 : COUT1%=COUT1%-256	'inx MSB, dx LSB
220 LST2%=COUT2% : LST1%=COUT1%+3	'bump up 3 bytes from COUT to LIST
230   IF LST1%<256 THEN 280		'no need to increase MSB
240 LST2%=LST2%+256 : LST1%=LST1%-256	'inx MSB, dx LSB
250 '
260 '== Initialize Normal Distribution Constants
270 '
280 RN=15: RS=SQR(3/RN)
290 CONOUT%= &H41B8	'Loc in MBASIC 5.1 of call to CONOUT
300 '			 old value for MBASIC 5.21 was &H41E4
310 CLR$=CHR$(27)+"*"	' Home cursor and clear screen for Freedom 100 terminal
320 '
330 ' == Input Data ==
340 ' 
350 PRINT CLR$;
360 PRINT "CPM or PERT Simulation?  (C/P):  ";
370 Q$=INKEY$:IF LEN(Q$)<1 THEN 370 ELSE PRINT Q$
380   IF Q$<>"C" AND Q$<>"P" THEN PRINT "ERROR!  Try again.":GOTO 360
390 PRINT "Do you want a HARD-COPY record?  (Y/N):  ";
400 HC$=INKEY$:IF LEN(HC$)<1 THEN 400 ELSE PRINT HC$
410   IF HC$<>"Y" AND HC$<>"N" THEN PRINT "ERROR!  Try again.":GOTO 390
420   IF HC$<>"Y" THEN 450
430 PRINT "Note - SETUP.ASM must be loaded before MBASIC"
440 PRINT "or printer will not function!"
450 PRINT:INPUT "Number of Activities:  ",N
460 DIM ML(N), MO(N), MP(N), CP(N), ME(N), SD(N), IC(20)
470 DIM S(N), F(N), D(N), E(N), L(N), F1(N)
480 FOR I=1 TO N
490   PRINT CLR$: PRINT "Activity:  ",I: PRINT
500   GOSUB 2190				'Go to Input Data routine
510 NEXT I
520 PRINT CLR$;
530 PRINT "Would you like to examine or edit the Input Data?  (Y/N):  ";
540 Q1$=INKEY$:IF LEN(Q1$)<1 THEN 540 ELSE PRINT Q1$
550   IF Q1$<>"Y" AND Q1$<>"N" THEN PRINT "ERROR!  Try again.":GOTO 530
560   IF Q1$="N" THEN 860
570 GOSUB 2350		'Sort Input Data
580 '
590 '== Display Input Data ==
600 '
610 IF HC$<>"Y" THEN 640
620 IF HC$<>"Y" THEN 640
630   POKE CONOUT%,LST1%:POKE CONOUT%+1,LST2%
640 PRINT CLR$:IF Q$<>"C" THEN 690
650 PRINT "ACTIVITY #    FROM       TO     DURATION"
660 FOR I = 1 TO N
670   PRINT TAB(5); I; TAB(15); S(I); TAB(25); F(I); TAB(35); D(I)
680 NEXT I:GOTO 740
690 PRINT "ACTIVITY #    FROM       TO        ML       MO        MP"
700 FOR I = 1 TO N
710   PRINT TAB(5); I; TAB(15); S(I); TAB(25); F(I);
720   PRINT TAB(35); ML(I); TAB(45); MO(I); TAB(55); MP(I)
730 NEXT I:PRINT
740 POKE CONOUT%,COUT1%:POKE CONOUT%+1,COUT2%
750 PRINT "Would you like to edit an Activity?  (Y/N):  ";
760 Q1$=INKEY$:IF LEN(Q1$)<1 THEN 760 ELSE PRINT Q1$
770   IF Q1$<>"Y" AND Q1$<>"N" THEN PRINT "ERROR!  Try again.":GOTO 750
780   IF Q1$="N" THEN 860
790 '
800 '== Edit Mode ==
810 '
820 PRINT:INPUT "What activity needs alteration?  (0 to end):  ",I
830   IF I=0 THEN 520
840 GOSUB 2190				'Go to Input Data Routine
850 GOTO 820
860 GOSUB 2350			'Go to Sort Routine
870   IF Q$<>"C" THEN 1210
880 '
890 ' Critical Path Analysis requested.  Perform Critical Path
900 ' Analysis once and display results.
910 '
920 GOSUB 2600
930 C2=0
940 IF HC$<>"Y" THEN 960
950   POKE CONOUT%,LST1%:POKE CONOUT%+1,LST2%
960 PRINT CLR$;"CP Analysis is:"
970 PRINT: PRINT: PRINT "FROM","TO","EST","LFT","FLOAT": PRINT
980 FOR I = 1 TO N:PRINT S(I),F(I),E(S(I)),L(F(I)),F1(I):NEXT I
990 PRINT "The Critical Path Length is: ";PL
1000 PRINT: PRINT "The Critical Path is:":PRINT "FROM","TO": PRINT
1010 FOR I = 1 TO N
1020     IF F1(I) = 0 THEN 1040
1030 NEXT I
1040 PRINT S(I),F(I): C2=C2+1: IF I>N THEN 1080
1050 FOR M= 1 TO N
1060     IF S(M)=F(I) AND F1(M) = 0 THEN I=M: GOTO 1040
1070 NEXT M
1080   IF C1<>C2 THEN PRINT: PRINT "There is more than one Critical Path."
1090 PRINT:POKE CONOUT%,COUT1%:POKE CONOUT%+1,COUT2%
1100 PRINT "Would you like to edit an Activity or stop program?  (E/S):  ";
1110 Q1$=INKEY$:IF LEN(Q1$)<1 THEN 1110 ELSE PRINT Q1$
1120   IF Q1$="E" THEN PRINT:GOTO 640
1130   IF Q1$<>"S" THEN PRINT "ERROR!  Try again.":GOTO 1100
1140 END
1150 '
1160 '== PERT Simulation requested.  Perform Critical Path Analysis the
1170 '   number of times specified.  Store path lengths and increment
1180 '  Activities which appear on Critical Path.  Construct Histogram
1190 '  and display results.
1200 '
1210 FOR I = 1 TO N
1220   ME(I) = (MO(I)+4*ML(I)+MP(I))/6	'Compute Mean of each activity.
1230   SD(I) = (MP(I)-MO(I))/6	'Compute Standard Deviation of each activity.
1240 NEXT I
1250 '== Compute Most Optimistic Path Length ==
1260 DU=0: FOR I=1 TO N: CP(I)=0: E(I)=0: L(I)=0: NEXT I
1270 FOR I = 1 TO N: D(I)=MO(I): NEXT I
1280 GOSUB 2600
1290 BC=PL
1300 '== Compute Most Pessimistic Path Length ==
1310 DU=0: FOR I=1 TO N: CP(I)=0: E(I)=0: L(I)=0: NEXT I
1320 FOR I = 1 TO N: D(I)=MP(I): NEXT I
1330 GOSUB 2600
1340 WC=PL
1350 '== Initialize Key Variables ==
1360 DU=0: FOR I = 1 TO N: CP(I)=0: E(I)=0: L(I)=0: NEXT I
1370 LS=0: HS=0: FOR I=1 TO 20: IC(I)=0: NEXT I
1380 '== Initialize Random Number Generator ==
1390 RANDOMIZE
1400 '== Propose # of Transactions as 20 * # of Activities ==
1410 PRINT "Number of transactions should be >= "; 20*N
1420 INPUT "Number of transactions:  ",NS
1430 PRINT: PRINT "++SIMULATION IN PROGRESS++"
1440 '
1450 '== Construct Histogram ==
1460 '-- Set Appropriate Interval (i.e., Integer >=1) --
1470 LL=INT(BC)
1480   IF WC-BC<=20 THEN IN=1
1490 IN=INT((WC-BC)/20)+1
1500 '
1510 '-- Perform Simulation --
1520 TC=100
1530 FOR K=1 TO NS
1540     IF K=TC THEN PRINT "++ Simulation in Progress ++";TC: TC=TC+100
1550   FOR J=1 TO N
1560     S=0: E(J)=0: L(J)=0
1570       IF ML(J)=0 THEN D(J)=0: GOTO 1600
1580     FOR I=1 TO RN: S=S+2*RND-1: NEXT I
1590     D(J)=ME(J)+SD(J)*S*RS
1600   NEXT J
1610   GOSUB 2600
1620 '-- Find Interval for This Path Length --
1630   I3=(PL-LL)/IN+2
1640     IF I3<1 THEN LS=LS+1: GOTO 1680
1650     IF I3>20 THEN HS=HS+1: GOTO 1680
1660   I3=INT(I3)
1670   IC(I3)=IC(I3)+1
1680 NEXT K
1690 '
1700 '-- Print Frequency Distribution Table --
1710 IF HC$<>"Y" THEN 1730
1720   POKE CONOUT%,LST1%:POKE CONOUT%+1,LST2%
1730 PRINT CLR$;"++FREQUENCY DISTRIBUTION TABLE++": PRINT
1740 PRINT "Most OPTIMISTIC  path length: "; BC
1750 PRINT "Most PESSIMISTIC path length: "; WC
1760 PRINT "Number of transactions LOWER  than histogram range: ";LS
1770 PRINT "Number of transactions HIGHER than histogram range: ";HS: PRINT
1780 PRINT "     INTERVAL      FREQ.      PCT."
1790 I1=LL-IN: I2=LL
1800 FOR M=1 TO 20
1810   PRINT"=>";I1;"<";I2;TAB(20);IC(M);TAB(30);INT(.5+100*IC(M)/NS)
1820   I1=I1+IN: I2=I2+IN
1830 NEXT M
1840 '
1850 '== Print Histogram ==
1860 '-- Compute Histogram Scale Factor --
1870 SC=0: LO=18: J=0: LL=INT(BC)
1880 FOR M=1 TO 20
1890     IF IC(M)>SC THEN SC=IC(M)
1900 NEXT M
1910 SC=50/SC: X$="PATH LENGTH"
1920 PRINT: PRINT: PRINT TAB(24); "++ HISTOGRAM ++": PRINT
1930 PRINT TAB(18);"RELATIVE FREQUENCY OF PATH LENGTHS"
1940 PRINT TAB(LO); "+------------------------------------------------+"
1950 FOR M=1 TO 20
1960   HM=IC(M)*SC
1970   FOR K=1 TO 3
1980     J=J+1: PRINT MID$(X$,J,1);TAB(2);
1990       IF K=2 THEN PRINT ">=";LL-IN;"<";LL;: LL=LL+IN
2000     PRINT TAB(LO);
2010       IF IC(M)=0 THEN PRINT: GOTO 2030
2020     FOR I=1 TO HM: PRINT "*";: NEXT I: PRINT
2030   NEXT K
2040 NEXT M
2050 '
2060 '-- Print Activity Analysis --
2070 PRINT: PRINT
2080 PRINT TAB(10); "+++ CP ACTIVITY ANALYSIS TABLE +++": PRINT
2090 PRINT "ACTIVITY #    FROM      TO     CP FREQ.    PCT."
2100 FOR I=1 TO N
2110   PRINT TAB(5);I;TAB(15);S(I);TAB(25);F(I);
2120   PRINT TAB(35);CP(I);TAB(45);INT(.5+100*CP(I)/NS)
2130 NEXT I
2140 PRINT: PRINT "DUPLICATE critical paths occurred";DU;"times."
2150 GOTO 1090		'Quit??
2160 '
2170 '== Input Data Routine ==
2180 '
2190 INPUT "FROM:  ",S(I)
2200 INPUT "  TO:  ",F(I)
2210   IF F(I)>N THEN PRINT "++End Node # NOT <= # of Activities++":GOTO 2200
2220   IF S(I)>F(I) THEN PRINT "++Start Node MUST be < End Node++":GOTO 2190
2230   IF LEFT$(Q$,1)="C" THEN INPUT "Duration:  ",D(I): GOTO 2310
2240 INPUT "     Most Likely:  ",ML(I)
2250 '-- Check for Dummy Activity --
2260   IF ML(I)=0 THEN MO(I)=0: MP(I)=0: GOTO 2310
2270 INPUT " Most Optimistic:  ", MO(I)
2280   IF MO(I)>ML(I) THEN PRINT "++MO MUST be <= ML++": GOTO 2270
2290 INPUT "Most Pessimistic:  ", MP(I)
2300   IF MP(I)<ML(I) THEN PRINT "++MP MUST be >= ML++": GOTO 2290
2310 RETURN
2320 '
2330 '== Sort Data Using Start Node as Key ==
2340 '
2350 PRINT: PRINT "Sorting in Progress": PRINT
2360 SW=0
2370 FOR I=1 TO N-1
2380   J=I+1
2390     IF S(I)<=S(J) THEN 2470
2400   EX=S(I): S(I)=S(J): S(J)=EX
2410   EX=F(I): F(I)=F(J): F(J)=EX
2420   EX=D(I): D(I)=D(J): D(J)=EX
2430   EX=ML(I): ML(I)=ML(J): ML(J)=EX
2440   EX=MO(I): MO(I)=MO(J): MO(J)=EX
2450   EX=MP(I): MP(I)=MP(J): MP(J)=EX
2460   SW=1
2470 NEXT I
2480   IF SW=1 THEN 2360
2490 RETURN
2500 '
2510 '== The following subroutine is used by both the CPM Analysis
2520 '   and the PERT Simulation Analysis.  While the CPM Analysis
2530 '   calls the routine only once, the Simulation calls the
2540 '   routine the number of times requested by the user.
2550 '   The Earliest, Latest, and Float Times are computed, and
2560 '   from this data the Critical Path Length and Critical Path
2570 '   are calculated.  Duplicate Critical Paths are only counted once.
2580 '
2590 '== Compute Earliest Starting Time ==
2600 C1=0: C2=0: PL=0
2610 FOR I=1 TO N
2620   M1=E(S(I))+D(I)
2630     IF E(F(I))<=M1 THEN E(F(I))=M1
2640 NEXT I
2650 '== Compute Latest Finishing Time ==
2660 L(F(N))=E(F(N))
2670 FOR I=N TO 1 STEP -1
2680   L1=S(I): M2=L(F(I))-D(I)
2690     IF L(L1)>=M2 OR L(L1)=0 THEN L(L1)=M2
2700 NEXT I
2710 '== Compute Float Time ==
2720 FOR I=1 TO N
2730   F1(I)=L(F(I))-E(S(I))-D(I)
2740     IF F1(I)<.0001 THEN F1(I)=0: C1=C1+1
2750 NEXT I
2760 '== Compute Critical Path Length ==
2770 FOR I=1 TO N
2780     IF L(F(I))>PL THEN PL=L(F(I))
2790 NEXT I
2800 '== Compute Critical Path ==
2810 FOR I=1 TO N
2820     IF F1(I)=0 THEN 2840
2830 NEXT I
2840 C2=C2+1: CP(I)=CP(I)+1
2850   IF I>N THEN 2890
2860 FOR M=1 TO N
2870     IF S(M)=F(I) AND F1(M)=0 THEN I=M: GOTO 2840
2880 NEXT M
2890   IF C1<>C2 THEN DU=DU+1
2900 RETURN
