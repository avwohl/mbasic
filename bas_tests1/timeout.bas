100	' TIMEOUT.BAS Version 1.3
101	' 
102	' Adapated from EXITRBBS.BAS by Bill Bolton
103	'
104	' August 26, 1982, Version 1.0
105	' This program is designed to run with a copy of BYE
106	' which executes a COM file after an "inactivity" timeout
107	' (Such as my BYE 7.2 Rev I or later). It logs the caller
108	' out, records the time off system and appends the
109	' marker "TIME" to their CALLERS entry so the SYSOP can
110	' easily tell who is timing out regularly. Bill Bolton
111	'------------------------------------------------------
112	' March 26, 1983, Version 1.1
113	' Fixed bug in elapsed time routine that gave strange
114	' results if login went over midnight. Bill Bolton
115	'------------------------------------------------------
117	' April 04, 1983, Version 1.2
118	' Added timout logging into DIRECT for SYSOP
119	' Bill Bolton
120	'------------------------------------------------------
121	' May 15, 1983, Version 1.3
122	' Added error trapping for case where DIRECT and CALLERS
123	' don't already exist (i.e. after general file purge or
124	' maintenance). The /X switch MUST be used at compile
125	' time. Bill Bolton
126	'------------------------------------------------------
200	'
220	DEFINT A-Z
240	DIM H(6),HT(6),HD(6),TOD(5),DOY(5)
250	ON ERROR GOTO 3000
260	MAGIC$ = "SUPER"
280	OPEN "I",1,"A:LASTCALR":
	INPUT #1,N$,O$,F$,DT$:
	CLOSE
300	GOSUB 1200:
	GOSUB 1840
320	IF N$ = MAGIC$ THEN
		GOSUB 580:
		GOTO 480		'Record timeout for SYSOP
340	OPEN "R",1,"A:C"+CHR$(&HC1)+"LLERS. "+CHR$(&HA0),60:
	FIELD#1, 60 AS RR$:
	GET #1,1
360	RE = VAL(RR$) + 1:
	RL = 60
380	GET #1,RE:
	INPUT#1,S$
400	IF INSTR(S$,":") THEN
		POINTER = INSTR(S$,":")
	ELSE
		POINTER = LEN(S$)
420	S$ = LEFT$(S$,POINTER + 2)  + " to " + TI$ + " " + F$ + MID$(S$,POINTER + 3) + " " + "TIME"
440	GOSUB 740
460	PUT #1,RE:
	CLOSE #1
480	'
500	GOSUB 2200
520	RUN "A:SUPER.COM"
540	END
560	'
580	OPEN "R",1,"A:D"+CHR$(&HC9)+"RECT. "+CHR$(&HA0),40:
	FIELD#1, 40 AS RR$:
	GET#1,1
600	RE = VAL(RR$) + 1:
	RL = 40
620	GET #1,RE:
	INPUT#1,S$
640	IF INSTR(S$,":") THEN
		POINTER = INSTR(S$,":")
	ELSE
		POINTER = LEN(S$)
660	S$ = LEFT$(S$,POINTER + 2)  + " to " + TI$ + " " + F$ + MID$(S$,POINTER + 3) + " " + "TIME"
680	GOSUB 740
700	PUT #1,RE:
	CLOSE #1
720	RETURN
740	'
760	'  Fill and store disk record
780	'
800	LSET RR$=LEFT$(S$+SPACE$(RL-2),RL-2)+CHR$(13)+CHR$(10)
820	RETURN
840	'
860	CHC=0:
	SAV$=""
880	NCH=ASC(INPUT$(1))
900	IF NCH=127 THEN
		1040
920	IF NCH<32 THEN
		1100
940	IF CHC>=62 THEN
		PRINT CHR$(7);:
		GOTO 880
960	SAV$=SAV$+CHR$(NCH):
	CHC=CHC+1:
	PRINT CHR$(NCH);
980	IF CHC=55 THEN
		PRINT CHR$(7);
1000	GOTO 880
1020	'
1040	IF CHC=0 THEN
		880
	ELSE
		PRINT RIGHT$(SAV$,1);:
		 GOTO 1080
1060	IF CHC=0 THEN
		880
	ELSE
		PRINT ERS$;
1080	CHC=CHC-1:
	SAV$=LEFT$(SAV$,CHC):
	GOTO 880
1100	IF NCH=8 THEN
		1060
1120	IF NCH=13 THEN
		PRINT:
		RETURN
1140	IF NCH=21 THEN
		PRINT " #":
		GOTO 860
1160	IF NCH<>24 OR CHC=0 THEN
		880
1180	FOR BCC=1 TO CHC:
		 PRINT ERS$;:
	NEXT BCC:
	GOTO 860
1200 ' Date getting subroutine
1220	BASEPORT = &H50
1240	CMDPORT = BASEPORT + 10
1260	DATAPORT = CMDPORT + 1
1280 '**********************************************************
1300 '*		READ THE DATE DIGITS			*
1320 '**********************************************************
1340	FOR DIGIT = 12 TO 7 STEP -1
1360		OUT CMDPORT,(&H10 + DIGIT)
1380		DOY(DIGIT - 7) = INP(DATAPORT)
1400	NEXT DIGIT
1420	YEAR= (DOY(5) * 10) + DOY(4)
1440	MONTH10 = DOY(3)
1460	MONTH1  = DOY(2)
1480	DAY10 = DOY(1)
1500	DAY1  = DOY(0)
1520 '**********************************************************
1540 '*		FORMAT THE FIRST DATE STRING		*
1560 '**********************************************************
1580	DATE1$="        "
1600	MID$(DATE1$,1,1) = RIGHT$(STR$(DAY10),1)
1620	MID$(DATE1$,2,1) = RIGHT$(STR$(DAY1),1)
1640	MID$(DATE1$,3,1) = "/"
1660	MID$(DATE1$,4,1) = RIGHT$(STR$(MONTH10),1)
1680	MID$(DATE1$,5,1) = RIGHT$(STR$(MONTH1),1)
1700	MID$(DATE1$,6,1) = "/"
1720	MID$(DATE1$,7,2) = RIGHT$(STR$(YEAR),2)
1740	DZ$ = DATE1$
1760	DT$ = LEFT$(DATE1$,5)
1780	DD$ = MID$(DATE1$,1,2)
1800	DM$ = MID$(DATE1$,4,2)
1820	RETURN
1840 '
1860 ' Time-finding subroutine
1880	FOR DIGIT = 5 TO 0 STEP -1
1900		OUT CMDPORT,(&H10 + DIGIT)
1920		TOD(DIGIT) = INP(DATAPORT)
1940		IF DIGIT = 5 THEN TOD(DIGIT) = TOD(DIGIT) AND 3
1960	NEXT DIGIT
1980	H(1) = TOD(5)
2000	H(2) = TOD(4)
2020	H(3) = TOD(3)
2040	H(4) = TOD(2)
2060	H(5) = TOD(1)
2080	H(6) = TOD(0)
2100	DH$ = "  ":
	DI$ = "  ":
	DS$ = "  "
2120	MID$(DH$,1,1) = RIGHT$(STR$(H(1)),1):
	MID$(DH$,2,1) = RIGHT$(STR$(H(2)),1):
	MID$(DI$,1,1) = RIGHT$(STR$(H(3)),1):
	MID$(DI$,2,1) = RIGHT$(STR$(H(4)),1):
	MID$(DS$,1,1) = RIGHT$(STR$(H(5)),1):
	MID$(DS$,2,1) = RIGHT$(STR$(H(6)),1)
2140	TI$=DD$+"-"+DH$+":"+DI$
2160	TD$=DH$+":"+DI$+":"+DS$
2180	RETURN
2200 '
2220 'CLOCK ROUTINES
2240 '
2260	PRINT:
	PRINT "The time now is (Hrs:Mins:Secs).... ";
2280	TF$="#"
2300	FOR I=1 TO 6
2320		PRINT USING TF$;H(I);
2340		IF I=2 THEN 
			PRINT ":";
2360		IF I=4 THEN 
			PRINT ":";
2380	NEXT I
2400	PRINT
2420 '  Now get hh/mm/ss stored by enterbbs
2440	HT(1)=PEEK(74):
	HT(2)=PEEK(75):
	HT(3)=PEEK(76)
2460	HT(4)=PEEK(77):
	HT(5)=PEEK(78):
	HT(6)=PEEK(79)
2480 '  And calculate the difference...
2500	IF H(1) < HT(1) THEN
		H(1) = H(1) + 2:
		H(2) = H(2) + 4
2520	IF H(6)<HT(6) THEN 
		H(6)=H(6)+10:
		H(5)=H(5)-1
2540	IF H(5)<HT(5) THEN 
		H(5)=H(5)+6:
		H(4)=H(4)-1
2560	IF H(4)<HT(4) THEN 
		H(4)=H(4)+10:
		H(3)=H(3)-1
2580	IF H(3)<HT(3) THEN 
		H(3)=H(3)+6:
		H(2)=H(2)-1
2600	IF H(2)<HT(2) THEN 
		H(2)=H(2)+10:
		H(1)=H(1)-1
2620	HD(6)=H(6)-HT(6):
	HD(5)=H(5)-HT(5):
	HD(4)=H(4)-HT(4)
2640	HD(3)=H(3)-HT(3):
	HD(2)=H(2)-HT(2):
	HD(1)=H(1)-HT(1)
2660	PRINT "You've been on the system for...... ";
2680	TF$="#"
2700	FOR I=1 TO 6
2720		PRINT USING TF$;HD(I);
2740		IF I=2 THEN 
			PRINT ":";
2760		IF I=4 THEN 
			PRINT ":";
2780	NEXT I
2800	PRINT:
	PRINT
2820	RETURN
2840 '
2860 '	Error handler for File Errors
2880 '
3000	IF ERL=380 THEN
		GOTO 460
3020	IF ERL=620 THEN
		GOTO 700
3040	ON ERROR GOTO 0
3060	END
