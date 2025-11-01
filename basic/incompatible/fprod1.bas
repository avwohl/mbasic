100	'****************************************************************
110	'*      DETERMINES THE SUPURIOUS PRODUCTS FROM 3 SPECIFIED	*
120	'*			FREQUENCIES				*
130	'*								*
140	'*	     FIXED PARAMETER, MULTI CHANNEL VERSION		*
150	'*								*
160	'*	By H. Aicher, from "News from Rhode and Schwarz",	*
170	'*	     ISSN 0028-9108 (1981) No. 94 pp 30-31		*
180	'*								*
190	'*	  Keyed in AND various format modifications by		*
200	'*	  Bill Bolton, Channel 0/28, Sydney, AUSTRALIA		*
210	'*			February 26, 1982			*
220	'****************************************************************
230	'
240	PRINT
250	PRINT
260	PROMPT$="PRODUCTS OF THREE FREQUENCIES"
270	PRINT TAB((79 - (LEN(PROMPT$)))/2);PROMPT$
280	PRINT
290	'
300	' S = Channel spacing
310	' C0= lower channel
320	' I = vision sound spacing
330	Z = 38.9
340	B=8
350	I=5.5
360	C0=2
370	S=7
380	M1 = 3
390	M2 = 3
400	M3 = 2
410	F1 = 48.25
420	'
430	FOR Q = 1 TO 3
440		F3 = F1 + Z
450		PRINT
460		F2 = F1 + I
470		PRINT "CHANNEL ";C0
480		PRINT
490		PRINT "VISION CARRIER = ";F1,
500		PRINT "SOUND CARRIER = ";F2,
510		PRINT "OSC = ";F3
520		PRINT
530		'
540		'Display the column headings
550		'
560		PRINT
570		PRINT
580		PRINT "N1"; TAB(5);"N2"; TAB(9);"N3"; TAB(14);"N1*F1";
590		PRINT TAB(26);"N2*F2"; TAB(38);"N3*F3";
600		PRINT TAB(51);"DIFFERENCE"; TAB(64);"PRODUCT"
610		PRINT
620		'
630		'The condition for a spurious product falling within
640		'within the IF region with a sideband of BW is:
650		'     || +- N1*F1 +- N2*F2 | - IF | <= BW
660		'Calculate the column enteries and display them
670		'
680		FOR N1 = 0 TO M1
690			FOR N2 = 0 TO M2
700				FOR N3 = 0 TO M3
710				'
720				'Calculate multiples of individual frequencies
730				'
740				V2 = N2 * F2
750				V3 = N3 * F3
760				'
770				V1 = N1 * F1
780				'
790				'Calculate sum frequencies
800				'
810				S1 = V1 + V2
820				S2 = V1 + V3
830				S3 = V2 + V3
840				S4 = V1 + V2 + V3
850				'
860				'Calculate difference frequencies
870				'
880				D1 = V1 - V2
890				E2 = V2 - V1
900				D2 = V1 - V3
910				E2 = V3 - V1
920				D3 = V2 - V3
930				E3 = V3 - V2
940				D4 = S1 - V3
950				E4 = V3 - S1
960				D5 = S2 - V2
970				E5 = V2 - S2
980				D6 = S3 - V1
990				E6 = V1 - S3
1000				'
1010				'Check if product within bandwidth
1020				'
1030				IF V1 = 0 OR N2 > 0 OR N3 > 0 THEN
					1110
1040				D = V1 - Z
1050				IF ABS(D) > B THEN
					1110
1060				PRINT N1;TAB(5);" .";TAB(9);" .";TAB(13);V1
1070				PRINT TAB(25);" ."; TAB(38);" ."; TAB(51);D; TAB(64);"V1";
1080				'
1090				'**************************************************
1100				'
1110				IF V2 = 0 OR N1 > 0 OR N3 > 0 THEN
					1190
1120				D2 = V2 - Z
1130				IF ABS(D) > B THEN
					1190
1140				PRINT " .";TAB(5);N2;TAB(9);" .";TAB(13);" .";
1150				PRINT TAB(25);V2;TAB(38);" .";TAB(51);D;TAB(64);"V2"
1160				'
1170				'***************************************************
1180				'
1190				IF V3 = 0 OR N1 > 0 OR N2 > 0 THEN
					1270
1200				D = V3 - Z
1210				IF ABS(D)>B THEN
					1270
1220				PRINT " ";TAB(5);" .";TAB(9);N3;TAB(13);" .";
1230				PRINT TAB(25);" .";TAB(38);V3;TAB(51);D;TAB(64);"V3"
1240				'
1250				'***************************************************
1260				'
1270				IF V1 = 0 OR V2 = 0 OR N3 > 0 THEN
					1350
1280				D = S1 - Z
1290				IF ABS(D)>B THEN
					1350
