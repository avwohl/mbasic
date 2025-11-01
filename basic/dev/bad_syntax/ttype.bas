1	'**********************************************************************
2	'* PROGRAM FUNCTION: Touch Typing Tutor.			      *
3	'* VERSION	   : 2.0  (Direct Cursor Addressing & Help.)          *
4	'* DATE WRITTEN    : 16th April 1982.                                 *
5	'*	BY	   : Tim Pearce & Richard Berthet.		      *
6	'*								      *
7	'* ADDRESS	   : 15/5 Cottonwood Cr., North Ryde 2113.	      *
8	'* PHONE           : (61-2)-88-1640.				      *
12	'*								      *
13	'*		Please leave this notice on the programme.	      *	
14	'**********************************************************************
15	'
20	'			######################## 
21	'			###### SECTION 1  ######
22	'			######################## 
23	'
48	'>>>>>>>>>>>>>>>>>>>>> ADM-31 ASCII CONTROL CODES <<<<<<<<<<<<<<<<<<<<<
49	'
50	'	***************************************************************
51	'	FUNCTION NAME		STRING NAME		ASCII CODE
52	'	***************************************************************
53	'
72	'	Return
73					RET$		=	CHR$ (13)
74	'
75	'	Escape
76					ESC$		=	CHR$ (27)
77	'
85	'	------ DYNAMIC VIDEO ATTRIBUTE CONTROL STRINGS ------
86	'	
87	'	***************************************************************
88	'    	FUNCTION NAME        STANDARD CHAR. GEN. 	ALT. CHAR. GEN.
89	'	***************************************************************
90	'	
91	'	Reset to Normal Video					      
92		STDVID$		=	ESC$+"G"+"0"                          
94	'
110	'	Reversing of Area
111		REVSTD$		=	ESC$+"G"+"4"
113	'
126	'	------ DYNAMIC EDITING CONTROL STRINGS ------
127	'
128	'	***************************************************************
129	'	OPERATION		HOW TO EXECUTE		DESCRIPTION
130	'	***************************************************************
131	'	
132	'	Clear Screen				     Clears to SPACES
133		CLRSCR$		=	ESC$+"+"
134	'
157	'	Line Erase
158		LINERA$		=	ESC$+"T"
159	'
160	'	Character Delete
170		CHRDEL$		=	ESC$+"W"
180	'
181	'	Definition of CURSOR LOAD Function.
			 i.e. Pushing the Cursor Around Onscreen.
182		DEF FNCSRLD$ (ROW%,COLUMN%) =
		 		ESC$+"="+CHR$ (ROW%+31)+CHR$ (COLUMN%+31)
183	'
200	'	Write Protect Mode On
201		WRTPRTON$	=	ESC$+")"
203	'	Write Protect Mode Off
204		WRTPRTOFF$	=	ESC$+"("
205	'
900	'**********************************************************************
910	'
915	'			########################
920	'			###### SECTION 2  ######
925	'			########################
930	'
1000    '>>>>>>>>>>>>>>>>>>>>>>>>>> ALTERATIONS <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
1010    '
1020    '	Date.			Description.  
1030	'
1040	'     28/06/82		Reformat HELP presentation. 		     RB
3950	'     29/06/82		Added SECTION headings.			     RB
3951	'     03/07/82		Added [%] to PARAGRAPH variable in Paragraph
3952	'			read portion of Section 5.		     
3953	'     			Subroutine [9]: Added missing <"> on string. 
3954	'     			Erase line before End of Exercise printed.   
3955	'     			Replace NEWLINE% variable in PARAGRAPH check,
3956	'			with LINESINPARA%			     RB
3957	'     04/07/82		Moved "End of Exercise" message to Exercise
3958	'			Row.					     
3959	'			Renovated Subroutine [7] to print 5 COMMENT
3960	'			lines each call, I found the scrolling NG.   RB
4000	'**********************************************************************
4010	'
4012	'			########################
4015	'			###### SECTION 3  ######
4017	'			########################
4020	'
4050	'>>>>>>>>>>>>>>>>>>>>>>> INITIALISING BLOCK <<<<<<<<<<<<<<<<<<<<<<<<<<<
4100	'
4150	'
4160	DIM		   PARAGRAPHIN$ (20),ADDRESS% (140,2)
4170	DIM		   DISPLAYCHAR% (127),COMMENT$(5)
4180	'
4200	'The following addresses and values are system dependant.
4250	'
4300	DATAPORT%  	=  0			'Decimal address of system
						  dataport.
