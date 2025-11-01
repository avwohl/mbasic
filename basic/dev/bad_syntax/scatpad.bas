1000 '*****   Simple Utility Program   *****
1010 '	If your sort program only allows
	records to be fixed length, then
	this program can be used to pad
	spaces to the end of each line.
1020 '	New addition - for those who must have
	fixed length fields too.
1022 '	Beware - This program is like tomato juice,
	i.e. possible insect fragments - it was put
	together very quickly and has been tested
	only minimally.
1030 '*****   Bill Norris, 12/13/81    *****

1040 INPUT "Type complete INPUT filename : ",IFIL$
1050 INPUT "Type complete OUTPUT filename : ",OFIL$
1060 OPEN "I",#1,IFIL$ : OPEN "O",#2,OFIL$ : PRINT
1070 PRINT "Type '1' for fixed length records (last field padded)."
1080 PRINT "Type '2' for fixed length fields too (slower than #1)."
1090 INPUT "     Type '1' or '2' : ",X : PRINT
1100 IF X<>1 AND X<>2 THEN GOTO 1070
1110 IF X=2 THEN GOTO 1190



1120 INPUT "What is the record length? ",RL
1130 PRINT "Only";RL-2;" bytes available for fields, as"
1140 INPUT "<cr/lf> occupies 2 bytes.  Retype ? ",X$
1150 IF ASC(X$)=89 OR ASC(X$)=121 THEN PRINT : GOTO 1120

1160 LINE INPUT #1,A$:B$=A$+SPACE$(RL-LEN(A$)):
     PRINT #2,B$:IF EOF(1) THEN GOTO 1170 ELSE GOTO 1160
1170 GOTO 9000

1190 INPUT "How many fields per record? ",NUMF : WIDTH 78
1195 INPUT "Do you want commas inserted between fields? ",X$
1198 IF ASC(X$)=89 OR ASC(X$) THEN COM$=","
1200 FOR I=1 TO NUMF :
	PRINT "How many bytes in field #";I; :
	INPUT " ",FL(I) :
     NEXT I
1210 Y$="":FOR I=1 TO NUMF-1:
	INPUT #1,X$:Y$=Y$+X$+SPACE$(FL(I)-LEN(X$))+COM$:
	NEXT I:INPUT #1,X$:Y$=Y$+X$+SPACE$(FL(NUMF)-LEN(X$)):
	X$=Y$+CHR$(13)+CHR$(10):PRINT #2,X$;
1220 IF EOF(1) THEN GOTO 9000 ELSE PRINT "*"; : GOTO 1210

9000 CLOSE : PRINT : PRINT "Fin" : END
