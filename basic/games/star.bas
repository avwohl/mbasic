10 REM
20 REM  STAR  JULY 15.1, 1981
30 REM        this program reads data from star catalog and prints it
40 REM 
50 PRINT
60 PRINT TAB(25);"STAR CATALOG"
70 PRINT
80 INPUT "What is the Yale Bright Star Number of the Star you want Info on";I
90 I=ABS(INT(I))
100 REM
110 REM	HOPEFULLY THE CORRECT DATA DISK IN IN THE CORRECT DRIVE
120 REM
130 IF I<=884 THEN OPEN "I",#1,"STAR1.DAT":GOTO 260
140 IF I<=2059 THEN OPEN "I",#1,"STAR2.DAT":GOTO 260
150 IF I<=3234 THEN OPEN "I",#1,"STAR3.DAT":GOTO 260
160 IF I<=4409 THEN OPEN "I",#1,"STAR4.DAT":GOTO 260
170 IF I<=5584 THEN OPEN "I",#1,"STAR5.DAT":GOTO 260
180 IF I<=6759 THEN OPEN "I",#1,"STAR6.DAT":GOTO 260
190 IF I<=7934 THEN OPEN "I",#1,"STAR7.DAT":GOTO 260
200 IF I<=9110 THEN OPEN "I",#1,"STAR8.DAT":GOTO 260
210 PRINT "invalid star number, try again"
220 GOTO 80
230 REM
240 REM		FIND THE STAR
250 REM
260 INPUT #1,A$
270 A=VAL(LEFT$(A$,4))
280 IF A<>I THEN 260
290 REM
300 REM		PRINT THE DATA
310 REM
320 PRINT "yale Bright Star (BS) Number       = ";LEFT$(A$,4)
330 PRINT "Flamsteed Number                   = ";MID$(A$,5,3)
340 PRINT "Name                               = ";MID$(A$,8,7)
350 PRINT "Sign of Bonner Durchmusterung (BD) = ";MID$(A$,15,1)
360 PRINT "DM Number                          = ";MID$(A$,16,7)
370 PRINT "Henry Draper (HD) Number)          = ";MID$(A$,23,6)
380 PRINT "Boss General Catalog (GC) Number   = ";MID$(A$,29,5)
390 PRINT "Trig. Parallax Catalog Number      = ";MID$(A$,34,4)
400 PRINT "Radial Velocity Catalog Number     = ";MID$(A$,38,6)
410 PRINT "Double Star Catalog                = ";MID$(A$,44,1)
420 PRINT "Double Star Catalog Number         = ";MID$(A$,45,5)
430 PRINT "Multiple Star Componet Index       = ";MID$(A$,50,2)
440 PRINT "Variable Star Cat #    = ";MID$(A$,52,8)
450 PRINT "Right Ascension (1900.0)"
460 PRINT "     Hours             = ";MID$(A$,60,2)
470 PRINT "     Minutes           = ";MID$(A$,62,2)
480 PRINT "     seconds           = ";MID$(A$,64,2)
490 PRINT "     sign of 10 yr ch  = ";MID$(A$,66,1)
500 PRINT "     10 yr change (sec)= ";MID$(A$,67,3)
510 PRINT "Declination (1900.0)"
520 PRINT "     Sign              = ";MID$(A$,70,1)
530 PRINT "     Degrees           = ";MID$(A$,71,2)
540 PRINT "     Minutes           = ";MID$(A$,73,2)
550 PRINT "Galactic Longitude"
560 PRINT "     Degrees           = ";MID$(A$,75,3)
570 PRINT "     Minutes           = ";MID$(A$,78,2)
580 PRINT "Galactic Latitude"
590 PRINT "     Sign              = ";MID$(A$,80,1)
600 PRINT "     Degrees           = ";MID$(A$,81,2)
610 PRINT "     Minutes           = ";MID$(A$,83,2)
620 PRINT "BS-HR Number           = ";MID$(A$,85,4)
630 PRINT "Right Ascension (epoch 2000.0)"
640 PRINT "     Hours             = ";MID$(A$,89,2)
650 PRINT "     Minutes           = ";MID$(A$,91,2)
660 PRINT "     Seconds           = ";MID$(A$,93,2)
670 PRINT "  Change in Right Ascension (epoch 2000.0 - 1900.0)"
680 PRINT "     Sign              = ";MID$(A$,95,1)
690 PRINT "     Minutes           = ";MID$(A$,96,2)
700 PRINT "     Seconds           = ";MID$(A$,98,2)
710 PRINT "Declination (2000.0)"
720 PRINT "     Sign              = ";MID$(A$,100,1)
730 PRINT "     Degrees           = ";MID$(A$,101,2)
740 PRINT "     Minutes           = ";MID$(A$,103,2)
750 PRINT "  Change in Declination (epoch 2000.0 - 1900.0)"
760 PRINT "     Sign              = ";MID$(A$,105,1)
770 PRINT "     Minutes           = ";MID$(A$,106,2)
780 PRINT "Visual Magnitude       = ";MID$(A$,108,2);".";MID$(A$,110,2)
790 PRINT "Source                 = ";MID$(A$,112,2)
800 PRINT "Color                  = ";MID$(A$,114,2);".";MID$(A$,116,2)
810 PRINT "Spectral Class         = ";MID$(A$,118,22)
820 PRINT "Annual Proper Motion in Right Ascension"
830 PRINT "                       = ";MID$(A$,140,2);".";MID$(A$,142,3)
840 PRINT "Annual Proper Motion in Declination"
850 PRINT "                       = ";MID$(A$,145,2);".";MID$(A$,147,3)
860 PRINT "Parallax               = ";MID$(A$,150,1);"0.";MID$(A$,151,3)
870 PRINT "D if Dynamical Parallax= ";MID$(A$,154,1)
880 PRINT "Radial Velocity        = ";MID$(A$,155,6)
890 PRINT "Double Star Data"
900 PRINT "     Magnitude Diff    = ";MID$(A$,161,2);".";MID$(A$,163,1)
910 PRINT "     Maxium Separation = ";MID$(A$,164,3);".";MID$(A$,167,1)
920 PRINT "     # of Componets    = ";MID$(A$,168,1)
930 PRINT "     Remarks           = ";MID$(A$,169,2)
940 PRINT "Data in Radians"
950 PRINT "Right Ascension (1900) = ";MID$(A$,171,8)
960 PRINT "Declination (1900)     = ";MID$(A$,179,8)
970 PRINT "Right Ascension (2000) = ";MID$(A$,187,8)
980 PRINT "Declination (2000)     = ";MID$(A$,195,8)
990 REM
1000 REM	CLOSE THE INPUT FILE, AND SERVICE ANY ADDITIONAL REQUESTS
1010 REM
1020 CLOSE
1030 GOTO 70
1040 END
