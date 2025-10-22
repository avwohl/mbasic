10	REM *************************************
	* CAT-XREF.BAS
	* by Simon J. Ewins
	* December 1, 1982
	*
	* This program takes the MAST.CAT file
	* created by NCAT32.COM and provides printed
	* cross-references by:
	* 			Disk # (-xxxx.###)
20	REM                       Filename
	*                       File extension
	*
	* This program is written to run on an
	* Osborne-1. Check throughout for chr$ etc. 
	* to locate Osborne specific code.
	*****************************************

30	ON ERROR GOTO 980
40	DIM CAT$(1000),EXT$(50)
50	PRINT CHR$(26);:
	PRINT "Catalogue Cross-Reference":
	PRINT STRING$(25,34):
	PRINT "by Simon J. Ewins": PRINT:
	PRINT "Portions of compiled version (c)1981 Microsoft"
60	PRINT: PRINT "MENU:":
	PRINT "====":
	PRINT "1. Print by Disk Number":
	PRINT "2. Print by Filename (alphabetical)":
	PRINT "3. Print by File extension":
	PRINT "4. End (if compiled then returns to CP/M)"
70	PRINT: PRINT "Mount 'MAST.CAT' disk in drive B:":
	PRINT "and ENTER your choice :";:
	SELECTION$ = INPUT$(1):
	IF SELECTION$ < "1" OR SELECTION$ > "5"
	   THEN GOTO 50
80	SEL = VAL(SELECTION$):
	IF SEL = 4 THEN END
90	ON SEL GOSUB 290, 510, 640
100	GOTO 50

110	REM ----- OPEN & READ FILE SUBROUTINE ----

120	PRINT: REC%=0: OPEN "I",1,"B:MAST.CAT"
130	IF EOF(1) THEN 160
140	LINE INPUT #1, CAT$(REC%)
150	REC%=REC%+1: GOTO 130
160	REC%=REC%-1: RETURN

170	REM ----- ERROR HANDLING-------------------

180	PRINT "FILE NOT FOUND ERROR.":
	PRINT: PRINT "Remount 'MAST.CAT' in drive 'B:'"
190	FOR I%=1 TO 2000: NEXT I%: GOTO 50
200	PRINT "DISK I/O ERROR"
210	GOTO 190

220	REM ----- PRINTER OPTION SUBROUTINE ------

230	PRINT: PRINT "Send to printer ";: INPUT ANS$
240	IF ANS$="Y" OR ANS$="y" THEN 245 ELSE
	GOTO 250
245	INPUT "Serial or Parallel (S/P)";ANS$
246	IF ANS$="S" OR ANS$="s" THEN IOBYTE=129:
	GOTO 270
247	IF ANS$="C" OR ANS$="c" THEN IOBYTE=128:
	GOTO 270
248	GOTO 245
250	IF ANS$="N" OR ANS$="n" THEN IOBYTE=128:
	GOTO 270
260	GOTO 230
270	PRINT STRING$(50,34): POKE 3,IOBYTE: RETURN

280	REM ----- SORT BY DISK NUMBER -----------

290	GOSUB 120: GOSUB 230: J%=1
300	FOR I%=1 TO REC%:
	IF LEFT$(CAT$(I%),1)<>"+" THEN 320
310	EXT$(J%)=RIGHT$(CAT$(I%),3):
	J%=J%+1: NEXT I%
320	GOSUB 860
330	LI%=1: FOR I%=1 TO J%-1:
	PRINT "DISK #";EXT$(I%):
	PRINT: PRINT:
	LI%=LI%+3
340	FOR K%=1 TO REC%:
	IF RIGHT$(CAT$(K%),3)<>EXT$(I%) THEN 420
350	A%=INSTR(CAT$(K%),","):
	B%=INSTR(CAT$(K%),"."):
	C%=POS(0)
360	A$=LEFT$(CAT$(K%),A%-1):
	B$=LEFT$(A$,B%-1):
	A$=MID$(A$,B%+1,3):
	B$=B$+STRING$(8-LEN(B$),32)+".":
	IF A$="" THEN A$="   "
