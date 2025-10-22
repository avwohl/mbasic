1	'**********************************************************************
2	'*								      *
3	'*	A POKER MACHINE SIMULATOR FOR INVETERATE GAMBLERS	      *
4	'*								      *
5	'*	WRITTEN BY:	Richard Berthet				      *
6	'*							              *
7	'*  	DATE:		11/09/82				      *
8	'*								      *
9	'*	PHONE:		H:(02)-88-1640	W:(02)-923-4801			      *
10	'*								      *
11	'**********************************************************************	
12	'
13	'	Note, it is written for a CRT terminal that will display
14	'	reverse video and supports the following escape sequences.
15	'	You will probably have to make suitable alterations.
16	'
17	'	There are a few small bugs in the presentation which shouldn't
18	'	be difficult to clean up.
19	'	
20	'	The original version came from a photocopy of a magazine
21	'	article, the source of which I could not identify. So I give
22	'	thanks to the original author whoever he/she is?  I have
23	'	given a fairly good work over to make it pretty.
24	'
25	'	Happy gambling, you will find it terribly generous. You may
26	'	like to put a "house loading" in it so that it will rip you 
27	'       off more !
46	'	
47	'
48	'	     ------ ADM-31 ASCII CONTROL CODES ------
49	'
50	'	***************************************************************
51	'	FUNCTION NAME		STRING NAME		ASCII CODE
52	'	***************************************************************
53	'
54	'	Bell
55					BEL$		=	CHR$(7)
56	'
57	'	Back Space
58					BS$		=	CHR$(8)
59	'
60	'	Horizontal Tab
61					HT$ 		=	CHR$(9)
62	'
63	'	Line Feed
64					LF$		=	CHR$(10)
65	'
66	'	Vertical Tab
67					VT$		=	CHR$(11)
68	'
69	'	Form Feed
70					FF$		=	CHR$(12)
71	'
72	'	Return
73					RET$		=	CHR$(13)
74	'
75	'	Escape
76					ESC$		=	CHR$(27)
77	'
78	'	Home
79					HOME$		=	CHR$(30)
80	'
81	'	New Line
82					NL$		=	CHR$(31)
83	'	Space
84					SP$		=	CHR$(32)
85	'
86	'
87	'	------ DYNAMIC VIDEO ATTRIBUTE CONTROL STRINGS ------
88	'	
89	'	***************************************************************
90	'    	FUNCTION NAME        STANDARD CHAR. GEN. 	ALT. CHAR. GEN.
91	'	***************************************************************
92	'	
93	'	Reset to Normal Video					      
94		STDVID$		=	ESC$+"G"+"0"                          
111	'
112	'	Reversing of Area
113		REVSTD$		=	ESC$+"G"+"4"
127	'
128	'	------ DYNAMIC EDITING CONTROL STRINGS ------
129	'
130	'	***************************************************************
131	'	OPERATION		HOW TO EXECUTE		DESCRIPTION
132	'	***************************************************************
133	'	
134	'	Clear Screen				     Clears to SPACES
135		CLRSCRN$	=	ESC$+"+"
136	'	
182	'
183	'**********************************************************************
184	'
185	'	------------- SCREEN ADDRESSES -------------
186	'
187	LHS%	=	1
188	RHS%	=	80
189	TOP%	=	1
190	BOTTOM%	=	24
191	'
192	'**********************************************************************
193	'
194	'	Definition of CURSOR LOAD Function. i.e. Pushing the Cursor
							 Around Onscreen.
195		DEF FNCSRLD$(ROW%,COLUMN%) = ESC$+"="+CHR$(ROW%+31)
					    +CHR$(COLUMN%+31)
196	'
200	'    		
201	'	------  FORMAT CONTROL OPERATION STRINGS ------
202	'
203	'	***************************************************************
204	'
205	'	***************************************************************
1000	DIM PRESREEL(3,3)	'Reels that are displayed(3 rows x 3 columns)
1050	DIM REEL(3,20)		'Holds combination of cards that each reel has
				  on it. As read from DATA at programme bottom.
1100	'
1150	'
1200	'*******	INITIALISE  DATA	********
1250	'
1300	STARTROW%	= TOP%+3
1350	NUMOFREELS%	= 3
1400	'
1450	PRINT CLRSCRN$
1500	PRINT "JACKPOT GAME":PRINT
1550	PRINT "DO YOU WANT A LIST OF PAYOFFS ? (Y=YES, <RET> = NO)";
1600	INPUT A$
1650	IF A$ = "Y"
		 THEN
			 1700
		 ELSE
			 2400