4350	STATUSPORT%  	=  DATAPORT%+1		'Decimal address of system
						  statusport.
4400	'
4450	ESCTYPE%  	=  127			'ASCII escape character from
						 typing exercise mode.
4500	ESCCHR$  	=  "RUB"		'String to print name of above
						 character.
4660	FILENUM1%  	=  1			'Filenumber for exercise files.
4670	FILENUM2%	=  2			'Filenumber for help files.
4680	FILENUM3%	=  3			'Filenumber for keyboard data.
4700	EXLINELENGTH% 	=  80 	
4750    COMMENTSTACK% 	=  0 	
4800    NUMOFREPEATS%	=  0 	
4850    PARAGRAPH% 	=  0 	
4900	ARRAYROWS% 	=  1 	
4950	ARRAYCOLUMNS%	=  2
5100	'
5150	WIDTH 255				'Remove  <CR>'s from long lines
5160	ON ERROR GOTO 40000			'Error handling department.
5170	DELAY%		=  500			'Time delay factor (See 34100)
5200	'                SCREEN ADDRESSES
5250	'
5300	LHS%  		=  1			'Set the left hand side of the
						  screen
5310	RHS%		=  80
5350	TOP%  		=  1			'Set the top of the screen
5400	ROWOFFSET% 	=  TOP%+15 		'Keyboard display
5450	COLUMNOFFSET% 	=  LHS%+10    		'Keyboard display
5500	EXERCISEROW% 	=  ROWOFFSET%+5		'Exercise line 	
5550	EXERCISECOLUMN% =  LHS%        		'Exercise line
5600	ECHOROW% 	=  EXERCISEROW%+1 	'Typing Echo
5650	ECHOCOLUMN% 	=  EXERCISECOLUMN% 	'Typing Echo
5700	COMMENTROW% 	=  ROWOFFSET%-7         'Comment area
5710	COMMENTCOLUMN%	=  EXERCISECOLUMN%	'Comment area
5850	'
5900	'**********************************************************************
5950	'
5951	'			########################
5952	'			###### SECTION 4  ######
5953	'			########################
5954	'
5955	'>>>>>>>>>>>>>>>>>>>> START OF ACTIVE PROGRAM CODE <<<<<<<<<<<<<<<<<<<<
6050	'###### 4a ###### 
6100	'
6150	'	First Screenful of instructions
6200	'
6250	PRINT	CLRSCR$
6260	IF CHARACTER$ = "N"
		 THEN
			6760
6300	HELPNUM$	= "0":
	 GOSUB 23300
6550	GOSUB 21400		'[1]:CAPITAL LETTER
6600	IF CHARACTER$	= "N"
		 THEN
			65529
		 ELSE
			 IF CHARACTER$ 	= "?"
				 THEN
					 HELPNUM$ = "1":
					 GOSUB 23300: 
					 GOTO 6550		
6650	'
6700	'----------------------------------------------------------------------
6750	'###### 4b ######
6752	'
6760	GOSUB	39500		'[9]:PRINT HELP MENU
6800	PRINT	FNCSRLD$ (ROWOFFSET%,10);
		 LINERA$;
		 "Error break ?";
6810	WAIT STATUSPORT%,2:
	CHARACTER$ = CHR$(INP(DATAPORT%))
6900	GOSUB 21400		'[1]:CAPITAL LETTER
6950	IF CHARACTER$	= "Y"
		 THEN
			 ERRORFLAG% = 1
		 ELSE
			 IF CHARACTER$ 	= "?"
				 THEN
					 HELPNUM$ = "2":
					 GOSUB 23300:
					 GOTO 6900
		  ELSE
			 ERRORFLAG% = 0	
