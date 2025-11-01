1	'	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
2	'	ADM-31 ONSCREEN EDITING AND CURSOR CONTROL UTILITY PROGRAM.
3	'	
4	'	Version : 1.0
5	'	Composed: R. Berthet. C/O Channel 0/28 SYDNEY. Ph. 02-923-4801.
6	'	Date    : 14/03/82
7	'       Language: BASIC
8	'
9	'	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
10	'
11	'	This program is designed to be added to the top of a BASIC     
12	'	program. Its aim is to save the agony of writing tedious
13	'	ESCAPE sequences for the terminals video attributes.      
14	'
15	'	Following is a list of abbreviations of common words associated
16	'	with these attributes. The abbreviations are then used to form
17	'	STRING variable names for the ESCAPE sequences.               
18	'								      
19	'	It is advisable to read the appropriate section of the ADM   
20	'	Terminal Operators Manual to familiarise yourself with the 
21	'	operation of the video attributes.                            
22	'
23	'	ABBREVIATIONS
24	'
25	'	ALL	ALL                       LIN	LINE          
26	'	ALT	ALTERNATE                 LD	LOAD          
27	'	B	BOTTOM                    MOD	MODE          
28	'	BS	BACKSPACE                 NL	NEWLINE       
29	'	BEL	BELL                      NUL	NULL          
30	'	BLA	BLANK                     OFF	OFF	      
31	'	BLI	BLINK                     ON	ON	      
32	'	BOT	BOTTOM                    PGM	PROGRAM       
33	'	CHR	CHARACTER                 PRT	PROTECT(ED)   
34	'	CLR	CLEAR                     RD	READ          
35	'	CSR	CURSOR                    RES	RESET         
36	'	DEL	DELETE                    RET	RETURN        
37	'	ERA	ERASE                     REV	REVERSE	      
38	'	ESC	ESCAPE                    R	RIGHT         
39	'	FF	FORMFEED                  SCR	SCREEN        
40	'	GRF	GRAPH                     SPC	SPACE(S)      
41	'	HT	HORIZONTAL TAB            STD	STANDARD      
42	'	HOME	HOME                      TP	TOP	      
43	'	INS	INSERT                    VT	VERTICAL TAB  
44	'	L	LEFT                      VID	VIDEO         
45	'	LF	LINEFEED                  WRT	WRITE                  
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
94		RESSTDVID$	=	ESC$+"G"+"0"                          
95		RESALTVID$	=				ESC$+"G"+"0"
96	'								      
97	'	Limited Grahics Mode Enable				      
98		ALTGRF$		=				ESC$+"G"+"8"
99	'
100	'	Blanking or Underlining of Area             		      
101		BLASTD$		=	ESC$+"G"+"1"			      
102		BLAALT$		=				ESC$+"G"+"9"   
103	'								      
104	'	Blinking of Area					      
105		BLISTD$		=	ESC$+"G"+"2"
106		BLIALT$		=				ESC$+"G"+"A"
107	'
108	'	Blanking or Underlining and Blinking of Area
109		BLABISTD$	=	ESC$+"G"+"3"
110		BLABIALT$	=				ESC$+"G"+"B"
111	'
112	'	Reversing of Area
113		REVSTD$		=	ESC$+"G"+"4"
114		REVALT$		=				ESC$+"G"+"C"
115	'
116	'	Blanking or Underlining and Reversing of Area
117		BLAREVSTD$	=	ESC$+"G"+"5"
118		BLAREVALT$	=				ESC$+"G"+"D"
119	'
120	'	Blinking and Reversing of Area
121		BLIREVSTD$	=	ESC$+"G"+"6"
122		BLIREVALT$	=				ESC$+"G"+"E"
123	'
124	'	Blanking or Underlining and Reversing of Area
125		BLAREVSTD$	=	ESC$+"G"+"7"
126		BLAREVALT$	=				ESC$+"G"+"F"
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
137	'	Clear all to NULL
138		CLRNUL$		=	ESC$+"*"
139	'
140	'	Clear all to PROTECTED SPACES
141		CLRPRT$		=	ESC$+","
142	'
143	'	Set Insert Mode(ON/OFF)			     See page 4-18
144		INSMODON$	=	ESC$+"q"
145		INSMODOFF$	=	ESC$+"r"
146	'
147	'	Character Insert(SPACE)
148		CHRINS$		=	ESC$+"Q"
149	'
150	'	Character Delete
151		CHRDEL$		=	ESC$+"W"
152	'
153	'	Line Insert	
154		LININS$		=	ESC$+"E"
155	'
156	'	Line Delete
157		LINDEL$		= 	ESC$+"R"
158	'
159	'	Line Erase
160		LINERA$		=	ESC$+"T"
161	'
162	'	Line Erase to NULLS
163		LINERANUL$	=	ESC$+"t"
164	'
165	'	Page Erase
166		PAGERA$		=	ESC$+"Y"
167	'
168	'	Page Erase to NULLS
169		PAGERANUL$	=	ESC$+"y"
170	'
171	'	Set Auto Page
172		SETAUTPAG$	=	ESC$+"v"
173	'	
174	'	Clear Auto Page
175		CLRAUTPAG$	=	ESC$+"w"
176	'
177	'	Page Back
178		PAGBAK$		=	ESC$+"J"
179	'
180	'	Page Forward
181		PAGFOR$		=	ESC$+"K"
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
197	'	Definition of CURSOR READ Function. i.e. Finding Where the
		Cursor is On the Screen.