370	IF C%=1 THEN 410
380	IF C%<19 THEN PRINT TAB(19)"";: GOTO 410
390	IF C%<37 THEN PRINT TAB(37)"";: GOTO 410
400	IF C%>45 THEN PRINT: LI%=LI%+1
410	PRINT B$;A$;
420	NEXT K%
430	PRINT: PRINT STRING$(50,34): LI%=LI%+2
440	IF LI%>50 THEN PRINT CHR$(12): LI%=1
450	NEXT I%
460	PRINT CHR$(12): POKE 3,128: PRINT: CLOSE
470	PRINT "Press <ENTER> for menu..... ";
480	A$=INKEY$: IF A$="" THEN 480
490	RETURN

500	REM ----- SORT BY FILENAME (ALPHABETICAL) -

510	GOSUB 120: GOSUB 230
520	LI%=1: FOR I%=1 TO REC%:
	C%=POS(0)
530	IF C%=1 THEN 570
540	IF C%<21 THEN PRINT TAB(21)"";: GOTO 570
550	IF C%<41 THEN PRINT TAB(41)"";: GOTO 570
560	IF C%>50 THEN PRINT: LI%=LI%+1
570	A%=INSTR(CAT$(I%),"."):
	A$=LEFT$(CAT$(I%),A%-1):
	A$=A$+STRING$(8-LEN(A$),32)+".":
	B$=MID$(CAT$(I%),A%+1,3):
	C$=RIGHT$(CAT$(I%),3)
580	IF LEFT$(B$,1)="," THEN B$="   "
590	IF LI%>60 THEN PRINT CHR$(12): LI%=1
600	PRINT A$;B$;"-";C$;
610	NEXT I%
620	GOTO 460

630	REM ----- SORT BY EXTENSION TYPE ---------

640	GOSUB 120: GOSUB 230
650	J%=1: FOR I%=1 TO REC%:
	CAT$=CAT$(I%):
	A%=INSTR(CAT$,".")+1:
	CAT$=MID$(CAT$,A%,3)
660	FOR K%=1 TO J%:
	IF EXT$(K%)=CAT$ THEN 690
670	NEXT K%
680	EXT$(J%)=CAT$: J%=J%+1
690	NEXT I%
700	GOSUB 860
710	LI%=1:
	FOR I%=1 TO J%-1:
	FOR K%=1 TO REC%:
	A%=INSTR(CAT$(K%),".")+1:
	CAT$=MID$(CAT$(K%),A%,3)
720	IF CAT$<>EXT$(I%) THEN 820
730	C%=POS(0):
740	IF C%=1 THEN 780
750	IF C%<21 THEN PRINT TAB(21)"";: GOTO 780
760	IF C%<41 THEN PRINT TAB(41)"";: GOTO 780
770	IF C%>50 THEN PRINT: LI%=LI%+1
780	A%=INSTR(CAT$(K%),"."):
	A$=LEFT$(CAT$(K%),A%-1):
	A$=A$+STRING$(8-LEN(A$),32)+".":
	B$=MID$(CAT$(K%),A%+1,3):
	C$=RIGHT$(CAT$(K%),3)
790	IF LEFT$(B$,1)="," THEN B$="   "
800	IF LI%>60 THEN PRINT CHR$(12): LI%=1
810	PRINT A$;B$;"-";C$;
820	NEXT K%
830	PRINT: PRINT: LI%=LI%+2: NEXT I%
840	GOTO 460

850	REM ----- SORTING ROUTINE FOR EXT$ -------

860	NUMB%=J%-1
870	SWITCH%=0
880	NUMB%=NUMB%-1
890	FOR K%=1 TO NUMB%
900	IF EXT$(K%)<=EXT$(K%+1) THEN 950
910	TEMP$=EXT$(K%)
920	EXT$(K%)=EXT$(K%+1)
930	EXT$(K%+1)=TEMP$
940	SWITCH%=1
950	NEXT K%
960	IF SWITCH%=1 THEN 870
970	RETURN

980	REM ----- ERROR ROUTING ------------------

990	IF ERR = 53 THEN RESUME 180
1000	IF ERR = 57 THEN RESUME 200
1010	PRINT "ERROR #";ERR:
	END
TING ------------------

99