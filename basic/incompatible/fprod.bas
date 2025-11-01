100	'****************************************************************
110	'*      DETERMINES THE SUPURIOUS PRODUCTS FROM 3 SPECIFIED	*
120	'*			FREQUENCIES				*
130	'*								*
140	'*	By H. Aicher, from "News from Rhode and Schwarz",	*
150	'*	     ISSN 0028-9108 (1981) No. 94 pp 30-31		*
160	'*								*
170	'*	  Keyed in AND various format modifications by		*
180	'*	  Bill Bolton, Channel 0/28, Sydney, AUSTRALIA		*
190	'*			February 26, 1982			*
200	'****************************************************************
210	'
220	PRINT
230	PRINT
240	PROMPT$="PRODUCT OF THREE FREQUENCIES"
250	PRINT TAB((79-(LEN(PROMPT$)))/2);PROMPT$
260	'
270	PRINT
280	PROMPT$ = "Enter IF and BANDWIDTH :"
290	PRINT PROMPT$
300	PRINT
310	OFFSET = LEN(PROMPT$) + 3
320	PRINT TAB(OFFSET);"IF Frequency = ";
330	INPUT "",Z
340	PRINT TAB(OFFSET);"Bandwidth    = ";
350	INPUT "",B
360	PRINT
370	PRINT "Enter the INPUT FREQUENCIES and MAX. ORDER numbers :"
380	PRINT
390	PRINT TAB(OFFSET);"Frequency  1 = ";
400	INPUT "",F1
410	PRINT TAB(OFFSET);"Max. order 1 = ";
420	INPUT "",M1
430	PRINT
440	PRINT TAB(OFFSET);"Frequency  2 = ";
450	INPUT "",F2
460	PRINT TAB(OFFSET);"Max. order 2 = ";
470	INPUT "",M2
480	PRINT
490	PRINT TAB(OFFSET);"Frequency  3 = ";
500	INPUT "",F3
510	PRINT TAB(OFFSET);"Max. order 3 = ";
520	INPUT "",M3
530	'
540	'Display the entered values
550	'
560	PRINT
570	PRINT
580	PRINT "F1 = ";F1,"F2 = ";F2,"F3 = ";F3
590	PRINT "IF = ";Z,"BW = ";B
600	'
610	'Display the column headings
620	'
630	PRINT
640	PRINT
650	PRINT "N1"; TAB(5);"N2"; TAB(9);"N3"; TAB(14);"N1*F1";
660	PRINT TAB(26);"N2*F2"; TAB(38);"N3*F3";
670	PRINT TAB(51);"DIFFERENCE"; TAB(64);"PRODUCT"
680	PRINT
690	'
700	'The condition for a spurious product falling
710	'within the IF region with a sideband of BW is:
720	'     || +- N1*F1 +- N2*F2 | - IF | <= BW
730	'
740	'Calculate the column enteries and display them
750	'
760	FOR N1 = 0 TO M1
770		FOR N2 = 0 TO M2
780			FOR N3 = 0 TO M3
790			'
800			'Calculate multiples of individual frequencies
810			'
820			V1 = N1 * F1
830			V2 = N2 * F2
840			V3 = N3 * F3
850			'
860			'Calculate sum frequencies
870			'
880			S1 = V1 + V2
890			S2 = V1 + V3
900			S3 = V2 + V3
910			S4 = V1 + V2 + V3
920			'
930			'Calculate difference frequencies
940			'
950			D1 = V1 - V2
960			E1 = V2 - V1
970			D2 = V1 - V3
980			E2 = V3 - V1
990			D3 = V2 - V3
1000			E3 = V3 - V2
1010			D4 = S1 - V3
1020			E4 = V3 - S1
1030			D5 = S2 - V2
1040			E5 = V2 - S2
1050			D6 = S3 - V1
1060			E6 = V1 - S3
1070			'
1080			'Check if product within bandwidth
1090			'
1100			IF V1 = 0 OR N2 > 0 OR N3 > 0 THEN
				1180
1110			D = V1 - Z
1120			IF ABS(D) > B THEN
				1180
1130			PRINT N1;TAB(5);" .";TAB(9);" .";TAB(13);V1
1140			PRINT TAB(25);" ."; TAB(38);" ."; TAB(51);D; TAB(64);"V1";
1150			'
1160			'**************************************************
1170			'
1180			IF V2 = 0 OR N1 > 0 OR N3 > 0 THEN
				1260
1190			D2 = V2 - Z
1200			IF ABS(D) > B THEN
				1260
1210			PRINT " .";TAB(5);N2;TAB(9);" .";TAB(13);" .";
1220			PRINT TAB(25);V2;TAB(38);" .";TAB(51);D;TAB(64);"V2"
1230			'
1240			'***************************************************
1250			'
1260			IF V3 = 0 OR N1 > 0 OR N2 > 0 THEN
				1340
