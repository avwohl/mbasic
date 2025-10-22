1	'Program to sort the RBBS USERS.BB# file into local and long distance
2	'priorities to speed name search for people calling long distance
3	'Written by Trevor Marshall, SYSOP TO Tech RBBS, 5/30/83
4	'The callers file is searched firstly for callers from local
5	'areas (Agoura, Moorpark,Thousand Oaks, Newbury Park)
6	'Then for those from CA, and the remainder are given top priority
7	' A temp file USERS.$$$ is created with the new list
8	DEFINT A-Z
9	DIM LOCAL(1000),CA(1000),US(1000) 'The arrays we sort people into
10	OPEN "R",1,"A:USERS.BB#",62	'A Random access file
20	FIELD#1,62 AS RR$		'with free format string field
30	GET #1,1			'Read the number of entries
40	LAST.RECORD=VAL(RR$)+1		'and convert to numeric
50	PRINT "There are ";LAST.RECORD-1;" callers in the file." : PRINT
58	J=1 : K=J : L=J			'Initialize the array pointers
60	FOR I=2 TO LAST.RECORD		'Now get the local callers
70	GET #1,I
80	SECOND.NAME=INSTR(5,RR$," ")	'Scan line to start of town
82	TOWN=INSTR(SECOND.NAME+1,RR$," ")+1
89	'Scan the town and state field for kew words...
90	IF(INSTR(TOWN,RR$,"MOORPARK") <> 0) THEN 300
100	IF(INSTR(TOWN,RR$,"THOUSAND") <> 0) THEN 300
110	IF(INSTR(TOWN,RR$,"WESTLAKE") <> 0) THEN 300
120	IF(INSTR(TOWN,RR$,"NEWBURY") <> 0) THEN 300
122	IF(INSTR(TOWN,RR$,"AGOURA") <> 0) THEN 300
129	'Now sort out the Californian ones
130	IF(INSTR(TOWN,RR$,",CA") <> 0) THEN 500
140	IF(INSTR(TOWN,RR$," CA") <> 0) THEN 500	'Pity about CATSUP, TX.....
160	'OK, so the rest are international or interstate
170	'Until I work out a way to sort the internationals I will do it by hand
180	US(J)=I : J=J+1		'Save the record pointer in the US array
190	IF J>1000 GOTO 800 ELSE GOTO 600	'And loop for more records
300	'These are the locals
310	LOCAL(K)=I : K=K+1	'whose pointers are in the LOCAL array
320	IF K>1000 THEN GOTO 800 ELSE GOTO 600
500	'These are within CAlifornia
510	CA(L)=I : L=L+1 :IF L>1000 GOTO 800 'whose pointers are in the CA array
600	NEXT I			'loop until all records have been read
602	PRINT "There are";J-1;" interstate callers," 'Then put statistics
604	PRINT "      and";L-1;" Californian callers,"
606	PRINT "      and";K-1;" local (non-toll) callers." : PRINT
610	OPEN "R",#2,"A:USERS.$$$",62	'We will put the output into a temp
620	FIELD #2,62 AS NW$		'file to allow easy backup
630	GET #1,1 : LSET NW$=RR$ : PUT #2,1 'Ok, start writing O/P file
640	I=2				'pointer to second O/P record
650	FOR INDEX=1 TO J-1	'The first of which processes the US callers
660	GET #1,US(INDEX):LSET NW$=RR$	'Get the long distance name
670	PUT #2,I : I=I+1 : NEXT INDEX	'loop until US(INDEX) empty
680	FOR INDEX=1 TO L-1
690	GET #1,CA(INDEX):LSET NW$=RR$		'Now put the californian ones
700	PUT #2,I : I=I+1 : NEXT INDEX
710	FOR INDEX=1 TO K-1
720	GET #1,LOCAL(INDEX):LSET NW$=RR$	'Lastly the local callers
730	PUT #2,I : I=I+1 : NEXT INDEX
740	IF I<>LAST.RECORD+1
	THEN PRINT "Output file incorrect size..ERROR..aborting" : STOP
748	KILL "A:USERS.BAK"			'delete any .BAK file
750	CLOSE #1 : NAME "A:USERS.BB#" AS "A:USERS.BAK" 'Rename old file
760	CLOSE #2 : NAME "A:USERS.$$$" AS "A:USERS.BB#" 'substitute new one
770	PRINT "Sorting completed": STOP
800	'Error entry point...
810	PRINT "Too many users..increase array size..ERROR.." : STOP
