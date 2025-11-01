100	' Simple keypad programmer for AD31 teminal
110	' Quickie effort in MBASIC
120	' Bill Bolton, Software Tools, Australia
130	'
140	' See KEY.C for a much more elegent version in "C"
150	'
200	ESC$ = CHR$(27)
210	PRINT "This program will program the numeric keypad on and ADM-31
220	PRINT "terminal with revision 4.xx software.
230	PRINT
240	PRINT "If you dont want to program a key just press 'RETURN'"
250	PRINT
260	PRINT ESC$;"!N"
270	FOR I = 0 TO 9
280		PRINT "String for numeric pad key '";I;"' : ";
290		INPUT ST$(I)
300		IF ST$(I) = "" THEN
			ST$(I) = CHR$(48 + I)
310	NEXT I
320	FOR I = 0 TO 9
330		LENGTH = LEN(ST$(I))
340		SEND$ = STRING$(LENGTH +1,32)
350		MID$(SEND$,1,1) = "H"
360		MID$(SEND$,2,LENGTH) = ST$(I)
370		PRINT SEND$;ESC$;"!";CHR$(48 + I)
380		PRINT ESC$;"*"
390	NEXT I
400	INPUT "Do you want to enable the programmed functions (Y/N 'Return' = N) ";A$
410	IF A$ = "N" OR A$ = "n" GOTO 430
420	PRINT ESC$;"!Y";"Done."
430	PRINT "Finished programming numeric keys."
