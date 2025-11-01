1  'FXPARMS.BAS  03/29/83  T. McCormick
2  'derived from EPSON FX-80 Printer Operation Manual
3  'This program illustrates various type styles and modes for the FX-80.
6 GOTO 10
7 RESET: SAVE "FXPARMS.BAS",A: STOP   'SAVE CORRECT FILE NAME
10 '---------- Define Constants ---------------
15 E$ = CHR$(27)		'Escape
100 '
110 'FX80 ENLARGED PRINT MODE WITH AUTO-RESET FROM LF
115 LPRINT "CHR$(14) causes change to....."
120 LPRINT CHR$(14); "Enlarged mode until line feed."
130 LPRINT "Then back to normal mode again."
200 'CONDENSED MODE
210 LPRINT CHR$(15); "Condensed mode shown here after CHR$(27);CHR$(15)."
220 LPRINT "...and still in condensed mode even after line feed."
230 LPRINT CHR$(14); "Now in Condensed Enlarged mode"
240 LPRINT "after CHR$(14) sent to printer."
300 LPRINT CHR$(18); "But CHR$(18) canceled the condensed mode."
400 LPRINT CHR$(20); "Enlarged print set on"
410 LPRINT "by CHR$(20)."
500 'Delete last character
510 LPRINT "Delete";
520 LPRINT CHR$(127); "ing last char by CHR$(127)."
600 ' 1/8 inch line spacing
610 LPRINT CHR$(27);"0"
620 FOR I = 1 TO 4
630 LPRINT "1/8 Inch Line Spacing from ESC 0."
640 NEXT
700 ' 7/72" line spacing
705 LPRINT:LPRINT
710 LPRINT CHR$(27);"1";
720 FOR I = 1 TO 5
730 LPRINT "7/72 Inch Line Spacing Example from ESC 1."
740 NEXT
800 ' 1/6" LINE SPACING
805 LPRINT:LPRINT
810 LPRINT CHR$(27);"2";
820 FOR I = 1 TO 4
830 LPRINT "1/6 inch  LINE SPACING from ESC 2."
840 NEXT
900 ' n/216 inch line spacing
905 LPRINT:LPRINT
910 LPRINT CHR$(27);"3";CHR$(20);
920 FOR I = 1 TO 4
930 LPRINT "Approx. 20/216 inch LINE SPACING from ESC 3 20."
940 NEXT
950 LPRINT CHR$(27);"2" 	'RESET TO 1/6 INCH LINE SPACING
1000 ' Selects Italic CG set
1010 LPRINT "Standard mode characters."
1020 LPRINT CHR$(27);"4";
1030 LPRINT "Italic   mode characters after ESC 4."
1040 LPRINT CHR$(27);"5";
1050 LPRINT "Standard mode again after ESC 5."
1100 ' Print mode examples of selected sizes/styles
1110 LPRINT
1120 LPRINT "Modes of print varyed by n after ESC '!'"
1125 LPRINT
1130 LPRINT "You enter ESCAPE; '!'; CHR$(n); ...where n = 0 to 63."
1135 DATA 32,40,62,35,47,63,36,52,2,8,24,3,17,4,22
1138 DIM J(15)
1140 FOR I = 1 TO 15: READ J(I): NEXT
1150 LPRINT: LPRINT CHR$(27);"2"	'RESET TO 1/6 INCH LINE SPACING
1160 LPRINT CHR$(27);"D";CHR$(20);	'SEND LEAD-IN CHARS TO FX-80.
1170 FOR I = 1 TO 15
1175 M = J(I)
1180 LPRINT CHR$(27); "!"; CHR$(0);
1190 LPRINT " Mode "; M; CHR$(9);
1200 LPRINT CHR$(27); "!"; CHR$(M);
1210 LPRINT "ABCDEabcde123#$"
1220 NEXT
1300 ' Proportional Spacing Mode
1305 LPRINT:LPRINT
1310 LPRINT "     [Normal Print Mode]"
1320 GOSUB 1400
1330 LPRINT
1340 LPRINT "     [Proportional Print Mode]"
1350 LPRINT CHR$(27);"p";CHR$(1);
1360 GOSUB 1400
1370 LPRINT CHR$(27);"p";CHR$(0)
1380 GOTO 1500
1400 LPRINT "The Earth, our planet, is located at"
1410 LPRINT "an average distance of 93 million miles"
1420 LPRINT "from the sun."
1430 RETURN
1500 STOP:END
