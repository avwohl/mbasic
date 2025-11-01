10 REM  File Transfer Time Program for RCPM's, by Kelly Smith
20 REM 
30 REM  This  program may be used by a RCPM user to  determine 
40 REM the  total time in minutes to transfer files to or from 
50 REM a RCPM system.  Time  is rounded down  to  the  nearest 
60 REM minute,  but  detailed information may be  obtained  by 
70 REM removing the 'REM's in the following code. This program 
80 REM is compatible with MBASIC, and will compile to 
90 REM a 11 kilobyte (Gag!) file utilizing BASCOM.
100 REM
110 PRINT:INPUT "What is the Baud Rate (60 to 1200)";B
120 IF B<>60 AND B<>110 AND B<>300 AND B<>450 THEN GOTO 140
130 GOTO 180
140 IF B<>600 AND B<>710 AND B<>1200 THEN GOTO 160
150 GOTO 180
160 PRINT:PRINT"+++ Invalid Baud Rate +++":PRINT
170 PRINT"Must be 60, 110, 300, 450, 600, 710, or 1200 Baud!":GOTO 110
180 INPUT "What is the File Size in kilobytes";S
190 IF S<1 THEN GOTO 180
200 S=S*1024:T=S/(B/10):TM=T/60
210 REM PRINT:PRINT"Total number of characters in this file is";S
220 REM PRINT"This file will take";T;"seconds"
230 REM PRINT"Which equals";TM;"minutes"
240 PRINT:PRINT"Transfer time will be approximately";
250 T=INT(TM):IF T>1 THEN PRINT T "minutes" ELSE PRINT" 1 minute""
