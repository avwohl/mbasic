BASIC BENCHMARK LISTINGS BM1 to 9 

LISTINGS OF BM1 to BM8 FROM COMPUTING EUROPE JULY 27 1978

100	REM    BM1
300	PRINT "Start BM1"
400	FOR K=1 TO 1000
500	NEXT K
700	PRINT "E"
800	END

------------------------

100	REM    BM2
300	PRINT "Start BM2"
400	K=0
500	K=K+1
600	IF K<1000 THEN 500
700	PRINT "E"
800	END

------------------

100	REM    BM3
300	PRINT "Start BM3"
400	K=0
500	K=K+1
550	A=K/K*K+K-K
600	IF K<1000 THEN 500
700	PRINT "E"
800	END

----------------------

100	REM    BM4
300	PRINT "Start BM4"
400	K=0
500	K=K+1
510	A=K/2*3+4-5
600	IF K<1000 THEN 500
700	PRINT "E"
800	END
                                   
----------------------             
                      
100	REM    BM5
300	PRINT "Start BM5"
400	K=0
500	K=K+1
510	K=K/2*3+4-5
520	GOSUB 820
600 	IF K<1000 THEN 500
700	PRINT "E"
800	STOP
820	RETURN

----------------------                                
                      
100	REM    BM6
300	PRINT "Start BM6"
400	K=0
500	K=K+1
510	A=K/2*3+4-5
520	GOSUB 820
530	FOR L=1 TO 5
540	NEXT L
600	IF K<1000 THEN 500
700	PRINT "E"
800	STOP
820	RETURN

----------------------

100	REM    BM7
300	PRINT "Start BM7"
400	K=0
430	DIM M(5)
500	K=K+I
510	A=K/2*3+4-5
520	GOSUB 820
530	FOR L=1 TO 5
535		M(L)=A
540	NEXT L
600	IF K <1000 THEN 500
700	PRINT "E"
800	STOP
820	RETURN

------------------------
                      
100	REM    BM8
300	PRINT "Start BM8"
400	K=0
500	K=K+1
550	A=K^2
560	B=LOG(K)
570	C=SIN(K)
580	IF K<100 THEN 500 
700	PRINT "E"
800	END
                      
----------------------                      

100	REM    BM9
130	PRINT "Start BM9"
140	FOR N= 1 TO 1000
150		FOR K= 2 TO 500
160			LET M=N/K
170			LET L=INT(M)
180			IF  L=0 THEN 230
190			IF  L=1 THEN 220
200			IF  M>L THEN 220
210			IF  M=L THEN 240
220		NEXT K
230		PRINT N;
240	NEXT L
250	PRINT "E"
260	END
                      
----------------------