1700	PRINT CLRSCRN$
1750	PRINT "REEL 1"	,"REEL 2"	,"REEL 3"	,"PAYOFF $":PRINT
1800	'
1850	PRINT "NINE"	,"ANYTHING"	,"ANYTHING"	,"3"
1900	PRINT "NINE"	,"NINE"		,"ANYTHING"	,"5"
1950	PRINT "JACK"	,"JACK"		,"ACE"		,"6"
2000	PRINT "KING"	,"KING"		,"JACK"		,"8"
2050	PRINT "TEN"	,"TEN"		,"TEN"		,"10"
2100	PRINT "QUEEN"	,"QUEEN"	,"ANYTHING"	,"15"
2150	PRINT "JACK"	,"JACK"		,"JACK"		,"18"
2200	PRINT "QUEEN"	,"QUEEN"	,"QUEEN"	,"20"
2250	PRINT "KING"	,"KING"		,"KING"		,"30"
2300	PRINT "ACE"	,"ACE"		,"ACE"		,"200"
2350	'
2400	FOR POSITION% = 1 TO NUMOFREELS%
2450		COLOFFSET%(POSITION%) = LHS%+OFFSET%
2500		OFFSET% = OFFSET%+15
2550	NEXT POSITION%
2600	FOR DISPLAYREEL% = 1 TO 6
2650		FOR SEG% = 1 TO 5			
2700			READ REEL$(DISPLAYREEL%,SEG%)	
2750		NEXT SEG%
2800	NEXT DISPLAYREEL%				
2850	PRINT
2900	PRINT "INPUT YOUR LUCKY NUMBER (IN THE RANGE -32766 TO 32767) TO START...";
2950	INPUT A
3000	RANDOMIZE(A)
3050	FOR CARD% = 1 TO 20
3100		FOR COLUMN% = 1 TO 3
3150			READ REEL(COLUMN%,CARD%)
3200		NEXT COLUMN%
3250	NEXT CARD%
3300	YOURCASH = 15
3350	PRINT CLRSCRN$
3351	'
3400	'>>>>>>>	LOOP RE-ENTRY POINT
3401	'
3500	'
3510	PRINT FNCSRLD$(TOP%,60);LINERA$;
3520	PRINT USING "$$#####-";YOURCASH
3550	FOR COLUMN% = 1 TO 3
3600		RANDOMCARD% = INT(20*RND+1)
3650		' Check for boundary condition, CARD%=1
3700		IF RANDOMCARD% = 1
			THEN
				PRESREEL (1,COLUMN%) = REEL(COLUMN%,20):
				GOTO 3800
3750		PRESREEL (1,COLUMN%) = REEL(COLUMN%,RANDOMCARD%-1)
3800		PRESREEL(2,COLUMN%) = REEL(COLUMN%,RANDOMCARD%)
3850		' Check for boundary condition, CARD%=20
3900		IF RANDOMCARD% = 20
			THEN
				PRESREEL (3,COLUMN%) = REEL(COLUMN%,1):
				GOTO 4000
3950		PRESREEL (3,COLUMN%) = REEL(COLUMN%,RANDOMCARD%+1)
4000		GOSUB 5550
4050	NEXT COLUMN%
4100	WINNINGS = 0 : BELLON$ = ""
4110	'
4120	'The following IF THEN statements check for winning combinations
4130	'
4150	IF PRESREEL(2,1) <> 4
		THEN
			4300
		ELSE
			IF PRESREEL(2,2) <> 4
				THEN
					4900
4200	IF PRESREEL(2,3) = 4
		THEN
			4250
		ELSE
			IF PRESREEL(2,3) <> 2
				THEN
					4900
				ELSE
					WINNINGS = 8 	:
					BELLON$ = BEL$	:
					GOTO 4900
4250	WINNINGS = 30 	:
	BELLON$ = BEL$ 	:
	GOTO 4900
4300	IF PRESREEL(2,1) <> 5
		THEN
			4400
		ELSE
			IF PRESREEL(2,2) <> 5
				THEN
					4900
				ELSE
					IF PRESREEL(2,3) <> 5
						THEN
							4900