198		DEF FNCSRRD$(ROW%,COLUMN%) = ESC$+"?"+CHR$(ROW%+31)
				           +CHR$(COLUMN%+31)
199	'
200	'    		
201	'	------  FORMAT CONTROL OPERATION STRINGS ------
202	'
203	'	***************************************************************
204	'
205	'	***************************************************************
206	'
207	'	Program Mode On
208		PGMON$	=	ESC$+"U"
209	'
210	'	Program Mode Off
211		PGMOFF$	=	ESC$+"X"
212	'
213	'	Write Protect Mode On
214		WRTPRTON$	=	ESC$+")"
215	'
216	'	Write Protect Mode Off
217		WRTPRTOFF$	=	ESC$+"("
218	'
219	'	Protect Mode On
220		PRTON$	=	ESC$+"&"
221	'
222	'	Protect Mode Off
223		PRTOFF$	=	ESC$+"'"
224	'
225	'	Terminal Reset
226		TERMRESET$	=	ESC$+"o"+"!"
1000	'**********************************************************************
1001	'
1002	'			THE CLOCK PROGRAM
1003	'			-----------------
1004	'	BY: Richard Berthet
1005	' 	    15/5 Cottonwood Cr.
1006	'	    North Ryde. 2113.
1007	'	    W:(02)-923-4801	H:(02)-88-1640.
1008	'	Thanks to Bill Bolton for the SYSTEM SUPPORT 1 CLOCK ROUTINES.
1009	'
1010	DIM DIGIT$(10,6),TOD(5),DOY(5),LASTIME%(5),COLOFFSET%(6)
1020	'
1030	FOR DIGIT% = 0 TO 9
1040		FOR SEG% = 1 TO 6
1050			READ DIGIT$(DIGIT%,SEG%) 
1060		NEXT SEG%
1070	NEXT DIGIT%
1080	'
1090	'----------------------------------------------------------------------
1100	PRINT CLRSCRN$
1110	PRINTLINE$	= "------- THE CLOCK PROGRAM -------"
1120	GOSUB 2450	'[2] CENTRE LINE
1130	PRINT FNCSRLD$(TOP%,LINECOL%);
	PRINTLINE$
1150	PRINT FNCSRLD$(TOP%+9,LHS%);
1160	INPUT "Do you want the BELL on(Y/N)?. Just remember it'll probably drive you mad.";BEEP$
1170	'----------------------------------------------------------------------
1180	'
1190	'		Column Offsets for the Digits.
1200	'
1210	COLOFFSET%(0)	=	RHS%-21			'SECONDS UNITS
1220	COLOFFSET%(1)	=	COLOFFSET%(0)-7		'SECONDS TENS
1230	COLOFFSET%(2)	=	COLOFFSET%(0)-18	'MINUTES UNITS
1240	COLOFFSET%(3)	=	COLOFFSET%(0)-25	'MINUTES TENS
1250	COLOFFSET%(4)	=	COLOFFSET%(0)-36	'HOURS   UNITS
1260	COLOFFSET%(5)	=	COLOFFSET%(0)-43	'HOURS   TENS
1270	'
1280	STARTROW%	= TOP%+8			'1st  of DIGIT ROWS
1290	'
1300	'----------------------------------------------------------------------
1310	IF BEEP$ <> "Y" THEN BEL$ = CHR$(0)
1320	PRINT CLRSCRN$
1330	PRINT FNCSRLD$(TOP%,10);"THE 0/28 ENGINEERING TIME IS............."
1340	PRINTLINE$	= "CONTROL C to ESCAPE"
1350	GOSUB 2450	'[2] CENTRE LINE
1360	PRINT FNCSRLD$(BOTTOM%-1,LINECOL%)
	PRINTLINE$
