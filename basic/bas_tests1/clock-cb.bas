
	REM *************************************************************
	REM *								*
	REM *	SYSTEM SUPPORT 1 BOARD CLOCK FUNCTIONS			*
	REM *	BY BILL BOLTON, Software Tools, Australia		*
	REM *	VERSION 1.0	JAN 17,1982	SUBROUTINES FOR MBASIC	*
	REM *	VERSION 1.0	JAN 18,1982	INITIAL REL FOR CB80	*
	REM *								*
	REM *************************************************************

	REM -------------------------------------------------------------

	DEF TIME$
	
	INTEGER BASEPORT,CMDPORT,DATAPORT,CREAD
	STRING LOCAL.TIME

	REM *************************************************************
	REM *		LOCAL VARIABLES USED IN TIME$			*
	REM *								*
	REM *BASEPORT	SYSTEM SUPPORT 1 BOARD BASE PORT ADDRESS	*
	REM *CMDPORT	SS1 CLOCK COMMAND PORT ADDRESS			*
	REM *DATAPORT	SS1 CLOCK DATA PORT ADDRESS			*
	REM *CREAD	SS1 CLOCK READ MASK				*
	REM *HOURS10	TENS OF HOURS DIGIT				*
	REM *HOURS1	UNIT HOURS DIGIT				*
	REM *MINUTES10	TENS OF MINUTES DIGIT				*
	REM *MINUTES1	UNIT MINUTES DIGIT				*
	REM *SECONDS10	TENS OF SECONDS DIGIT				*
	REM *SECONDS1	UNIT SECONDS DIGIT				*
	REM *LOCAL.TIME	TIME OF DAY STRING IN HH:MM:SS FORMAT		*
	REM *************************************************************

	BASEPORT = 50H
	CMDPORT = BASEPORT + 10
	DATAPORT = CMDPORT + 1
	CREAD = 10H

	REM *************************************************************
	REM *		READ THE TIME DIGITS				*
	REM *************************************************************

	OUT CMDPORT,(CREAD + 5)
	LOCAL.TIME = STR$((INP(DATAPORT) AND 3))
	OUT CMDPORT,(CREAD + 4)
	LOCAL.TIME = LOCAL.TIME + STR$(INP(DATAPORT)) + ":"
	OUT CMDPORT,(CREAD + 3)
	LOCAL.TIME = LOCAL.TIME + STR$((INP(DATAPORT)) AND 7H)
	OUT CMDPORT,(CREAD + 2)
	LOCAL.TIME = LOCAL.TIME + STR$(INP(DATAPORT)) + ":" 
	OUT CMDPORT,(CREAD + 1) 
	LOCAL.TIME = LOCAL.TIME + STR$(INP(DATAPORT))
	OUT CMDPORT,(CREAD + 0)
	LOCAL.TIME = LOCAL.TIME + STR$(INP(DATAPORT))

	TIME$ = LOCAL.TIME
	RETURN
	FEND

	REM ------------------------------------------------------------

	DEF WDAY$
	INTEGER BASEPORT,CMDPORT,DATPORT,CREAD,WEEKDAY
	
	REM *************************************************************
	REM *		LOCAL VARIABLES USED IN WDAY$			*
	REM *								*
	REM *BASEPORT	SYSTEM SUPPORT 1 BOARD BASE PORT ADDRESS	*
	REM *CMDPORT	SS1 CLOCK COMMAND PORT ADDRESS			*
	REM *DATAPORT	SS1 CLOCK DATA PORT ADDRESS			*
	REM *CREAD	SS1 CLOCK READ MASK				*
	REM *WEEKDAY	DAY OF WEEK DIGIT				*
	REM *WDAY$	DAY OF WEEK NAME STRING				*
	REM *************************************************************

	BASEPORT = 50H
	CMDPORT = BASEPORT + 10
	DATAPORT = CMDPORT + 1
	CREAD = 10H

	REM *************************************************************
	REM *	READ THE WEEKDAY DIGIT AND CONVERT IT TO A		*
	REM *               DAY NAME STRING				*
	REM *************************************************************

	OUT CMDPORT,(10H + 6)
	WEEKDAY = INP(DATAPORT)
	OUT CMDPORT,0
	IF WEEKDAY = 0 THEN WDAY$ = "Sunday"
	IF WEEKDAY = 1 THEN WDAY$ = "Monday"
	IF WEEKDAY = 2 THEN WDAY$ = "Tuesday"
	IF WEEKDAY = 3 THEN WDAY$ = "Wednesday"
	IF WEEKDAY = 4 THEN WDAY$ = "Thursday"
	IF WEEKDAY = 5 THEN WDAY$ = "Friday"
	IF WEEKDAY = 6 THEN WDAY$ = "Saturday"

	RETURN
	FEND

	REM -------------------------------------------------------------

	DEF DATE1$
	INTEGER BASEPORT,CMDPORT,DATAPORT,CREAD
	INTEGER YEAR10,YEAR1,MONTH10,MONTH1,DAY10,DAY1

	REM *************************************************************
	REM *		LOCAL VARIABLES FOR DATE1$			*
	REM *								*
	REM *BASEPORT	SYSTEM SUPPORT 1 BOARD BASE PORT ADDRESS	*
	REM *CMDPORT	SS1 CLOCK COMMAND PORT ADDRESS			*
	REM *DATAPORT	SS1 CLOCK DATA PORT ADDRESS			*
	REM *CREAD	SS1 CLOCK READ MASK				*
	REM *YEAR10	TENS OF	YEARS INTEGER				*
	REM *YEAR1	UNIT YEAR INTEGER				*
	REM *MONTH10	TENS OF MONTHS INTEGER				*
	REM *MONTH1	UNIT MONTH INTEGER				*
	REM *DAY10	TENS OF DAYS INTEGER				*
	REM *DAY	UNIT DAY INTEGER				*
	REM *************************************************************

	BASEPORT = 50H
	CMDPORT = BASEPORT + 10
	DATAPORT = CMDPORT + 1
	CREAD = 10H

	REM *************************************************************
	REM *		READ THE DATE DIGITS				*
	REM *************************************************************

	OUT CMDPORT,(CREAD + 9)
	MONTH1 = INP(DATAPORT)
	OUT CMDPORT,(CREAD + 10)
	MONTH10 = ((INP(DATAPORT) AND 1) * 10)
	OUT CMDPORT,(CREAD + 7)
	DAY1 = INP(DATAPORT)
	OUT CMDPORT,(CREAD + 8)
	DAY10 = ((INP(DATAPORT) AND 3) * 10)
	OUT CMDPORT,(CREAD + 11)
	YEAR1 = INP(DATAPORT)
	OUT CMDPORT,(CREAD + 12)
	YEAR10 = (INP(DATAPORT) * 10)
	OUT CMDPORT,0

	REM *************************************************************
	REM *		FORMAT THE FIRST DATE STRING			*
	REM *************************************************************

	DATE1$ = STR$(DAY10 + DAY1) + "/" + STR$(MONTH10 + MONTH1)\
			+ "/" + STR$(YEAR10 + YEAR1)

	RETURN
	FEND

	REM -------------------------------------------------------------

	DEF DATE2$
	INTEGER BASEPORT,CMDPORT,DATAPORT,CREAD
	INTEGER YEAR10,YEAR1,MONTH10,MONTH1,MONTH,DAY10,DAY1
	STRING MONTH.NAME

	REM *************************************************************
	REM *		LOCAL VARIABLES FOR DATE2$			*
	REM *								*
	REM *BASEPORT	SYSTEM SUPPORT 1 BOARD BASE PORT ADDRESS	*
	REM *CMDPORT	SS1 CLOCK COMMAND PORT ADDRESS			*
	REM *DATAPORT	SS1 CLOCK DATA PORT ADDRESS			*
	REM *CREAD	SS1 CLOCK READ MASK				*
	REM *YEAR10	TENS OF	YEARS INTEGER				*
	REM *YEAR1	UNIT YEAR INTEGER				*
	REM *MONTH10	TENS OF MONTHS INTEGER				*
	REM *MONTH1	UNIT MONTH INTEGER				*
	REM *MONTH	MONTH INTEGER					*
	REM *DAY10	TENS OF DAYS INTEGER				*
	REM *DAY	UNIT DAY INTEGER				*
	REM *MONTH.NAME NAME OF THE MONTH STRING			*
	REM *************************************************************

	BASEPORT = 50H
	CMDPORT = BASEPORT + 10
	DATAPORT = CMDPORT + 1
	CREAD = 10H

	REM *************************************************************
	REM *		FORMAT THE SECOND DATE STRING			*
	REM *************************************************************

	OUT CMDPORT,(CREAD + 9)
	MONTH1 = INP(DATAPORT)
	OUT CMDPORT,(CREAD + 10)
	MONTH10 = ((INP(DATAPORT) AND 1H) * 10)
	OUT CMDPORT,(CREAD + 7)
	DAY1 = INP(DATAPORT)
	OUT CMDPORT,(CREAD + 8)
	DAY10 = ((INP(DATAPORT) AND 3H) * 10)
	OUT CMDPORT,(CREAD + 11)
	YEAR1 = INP(DATAPORT)
	OUT CMDPORT,(CREAD + 12)
	YEAR10 = (INP(DATAPORT) * 10)
	OUT CMDPORT,0

	MONTH = MONTH10 + MONTH1

	IF MONTH = 1 THEN MONTH.NAME = "January"
	IF MONTH = 2 THEN MONTH.NAME = "February"
	IF MONTH = 3 THEN MONTH.NAME = "March"
	IF MONTH = 4 THEN MONTH.NAME = "April"
	IF MONTH = 5 THEN MONTH.NAME = "May"
	IF MONTH = 6 THEN MONTH.NAME = "June"
	IF MONTH = 7 THEN MONTH.NAME = "July"
	IF MONTH = 8 THEN MONTH.NAME = "August"
	IF MONTH = 9 THEN MONTH.NAME = "September"
	IF MONTH = 10 THEN MONTH.NAME = "October"
	IF MONTH = 11 THEN MONTH.NAME = "November"
	IF MONTH = 12 THEN MONTH.NAME = "December"

	DATE2$ = MONTH.NAME + " " + STR$(DAY10 + DAY1) \
			+ ", 19" + STR$(YEAR10 + YEAR1)

	RETURN
	FEND

	REM -------------------------------------------------------------

	REM *************************************************************
	REM *		EXAMPLES OF DISPLAYING TIME AND DATE IN		*
	REM *			TWO DIFFERENT FORMATS			*
	REM *								*
	REM * PRINT "The time is ";LOCAL.TIME;" on ";WDAY$;" ";DATE1$	*
	REM * PRINT "The time is ";LOCAL.TIME;" on ";WDAY$;" ";DATE2$	*
	REM *************************************************************

	PRINT "BASIC CLOCK SUBROUTINE DEMONSTRATION PROGRAM"
	PRINT "The time is ";TIME$;" on ";WDAY$;" ";DATE1$
	PRINT "The time is ";TIME$;" on ";WDAY$;" ";DATE2$
	PRINT
	END