7000	'
7050	'----------------------------------------------------------------------
7100	'###### 4c ######
7105	'
7110	GOSUB	39500		'[9]:PRINT HELP MENU
7115	PRINT	FNCSRLD$ (COMMENTROW%,COMMENTCOLUMN%);
		 LINERA$;
"Any LETTER is a valid exercise but presently (28/06/82) only A-J exist."
7150	PRINT	FNCSRLD$ (ROWOFFSET%,10);
		 LINERA$;
		 "Which Exercise ?";
7200	WAIT STATUSPORT%,2:
	CHARACTER$ = CHR$(INP(DATAPORT%))
7250	GOSUB 21400		'[1]:CAPITAL LETTER
7300    IF CHARACTER$ < "A" OR CHARACTER$ > "J"
		 THEN
			 7150
7400	PRINT	FNCSRLD$ (COMMENTROW%,COMMENTCOLUMN%);
		 LINERA$;
8050	FILE$ 		=  "TTYPEX"+CHARACTER$+".DAT"  
8051	'
8052	'----------------------------------------------------------------------
8053	'###### 4d ######
8054	'
8060	GOSUB	39500		'[9]:PRINT HELP MENU
8100	PRINT	FNCSRLD$ (13,1);
		 LINERA$;
		 FNCSRLD$ (ROWOFFSET%,10);
		 LINERA$;
		 "Echo ?";
8110	WAIT STATUSPORT%,2:
	CHARACTER$ = CHR$(INP(DATAPORT%))
8200	GOSUB 21400		'[1]:CAPITAL LETTER
8250	ECHOFLAG% 	= 0	
8300	IF CHARACTER$	= "N"
		 THEN
			 ECHOFLAG% = 1
		 ELSE
			 IF CHARACTER$ 	= "?"
				 THEN
					 HELPNUM$ = "3":
					 GOSUB 23300:
					 GOTO 8200		
8350	'
8400	'**********************************************************************
8450	'
8451	'			########################
8452	'                       ###### SECTION 5  ######
8453	'			########################
8454	'
8460	'>>>>>>>>>>>>>>>>>>>  SET UP & CHECK EXERCISE FILE <<<<<<<<<<<<<<<<<<<<
8465	'
8500	PRINT	CLRSCR$         
8550	'                       
8600	GOSUB 29500		'[5]:PRINT KEYBOARD
10950	'
11300	'	set up input file.
11400	OPEN "I",#FILENUM1%,FILE$
11500	'
11550	'	Remove old line
11600	ECHOCOLUMN% 	= LHS% 	
11650	LINEFLAG% 	= 0
11700	PRINT	FNCSRLD$ (EXERCISEROW%,EXERCISECOLUMN%);
		 LINERA$;
		 FNCSRLD$ (ECHOROW%,ECHOCOLUMN%);
		 LINERA$; 
11750	TYPEDIN$	= ""
11800	'	Check that it is not a paragraph
11850	IF PARAGRAPH%	= 0
		 THEN
			 12300
11900	ALINE$ 		= PARAGRAPHIN$ (NUMOFTEXTLINES%):
	NUMOFTEXTLINES% 	= NUMOFTEXTLINES% +1:
	IF NUMOFTEXTLINES% = LINESINPARA%+1
		 THEN
			 NUMOFREPEATS% = NUMOFREPEATS%-1:
			 NUMOFTEXTLINES% 	= 1:
			 IF NUMOFREPEATS%	= 0
				 THEN
					 PARAGRAPH% = 0
12150	'
12200	GOTO 12700	
12250	'
12300	IF NUMOFREPEATS%	= 0
		 THEN
			 12550
12350	NUMOFREPEATS%		= NUMOFREPEATS% -1:
	 GOTO 14050
