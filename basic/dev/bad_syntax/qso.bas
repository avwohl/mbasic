1	PRINT
	PRINT "******************** QSO RECORDS *********************"
	PRINT "               By WA2USS, January 1980":PRINT
2	PRINT:PRINT "Select from the following"
	PRINT "	1. Scan per page and change."
	PRINT " 2. Find any string."
	PRINT "	3. List file (for printout)"
	PRINT "	4. Enter new QSO's, sort, merge."
	PRINT "	5. End (back to CP/M)"
	PRINT:INPUT "Which number/item you select? ";A
	IF A>0 OR A<6 THEN 3
	PRINT "Select by number from '1' to '5' !":GOTO 2
3	ON A GOTO 1000, 2000, 3000, 4000, 9999
%INCLUDE QSOSCAN
%INCLUDE QSOFIND
%INCLUDE QSOLIST
%INCLUDE QSOEDIT
%INCLUDE QSOMERGE
9999	END
