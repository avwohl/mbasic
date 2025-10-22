2    REM  Program is for joint estimation of common mean and individual
4    REM  variances for two independent normal populations.  See "Joint
6    REM  Estimation of the Parameters of Two Normal Populations" in J.
7    REM  American Statistical Association, June 1962, v. 57, pp. 446 -
8    REM  454.  I have added (ad hoc) an estimate of true variance.  All
9    REM  the rest is rigorous.----Mark Aldon Weiss   August 9, 1984
10 MAXNUMIT% = 100
15 DIM   M(MAXNUMIT%), WX(MAXNUMIT%), WY(MAXNUMIT%)
20 PRINT
30 PRINT
40 [9E]  CHR$(27) "G"  CHR$(15)  CHR$(27) "0"  CHR$(27) "U"  CHR$(1)
50 [9E]
60 [9E]
70 INPUT " What is nx"; NX% 
80 INPUT " What is ny"; NY%
90 INPUT " What is x-bar"; XBAR
100 INPUT " What is y-bar"; YBAR
110 INPUT " What is Sx-squared"; SX2
120 INPUT " What is Sy-squared"; SY2
130 M(0) = (NX%*SY2*XBAR + NY%*SX2*YBAR) / (NX%*SY2 + NY%*SX2)
140 PRINT
150 PRINT
160 PRINT " You are allowed a maximum of ",MAXNUMIT%," iterations."
170 INPUT " How many iterations do you want             ";NUMIT%
180 PRINT
190 PRINT
200 PRINT " M0 is ", M(0)
210 PRINT 
220 [9E] " M0 is ", M(0)
230 [9E]
240 FOR R% = 1  TO NUMIT%
250     WX(R%) = NX% * ( SY2 + ( YBAR - M(R%-1) )^2 )
260     WY(R%) = NY% * ( SX2 + ( XBAR - M(R%-1) )^2 )
270     M(R%) = (WX(R%)*XBAR + WY(R%)*YBAR) / (WX(R%) + WY(R%))
280      PRINT " Wx",R%,"  is  ",WX(R%)
290      PRINT " Wy",R%,"  is  ",WY(R%)
300      PRINT " M",R%,"  is  ",M(R%)
310      PRINT
320    [9E] " Wx",R%,"  is  ",WX(R%)
330    [9E] " Wy",R%,"  is  ",WY(R%)
340    [9E] " M",R%,"  is  ",M(R%)
350    [9E]
355    MLIMIT = M(R%)
360 NEXT R%
370 SXI2 = SX2 + (XBAR - MLIMIT)^2
380 SYI2 = SY2 + (YBAR - MLIMIT)^2
390 PRINT " Sx(I)-squared is ", SXI2
400 PRINT " Sy(I)-squared is ", SYI2
410 [9E] " Sx(I)-squared is ", SXI2
420 [9E] " Sy(I)-squared is ", SYI2
430 PRINT : [9E]
440 VARIANCE = (NY%*(MLIMIT-XBAR)^2*SYI2 + NX%*(MLIMIT-YBAR)^2*SXI2) / (NY%*(MLIMIT-XBAR)^2 + NX%*(MLIMIT-YBAR)^2)
450 PRINT " Estimate of VARIANCE of final mean = ", VARIANCE
460 [9E] " Estimate of VARIANCE of final mean = ", VARIANCE
470 PRINT
480 [9E]  CHR$(27) "@"
6682 ate of VARIANCE of final mean = ", VARIANCE
460 [9E] " Estimate of VARIANCE of final mean = ", VARIANCE
470 PRINT
480 [9E]  CHR$(27