12500	'
12550	IF EOF (FILENUM1%)
		 THEN
			 PRINT	 FNCSRLD$(EXERCISEROW%,EXERCISECOLUMN%+15);
				 LINERA$;
				 "END of EXERCISE, Please WAIT for MENU.";:
			 GOSUB 34100:
		 	 GOTO 17200
12600	'
12650	LINE INPUT# FILENUM1%,ALINE$
12700	ALINE$  	= ALINE$+CHR$ (13)
12750	IF PARAGRAPH% 	= 0
		 THEN
			 NEWLINE% = NEWLINE%+1
12800	EXLINELENGTH% 	= LEN (ALINE$)
12850	'	CHECK for repeated line.
12900	IF LEFT$ (ALINE$,1) <> "|"
		 THEN
			 13950
12950	CHARACTER$ 	= MID$ (ALINE$,2,1) 	
13000	GOSUB 21400		'[1]:CAPITAL LETTER
13050	IF CHARACTER$ 	= "P"
		 THEN
			 13400
13100	NUMOFREPEATS%	= VAL (CHARACTER$)-1
13150	EXLINELENGTH% 	= EXLINELENGTH%-2 	
13200	ALINE$ 		= RIGHT$ (ALINE$,EXLINELENGTH%)
13250	'
13300	GOTO 13950
13350	'
13400	'	Paragraph Read In. 
13450	NUMOFREPEATS%	= VAL (MID$ (ALINE$,3,1)) 	
13500	LINESINPARA%  	= VAL (MID$ (ALINE$,5,2)) 	
13550	PARAGRAPH% 	= 1	
13600	NUMOFTEXTLINES%	= 1
13650	FOR ILOOP% = 1 TO  LINESINPARA% 
13660		'PARAGRAPHIN$ contains up to 20 lines of input for repeating
		 whole paragraphs.
13700		LINE INPUT# FILENUM1%,PARAGRAPHIN$ (ILOOP%) 	
13750	NEXT ILOOP%
13800	'
13850	GOTO 11550
13900	'
13950	'	CHECK FOR COMMENT
14000	IF LEFT$ (ALINE$,2) = "!#"
		THEN
			 GOSUB 33020:
			 GOTO 11550
14050	CHARCOUNT% 	= EXLINELENGTH%
14100	PRINT	 FNCSRLD$ (EXERCISEROW%,EXERCISECOLUMN%)
14150	PRINT	 FNCSRLD$ (EXERCISEROW%,EXERCISECOLUMN%);
		  LEFT$ (ALINE$,EXLINELENGTH%-1)
14200	'
14201	'**********************************************************************
14202	'
14203	'			########################
14204	'                       ###### SECTION 6  ######
14205	'                       ########################
14206	'
14250	'>>>>>>>>>>>>>>>>>>>>>>>> KEYBOARD SCAN SECTION <<<<<<<<<<<<<<<<<<<<<<<
14300	'	         I.E. The actual exercise begins here
14350	'
14400	FOR ILOOP% = 1 TO EXLINELENGTH%
14450		IF ILOOP% 	=  EXLINELENGTH%
			 THEN
				 LINEFLAG% = 1
14500		CHARACTER$ 	=  MID$ (ALINE$,ILOOP%,1)
14550		ASCIINUMBER% 	=  ASC (CHARACTER$)
14600		'	Change ROW% and COLUMN% for different 
			 Direct Cursor Addressing.
14650		ROW% 		=  ADDRESS% (ASCIINUMBER%,ARRAYROWS%) 	
14700	 	COLUMN% 	=  ADDRESS% (ASCIINUMBER%,ARRAYCOLUMNS%) 
14750		PRINT	FNCSRLD$ (ROW%,COLUMN%-1);
			 REVSTD$;
			 CHARACTER$;
			 STDVID$;
