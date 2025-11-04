1000 REM Written July 22, 1983 by B.Norris
         To use this program, first get
         UN.COM installed, load this program,
         save it (protected - with another
         name), load the protected version,
	 and finally - run it.

1001 REM UN.COM is available in both the
     SIG/M and CPMUG libraries.
     ( SIG/M Volume 52, CPMUG Volume ??? )

1002 REM Questions?  Call (212) 881-4898

1010 FOR I=1 TO 10: PRINT: NEXT I:
     PRINT "        Fixup for ** UN.COM **":
     PRINT "        For MBASIC 5.2 (Apple)":
     PRINT: PRINT
1020 PRINT "    0 - Exit this program.":
     PRINT
1030 PRINT "    1 - CP/MUG Version of UN.COM":
     PRINT "       (for versions up to 5.20 )":
     PRINT
1040 PRINT "    2 - SIG/M  Version of UN.COM":
     PRINT "       (FOR VERSIONS UP TO 5.21)":
     PRINT: PRINT
1050 PRINT "Select the appropriate number:";
1060 X$=INPUT$(1): X=ASC(X$):
     IF X>96 AND X<123 THEN X=X-32
1070 X$=CHR$(X): IF X$<"0" OR X$>"2" THEN
     FOR I=1 TO 15: PRINT: NEXT I: GOTO 1010
1080 PRINT X$: IF X$="0" THEN STOP
1090 IF X$="1" THEN A=33 ELSE A=29
1100 IF PEEK(A)<>15 OR PEEK(A+1)<>12 THEN
     PRINT "UN.COM not installed, already":
     PRINT "patched, or wrong version.":
     STOP

1110 C=12: D=188: B=256*C+D:
     IF PEEK(B)=254 AND NOT PEEK(B+1) THEN 1130
1120 PRINT "Wrong version of MBASIC, or":
     PRINT "this program is not protected.":
     STOP

1130 POKE A,D: POKE A+1,C:
     PRINT "Done."