4350	WINNINGS = 10 	:
	BELLON$	= BEL$	:
	GOTO 4900
4400	IF PRESREEL(2,1) <> 3
		THEN
			4500
		ELSE
			IF PRESREEL(2,2) <> 3
				THEN
					4900
				ELSE
					IF PRESREEL(2,3) <> 3
						THEN
							4900
4450	WINNINGS = 200 	:
	BELLON$ = BEL$	:
	GOTO 4900
4500	IF PRESREEL(2,1) <> 1
		THEN
			4600
		ELSE
			IF PRESREEL(2,2) = 1
				THEN
					4550
				ELSE
					WINNINGS = 3 	:
					BELLON$ = BEL$	:
					GOTO 4900
4550	WINNINGS = 5 	:
	BELLON$ = BEL$	:
	GOTO 4900
4600	IF PRESREEL(2,1) <> 2
		THEN
			4750
		ELSE
			IF PRESREEL(2,2) <> 2
				THEN
					4900
				ELSE
					IF PRESREEL(2,3) = 3
						THEN
							4700
4650	IF PRESREEL(2,3) <> 2
		THEN
			4900
		ELSE
			WINNINGS = 18 	:
			BELLON$ = BEL$	:
			GOTO 4900
4700	WINNINGS = 6 	:
	BELLON$ = BEL$	:
	GOTO 4900
4750	IF PRESREEL(2,1) <> 6
		THEN
			4900
		ELSE
			IF PRESREEL(2,2) <> 6
				THEN
					4900
				ELSE
					IF PRESREEL(2,3) = 3
						THEN
							4850
4800	IF PRESREEL(2,3) <> 6
		THEN
			4900
		ELSE
			WINNINGS = 20 	:
			BELLON$ = BEL$	:
			GOTO 4900
4850	WINNINGS = 15	:
	BELLON$ = BEL$
4900	IF WINNINGS = 200
		THEN
			GOSUB 6050	:
			PRINT FNCSRLD$(T0P%,40);"***** JACKPOT *****"
4950	IF BELLON$ = BEL$
		THEN
			GOSUB 6050
5100	PRINT FNCSRLD$(TOP%,LHS%);
	"To 'PULL HANDLE' hit <RETURN>, else 'N' TO END";
5150	INPUT A$
5160	YOURCASH = YOURCASH-1
5200	IF A$ = "N"
		 THEN
			 5250
		 ELSE
			 3400	
5250	IF YOURCASH < 15
		THEN
			5350
		ELSE
			PRINT FNCSRLD$(TOP%,LHS%);
			LINERA$;
			"CONGRATULATIONS, YOU WON ";YOURCASH-15;" DOLLARS"
5300	GOTO 10250
5350	IF YOURCASH < 0
		THEN
			5400
		ELSE
			PRINT FNCSRLD$(TOP%,LHS%);
			CLRSCRN$;
			"TOO BAD, YOU LOST ";15-YOURCASH;" DOLLARS"
5400	PRINT  FNCSRLD$(TOP%+1,LHS%);
		"YOU HAVE TEN DAYS TO PAY ME THE ";15-YOURCASH;" AFTER THAT"
5450	PRINT FNCSRLD$(TOP%+2,LHS%);
		"IT IS OUT OF MY HANDS AS TO WHAT HAPPENS TO YOU!!!"
5500	GOTO 10250
5550	IF PRESREEL(2,COLUMN%) = 1 
		THEN
			GOSUB 6650 : RETURN
5600	IF PRESREEL(2,COLUMN%) = 2
		THEN
			GOSUB 6650 : RETURN
5650	IF PRESREEL(2,COLUMN%) = 3
		THEN
			GOSUB 6650 : RETURN
5700	IF PRESREEL(2,COLUMN%) = 4
		THEN
			GOSUB 6650 : RETURN
5750	IF PRESREEL(2,COLUMN%) = 5
		THEN
			GOSUB 6650 : RETURN