14760		PRINT 	FNCSRLD$ (ECHOROW%,ECHOCOLUMN%); 
14800		'	Program waits for change of input status.
14850		WAIT STATUSPORT%,2 
14900		NUMOFWORDS 	=  NUMOFWORDS+.2
14950		'	Program reads data from dataport.
15000		KEYBDCHAR%	=  INP (DATAPORT%)
15050		PRINT 	FNCSRLD$ (ROW%,COLUMN%-1);
			 WRTPRTON$;
			 STDVID$;
			 CHR$ (DISPLAYCHAR% (ASCIINUMBER%));
			 WRTPRTOFF$
15100		IF KEYBDCHAR%	=  ESCTYPE%
			 THEN
				 17200
15150		IF KEYBDCHAR%	=  13
			 THEN
				 LINEFLAG% = 1:
				 GOTO 16250
15200		'
15300		'
15350		IF ECHOFLAG% 	=  1
			 THEN
				 TYPEDIN$ = TYPEDIN$+CHR$ (KEYBDCHAR%):
			 IF KEYBDCHAR%	=  ASCIINUMBER%
				 THEN
					 16250
				 ELSE
					 15700
15450		'	Change the typing Echo definition in the next line for
			 different Dir Cus Adr.
15550	 	PRINT	 FNCSRLD$ (ECHOROW%,ECHOCOLUMN%);
			 CHR$ (KEYBDCHAR%);
15600		ECHOCOLUMN% 	=  ECHOCOLUMN%+1 
15650		IF KEYBDCHAR%	=  ASCIINUMBER%
			 THEN
				 16250
15700		'	Error
15750		ERRORCOUNT% 	=  ERRORCOUNT%+1
15800	 	CHARCOUNT% 	=  CHARCOUNT%+1
15850		IF ERRORFLAG% 	=  0
			 THEN
				 16250
15900		ECHOCOLUMN% 	=  ECHOCOLUMN%-1
15950		PRINT	 	CHR$ (7)
16100		IF ECHOCOLUMN% 	<  0
			 THEN
				 ECHOCOLUMN% = 0
16150		'
16200		GOTO 14750
16250		'
16300		IF LINEFLAG% 	=  0
			 THEN
				 16950
16350		IF ECHOFLAG% 	=  0
			 THEN
				 11550
16400		'	Display line that was typed in but not echoed
			 previously
16450		PRINT	 FNCSRLD$ (ECHOROW%,ECHOCOLUMN%);
			  TYPEDIN$ 
16500		'	Program waits for change of input status.
16550		WAIT STATUSPORT%,2
16600		'	Program reads data from dataport.
16650		KEYBDCHAR%	=  INP (DATAPORT%)
16700		IF KEYBDCHAR%	=  13
			 THEN
				 11550
16750		IF KEYBDCHAR%	=  ESCTYPE%
			 THEN
				 17200
16800		'
16850		GOTO 16550
16900		'
16950	NEXT ILOOP%
17000	'
17050	'	End of keyboard scan 
17100	'
17150	GOTO 11550
17151	'
17160	'**********************************************************************
17200	'	
17201	'			########################
17202	'                       ###### SECTION 7  ######
17203	'                       ########################
17204	'
17210	'>>>>>>>>>>>>>>>>>>> SECTION PROVIDES POSSIBILITIES <<<<<<<<<<<<<<<<<<<
17220	'	             TO ESCAPE OR ALTER PROGRAM FLOW. 
17230	'
17250	HELPNUM$ = "4":
			 GOSUB 23300:
			 GOTO 17450
17450	CHARACTER$ 	= CHARACTER$+"e"
17500   GOSUB 21400		'[1]:CAPITAL LETTER
17510	'
17550	IF CHARACTER$ 	= "N"
		 THEN
			 CLOSE  FILENUM1%:
			 GOTO 4300
17560	'
17760	'
17800	IF CHARACTER$ 	= "R"
		 THEN
			 NUMOFREPEATS% = NUMOFREPEATS% +1:
			 GOSUB 29500:
			 GOTO 11550
17850	'
17900	IF CHARACTER$ 	= CHR$(13)
		 THEN
			 GOSUB 29500:
			 GOTO  11550
