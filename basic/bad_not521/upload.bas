090 CLEAR 10000:	REM  RESERVE SOME SPACE FOR STRINGS
100 REM-----------PLOT PACKAGE-------------
101 REM VARIABLES:
102 REM CX      CHARACTER SIZE
103 REM LY      LINE SIZE IN Y DIRECTION
104 REM ML      LEFT MARGIN
105 REM MR      RIGHT MARGIN
106 REM MB      BOTTOM MARGIN
107 REM MT      TOP MARGIN
108 REM NY%     NUMBER OF CHARACTERS IN Y AXIS LABELS
109 REM NX%     NUMBER OF CHARACTERS IN X AXIS LABELS
110 REM LX%     NUMBER OF LINES OF X AXIS LABELS
111 REM DX,DY   REAL INCREMENTS BETWEEN GRID TIC MARKS
112 REM XL,XR   REAL VALUES FOR ENDS OF X AXIS
113 REM YB,YT   REAL VALUES FOR ENDS OF Y AXIS
114 REM GD      PLOTTER INCREMENT BETEEN DOTS IN GRID LINES
115 REM X1,Y1   STARTING PLOTTER COORDINATES FOR LINE SEGMENTS OR STRINGS
116 REM X2,Y2   ENDING PLOTTER COORDINATES FOR LINE SEGMENTS
117 REM G1-G7   GRAPHICS PACKAGE TEMPORARY VARIABLES
118 REM GF$     FILE NAME FOR VECTOR FILE
119 REM GB$     BUFFER STRING FOR VECTOR FILE
120 REM GC$     GRAPHIC COMMAND STRING
121 REM GC%	COLOR VALUE 0=WHITE, 1-63=PATTERNED, 64-127=GREY,NEG=XOR
122 REM GL$     LABEL STRING
123 REM --------------------------------
124 REM ------------------------------------------------------------------------
125 REM !                              ^                                       !
126 REM !                              MT                                      !
127 REM !                              !                                       !
128 REM !                              V                                       !
129 REM !          --------------------------------------------------          !
130 REM !          !                                                !          !
131 REM !<--ML---->!                                                !<---MR--->!
132 REM !          !   1000 I    .    .    .    .    .    .    .    !          !
133 REM !          !        I         .         .         .         !          !
134 REM !          !        I         .         .         .         !          !
135 REM !          !    950 I    .    .    .    .    .    .    .    !          !
136 REM !          !        I         !<-->!    .         .         !          !
137 REM !          !        I         . GD      .         .         !          !
138 REM !          !    900 I    .    .    .    .    .    .    .    !          !
139 REM !          !        I         .         .         .         !          !
140 REM !          !        I         .         .         .         !          !
141 REM !          !    850 I    .    .    .    .    .    .    .    !          !
142 REM !          !        I         .         .         .         !          !
143 REM !          !        I         .         .         .         !          !
144 REM !          !    800 I=======================================!          !
145 REM !          !      10.01     10.02     10.03     10.04       !          !
146 REM !          !                                                !          !
147 REM !          --------------------------------------------------          !
148 REM !                              ^                                       !
149 REM !                              !                                       !
150 REM !                              MB                                      !
151 REM !                              !                                       !
152 REM !                              V                                       !
153 REM ------------------------------------------------------------------------
154 REM XL=10.01, XR=10.05, DX=.01, YB=800, YT=1000, DY=50
155 REM NX%=5, LX%=1, NY%=4
156 REM WHEN LX%=-1, ADDITIONAL LINES WILL BE ADDED AUTOMATICALLY TO AVOID 
157 REM OVERLAP IN THE X AXIS LABELS.
158 REM
159 REM
160  REM  SCALING & CONVERSION FUNCTIONS
161 CX=1/80:LY=1/82: REM VALUES FOR MX-80
162 GK=32767: REM CONVERSION CONSTANT FOR COORDINATES
163  DEF  FN RX(X) =  ML + NY% * CX + (1 - ML - MR - NY% * CX) * (X - XL) / (XR - XL)
164  DEF  FN RY(Y) =  MB + LX% * LY +(1 - MT - MB - LX% * LY) * (Y - YB) / (YT - YB)
165  DEF  FN UX(X) = (X - ML - NY% * CX) * (XR - XL) / (1 - ML - MR - NY% * CX) + XL
166 DEF FN UY(Y) = (Y - MB - LX% * LY) * (YT - YB)/(1 - MT - MB - LX% * LY) + YB
167 REM OPEN .VEC FILE
168 GOSUB 200
169  GOTO 278: REM  TRANSFER TO USER PROGRAM
170 REM WRITE COMMAND STRING SUBROUTINE ****************************************
171 IF LEN(GB$)+LEN(GC$)<=126 THEN 174
172 GB$=GB$+STRING$(126-LEN(GB$),"N")
173 PRINT #1, GB$: GB$=MKS$(FRE(0)):GB$=""
174 GB$=GB$+GC$: RETURN
175 REM DRAW LINE SEGMENT               ****************************************
176 GC$="D"+MKI$(INT(X1*GK))+MKI$(INT(Y1*GK))+MKI$(INT(X2*GK))+MKI$(INT(Y2*GK))
177 GOSUB 171: RETURN
178 REM PLOT POINT                      ****************************************
179 GC$="P"+MKI$(INT(X1*GK))+MKI$(INT(Y1*GK)): GOSUB 171: RETURN
180 REM PLOT INCREMENTAL SEGMENT        ****************************************
181 GC$="I"+MKI$(INT(X1*GK))+MKI$(INT(Y1*GK)): GOSUB 171: RETURN
182 REM SET COLOR CODE                  ****************************************
183 GC$="C"+LEFT$(MKI$(GC%),1)
184 GOSUB 171: RETURN
185 REM ERASE PICTURE                   ****************************************
186 GC$="C"+LEFT$(MKI$(GC%),1)+"E"
187 GOSUB 171: RETURN
188 REM PLOT PRINTED STRING             ****************************************
189 GC$="S"+MKI$(INT(X1*GK))+MKI$(INT(Y1*GK))+GL$+CHR$(13): GOSUB 171: RETURN
190 REM PLOT FILLED SEGMENT             ****************************************
191 GC$="F"+MKI$(INT(X1*GK))+MKI$(INT(Y1*GK))+MKI$(INT(X2*GK))+MKI$(INT(Y2*GK))
192 GC$=GC$+MKI$(INT(YF*GK))
193 GOSUB 171:RETURN
194 REM SEND PRINT PICTURE COMMAND      ****************************************
195 GC$="O": GOSUB 171: RETURN
196 REM QUIT PLOTTING, PRINT GRAPH      ****************************************
197 GC$="OQ":GOSUB 171
198 GB$=GB$+GC$: GB$=GB$+STRING$(126-LEN(GB$),"N")
199 PRINT #1,GB$: CLOSE 1: RETURN
200 REM OPEN NEW OUTPUT FILE            ****************************************
201 INPUT "ENTER PLOT OUTPUT FILENAME";GF$
202 IF INSTR(GF$,".")=0 THEN GF$=GF$+".VEC"
203 OPEN "O",#1,GF$:GB$="":GC$="C"+CHR$(0)+"EC"+CHR$(127): GOSUB 171: RETURN
204  REM  SET DEFAULT VALUES            ****************************************
205 GC%=127
206 MT = 0:MB = 0:MR = 0:ML = 0
207 XL = 0:XR = 1:YB = 1:YT = 0:DX = 1:DY = 1
208 NX% = 0:NY% = 0:LX% =  - 1:GD = .01
209  RETURN 
210  REM  CALCULATE GRID                ****************************************
211 G1 =  FRE (0):G1 = 1 - ML - MR - CX * NX%: REM  PLOTTER LN OF X AXIS
212  IF G1 > CX THEN 214
213 VTAB 24:INVERSE:  PRINT "GRAPH TOO NARROW": NORMAL : RETURN 
214 G3 =  ABS ( FN RX(XL) -  FN RX(XL + DX)): REM  PLOTTER DX
215  IF LX% >  = 0 THEN 217
216 LX% = INT(NX% * CX/ G3) + 1
217 G2 = 1 - MT - MB - LY * LX%: REM  PLOTTER LN OF Y AXIS
218  IF G2 > CX THEN 220
219  VTAB 24: INVERSE : PRINT "GRAPH TOO SHORT": NORMAL : RETURN 
220  RETURN 
221  REM  DRAW GRID                     ****************************************
222 REM
226  Y1=FN RY(YB):Y2=FN RY(YT)
227  GC$="C"+CHR$(8): GOSUB 171
228  FOR G4 = XL TO XR STEP DX
229 X1 =  FN RX(G4): X2=X1
231  GOSUB 176
232 NEXT G4
233 GC$="C"+CHR$(1): GOSUB 171
234  X1=FN RX(XL):X2=FN RX(XR)
235  FOR G4 = YB TO YT STEP DY
236  Y1=FN RY(G4):Y2=Y1
237  GOSUB 176
239 NEXT G4
240  GOSUB 182: RETURN 
241 IF NX%=0 THEN GOTO 246 ELSE G6 =  FN RY(YB)
242  FOR G4 = XL TO XR STEP DX
243 G5 =  FN RX(G4)
244 X1=G5:Y1=G6:X2=G5:Y2=G6-CX:GOSUB 176
245  NEXT G4:  X1=FN RX(XR):Y1=FN RY(YB):X2=FN RX(XL): Y2=Y1: GOSUB 176
246 IF NY%=0 THEN GOTO 251 ELSE G5 =  FN RX(XL)
247  FOR G4 = YB TO YT STEP DY
248 G6 =  FN RY(G4)
249  X1=G5:Y1=G6:X2=G5-CX:Y2=G6:GOSUB 176
250  NEXT G4: X1=FN RX(XL):Y1=FN RY(YT):X2=X1: Y2=FN RY(YB): GOSUB 176
251  RETURN 
252  REM  LABEL X AXIS                  ****************************************
253 IF NX%=0 THEN RETURN ELSE G7 =  FRE (0):G7 = 0
254 G6=FN RY(YB)-2*LY
255  FOR G4 = XL TO XR STEP DX
256 G5 =  FN RX(G4):G7 = G7 + 1
257 Y1=G6- (-INT (G7 / LX%) * LX% + G7)*LY
258 X1= INT((G5-NX%*CX/2)/CX)*CX
259 GL$ = LEFT$( STR$ (G4),NX%)
260 GOSUB 189
261 NEXT G4: X1=FN RX(XR):Y1=FN RY(YB): X2=FN RX(XL): Y2=Y1: GOSUB 176
262  RETURN 
263  REM  LABEL Y AXIS                  ****************************************
264 IF NY%=0 THEN RETURN ELSE G7 =  FRE (0):G7 = 0
265 X1=ML
266  FOR G4 = YB TO YT STEP DY
267 Y1=FN RY(G4)
268 GL$ =  LEFT$( STR$ (G4), NY% )
269 GOSUB 189
270  NEXT G4: X1=FN RX(XL):Y1=FN RY(YT):X2=X1: Y2=FN RY(YB): GOSUB 176
271  RETURN 
272  REM  DO WHOLE GRID                 ****************************************
273  GOSUB 210
274  GOSUB 222
275  GOSUB 252
276  GOSUB 263
277  RETURN 
278  GOSUB 204
279 REM -------- TOP OF USER PROGRAM -------------------------------------------
280 REM UPLOAD NEW COLOR VALUES
281 REM
282 DATA 63,111,85,103,75,115,93,95
283 DATA 112,69,104,86,116,76,96,94
284 DATA 79,105,65,117,87,97,77,121
285 DATA 106,80,118,66,98,88,122,78
286 DATA 71,119,81,99,67,123,89,107
287 DATA 120,72,100,82,124,68,108,90
288 DATA 91,101,73,125,83,109,69,113
289 DATA 102,92,126,74,110,84,114,70
290 GC$="U"+MKI$(64)
300 FOR I=1 TO 64:READ GC%:GC$=GC$+CHR$(GC%):NEXT I
310 GOSUB 171:  REM UPLOAD NEW DITHER MATRIX
320 REM
330 GC$="U"+MKI$(8)
340 DATA 0,&H11,&H13,&H1F,&H35,&H75,&H73,&H07
350 FOR I=1 TO 8:READ GC% :GC$=GC$+CHR$(GC%):NEXT I
360 GOSUB 171:  REM UPLOAD NEW PLAID ARRAY
500 TY=1/15:HT=1/16:TX=1/11:LN=1/12
510 X1=0:X2=LN:YF=1-TY:Y1=YF+HT:Y2=Y1
520 FOR I%=1 TO 13
530 FOR J%=1 TO 10
540 GC%=(I%-1)*10+J%
550 IF GC%>127 GOTO 620
560 GOSUB 182: REM SET COLOR
570 GOSUB 190: REM FILL BLOCK
580 X1=X1+TX:X2=X1+LN
590 NEXT J%
600 X1=0:X2=LN:YF=YF-TY:Y1=YF+HT:Y2=Y1
610 NEXT I%
620 X1=0:LN=1/65:YF=0:Y1=HT:Y2=Y1:X2=LN
630 FOR GC%=64 TO 127
640 GOSUB 182:  REM SET COLOR
650 GOSUB 190:  REM FILL BLOCK
660 X1=X2:X2=X2+LN
670 NEXT GC%
680 GOSUB 196:  REM CLOSE OUT PLOT
690 END