5800	PRESREEL(2,COLUMN%) = 6
5850	GOSUB 6650
5900	RETURN
5950	'
6000	'----------------------------------------------------------------------
6050	'	Subroutine [1]: DING BELL & INCREMENT EARNINGS 
6100	'
6150	FOR LOOP = 1 TO WINNINGS
6200		PRINT BEL$;
6210		YOURCASH = YOURCASH+1
6220		PRINT FNCSRLD$(TOP%,60);LINERA$;
6230		PRINT USING "$$#####-";YOURCASH
6400	NEXT LOOP
6450	RETURN
6500	'
6550	'----------------------------------------------------------------------
6600	'
6650	'	Subroutine [2]: PRINT REELS 
6700	'
6750	'
6800	PRINTROW% = STARTROW%
6850	FOR ROW% = 1 TO 3
6900		FOR SEG%	= 1 TO 5
6950				PRINT FNCSRLD$
				(PRINTROW%+SEG%,COLOFFSET%(COLUMN%)+15);
				REVSTD$;
				REEL$(PRESREEL(ROW%,COLUMN%),SEG%);
				STDVID$
7000		NEXT SEG%
7050		PRINTROW% = PRINTROW%+6
7100	NEXT ROW%
7150	PRINT HOME$
7200	RETURN
7250	'
7300	'~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
7350	'
7400	'	REEL DISPLAY DATA
7450	'
7500	DATA "999999999"
7550	DATA "9       9"
7600	DATA " N I N E "
7650	DATA "9       9"
7700	DATA "999999999"
7750	DATA "JJJJJJJJJ"
7800	DATA "J       J"
7850	DATA " J A C K "
7900	DATA "J       J"
7950	DATA "JJJJJJJJJ"
8000	DATA "    *    "
8050	DATA "   * *   "
8100	DATA " A  C  E "
8150	DATA " ******* "
8200	DATA "*       *"
8250	DATA "KKKKKKKKK"
8300	DATA "K\\\ ///K"
8350	DATA " K I N G "
8400	DATA "K/// \\\K"
8450	DATA "KKKKKKKKK"
8500	DATA "10     10"
8550	DATA "    T    "
8600	DATA " T  E  N "
8650	DATA "    N    "
8700	DATA "10     10"
8750	DATA "QQQQQQQQQ"
8800	DATA "Q-------Q"
8850	DATA "Q U E E N"
8900	DATA "Q-------Q"
8950	DATA "QQQQQQQQQ"
9000	'
9050	'	REEL COMBINATION DATA
9100	'
9110	' This data is sequence the cards appear on each reel these are NOT
9120	' the winning combinations, they are determined in the programme by
9130	' the IF THEN statements so marked.
9131	'
9150	'      REEL 1, REEL 2, REEL 3
9200	'	
9249	'	JACK	KING	JACK
9250	DATA	2,	4,	2
9251	'
9299	'	TEN	NINE	KING
9300	DATA	5,	1,	4
9301	'
9349	'	JACK	JACK	TEN
9350	DATA	2,	2,	5
9351	'
9399	'	QUEEN	KING	QUEEN
9400	DATA	6,	4,	6
9401	'
9449	'	NINE	NINE	JACK
9450	DATA	1,	1,	2
9451	'
9499	'	KING	JACK	QUEEN
9500	DATA	4,	2,	6
9501	'
9549	'	TEN	KING	TEN
9550	DATA	5,	4,	5
9551	'
9599	'	QUEEEN	NINE	KING
9600	DATA	6,	1,	4
9601	'
9649	'	KING	TEN ***ACE***
9650	DATA	4,	5,	3
9651	'
9699	'	TEN	TEN	TEN
9700	DATA	5,	5,	5
9701	'
9749	'	NINE	NINE	JACK
9750	DATA	1,	1,	2
9751	'
9799	'	JACK	JACK	KING
9800	DATA	2,	2,	4
9801	'
9849	'	KING	KING	QUEEN
9850	DATA	4,	4,	6
9851	'
9899	'	NINE ***ACE***	JACK
9900	DATA	1,	3,	2
9901	'
9949	'   ***ACE***	KING	JACK	
9950	DATA	3,	4,	2
9951	'
9999	'	JACK	NINE	KING
10000	DATA	2,	1,	4
10001	'
10049	'	QUEEN	JACK	TEN
10050	DATA	6,	2,	5
10051	'
10099	'	NINE	KING	JACK
10100	DATA	1,	4,	2
10101	'
10149	'	KING	QUEEN	KING
10150	DATA	4,	6,	4
10151	'
10199	'	JACK	NINE	JACK
10200	DATA	2,	1,	2
10201	'
10250	END