17930	'
17990	'
18000	IF CHARACTER$ 	= "M"
		 THEN
			 HELPNUM$ = "5":
			 GOSUB 23300:
			 GOTO 17450
18040	'
18050	IF CHARACTER$ 	= "S"
		 THEN
			 GOSUB 32110:
			 GOSUB 29500:
			 GOTO 11550
18090	'	
18100	IF CHARACTER$ 	= "L"
		 THEN
			 PRINT	 FNCSRLD$(COMMENTROW%,COMMENTCOLUMN%+10);
			 " Exercise line Number is;  "; NEWLINE%;:
			 GOSUB 34100:
			 GOTO 17250
18145	'
18150	IF CHARACTER$ 	= "W"
		 THEN
			 18160
		 ELSE
			 18250
18160			GOSUB 21900	'[2]:ERROR COUNT
18165			PRINT FNCSRLD$(COMMENTROW%,COMMENTCOLUMN%+10);
			        LINERA$;
				"Reset ERROR count (Y/N) ?";
18166			WAIT STATUSPORT%,2:
			CHARACTER$ = CHR$(INP(DATAPORT%)) 
18170			GOSUB 21400	'[1]:CAPITAL LETTER
18190			IF CHARACTER$ 	= "Y"
				 THEN
					 NUMOFWORDS = 0:
					 ERRORCOUNT% = 0:
					 GOTO 17250
18196	'
18197	'
18198	'
18250	IF CHARACTER$ 	= "Q"
		 THEN
			 SYSTEM
18300	'
18320	IF CHARACTER$	= "E"
		THEN
			 GOTO 65529
18350	GOTO 17250	'IF NOT MATCHED, RETURN TO MENU
20800	'
21150	'
21200	'**********************************************************************
21250	'
21251	'			########################
21252	'                       ###### SECTION 8  ######
21253	'                       ########################
21254	'
21255	'>>>>>>>>>>>>>>>>>>>>>>>>>>>> SUBROUTINES <<<<<<<<<<<<<<<<<<<<<<<<<<<<<
21300	'
21350	'
21400	'	Subroutine [1]: Returns  first letter of a string as a CAPITAL.
21450	'
21500	CHARACTER$ 	= LEFT$ (CHARACTER$,1)
21550	IF CHARACTER$ 	> "`"
		 THEN
			 IF CHARACTER$ < "{"
				 THEN
					 21650
21600	RETURN
21650	CHARACTER$ 	= CHR$ (ASC (CHARACTER$)-32)
21700	RETURN
21750	'
21800	'~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
21850	'
21900	'	Subroutine [2]: Prints ERROR COUNT message and total.
21950	'
22000	PRINT	 CLRSCR$	
22050	PRINT	 FNCSRLD$(COMMENTROW%,COMMENTCOLUMN%+10);
		 ERRORCOUNT%;
		 " ERRORS in";
		 NUMOFWORDS;
		 " Words ";:
		 GOSUB 34100 
22100	IF ERRORCOUNT% 	= 0
		 THEN
			 RETURN
22150	PRINT	 " I.E.";
		 NUMOFWORDS/ERRORCOUNT%;
		 " Words per error":
		 GOSUB 34100	
22200	RETURN
22250	'
22300	'~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
22350	'
22400	'	Subroutine [3]: Changes the INSTRUCTION line ADDRESS.
22450	'
22460	'	+++++ THIS SUBROUTINE NOT USED IN THIS VERSION +++++		
22470	'
22500	'IF INSTCOLUMN% 	< 70
		 THEN
			 RETURN
22550	'INSTCOLUMN% 	= LHS%
22600	'INSTROW% 	= INSTROW%+1
22650	'PRINT 
22700	'IF INSTROW%   	>=   TOP%+6
		 THEN
			 INSTROW% = TOP%
