100 REM BRUTEF.BAS
110 REM
120 REM This program was designed to test the hypothesis of how
130 REM CP/M MBASIC v.5.21 saves "protected" versions of BASIC
140 REM programs.
150 REM
160 REM By Jim McClanahan W4JBM, August 2020
170 REM
180 REM
190 REM Array T1 is the unprotected, tolkenized stream consisting
200 REM Array K is the decryption "key" extracted from T1 and P1.
210 REM Array P1 is the same stream protected.
220 REM Array P2 is the "unknown" stream to be decrypted in protected,
230 REM      tolkenized format.
240 REM Array T2 will be the (hopefully) decrypted stream from P2.
250 REM
260 PRINT "Load arrays and initialize data..."
270 DIM T1%(53),P1%(53),T2%(53),P2%(53),K%(53)
280 FOR I%=1 TO 53:T1%(I%)=65:NEXT
290 FOR I%=0 TO 52:READ P1%(I%):NEXT
300 FOR I%=0 TO 52:READ P2%(I%):NEXT
310 REM
320 REM K%(x) will (hopefully) contain the decryption KEY (position dependent)
330 REM T2%(x) will (hopefully) contain the decrypted uoriginal (all As)
340 REM
350 X%=13:REM Initialize PRE adder that runs from 13 to 1 and then cycles
360 Y%=11:REM Initialize POST adder that runs from 11 to 1 and then cycles
370 REM
380 REM The next two lines put us ahead 6 postions skipping the next memory
390 REM address (2 bytes), the line number (2 bytes), the REM tolken and
400 REM the space that follows it.
410 REM
420 X%=X%-6
430 Y%=Y%-6
440 Z%=1
450 REM Print header...
460 PRINT
470 PRINT "SEQ  PR PO   T1  P1  KEY   P2  T2"
480 REM
490 REM And now we try to find the key...
500 REM
510 REM First, let's subtract out the post-XOR add from the protected result...
520 KP% = (P1%(Z%) - Y% + 256) MOD 256
530 REM Now lets subtract out the pre-XOR add from the raw tolken stream....
540 KT% = (T1%(Z%) - X% + 256) MOD 256
550 REM Now let's XOR those results and hopefully produce a key...
560 K%(Z%) = KP% XOR KT%
570 REM
580 REM Let's see if we can use it to decode things...
590 REM
600 REM First we subtract out the post-XOR add from the protected result...
610 C% = (P2%(Z%) - Y% + 256) MOD 256
620 REM Now let's reverse the XOR using the key we found...
630 C% = C% XOR K%(Z%)
640 REM And finally we add back in the pre-XOR subtract...
650 T2%(Z%) = (C% + X%) MOD 256
660 REM
670 REM Print our progress...
680 PRINT USING "###  ## ##  ### ###  ###  ### ### !";Z%,X%,Y%,T1%(Z%),P1%(Z%),K%(Z%),P2%(Z%),T2%(Z%),CHR$(T2%(Z%))
690 REM
700 REM Now increment and loop...
710 Z% = Z% + 1
720 IF Z%=52 THEN GOTO 790
730 Y%=Y%-1:IF Y%=0 THEN Y%=11
740 X%=X%-1:IF X%=0 THEN X%=13
750 GOTO 520
760 REM
770 REM Print the results...
780 REM
790 PRINT
800 FOR I%=1 TO 51:PRINT CHR$(T2%(I%));:NEXT
810 PRINT
820 END
830 REM
840 REM DATA IS A STRING OF ENCRYPED CHARACTER As...
850 REM
860 DATA &HF7,&HA6,&H69,&H65,&H6E,&H6B,&HD2,&H84,&H34,&HD1
870 DATA &H98,&H73,&H67,&HCA,&H9B,&HCC,&H14,&H9F,&HEB,&H1F
880 DATA &HC8,&H58,&HE2,&H1C,&H7F,&H5E,&H6B,&HEA,&H3D,&HA2
890 DATA &H4E,&H63,&H73,&HDB,&HDC,&HCE,&H31,&HD6,&H2B,&H9C
900 DATA &H6C,&HEC,&H2A,&H46,&H54,&HEF,&HC7,&HF1,&H67,&H60
910 DATA &H37,&HAB,&H49
920 REM
930 REM DATA IS ENCRYPTED 'QUICK BROWN FOX...' STRING...
940 REM (I realized later that the fox is actually red.)
950 REM
960 DATA &HF7,&HDB,&H40,&H41,&H4F,&H3B,&H96,&H5C,&H52,&HAB
970 DATA &HB9,&H08,&H38,&H9C,&HD5,&H9B,&H35,&HD6,&HBD,&H68
980 DATA &HA7,&H3F,&H86,&H48,&H2E,&H42,&H0E,&HCB,&H6B,&HDF
990 DATA &H22,&H12,&H54,&HEC,&HBD,&HAA,&H10,&H83,&H4B,&HE5
1000 DATA &H34,&HCB,&H4B,&H73,&H22,&HA5,&HF2,&HCC,&H0A,&H0E
1010 DATA &H51,&HC6,&H68
H54,&HEC,&HBD,&HAA,&H10,&H83,&H4B,&HE5
1000 