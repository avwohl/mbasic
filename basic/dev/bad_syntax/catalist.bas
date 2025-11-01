1000 '***************************************************************
1002 '**                                                           **
1004 '**     Filename is CATALIST.BAS.  Uses Basic-80 ver. 5.xx    **
1006 '**     Input is modified output of UCAT.COM (MAST.CAT).      **
1008 '**     MAST.CAT records of 2 fields are made 4 fields per    **
1010 '**      record by changing all periods to commas.  This      **
1012 '**      program accepts only CATALOG or SIGMLOG as valid     **
1014 '**      disk labels.                                         **
1016 '**     Written Dec. 13, 1981 by Bill Norris, ( b.p.p.l.).    **
1018 '**     Version 1.01                                          **
1020 '***************************************************************



1021 PRINT : PRINT : PRINT : PRINT : PRINT : PRINT
1022 PRINT "Program compiled from 'CATALIST.BAS', Version 1.01"
1024 COMPILE.ID$ = "Written Dec. 13, 1981 by Bill Norris, ( b.p.p.l.)."

1030 GOSUB 2400 : ACTION=SETUP.CONSTANTS
1040 GOSUB 2200 : ACT=SETUP.VARIABLES
1050 GOSUB 2000 : ACT=SETUP.FILES

1060 GOSUB 3000 : ACT=G.ET.PAGE.OF.DATA
1070 GOSUB 4000 : ACT=PRINT.PAGE.OF.DATA

1080 IF JOB=DONE THEN GOTO 9000 ELSE GOTO 1060



2000 '***** Get Disk Filenames & Open for Processing *****
2010 X1$="INPUT" : X2$="SCAT" : PRINT : GOSUB 2080 : GOSUB 8150 
2020 IF NOGO=YES THEN PRINT BEL$;"***** ";FIL$;" not found *****":GOTO 2010
2030 IFIL$=FIL$
2040 X1$="OUTPUT": X2$="SLIST": GOSUB 2080 : GOSUB 8150
2050 IF NOGO=OFF THEN PRINT BEL$;"***** ";FIL$;" already exists *****" :
     PRINT "Type 'y' to accept (old ";FIL$;" will be lost) :"; :
     INPUT " ",X$ : GOSUB 8120
2060 IF XX$="Y" THEN OFIL$=FIL$ : GOTO 2070 ELSE PRINT : GOTO 2040

2070 OPEN "I",#1,IFIL$ : OPEN "O",#2,OFIL$ : INPUT #1,D1$,D2$,D3$,D4$ : RETURN

2080 PRINT "Default ";X1$;" filename is ";X2$;".  Type <cr> to accept :";:
     INPUT " ",X$ : IF X$=""THEN FIL$=X2$ : RETURN ELSE GOSUB 8000 : RETURN



2200 '***** Parameter definitions & variable initialization *****

2203 FIL$="CAT.DAT" : GOSUB 8150 : IF NOGO=NO THEN GOTO 2233 ELSE PRINT
2204 INPUT "Does your terminal have a bell? ",X$ : IF X$="" GOTO 2204
2205 GOSUB 8120 : IF XXX$="Y" THEN BEL$=CHR$(7)
2206 PRINT : PRINT "Define output page format:" : PRINT
2209 INPUT "Type TOP MARGIN, BOTTOM MARGIN : ", TOP.MARGIN,BOT.MARGIN
2212 INPUT "Type PAGE LENGTH : ", PAGE.LENGTH
2214 INPUT "Type LEFT MARGIN, RIGHT MARGIN : ", LEFT.MARGIN, RIGHT.MARGIN
2216 INPUT "Type PAGE WIDTH : ", COLUMNS
2217 PRINT : INPUT "Force new page with new initial filename letter? ",X$ :
     IF X$="" THEN PRINT BEL$ : GOTO 2217
2218 GOSUB 8120 : IF XXX$="Y" THEN PAGE.CHEK$="Yes" ELSE PAGE.CHEK$="No"
2219 BAP$=
"123456789 123456789 123456789 123456789 123456789 123456789 123456789 123456":
     PRINT "Type PAGE HEADER :" : PRINT BAP$ : INPUT "", HEAD.LINE$:
     IF HEAD.LINE$="x" THEN HEAD.LINE$=HLIN$

