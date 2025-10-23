10 REM BUILDSUB.BAS by Keith Petersen, W8SDZ 1/24/81
20 REM This illustrates how to execute another program from
30 REM BASIC. The secret is setting up a submit file, which
40 REM CP/M then automatically executes when we leave this
50 REM program and return to CP/M.
60 OPEN "O",1,"A:$$$.SUB":REM This is the submit file
70 REM Now lets tell CP/M to do a "DIR" after we reboot.
80 REM This could just as well be a name of a .COM file
90 REM we want to execute.
100 PRINT #1,CHR$(3);"DIR";CHR$(0)
110 REM length of ^ the command string
120 REM the command   ^^^  string
130 REM and a terminating zero  ^
140 CLOSE
150 POKE 4,0 : REM Assure we are on drive A: so submit will work
160 SYSTEM