1370	GOSUB 1890
1380	'----------------------------------------------------------------------
1390	'		DRAW THE SURROUND BOX
1400	PRINT WRTPRTON$;
1410	START%	= COLOFFSET%(5)-1
1420	FINISH%	= COLOFFSET%(0)+6
1430	FOR LOOP%	= START% TO FINISH%
1440		PRINT FNCSRLD$(STARTROW%-1,LOOP%);
		"-";
1450		PRINT FNCSRLD$(STARTROW%+8,LOOP%);
		"-";
1460	NEXT LOOP%
1470	FOR LOOP%	= (STARTROW%+1) TO (STARTROW%+6)
1480		COUNTER%	= COLOFFSET%(5)-3
1490		FOR LOOP2%	= 1 TO 4
1500			PRINT FNCSRLD$(LOOP%,COUNTER%);
			"|";
1510			COUNTER%	= COUNTER%+18
1520		NEXT LOOP2%
1530	NEXT LOOP%
1540	PRINT WRTPRTOFF$
1550	'----------------------------------------------------------------------
1560	CHANGE%	= 0
1570	FOR DISPLAY%	= 1 TO 6
1580		GOSUB 2530	'[3] PRINT DIGIT  
1590		CHANGE%	= CHANGE%+1
1600		'
1610	NEXT DISPLAY%
1620	FOREVER = 1
1630	WHILE FOREVER
1640		K$ = INKEY$
1650		IF K$ = CHR$(3)
			 THEN
				 FOREVER = 0
1660		GOSUB 1890
1670		'
1680		CHANGE%	= 0
1690		GOSUB 2530	'[3] PRINT DIGIT
1700		FOR LOOP%	= 1 TO 5
1710			'
1720			IF TOD(LOOP%)	= LASTIME%(LOOP%)
				THEN
					1750
1730			CHANGE%	= LOOP%
1740			GOSUB 2530	'[3] PRINT DIGIT
1750		NEXT LOOP%
1760		PRINT BEL$+HOME$
1770		OUT CMDPORT,(&H10)	'SET UP FOR CLOCK READ OF SECONDS
1780		WHILE TOD(0) = INP(DATAPORT)
1790		WEND			'LOOP UNTIL SECONDS CHANGE
1800		FOR LOOP%	= 1 TO 5
1810			LASTIME%(LOOP%)	= TOD(LOOP%)
1820		NEXT LOOP%
1830	WEND
1840	PRINTLINE$	= "Exiting to CP/M"
1850	GOSUB 2450	'[2] CENTRE LINE
1860	PRINT FNCSRLD$(BOTTOM%-1,LHS%);
	LINERA$
1870	PRINT FNCSRLD$(BOTTOM%-1,LINECOL%);
	PRINTLINE$