1270			D = V3 - Z
1280			IF ABS(D)>B THEN
				1340
1290			PRINT " ";TAB(5);" .";TAB(9);N3;TAB(13);" .";
1300			PRINT TAB(25);" .";TAB(38);V3;TAB(51);D;TAB(64);"V3"
1310			'
1320			'***************************************************
1330			'
1340			IF V1 = 0 OR V2 = 0 OR N3 > 0 THEN
				1420
1350			D = S1 - Z
1360			IF ABS(D)>B THEN
				1420
1370	 		GOSUB 3000
1380			PRINT TAB(64);"V1+V2"
1390			'
1400			'***************************************************
1410			'
1420			IF V1 = 0 OR V3 = 0 OR N2 > 0 THEN
				1500
1430			D = S2 - Z
1440			IF ABS(D)>B THEN
				1500
1450			GOSUB 3040
1460			PRINT TAB(64);"V1+V3"
1470			'
1480			'***************************************************
1490			'
1500			IF V2 = 0 OR V3 = 0 OR N1 > 0 THEN
				1580
1510	 		D = S3 - Z
1520			IF ABS(D)>B THEN
				1580
1530			GOSUB 3080
1540			PRINT TAB(64);"V2+V3"
1550			'
1560			'***************************************************
1570			'
1580			IF V1 = 0 OR V2 = 0 OR V3 = 0 THEN
				1660
1590			D = S4 - Z
1600			IF ABS(D)>B THEN
				1660
1610			GOSUB 3120
1620			PRINT TAB(64);"V1+V2+V3"
1630			'
1640			'***************************************************
1650			'
1660			IF V1 = 0 OR V2 = 0 OR N3 > 0 THEN
				1780
1670			D = D1 - Z
1680			IF ABS(D)>B THEN
				1710
1690			GOSUB 3000
1700			PRINT TAB(64);"V1-V2"
1710			D = E1 -Z
1720			IF ABS(D)>B THEN
				1780
1730			GOSUB 3000
1740			PRINT TAB(64);"V2-V1"
1750			'
1760			'***************************************************
1770			'
1780			IF V1 = 0 OR V3 = 0 OR N2 > 0 THEN
				1900
1790			D = D2 - Z
1800			IF ABS(D)>B THEN
				1830
1810			GOSUB 3040
1820			PRINT TAB(64);"V1-V3"
1830			D = E2 - Z
1840			IF ABS(D)>B THEN
				1900
1850			GOSUB 3040
1860			PRINT TAB(64);"V3-V1"
1870			'
1880			'*************************************************
1890			'
1900			IF V2 = 0 OR V3 = 0 OR N1 > 0 THEN
				2050
1910			D = D3 - Z
1920			IF ABS(D)>B THEN
				1980
1930			GOSUB 3080
1940			PRINT TAB(64);"V2-V3"
1950			'
1960			'************************************************
1970			'
1980			D = E3 - Z
1990			IF ABS(D)>B THEN
				2050
2000			GOSUB 3080
2010			PRINT TAB(64);"V3-V2"
2020			'
2030			'************************************************
2040			'
2050			IF V1 = 0 OR V2 = 0 OR V3 = 0 THEN
				2440
2060			D = D4 - Z
2070			IF ABS(D)>B THEN
				2130
2080			GOSUB 3120
2090			PRINT TAB(64);"V1+V2+V3"
2100			'
2110			'***********************************************
2120			'
2130			D = E4 - Z
2140			IF ABS(D)>B THEN
				2200
2150			GOSUB 3120
2160			PRINT TAB(64);"V3-(V1+V2)"
2170			'
2180			'***********************************************
2190			'
2200			D = D5 - Z
2210			IF ABS(D)>B THEN
				2260
2220			GOSUB 3120
2230			PRINT TAB(64);"V1+V3-V2"
2240			'
2250			'***********************************************
2260			D = E5 - Z
2270			IF ABS(D)>B THEN
				2330
2280			GOSUB 3120
2290			PRINT TAB(64);"V2-(V1+V3)"
2300			'
2310			'**********************************************
2320			'
2330			D = D6 - Z
2340			IF ABS(D)>B THEN
				2400
2350			GOSUB 3120
2360			PRINT TAB(64);"V2+V3-V1"
2370			'
2380			'*********************************************
2390			'
2400			D = E6 - Z
2410			IF ABS(D)>B THEN
				2440
2420			GOSUB 3120
2430			PRINT TAB(64);"V1-(V2+V3)"
2440			NEXT N3
2450		NEXT N2
2460	NEXT N1
2470	'
2480	PRINT
2490	PRINT "V1 TO V3 ARE MULTIPLES OF INDIVIDUAL FREQUENCIES!"
2500	PRINT
2510	PRINT
2520	END
2530	'
2540	'
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