22750	'RETURN
22800	'
22850	'~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
23270	'
23300	'	Subroutine [4]: Access and PRINT HELP Files.
23310	'
23320	PRINT	 CLRSCR$
23330	OPEN "I", # FILENUM2%, "TTHELP"+HELPNUM$+".DAT"
23340	IF EOF (FILENUM2%)
		 THEN
			 WAIT STATUSPORT%, 2:
			 CHARACTER$ = CHR$ (INP (DATAPORT%)):
			 CLOSE # FILENUM2%:
			 PRINT	 CLRSCR$:
			 RETURN
23350	LINE INPUT # FILENUM2%, LINES$
23360	IF LEFT$ (LINES$,1) = "#"
		 THEN
			 WHILE INKEY$ <> RET$:
			 WEND:
			 PRINT	 CLRSCR$:
			 GOTO  23340
23370	PRINT	 LINES$
23380	GOTO 23340
23400	'
29450	'~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
29460	'
29500	'	Subroutine [5]: Set up Addresses & Keyboard locations          
29550	'               and PRINT KEYBOARD.
29600	'
29605	PRINT	FNCSRLD$ (1,25);
		 LINERA$;
		 WRTPRTON$;
		 "Hit "+ESCCHR$+" key for MENU";
29606	'
29610	OPEN "I",# FILENUM3%,"TTKEYBD.DAT"
29620	'
29650	ROW% 	= ROWOFFSET%
29700	COLUMN% = COLUMNOFFSET%
29750	FOR ILOOP%= 1 TO 140
29800		ADDRESS% (ILOOP%, 1) = 1
29850		ADDRESS% (ILOOP%, 2) = 1
29900	NEXT ILOOP%
29950  	'	ADDRESS% contains the character addresses. DISPLAYCHAR%
30000	' 	contains the displayed character corresponding to that address.
30050	'
30100	FOR JLOOP% = 1 TO 5
30150		INPUT # FILENUM3%, NUMOFKEYS%
30250		ADDCHAR$ = ""
30300		FOR ILOOP% = 1 TO NUMOFKEYS%
30350			INPUT # FILENUM3%, CHARACTER$
30400			ASCIINUMBER% = ASC (CHARACTER$)
30450			'	Save character address
30500			ADDRESS% (ASCIINUMBER%,ARRAYROWS%) = ROW% 	
30550			ADDRESS% (ASCIINUMBER%,ARRAYCOLUMNS%) = COLUMN%
30600			PRINT	 FNCSRLD$ (ROW%,COLUMN%);
				  CHARACTER$; 
30650			'	Keep record of character corresponding to this
				 address
30700			ADDCHAR$ 	= ADDCHAR$+CHARACTER$ 	
30750			DISPLAYCHAR% (ASCIINUMBER%) 	= ASCIINUMBER%
30800  			COLUMN% 	= COLUMN%+4 
30850		NEXT ILOOP%
30900		COLUMN% = COLUMN%-4*NUMOFKEYS% 
30950		FOR ILOOP% = 1 TO NUMOFKEYS% 	
31000			INPUT # FILENUM3%, CHARACTER$
31050			'	SAVE shift character address (BASIC can't get
				 a " from data)
31100			IF ILOOP% = 2
				 THEN
					 IF JLOOP% = 1
						 THEN
							 CHARACTER$ = CHR$ (34)
31150			ASCIINUMBER% = ASC (CHARACTER$)	
31200			ADDRESS% (ASCIINUMBER%,ARRAYROWS%) = ROW%	
31250			ADDRESS% (ASCIINUMBER%,ARRAYCOLUMNS%) = COLUMN%
31300			DISPLAYCHAR% (ASCIINUMBER%) =
					 ASC (MID$ (ADDCHAR$,ILOOP%,1))
31350			'	DISPLAYCHAR% (ASCIINUMBER%) now contains the
				 normally displayed char. at the pos'n of l$
31400			COLUMN% = COLUMN%+4 
31450		NEXT ILOOP%
31500		COLUMN% = COLUMN%-4*NUMOFKEYS%+2 	
31550		ROW% 	= ROW%+1 
31600	NEXT JLOOP%
31610	PRINT	 WRTPRTOFF$
31620	CLOSE FILENUM3%
31650	'	End of keyboard setup
31700	'
31750	RETURN
31760	'
32000	'~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
32100	'
32110	'	Subroutine [6]: SKIP Exercise LINES.
32120	'
32130	PRINT FNCSRLD$(COMMENTROW%,COMMENTCOLUMN%+10);
		"Number of lines to SKIP ?";
