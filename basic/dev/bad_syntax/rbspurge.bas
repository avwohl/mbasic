10n"FL:1 A-Z
120 '
140 VERS$="verslgEH 60 '                           PURGNAS
180 (:11Orig
r.S2
4y:1L22.BSQ
200 '                         B Rn Fowle0
220 '
20T.dited by Rg,
,aA"mmerly, LA$9O TBM1RC
LN4S  00 ) A3-3753 tg l
T0T(9:>W82    This pigram washH0 H0Gly written2I " full utility
300 ' oM2=46"D,:111O o$I2m.  0nce I use the Purge eaEeG(STHDr1' of SP MM0me,  
RSM2 d)EPO((RE+$"ot file,TTeited this fine040 ' program down i the  'bare bones'Aor S( -ED"0E O2GaCNG2"P2.no )F
"
0RP   oP1urter etails.i- LRg,












































gI 6Z",R0E0$0
380l
400 PRINT:sK  :P6k"                                                 RB5PURGE UTILITY ";VERS$
42nLn S0,2)
440 1s:r 29D460 CRLF$=CHR$ 3)+

RR g1P FA4tUT SEP$10 F=n
0:BAFNP=0
520 G$I8GSLE111111111111111111111111111111111111111' buil msg indel
540 N$="r,e
R
:"
560+1Yu:C6S2IlsLU6
CAS2SG0
580:INT:PRR1
600 GOI8Z60
3 '                                                  end of progrEi
640 PRR1:PRI  "++DR"S 56=6Hto 'Apurge kiE S=neOg"2s
A0T(Afrm iles
00F)K$ 1iH
#8 4tUTFiles alreeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee purged.":RET$R0
720 TTE$="a, "
740 OPEN "R",1
AT8TSEARCD760 IF LO ,20 THEN PRINTArchive ile: ";
              RTTE$+".A1";"sMst#Ze1 7Z"1URN
780 CLO10104tUT "Prging summary file...................................:OPEN "R",1,"SUMMARY",30
82FL"+
#1,30 AS1$
840 R1=nI60 OZT"R",2,"$SUMMARY.$$$$",3nI80N
S+ $00S 
o
900 R2=1Er1PRR1 SEP$:'S1
T:N.OF(1) THEgPi
940FPE8ccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccP
0 THEN R1=RFeB8  "De2tion":GOTO 920
9G+,1  R2$=Ri
980 PUT #2,l
12R)B:1 LE1$(R2$,28)
1 Ns61L(R1$)>99998 THA1140
1040 F)L
1 TO 5
60 R1=R1+1P2$ ,ls"1#=T:LSET R2$=R1,4R1#2,l
110RINT LEFTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT
N8)
00lL1  I
11201=R1+1:R2=R2+1:GOT0ErE" N0(W#ROPA"O",112NMMARY.BAK":CLOSE:KILLSUMM> EBAK":
       NAME "SUM1RY" AS "SUB RY.BAK":NAME "$SUMMAO#s7$G5"SUB RY"
1160:INT "Purging
,:111O le...................................:MSGN=IcC
l=l
110PEN "R",1,"0#fGES":T:F9EIS1 ,65 AS R1$
120P VI.R7eD8#fGS.$$$$",65:FIELD #2,T AR20u220 OPEN "O",3,DATE$+".A1":R1s48L=0
120=T=1:R2=1SM:INT SEP$ u  #=T:IF EOF(1) LZT160H 280 IF VAL(R1$
0 THAKIL=-2B8NT "Archiving messa2": AO 1360
130FLM
H 320 LSTR2$=RUO:INT LEFT$(RNENP0
Go PUT #2,l
1tGLUMI("L1GOI8g#3:sK   #3,KL0u380 IF VAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA$)>99998 THEN 1600
1400 F)L
1 TO 5
R3 R1C+1:N425 KIL THEN R2=R2+1
1440 GET #1,:6N
2  HEN GOSN 1920:PRINT #3F6Ka
O 1480
1460 LSET R2$=R1,4R1 #$ $,4tUT LN $(R2#:0)" T04+T I
1500 FOR ITTO61LpssT=R1+1:IF NOKIL THEN 2$ ,l3
1520 GET #=T:IF KSCHE0============================================================================ 1920:PRR1 #3,M4r=fOA60"S 407 R:$  $4R1 $2O42INT LEFT$(
NEG EH tG:T $C=Rs8F NOT KSCHE
e=R2+1
 80 GOTOd0u600 CLO6
etaO",aMESSAGP0NU6e1LOSPFH8(/5GES.BAK":
       NAME "M"fGE fSMES GES.BAK":NAME$MESSAGS.$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$ A"MESS i29D1620:INT "Updating counters 2S0u640 OPEN "O",1,"COU EP0NU6e1LOSPFH8(21OU EP0NUS0660OmI 6#,1,"C::1 2"S :FI#A#11AS C1$T AC2$"Z80 OZT"R",2,"C::1 2:TK",15FM9EIS1"S  AR20u701u  #1,1:LSTR2$=C1$+C2$:PU#2,1
e3 M(,10u740 PURGED=-1 RNB W0:RETURN
1760 (,S-ild mess11EDRn l
1780 MX6c6=0
180P VI.R"2aSUMMAR",30:RE=1FM9EI"141fSR$te0 GET#1,RE:IF EO ("LZT1900
1840 G=IccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccRR N6=MZ+/ T
6,1)=G:IF G=0 THEN 1I0
1tGLUeYS 7$I THAMZ=MZ-1:GOTOS00 1880 GET#=u#T:C
6, $tccccccccccccccccccccccccccccccccccccc):MX=++M(MZe L0FsuR$' 1R5O 1r 0u900 M(,6"1URN
1920 '                                                unpack record
1B0:,tB(R1$uD196/H6000000000000000000000000000000000000000000000000000000000ssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssss$,Z.)2r(l0LAtBiVU11:IFENu THEN S
20000 WEND 0r1KL$=LEFT$p4mEHr N0"1UrnX3VR,tBps"SEH 0nPOg"B"
fO 1360
130FLM
H 320 LSTR2$=RUO:INT LEFT$(RNENP0
Go PUT #2,l
1tGLUMI("L1g000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000