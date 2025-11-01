100 REM UNPRO2.BAS
110 REM
120 REM This program is designed to protect or unprotect file
130 REM saved under MBASIC 5.21 (and likely other versions).
140 REM
150 REM By Jim McClanahan W4JBM, September 2020
160 REM
170 REM Thanks to Martin from the Google comp.os.cpm group as well as
180 REM to R. van den Assem and W.J. van Elk for the 1986 article
190 REM "A Chosen-Plaintext Attack on the MBASIC Protection".
200 REM
210 REM This program will ONLY work when compiled with BASCOM.
220 REM Commands to save and build:
230 REM in MBASIC...
240 REM   SAVE "UNPRO2.BAS",A
250 REM   SYSTEM
260 REM from CP/M prompt...
270 REM   BASCOM =UNPRO2/N/E
280 REM   L80 UNPRO2,UNPRO2/N/E
290 REM
300 REM Create and load SIN and ATN constants array...
310 DIM SN%(15),AN%(15)
320 FOR I%=0 TO 15:READ SN%(I%):NEXT
330 FOR I%=0 TO 15:READ AN%(I%):NEXT
340 REM
350 REM Load argument (filename) from the command line...
360 L%=PEEK(128)
370 IF L%<2 THEN GOTO 1170:REM Print Help
380 P%=0:REM Flag for if we hit period in name
390 FOR I%=2 TO L%
400 C%=PEEK(128+I%)
410 FI$=FI$+CHR$(C%)
420 IF C%=46 THEN P%=-1
430 IF P% THEN GOTO 460
440 FO$=FO$+CHR$(C%)
450 FB$=FB$+CHR$(C%)
460 NEXT I%
470 FO$=FO$+".$$$"
480 FB$=FB$+".BAK"
490 REM
500 REM At this point hopefully we have:
510 REM FI$ - Input file name, filename.BAS
520 REM FO$ - Temporary output file name, filename.$$$
530 REM FB$ - The name we will backup the original file to,
540 REM       filename.BAK
550 REM
560 REM No error checking yet because we will overwrite the
570 REM temporary file, even if it already exists.
580 REM
590 OPEN "R",#3,FO$,1
600 FIELD  #3,1 AS U$
610 REM
620 REM We turn on error checking before opening input file
630 REM because if it doesn't exist we will issue a "file
640 REM not found" error.
650 REM
660 ON ERROR GOTO 1160
670 OPEN "R",#2,FI$,1
680 ON ERROR GOTO 0
690 FIELD #2,1 AS I$
700 REM Find out what kind of file (if any) we have...
710 GET #2
720 A1%=ASC(I$)
730 IF A1%<254 THEN 1270 : REM Tolkenized BASIC should start with either
740 REM                       $FE OR $FF.
750 REM Look at first by to determine whether we Encrypt or Decrypt
760 IF A1%=254 THEN Z%=0 ELSE Z%=1
770 IF Z%=0 THEN PRINT "Decrypting file ";FI$;"...":LSET U$=CHR$(255)
780 IF Z%=1 THEN PRINT "Encrypting file ";FI$;"...":LSET U$=CHR$(254)
790 PUT #3
800 REM
810 REM Get ready for main loop...
820 A%=13:B%=11:REM Initialized indexes for main loop
830 Z0%=0:REM We use this to watch for the three zeros marking the EOF
840 REM
850 REM And now for the main loop...
860 WHILE Z0%<3
870 GET #2
880 X%=ASC(I$)
890 IF Z%=1 THEN 950
900 H%=(X%-B%+256) MOD 256
910 H%=H% XOR (SN%(A%) XOR AN%(B%))
920 H%=(H%+A%) MOD 256
930 IF H%=0 THEN Z0%=Z0%+1 ELSE Z0%=0
940 GOTO 990
950 H%=(X%-A%+256) MOD 256
960 H%=H% XOR (SN%(A%) XOR AN%(B%))
970 H%=(H%+B%) MOD 256
980 IF X%=0 THEN Z0%=Z0%+1 ELSE Z0%=0
990 LSET U$=CHR$(H%)
1000 PUT #3
1010 A%=A%-1:IF A%=0 THEN A%=13
1020 B%=B%-1:IF B%=0 THEN B%=11
1030 WEND
1040 REM
1050 REM We need to rename things...
1060 CLOSE
1070 REM
1080 REM Delete old backup file if it exists...
1090 ON ERROR GOTO 1110
1100 KILL FB$
1110 RESUME 1120
1120 NAME FI$ AS FB$
1130 NAME FO$ AS FI$
1140 GOTO 1300
1150 REM
1160 REM Jump here if no arguments are passed...
1170 PRINT "UNPRO2.COM by Jim McClanahan W4JBM (2020)"
1180 PRINT "Unprotect or Protect a tolkenized MBASIC file."
1190 PRINT "Usage: UNPRO2 filename.bas"
1200 GOTO 1300
1210 REM
1220 REM Jump here if input file does not exist...
1230 PRINT "File does not exist!"
1240 GOTO 1300
1250 REM
1260 REM First byte of file wasn't an $FE or $FF...
1270 PRINT "Input File Error (no such file or unknown file type)..."
1280 REM
1290 REM We will close files, delete temporary files, and end...
1300 CLOSE:END
1310 REM
1320 REM SINCON Table
1330 DATA 5,251,215,30,134,101,38,153,135,88,52,35,135,225,93,165
1340 REM ATNCON Table
1350 DATA 9,74,215,59,120,2,110,132,123,254,193,47,124,116,49,154
1360 REM (we really only need positions 1 thru 13 and 1 thru 11,
1370 REM but I snagged a few more...)
