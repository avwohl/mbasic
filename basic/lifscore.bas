100 DIM D(114)
110 DATA 54,55,56,57,58,59,61,62,64,65,67,68,70,71,73,74,76,77,79
120 DATA 58,59,60,62,63,65,66,67,69,70,71,73,75,77,78,80,82,84,86
130 DATA 63,65,66,68,69,70,72,73,75,76,78,79,81,83,85,86,88,90,92
140 DATA 45,46,47,48,49,50,51,52,53,55,56,58,59,61,62,64,65,67,68
150 DATA 49,50,51,52,53,54,55,57,58,60,61,63,64,66,67,69,70,72,73
160 DATA 54,55,56,57,58,59,61,62,63,65,66,68,69,71,72,74,76,78,79
400 LET Y=25
410 GOSUB 9900
420 PRINT "             *****  WARNING  *****"
430 PRINT " Lifescore is for adults who do not have a chronic disease"
440 PRINT " or major disability, and have never had a heart attack or stroke"
450 PRINT "If you already have one of these problems, Lifescore cannot apply"
460 PRINT " to you and you should be seeing your doctor regularly"
470 LET Y=8
480 GOSUB 9900
490 PRINT
500 PRINT "       Press RETURN when ready to continue"
510 INPUT "",Y$
520 LET Y=25
530 GOSUB 9900
540 PRINT "            HI!  THIS IS YOUR LIFESCORE"
550 LET Y=10
560 GOSUB 9900
570 INPUT "Are you male or female  (M/F)",G$
580 PRINT
590 IF G$="M"THEN 610
600 IF G$<>"F"THEN 570
610 PRINT
620 INPUT "What is your name",N$
630 PRINT
640 PRINT "How old are you ";N$
650 INPUT"",A               
660 IF A>17 THEN 690
670 PRINT "SORRY ";N$;" YOU ARE TOO YOUNG FOR THIS TEST"
680 GOTO 9990
690 IF A<25 THEN 710
700 GOTO 730
710 IF G$="F" THEN 730
720 GOTO 670
730 PRINT
740 IF G$="M" THEN 800
750 INPUT "What is your weight (in Kilograms) in indoor clothing",W
760 IF W<42 THEN 750
770 IF W>79 THEN 750
780 GOTO 820
790 INPUT "What is your weight (in Kilograms) in indoor clothing",W
800 IF W<50 THEN 790
810 IF W>92 THEN 790
820 PRINT
830 IF G$="M" THEN 880
840 INPUT "What is your height in shoes with 5cm heels (in cms)",H
850 IF H<148 THEN 840
860 IF H>184 THEN 840
870 GOTO 905
880 INPUT "What is your height in shoes with 3cm heels (in cms)",H
890 IF H<158 THEN 880
900 IF H>194 THEN 880
905 PRINT
906 H=INT(H)
907 I=H-148
908 FOR Z=0 TO 46 STEP 2
909 J=I-Z
910 IF J=0 THEN 920
911 IF J<0 THEN 918
912 NEXT Z
918 H=H+1
920 INPUT "Is your frame size small, medium or large (S/M/L)",F$
930 IF F$="S" THEN 962
940 IF F$="M" THEN 962
950 IF F$="L" THEN 962
960 GOTO 920
962 LET Y=25
964 GOSUB 9900
966 PRINT "             ** I'm thinking **"
968 LET Y=10
969 GOSUB 9900
970 PRINT
1100 FOR Z=1 TO 114
1110 READ D(Z)
1120 NEXT Z
1121 LET L=0
1200 LET X=1
1205 IF G$="F" THEN 1400
1210 FOR Z=158 TO 194 STEP 2
1220 IF H=Z THEN 1300
1230 X=X+1
1240 NEXT Z
1245 STOP
1300 IF F$="S" THEN X=X+0
1310 IF F$="M" THEN X=X+19
1320 IF F$="L" THEN X=X+38
1330 C=D(X)
1340 GOTO 1500
1400 FOR Z=148 TO 184 STEP 2
1410 IF H=Z THEN 1440
1420 X=X+1
1430 NEXT Z
1440 IF F$="S" THEN X=X+57
1450 IF F$="M" THEN X=X+76
1460 IF F$="L" THEN X=X+95
1470 IF A<25 THEN C=.5*(A-18)
1480 C=D(X)-C
1500 C=W-C
1510 IF C<2.5 THEN 1900
1520 IF C<6.5 THEN 1700
1530 IF C<11 THEN 1720
1540 IF C<15.5 THEN 1740
1541 IF C<20.5 THEN 1760
1550 GOTO 1780
1700 L=L-2
1710 GOTO 1900
1720 L=L-6
1730 GOTO 1900
1740 L=L-10
1750 GOTO 1900
1760 L=L-12
1770 GOTO 1900
1780 L=L-15
1900 LET C=0
1910 LET Y=25
1920 GOSUB 9900
2000 PRINT "                       EXERCISE"
2010 PRINT " Count the minutes per week you engage in conditioning"
2020 PRINT " exercise in which your heart rate (pulse) is raised to"
2030 PRINT " 120 beats per minute or more. Exercise sessions should"
2040 PRINT " last at least 15 minutes at the 120 beat level."
2050 PRINT " Exercise that usually does not produce conditioning"
2060 PRINT " include bowling, golf and slow tennis. Conditioning"
2070 PRINT " exercise usually does come from brisk walking,squash"
2080 PRINT " fast tennis, jogging and other vigorous activities."
2090 PRINT
2100 INPUT " How many minutes of conditioning would you do each week",E
2110 IF E<15 THEN 2300
2120 IF E<30 THEN 2320
2130 IF E<45 THEN 2340
2140 IF E<75 THEN 2360
2150 IF E<120 THEN 2380
2160 IF E<180 THEN 2400
2170 IF E<500 THEN 2420
2180 PRINT
2190 PRINT "     WOW!  You must be FIT"
2200 GOTO 2420
2300 C=C+0
2310 GOTO 2480
2320 C=C+2
2330 GOTO 2480
2340 C=C+6
2350 GOTO 2480
2360 C=C+12
2370 GOTO 2480
2380 C=C+16
2390 GOTO 2480
2400 C=C+20
2410 GOTO 2480
2420 C=C+24
2430 GOTO 2480
2480 E1=C
2500 LET Y=25
2510 GOSUB 9900
2520 D=0
2530 PRINT "                            DIET"
2540 PRINT " Do you eat a balanced diet-one that includes vegetables,"
2550 PRINT "fruits,breads and cereals, protein foods and "
2560 INPUT "    dairy products  (Y/N)",D$
2570 IF D$="N" THEN 2590
2580 D=D+4
2590 PRINT " Do you avoid saturated fats and cholesterol, mostly found"
2600 INPUT " in animal fats (Y/N)",D$
2610 IF D$="N" THEN 2700
2620 D=D+2
2700 LET Y=25
2710 GOSUB 9900
2715 LET T=0
2720 LET C=0
2730 PRINT "                             SMOKING"
2740 INPUT "Do you smoke at all (Y,N) ",T$
2750 IF T$="N" THEN 3000
2760 INPUT " Do you smoke only a pipe (Y/N) ",U$
2770 IF U$="N" THEN 2800
2780 L=L-4
2790 GOTO 3000
2800 PRINT
2810 PRINT "  One cigar is equivalent to one cigarette. "
2820 PRINT
2830 INPUT "  How many cigarettes do you smoke each day ",T
2840 IF T=0 THEN 2740
2850 IF T<9 THEN 2900
2852 IF T<19 THEN 2910
2854 IF T<29 THEN 2920
2856 IF T<39 THEN 2930
2858 IF T<49 THEN 2940
2860 IF T>49 THEN 2950
2900 LET T=-13
2905 GOTO 2980
2910 LET T=-15
2915 GOTO 2980
2920 LET T=-17
2925 GOTO 2980
2930 LET T=-20
2935 GOTO 2980
2940 LET T=-24
2945 GOTO 2980
2950 LET T=-28
2955 GOTO 2980
2980 IF G$="M" THEN 3000
2982 INPUT " Do you take birth control pills (Y/N)",U$
2984 IF U$="N" THEN 3000
2986 T=T-7
3000 LET Y=25
3010 GOSUB 9900
3020 LET C=0
3030 PRINT "                           ALCOHOL"
3040 PRINT
3050 PRINT " Calculate the number of alcoholic beverages you drink each"
3060 PRINT " day. If your drinks are large, allow extra. "
3070 PRINT "What would be your average daily number of mixed dirnks, "
3080 INPUT " beers or glasses of wine",G
3090 IF G=0 GOTO 3300
3100 IF G<3 GOTO 3320
3110 IF G<5 GOTO 3340
3120 IF G<7 GOTO 3360
3130 IF G<10 GOTO 3380
3140 IF G>=10 GOTO 3400
3300 LET G1=0
3310 GOTO 3500
3320 LET G1=1
3330 GOTO 3500
3340 LET G1=-4
3350 GOTO 3500
3360 LET G1=-12
3370 GOTO 3500
3380 LET G1=-20
3390 GOTO 3500
3400 LET G1=-30
3410 GOTO 3500
3500 LET Y=25
3510 GOSUB 9900
3520 PRINT "                        CAR ACCIDENTS"
3530 PRINT
3540 PRINT " The car is the No.1 cause of accidental death, and seat belts"
3550 PRINT " save about 50% of car accident victims. Some people think"
3560 PRINT " they wear them more than they actually wear seat belts. "
3561 PRINT
3570 INPUT " Honestly, what percentage of the time do you wear them",P
3580 IF P<25 THEN 3700
3590 IF P<40 THEN 3720
3600 IF P<60 THEN 3740
3610 IF P<80 THEN 3760
3620 IF P<101 THEN 3780
3630 IF P>100 THEN 3561
3700 LET P1=0
3710 GOTO 4000
3720 LET P1=2
3730 GOTO 4000
3740 LET P1=4
3750 GOTO 4000
3760 LET P1=6
3770 GOTO 4000
3780 LET P1=8
3790 GOTO 4000
4000 LET Y=25
4010 GOSUB 9900
4011 LET C=0
4020 PRINT "                             STRESS"
4030 PRINT " One way of measuring your stress level is to look at the"
4040 PRINT " changes in your life. "
4050 PRINT
4060 PRINT " Answer Y or N to the following questions  about events that"
4070 PRINT " have happened to you in the past year."
4080 PRINT
4090 INPUT "Death of spouse",H$
4100 IF H$="Y" THEN C=C+100
4110 INPUT "Divorce",H$
4120 IF H$="Y" THEN C=C+73
4130 INPUT " Marital Seperation",H$
4140 IF H$="Y" THEN C=C+65
4150 INPUT "Jail term",H$
4160 IF H$="Y" THEN C=C+63
4170 INPUT "Death of close family member",H$
4180 IF H$="Y" THEN C=C+63
4190 INPUT "Personal injury or illness",H$
4200 IF H$="Y" THEN C=C+53
4210 INPUT "Marriage",H$
4220 IF H$="Y" THEN C=C+50
4230 INPUT "Fired at work",H$
4240 IF H$="Y" THEN C=C+47
4250 INPUT "Marital reconcillation",H$
4260 IF H$="Y" THEN C=C+45
4270 INPUT "Retirement",H$
4280 IF H$="Y" THEN C=C+45
4290 INPUT "Change in health of family member ",H$
4300 IF H$="Y" THEN C=C+44
4305 IF G$="M" THEN 4330
4310 INPUT " Pregnancy",H$
4320 IF H$="Y" THEN C=C+40
4330 INPUT "Sex difficulties",H$
4340 IF H$="Y" THEN C=C+39
4350 INPUT "Gain of a new family member",H$
4360 IF H$="Y" THEN C=C+39
4370 INPUT "Business readjustment",H$
4380 IF H$="Y" THEN C=C+39
4390 INPUT "Change in financial status",H$
4400 IF H$="Y" THEN C=C+38
4410 INPUT "Death of a close friend",H$
4420 IF H$="Y" THEN C=C+37
4430 INPUT "Change to a different kind of work",H$
4440 IF H$="Y" THEN C=C+36
4450 INPUT "Change in number of arguments with spouse",H$
4460 IF H$="Y" THEN C=C+350
4470 INPUT "Large mortgage",H$
4480 IF H$="Y" THEN C=C+31
4490 INPUT " Foreclosure of mortgage or loan",H$
4500 IF H$="Y" THEN C=C+30
4510 INPUT "Change in responsibilities at work",H$
4520 IF H$="Y" THEN C=C+29
4530 INPUT "Son or daughter leaving home",H$
4540 IF H$="Y" THEN C=C+29
4550 INPUT "Trouble with inlaws",H$
4560 IF H$="Y" THEN C=C+29
4570 INPUT "Outstanding personal achievement",H$
4580 IF H$="Y" THEN C=C+28
4590 INPUT "Spouse begin or stop work",H$
4600 IF H$="Y" THEN C=C+26
4610 INPUT "Begin or end school",H$
4620 IF H$="Y" THEN C=C+26
4630 INPUT "Change in living conditions",H$
4640 IF H$="Y" THEN C=C+25
4650 INPUT "Change in personal habits ",H$
4660 IF H$="Y" THEN C=C+24
4670 INPUT " Trouble with boss",H$
4680 IF H$="Y" THEN C=C+23
4690 INPUT "Change in work hours or conditions",H$
4700 IF H$="Y" THEN C=C+20
4710 INPUT "Change in residence",H$
4720 IF H$="Y" THEN C=C+20
4730 INPUT "Change in schools",H$
4740 IF H$="Y" THEN C=C+20
4750 INPUT "Change in recreation",H$
4760 IF H$="Y" THEN C=C+19
4770 INPUT "Change in social activities",H$
4780 IF H$="Y" THEN C=C+18
4790 INPUT "Small mortgage or loan",H$
4800 IF H$="Y" THEN C=C+17
4810 INPUT "Change in sleeping habits",H$
4820 IF H$="Y" THEN C=C+16
4830 INPUT "Change in number of family get-togethers",H$
4840 IF H$="Y" THEN C=C+15
4850 INPUT "Change in eating habits",H$
4860 IF H$="Y" THEN C=C+15
4870 INPUT "Take a holiday",H$
4880 IF H$="Y" THEN C=C+13
4890 INPUT "Celebrate Christmas",H$
4900 IF H$="Y" THEN C=C+12
4910 INPUT "Minor violation of the law",H$
4920 IF H$="Y" THEN C=C+11
4930 IF C<150 THEN  4970
4940 IF C<250 THEN  4975
4950 IF C<300 THEN  4980
4960 IF C>=300 THEN 4985
4970 LET S=0
4971 GOTO 5000
4975 LET S=-4
4976 GOTO 5000
4980 LET S=-7
4981 GOTO 5000
4985 LET S=-10
5000 F=0
5010 Y=25
5020 GOSUB 9900
5030 PRINT "                   PERSONAL HISTORY"
5040 PRINT
5050 PRINT
5060 PRINT
5070 PRINT " Have you been in close contact for a year or more with "
5080 INPUT " someone with tuberculosis",H$
5090 IF H$="Y" THEN LET F=F-4
5100 PRINT "Have you had X-ray treatment of tonsils,adenoids,acne or"
5110 INPUT " ringworm of the scalp",H$
5120 IF H$="Y" THEN LET F=F-6
5130 INPUT "Do you work regularly with asbestos",H$
5140 IF H$="N" THEN 5200
5150 IF T$="Y" THEN F=F-10
5160 IF T$="N" THEN F=F-2
5200 INPUT " Do you work regularly with vinyl chloride",H$
5210 IF H$="N" THEN 5230
5220 F=F-4
5230 INPUT " Do you live or work in a city",H$
5240 IF H$="N" THEN  5260
5250 F=F-6
5260 PRINT " Has sexual activity been frequent and with many different"
5270 INPUT " parteners ( for potential of VD )",H$
5280 IF H$="N"THEN   5300
5290 F=F-1
5300 IF G$="M" THEN  6000
5310 PRINT "   For risk of uterine cancer:"
5320 INPUT "  Did you begin regular sexual activity before age 18",H$
5330 IF H$="N" THEN  6000
5340 F=F-1
6000 H=0
6010 LET Y=25
6020 GOSUB 9900
6030 PRINT "                 FAMILY HISTORY"
6040 PRINT
6050 PRINT "How many parents, brothers or sisters had a heart attack"
6060 INPUT " before the age of 40",U
6070 IF U=0 THEN 6100
6080 H=H+U*(-4)
6100 PRINT "How many grandparents, uncles or aunts had a heart attack"
6110 INPUT " before age 40",U
6120 IF U=0 THEN 6140
6130  H=H+(U*(-1))
6140 PRINT "How many parents, brothers or sisters with high blood"
6150 INPUT " pressure requiring treatment",U
6160 IF U=0 THEN 6180
6170 H=H+(U*(-2))
6180 PRINT " How many grandparents uncles or aunts with high blood"
6190 INPUT " pressure requiring treatment",U
6200 IF U=0 THEN 6220
6210 H=H+(U*(-1))
6220 PRINT " How many parents, brothers or sisters got diabetes"
6230 INPUT " before age 25",U
6240 IF U=0 THEN 6260
6250  H=H+(U*(-6))
6260 PRINT "How many grandparents, uncles or aunts got diabetes"
6270 INPUT " before age 25",U
6280 IF U=0 THEN 6300
6290 H=H+(U*(-2))
6300 PRINT "How many parents, brothers or sisters got diabetes"
6310 INPUT " after age 25",U
6320 IF U=0 THEN 6350
6330  H=H+(U*(-2))
6350 PRINT "How many grandparents, uncles or aunts got diabetes"
6360 INPUT " after age 25",U
6370 IF U=0 THEN 6390
6380 H=H+(U*(-1))
6390 PRINT "Do you have a parent, grandparent, brother, sister"
6400 INPUT "uncle or aunt with glaucoma (Y/N)",U$
6410 IF U$="N" THEN 6430
6420 H=H-2
6430 PRINT "Do you have a parent, grandparent, brother, sister"
6440 INPUT "uncle or aunt with gout (Y/N)",U$
6450 IF U$="N" THEN 6470
6460  H=H-1
6470 IF G$="M" THEN 6600
6480 INPUT " Has your mother or sister had breast cancer (Y/N) ",U$
6490 IF U$="N" THEN  6600
6500 H=H-4
6600 M=0
6610 Y=25
6620 GOSUB 9900
6630 PRINT "                MEDICAL CARE"
6640 PRINT
6650 INPUT " Do you have a blood pressure check every year (Y/N)",U$
6660 IF U$="N" THEN 6680
6670  M=M+4
6680 IF G$="M" THEN  6800
6690 PRINT "   For risk of breast cancer:"
6700 PRINT "Do you self examine breasts each month and have check by"
6710 INPUT "doctor every year or two (Y/N)",U$
6720 IF U$="N" THEN  6740
6730  M=M+2
6740 PRINT "      For risk of cancer of the uterus:"
6750 INPUT " Do you have Pap smear every year or two (Y/N)",U$
6760 IF U$="N" THEN  6800
6770 M=M+2
6800 INPUT " Do you have a tuberculosis skin test every 5 to 10 years",U$
6810 IF U$="N" THEN  6830
6820  M=M+1
6830 INPUT "Do you have a glaucoma test every 4 years",U$
6840 IF U$="N" THEN  6851
6850  M=M+1
6851 IF A<41 THEN 7000
6860 PRINT " Do you have test for hidden blood in stool every two"
6870 INPUT " years after age 40, every year after age 50",U$
6880 IF U$="N" THEN  6891
6890  M=M+1
6891 IF A<51 THEN 7000
6900 INPUT "Do you have Proctosigmoidoscopy (rectal exam) after age 50",U$
6910 IF U$="N" THEN  7000
6920  M=M+1
7000 LET Y=25
7010 GOSUB 9900
7020 PRINT"A   ** LIFESCORE **  of 0 is average."
7100 PRINT
7110 PRINT
7119  L1=L+E1+D+T+G1+P1+S+F+H+M
7120 PRINT"   Your  ** LIFESCORE ** is ... ";L1
7130 PRINT
7140 PRINT
7150 PRINT"  This was made up from these individual scores:"
7160 PRINT"     Weight...........";L;"   Exercise............";E1  
7170 PRINT"     Diet.............";D;"   Smoking.............";T
7180 PRINT"     Alcohol..........";G1;"   Car.................";P1
7190 PRINT"     Stress...........";S;"   Personal History....";F
7200 PRINT"     Family History...";H;"   Medical Care........";M
7210 PRINT
7300 IF L1>29 THEN 7400
7310 IF L1>14 THEN 7420
7320 IF L1>-14 THEN 7440
7330 IF L1>-29 THEN 7460
7340 GOTO 7480
7400 PRINT" This means the odds of a long, healthy life are overwhelmingly"
7410 PRINT" in your favour"
7411 GOTO 7500
7420 PRINT" This means you have an excellent chance of enjoying"
7421 PRINT" better then average health"
7430 GOTO 7500
7440 PRINT" This places you in the average catagory"
7450 GOTO 7500
7460 PRINT" Your score indicates your probability of a"
7470 PRINT" healthy life is decreased"
7471 GOTO 7500
7480 PRINT" Your score shows that you probably heading"
7481 PRINT" for a serious illness"
7500 PRINT
7510 IF G$="F" THEN 7600
7520 IF L1>29 THEN 7580
7530 IF L1 >10 THEN 7582
7540 IF L1 >-10 THEN 7584
7550 IF L1>-30 THEN 7586
7560 Z$="below 60"
7570 GOTO 7700
7580 Z$="81+"
7581 GOTO 7700
7582 Z$="74 - 80"
7583 GOTO 7700
7584 Z$="67 - 73"
7585 GOTO 7700
7586 Z$="60 - 66"
7587 GOTO 7700
7588 Z$="below 60"
7589 GOTO 7700
7600 IF L1>29 THEN 7606
7601 IF L1 >10 THEN 7608
7602 IF L1 >-10 THEN 7610
7603 IF L1>-30 THEN 7612
7604 IF L1<-29 THEN 7614
7605 GOTO 7700
7606 Z$="86+"
7607 GOTO 7700
7608 Z$="79 - 85"
7609 GOTO 7700
7610 Z$="72 - 78" 
7611 GOTO 7700
7612 Z$="65 - 71"
7613 GOTO 7700
7614 Z$="below 65"
7700 PRINT
7710 PRINT"Your life expectancy is ";Z$;" years"
9240 STOP
9900 FOR Z=1 TO Y
9910 PRINT
9920 NEXT Z
9930 RETURN
9990 END