1880	END
1890 '******************************************************************
1900 '*								*
1910 '*	SYSTEM SUPPORT 1 BOARD CLOCK SUBROUTINES		*
1920 '*	BY BILL BOLTON						*
1930 '*	VERSION 1.0	JAN 17,1982	INITIAL RELEASE		*
1940 '*								*
1950 '*		VARIABLES USED IN THESE ROUTINES		*
1960 '*		IN APPROXIMATE ORDER OF APPEARANCE		*
1970 '*								*
1980 '*TOD		STORAGE ARRAY FOR TIME OF DAY (TOD) DIGITS	*
1990 '*DOY		STORAGE ARRAY FOR DAY OF YEAR (DOY) DIGITS	*
2000 '*BASEPORT	SYSTEM SUPPORT 1 BOARD BASE PORT ADDRESS	*
2010 '*CMDPORT		SS1 CLOCK COMMAND PORT ADDRESS			*
2020 '*DATAPORT	SS1 CLOCK DATA PORT ADDRESS			*
2030 '*HOURS10		TENS OF HOURS DIGIT				*
2040 '*HOURS1		UNIT HOURS DIGIT				*
2050 '*MINUTES10	TENS OF MINUTES DIGIT				*
2060 '*MINUTES1	UNIT MINUTES DIGIT				*
2070 '*SECONDS10	TENS OF SECONDS DIGIT				*
2080 '*SECONDS1	UNIT SECONDS DIGIT				*
2090 '*TIME$		TIME OF DAY STRING IN HH:MM:SS FORMAT		*
2100 '*WEEKDAY		DAY OF WEEK DIGIT				*
2110 '*WDAY$		DAY OF WEEK NAME STRING				*
2120 '*YEAR		YEAR INTEGER					*
2130 '*MONTH10		TENS OF MONTHS DIGIT				*
2140 '*MONTH1		UNIT MONTHS DIGIT				*
2150 '*DAY10		TENS OF DAYS DIGIT				*
2160 '*DAY1		UNIT DAYS DIGIT					*
2170 '*DATE1$		DATE STRING IN DD/MM/YY FORMAT			*
2180 '*MONTH		MONTH INTEGER					*
2190 '*DATE2$		DATE STRING IN MONTH DD,19YY FORMAT		*
2200 '*TDAY$		TEMPORARY DAY STRING				*
2210 '*								*
2220 '*		###### NOTE ######				*
2230 '*								*
2240 '* THE FOLLOWING ARRAYS MUST BE DIMENSIONED IN THE MAIN BODY	*
2250 '* THE PROGRAM CALLING THESE SUBROUTINES				*
2260 '*								*
2270 '* DIM TOD(5)							*
2280 '* DIM DOY(5)							*
2290 '*								*
2300 '******************************************************************
2310 BASEPORT = &H50
2320 CMDPORT = BASEPORT + 10
2330 DATAPORT = CMDPORT + 1
2340 '**********************************************************
2350 '*		READ THE TIME DIGITS			*
2360 '**********************************************************
2370 FOR DIGIT = 5 TO 0 STEP -1
2380	OUT CMDPORT,(&H10 + DIGIT)
2390	TOD(DIGIT) = INP(DATAPORT)
2400	IF DIGIT = 5 THEN TOD(DIGIT) = TOD(DIGIT) AND 3
2410 NEXT DIGIT
2420 RETURN
2430	'~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
2440	'
2450	'	Subroutine [2]: LINE CENTERING
2460	'
2470	NUMOFCHAR%	= LEN(PRINTLINE$)
2480	LINECOL%	= (RHS%-NUMOFCHAR%)/2
2490	RETURN
2500	'
2510	'~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
2520	'
2530	'	Subroutine [3]: PRINT DIGIT
2540	'
2550	'
2560	FOR SEG%	= 1 TO 6
2570		PRINT FNCSRLD$(STARTROW%+SEG%,COLOFFSET%(CHANGE%));
			DIGIT$(TOD(CHANGE%),SEG%);
2580	NEXT SEG%
2590	PRINT HOME$
2600	RETURN
2610	'
2620	'~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
2630	DATA " ***  "
2640	DATA "*   * "
2650	DATA "*   * "
2660	DATA "*   * "
2670	DATA "*   * "
2680	DATA " ***  "
2690	'
2700	DATA "   *  "
2710	DATA "  **  "
2720	DATA "   *  "
2730	DATA "   *  "
2740	DATA "   *  "
2750	DATA "  *** "
2760	'
2770	DATA " ***  "
2780	DATA "*   * "
2790	DATA "   *  "
2800	DATA "  *   "
2810	DATA " *    "
2820	DATA "***** "
2830	'
2840	DATA "****  "
2850	DATA "    * "
2860	DATA "  **  "
2870	DATA "    * "
2880	DATA "*   * "
2890	DATA " ***  "
2900	'
2910	DATA "   *  "
2920	DATA "  **  "
2930	DATA " * *  "
2940	DATA "*  *  "
2950	DATA "***** "
2960	DATA "   *  "
2970	'
2980	DATA "***** "
2990	DATA "*     "
3000	DATA "****  "
3010	DATA "    * "
3020	DATA "    * "
3030	DATA "****  "
3040	'            
3050	DATA " ***  "
3060	DATA "*     "
3070	DATA "****  "
3080	DATA "*   * "
3090	DATA "*   * "
3100	DATA " ***  "
3110	'
3120	DATA "***** "
3130	DATA "    * "
3140	DATA "   *  "
3150   DATA "  *   "
3160   DATA " *    "
3170   DATA " *    "
3180	'
3190   DATA " ***  "             
3200   DATA "*   * "             
3210   DATA " ***  "             
3220	DATA "*   * "             
3230   DATA "*   * "             
3240   DATA " ***  "
3250	'             
3260   DATA " ***  "             
3270   DATA "*   * "             
3280   DATA " **** "             
3290   DATA "    * "             
3300   DATA "*   * "             
3310   DATA " ***  "
3320	'
3330	'**********************************************************************
3340	END