2221 OPEN "O",#1,FIL$
2223 WRITE #1, TOP.MARGIN, BOT.MARGIN, PAGE.LENGTH
2225 WRITE #1, LEFT.MARGIN, RIGHT.MARGIN, COLUMNS
2227 WRITE #1, BEL$, PAGE.CHEK$
2228 WRITE #1, HEAD.LINE$
2230 CLOSE : GOTO 2242

2233 OPEN "I",#1,FIL$
2235 INPUT #1, TOP.MARGIN, BOT.MARGIN, PAGE.LENGTH
2237 INPUT #1, LEFT.MARGIN, RIGHT.MARGIN, COLUMNS
2239 INPUT #1, BEL$, PAGE.CHEK$
2240 INPUT #1, HEAD.LINE$
2242 CLOSE : Z=16 : PRINT :
     PRINT "Default Parameters are :"
2244 PRINT: PRINT "Top Margin =";TAB(Z);TOP.MARGIN:
     PRINT "Bottom Margin =";TAB(Z);BOT.MARGIN:
     PRINT "Page Length =";TAB(Z);PAGE.LENGTH
2245 PRINT "Left Margin =";TAB(Z);LEFT.MARGIN:
     PRINT  "Right Margin =";TAB(Z); RIGHT.MARGIN:
     PRINT "Page Width =";TAB(Z);COLUMNS
2246 PRINT : PRINT "Page Header is :" : PRINT HEAD.LINE$
2247 IF PAGE.CHEK$="Yes" THEN PRINT : PRINT
     "Output list skips page before new initial letter."
2248 PRINT : INPUT "Type 'y' to accept, 'n' to change : ", X$ :
     IF X$="" THEN PRINT BEL$; : GOTO 2248
2251 GOSUB 8120 : IF XXX$="N" THEN GOTO 2206
2254 IF XXX$<>"Y" THEN PRINT BEL$; : GOTO 2242

2257 LPP=PAGE.LENGTH-TOP.MARGIN-BOT.MARGIN
2260 CPL=COLUMNS-LEFT.MARGIN-RIGHT.MARGIN
2263 CHARS.PER.FIELD=18 : INTER.COL.GAP$="   |   "
2266 HL=LEN(HEAD.LINE$)
2280 CPF=CHARS.PER.FIELD : ICG=LEN(INTER.COL.GAP$) :XX=ICG : STICKS=1 : Y=CPF
2290 Y=Y+CPF+XX : IF Y<CPL THEN STICKS=STICKS+1 : GOTO 2290
2300 '***** STICKS = the number of data columns per page *****
2310 IF STICKS>3 THEN HEAD.OFF$=SPACE$((CPF+ICG)*(STICKS-3)/2)
2320 '*****     Reserve 2 header lines from LinesPerPage.    *****
2330 ARAY = (LPP-2)*STICKS
2340 DIM LINDAT$(555)
2350 RETURN

2400 NO=0 : YES=-1 : EMPTY=NO : FULL=YES : BEL$="***** ding ***** "
2410 JOB=NO : DONE=YES '***** JOB = done after input file is exhausted *****
2416 MAX.DR$="D" : HLIN$=
"Format = filename, extension, disk volume, source (c=CPMUG, s=SIG/M)"
2420 NEX.LETTER=65 '***** Letter "A" = 65, "B" = 66, etc.
2430 RETURN



3000 '***** Get one pageful of data *****
3010 PAGE=EMPTY : CNT=0
3020 GOSUB 3500 : IF PAGE=FULL THEN GOTO 3040
3030 LINS=LINS+1: IF CNT < ARAY THEN GOTO 3020
3040 PAGES=PAGES+1 : IF CNT < ARAY THEN GOSUB 3100 : RETURN

3100 FOR M=CNT+1 TO ARAY : LINDAT$(M)=SPACE$(CPF) : NEXT M : RETURN

3500 '***** Input data through one line buffer *****
3510 D5$=D1$ : D6$=D2$ : D7$=D3$ : D8$=D4$
3520 IF EOF(1) THEN PAGE=FULL : JOB=DONE : GOTO 3550
3525 INPUT #1, D1$, D2$, D3$, D4$
3530 IF PAGE.CHEK$<>"Yes" THEN GOTO 3550
3540 IF ASC(D1$)>=NEX.LETTER THEN PAGE=FULL : NEX.LETTER=ASC(D1$)+1
3550 CNT=CNT+1 : XX$="" '***** right fill strings with spaces *****
3560 X$=D5$ : X=8 : GOSUB 6000
3570 X$="."+D6$ : X=5 : GOSUB 6000
3580 IF D7$="CATALOG" THEN X7$="c" : GOTO 3640
3590 IF D7$="SIGMLOG" THEN X7$="s" : GOTO 3640

