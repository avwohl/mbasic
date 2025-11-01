1	'PIr5 4to sort the RBBS USERS.BB# fii N
Ri2coi8Ri	lodis=ce
2	'pri	r3Doto Rd namee	06h for people ca,lh	g ng dd)hei
 lhtkow Ahs1o:D0f0Fa0tS'c2,EdXaE' AARBBS, 5/30/83
4	'Th2c2efooeA is searl'otL1 N for c2erSLom local
5	06as (Agour  Moorpark<ousarR <tIets:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::hark)
aiThen f$<"To m CA, and nu6maiORrc given top prior+ 	(n uI R  eA fOtotRBd  S6r$'8to$9 Pe REldm(
	DBeEA1 'o h  siN LOCALgrt),CA(10000),USgrt) 'The arras wW tnNPei lwTK
R	ipD N "R",1,"A:USERS.BB#",62	e Random acTBTooe	(l0	FIELD#1,6ITRr aiwith fr format string fieldiRnoOFN0 #  ,l2C he number of entr E	(a:	LAST.RE ePN	LTCP	 n l,	l convert toumer'o Ra	 1I tAcre are 6LAST.RECORD-1;" callers in the fi  OD0	 UmOO
)n	9r hTO : LEl #  , AU$ 	e,h c thRC RsTa31R"rs 0	FORhnn DrASTw CORD	Mow et the lococall#: rnoOE#1,I
80	SECOND.eME=Ia O1aar " n.0lh'n leT X# ptTot X )
82	TOWN=INSTrf(
fFe  f +1,RR$,I n+1
89	'Scan the d) and st" fe(MNL kewSdr#t s
90	IF(INS  hETai00thI  R2 el
'0":fH1Sg0
10 1E
tDTnS  hETai00thIDH N" " ) <> 0) THEN 300
lGN / fnS JWN,RR$,"WE#Ke) <> 0) THEN 300  'l0	IF(fnS  OWN,RR$,"NEWBURY"sg":) THEN 300
l2	IF(INS  hET7ai00t2eGOU''hW0":) THENgo eP G  )dB tdt Pe Californiannes
130	IF(fnS  OWN,RR$,",CA"sg":) THEN 500
a:	IF(INS  hET7ai00tAd 'hW0":) H N 500	'Pity abouCATSh, TX......
16hraiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii th0Dr.e internatio2 or interstate  'orn,c)tiI w 	 ut a way to sort the R"rrXi	nRNs'tcodo it b hand'
0	US(J)=I : J=J+1		'Save nu6cord pointO1u<es$0(pK1 rnN .#Z10000 GOTO 00 ELSa"J 600	'And lo0NNLi T0e2 tbi
 laah,PesR0eEPe localsi n- l
e 0n=I : K=K+1	',TNeNO3	 2TR0e3h.Td l
eL  5 N
20	IF K>1- OH#sT	RO 800 ELSE GO,600
50h,Pese are within ChONLnia R0a0
e(ahT0 l s1 :IF L>10000 GOTO 00 'wh"Ta1R"rs are u<8RC Rs 	(Akoto	BeLt'loop=til allecords have Aehn(W
602	PRINT "nRcre"; d1 e intersr" callers,,u=eRut statisticsAr	PRIN"       and";L-1;" CaONLn= c2erTU	(re	PRIE"       and";K-1;"oca(non-toll) caArs.LThRINT 0rn
EN "R"JRDeA:USERS.$$$$"2l	'We will put thiTwa,r
 lwiST UR
6GN t:Tts"PTe ayW$hOS2e .c2owRFI#Oala R 0gnETt'T: LSET NW$=RR$ : PUT #2,15, start writing O/P3
640	I=2					'p=teto second O/Pecord
650	OR INDEX=1 TO J-1	'nDTirst of =)lRroct" S.=uD2c2e
o 0la 
 tsI1S(INDiSito
S< Pektn	eR.<e long distan'	R'o 0l	i,E#2,I : I=I+1oNEXT INDEX	'loop until US(" sN.hU7Rty
680	OR INDEX=1 TO L-1
690	GET #1,CA1ITFo a 0LSET NW$=RR$		)dMPdt Pe	e, Torniaones
00	PUT #2,IoI=I lTSME" sN.o 0 IrnsJR " sNolfO K-1
720	GET #1, lTCr1ITFo a 0LSET N$=RRaiLastly theocacal0#K: Sg	PU#DU: nI+1 : NEXT " sNi: (a 1ETh>LAsIt(ePH
T noHFI<RINT "Ou0T$NS2encocct size..ERROR..aborting" : STOP
748	ILL "A:USERStIReo#  , eAte an .BA file 0aGrtrOSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSNA 2e:USET F AITRIc TfOtot  Nlo e 'Ret	e old fileoloo
 eo: NAME "Aes 
wT aEs" ASc 0USERS.BB#" 'sE -o$T$e)ewne
770	PRINT "So3KsoaR"d"s	ERuo Caaaht rroentry point. COohR"E"Too many uR E ,lnRcase artIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIc..ERROR.." : JP    suW"00
50h,Pese are within ChONLnia R0a0
e(ahT0 l s1 :IF L>10000 GOTO 00 'wh"Ta1R"rs are u<8RC Rs 	(Akoto	BeLt'loop=til allecords have Aehn(W
602	PRINT "nRc