1300		 		GOSUB 3000
1310				PRINT TAB(64);"V1+V2"
1320				'
1330				'***************************************************
1340				'
1350				IF V1 = 0 OR V3 = 0 OR N2 > 0 THEN
					1430
1360				D = S2 - Z
1370				IF ABS(D)>B THEN
					1430
1380				GOSUB 3040
1390				PRINT TAB(64);"V1+V3"
1400				'
1410				'***************************************************
1420				'
1430				IF V2 = 0 OR V3 = 0 OR N1 > 0 THEN
					1510
1440		 		D = S3 - Z
1450				IF ABS(D)>B THEN
					1510
1460				GOSUB 3080
1470				PRINT TAB(64);"V2+V3"
1480				'
1490				'***************************************************
1500				'
1510				IF V1 = 0 OR V2 = 0 OR V3 = 0 THEN
					1590
1520				D = S4 - Z
1530				IF ABS(D)>B THEN
					1590
1540				GOSUB 3120
1550				PRINT TAB(64);"V1+V2+V3"
1560				'
1570				'***************************************************
1580				'
1590				IF V1 = 0 OR V2 = 0 OR N3 > 0 THEN
					1710
1600				D = D1 - Z
1610				IF ABS(D)>B THEN
					1640
1620				GOSUB 3000
1630				PRINT TAB(64);"V1-V2"
1640				D = E1 -Z
1650				IF ABS(D)>B THEN
					1710
1660				GOSUB 3000
1670				PRINT TAB(64);"V2-V1"
1680				'
1690				'***************************************************
1700				'
1710				IF V1 = 0 OR V3 = 0 OR N2 > 0 THEN
					1830
1720				D = D2 - Z
1730				IF ABS(D)>B THEN
					1760
1740				GOSUB 3040
1750				PRINT TAB(64);"V1-V3"
1760				D = E2 - Z
1770				IF ABS(D)>B THEN
					1830
1780				GOSUB 3040
1790				PRINT TAB(64);"V3-V1"
1800				'
1810				'*************************************************
1820				'
1830				IF V2 = 0 OR V3 = 0 OR N1 > 0 THEN
					1980
1840				D = D3 - Z
1850				IF ABS(D)>B THEN
					1910
1860				GOSUB 3080
1870				PRINT TAB(64);"V2-V3"
1880				'
1890				'************************************************
1900				'
1910				D = E3 - Z
1920				IF ABS(D)>B THEN
					1980
1930				GOSUB 3080
1940				PRINT TAB(64);"V3-V2"
1950				'
1960				'************************************************
1970				'
1980				IF V1 = 0 OR V2 = 0 OR V3 = 0 THEN
					2370
1990				D = D4 - Z
2000				IF ABS(D)>B THEN
					2060
2010				GOSUB 3120
2020				PRINT TAB(64);"V1+V2+V3"
2030				'
2040				'***********************************************
2050				'
2060				D = E4 - Z
2070				IF ABS(D)>B THEN
					2130
2080				GOSUB 3120
2090				PRINT TAB(64);"V3-(V1+V2)"
2100				'
2110				'***********************************************
2120				'
2130				D = D5 - Z
2140				IF ABS(D)>B THEN
					2190
2150				GOSUB 3120
2160				PRINT TAB(64);"V1+V3-V2"
2170				'
2180				'***********************************************
2190				D = E5 - Z
2200				IF ABS(D)>B THEN
					2260
2210				GOSUB 3120
2220				PRINT TAB(64);"V2-(V1+V3)"
2230				'
2240				'**********************************************
2250				'
2260				D = D6 - Z
2270				IF ABS(D)>B THEN
					2330
2280				GOSUB 3120
2290				PRINT TAB(64);"V2+V3-V1"
2300				'
2310				'*********************************************
2320				'
2330				D = E6 - Z
2340				IF ABS(D)>B THEN
					2370
2350				GOSUB 3120
2360				PRINT TAB(64);"V1-(V2+V3)"
2370				NEXT N3
2380			NEXT N2
2390		NEXT N1
2400		'
2410		PRINT
2420		C0=C0+1:F1=F1+S
2430	NEXT Q
2440	PRINT
2450	END
2460		'
2470		'
3000	PRINT N1;TAB(5);N2;TAB(9);" .";TAB(13);V1;
3010	PRINT TAB(25);V2;TAB(38);" .";TAB(51);D;
3020	RETURN
3030	'
3040	PRINT N1;TAB(5);" .";TAB(9);N3;TAB(13);V1;
3050	PRINT TAB(25);" .";TAB(38);V3;TAB(51);D;
3060	RETURN
3070	'
3080	PRINT " .";TAB(5);N2;TAB(9);N3;TAB(13);" .";
3090	PRINT TAB(25);V2;TAB(38);V3;TAB(51);D;
3100	RETURN
3110	'
3120	PRINT N1;TAB(5);N2;TAB(9);N3;TAB(13);V1;
3130	PRINT TAB(25);V2;TAB(38);V3;TAB(51);D;
3140	RETURN