3600 PRINT : PRINT "***** ERROR IN LINE 3600 *****
3610 PRINT "Source volume should be CATALOG or SIGMLOG."
3620 PRINT "Value read in is "; : WRITE D7$ : PRINT BEL$
3630 STOP

3640 X$=D8$ : X=4 : GOSUB 6000
3650 LINDAT$(CNT)=XX$+X7$
3660 RETURN

4000 '***** Print the matrix one page at a time *****

4020 FOR I=1 TO TOP.MARGIN : PRINT #2, " " : NEXT I
4030 PRINT #2,SPACE$(LEFT.MARGIN);HEAD.OFF$;HEAD.LINE$:PRINT #2, " "
4033 PRINT "***** on page ";PAGES;
4050 ' cnt / sticks = printable data lines
4060 LIN.WRITS=INT((CNT-.001)/STICKS)+1
4070 ICG$=INTER.COL.GAP$

4080 FOR LOOPS=1 TO LIN.WRITS
4090     PRINT #2, SPACE$(LEFT.MARGIN); LINDAT$(LOOPS);
4100     FOR LL=1 TO STICKS-1
4110         IF LINDAT$(LOOPS+LL*LIN.WRITS)="" THEN GOTO 4120
             ELSE PRINT #2, ICG$;LINDAT$(LOOPS+LL*LIN.WRITS);
4120         NEXT LL
4130     PRINT #2, " "
4140     NEXT LOOPS
4150 FOR I=1 TO BOT.MARGIN+(LPP-2-LIN.WRITS) : PRINT #2, " " : NEXT I
4160 PAG.NUM=PAG.NUM+1 : PRINT "*****" : RETURN



6000 '***** Pad right end of string with spaces *****
6010 XX$=XX$+X$+SPACE$(X-LEN(X$)) : RETURN

8000 '***** Get a valid CP/M filename *****
8010 FIL$="" : INPUT "Disk drive used - ",X$ : IF LEN(X$)=0 THEN GOTO 8030
8020 GOSUB 8120 : FIL$=LEFT$(XX$,1)+":" :
     IF ASC(XX$)<65 OR ASC(XX$)>ASC(MAX.DR$) THEN PRINT :
     PRINT "INVALID DISK DRIVE - RETYPE -" : GOTO 8010
8030 INPUT "Name of file - ",X$ : IF LEN(X$)=0 THEN GOTO 8030
8040 GOSUB 8120 : FIL$=FIL$+XX$ : F1$=XX$
8050 INPUT "File extension ? ",X$ : IF LEN(X$)=0 THEN
     F2$="" : GOTO 8070
8060 XX$=LEFT$(X$,3) : X$=XX$ : GOSUB 8120 :
     F2$=XX$ : FIL$=FIL$+"."+XX$
8070 PRINT : PRINT "File selected is ";FIL$
8080 INPUT "O.K.? ",X$ : IF LEN(X$)=0 THEN X$="Y"
8090 GOSUB 8120 : IF LEFT$(XX$,1)="N" THEN PRINT "ReType..." : GOTO 8010
8100 PRINT : RETURN

8110 '***** Make UPPERcase XX$ from x$ *****
8120 XX$="" : FOR I=1 TO LEN(X$) : Y$=MID$(X$,I,1) : YY$=Y$ :
     IF Y$>="a" THEN YY$=CHR$(ASC(Y$)-32)
8130 XX$=XX$+YY$ : NEXT I
8140 XXX$=LEFT$(XX$,1) :  RETURN

8150 '***** Code looks for file on disk. *****
8160 NOGO=YES : ON ERROR GOTO 8190
8170 OPEN "I",#1,FIL$ : NOGO=OFF
8180 CLOSE #1 : ON ERROR GOTO 0 : RETURN
8190 RESUME 8180

9000 '***** It's a closed shop here... *****
9010 CLOSE : PRINT : PRINT "Fin" : PRINT
9020 END