32135	WAIT STATUSPORT%,2:
	NUMOFLINES% = VAL(CHR$(INP(DATAPORT%))) 
32140	FOR ILOOP% = 1 TO  NUMOFLINES% 
32150		IF EOF (FILENUM1%)
			 THEN
				 12550
32160		LINE INPUT# FILENUM1%,INPCHAR$
32170	NEXT ILOOP%
32180	NUMOFREPEATS%	= 0
32190	NEWLINE% 	= NEWLINE%+NUMOFLINES% 
32200	'
32210	PRINT	FNCSRLD$ (COMMENTROW%,COMMENTCOLUMN%+10);
		LINERA$;
32220	RETURN
32230	'
33000	'~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
33002	'
33020	'	Subroutine [7]: COMMENT PRINT
33025	'
33070	IF EOF(FILENUM1%)
		THEN
			RETURN
33080	'
33082	COMMENT$(0)	= MID$(ALINE$,3)
33084	FOR ILOOP%	= 1 TO 4
33090		LINE INPUT #FILENUM1%,ALINE$
33095		COMMENT$(ILOOP%)	= MID$(ALINE$,3)
33100	NEXT ILOOP%
33101	'
33105	FOR ILOOP%	= 0 TO 4
33110		PRINT FNCSRLD$(COMMENTROW%+ILOOP%,COMMENTCOLUMN%);
		       LINERA$;
		       COMMENT$(ILOOP%)
33120	NEXT ILOOP%
33130	'		
33180	RETURN
33190	'
34000	'~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
34050	'
34100	'	Subroutine [8]: TIME DELAY.
34150	'
34200	FOR TIMEOUT% = 1 TO DELAY%
34210			FOR MORE% = DELAY% TO 1 STEP -1
34220				WASTE% = WASTE%+1
34230			NEXT MORE%
34300	NEXT TIMEOUT%
34350	RETURN
39000	'
39010	'~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
39020	'
39500	'	Subroutine [9]: PRINT HELP MENU.
39510	'
39520	PRINT 	FNCSRLD$ (TOP%,10);
		 "<?> - Will PRINT an explanation of the question. "
39530	PRINT	FNCSRLD$ (TOP%+2,10);
		 "<Y> - ENABLES the function."
39540	PRINT	FNCSRLD$ (TOP%+4,10);
		 "<N> - DISABLES the function."
39550	PRINT	FNCSRLD$ (TOP%+6,10);
		 "<RETURN> - Is the DEFAULT condition."
39900	'
39905	RETURN
39910	'
39999	'**********************************************************************
40000	'
40001	'			########################
40002	'                       ###### SECTION 9  ######
40003	'                       ########################
40004	'
40005	'>>>>>>>>>>>>>>>>>>>>>>>>>> ERROR TRAPPING <<<<<<<<<<<<<<<<<<<<<<<<<<<<
40020	'
40030	DRIVE$	="B:"
40100	IF ERR = 53 AND ERL = 11400
		THEN
			 CLOSE #FILENUM1%:
			 OPEN "I",#FILENUM1%,DRIVE$+FILE$:
			 RESUME 11600	
40400	'
40410	IF ERR = 53 AND ERL = 29610
		THEN
			 CLOSE #FILENUM3%:
			 OPEN "I",#FILENUM3%,DRIVE$+"TTKEYBD.DAT":
			 RESUME 29650
40500	'
40510	IF ERR	= 53 AND ERL = 23330
		THEN
			 CLOSE #FILENUM2%:
			 OPEN "I",#FILENUM2%,DRIVE$+"TTHELP"+HELPNUM$+".DAT":
			 RESUME 23340			 
65500	'**********************************************************************
65529	END
