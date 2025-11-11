10 REM Test SWAP and RANDOMIZE statements
20 A% = 10
30 B% = 20
40 PRINT "Before SWAP: A% = "; A%; ", B% = "; B%
50 SWAP A%, B%
60 PRINT "After SWAP: A% = "; A%; ", B% = "; B%
70 X! = 3.14
80 Y! = 2.71
90 PRINT "Before SWAP: X! = "; X!; ", Y! = "; Y!
100 SWAP X!, Y!
110 PRINT "After SWAP: X! = "; X!; ", Y! = "; Y!
120 REM Test RANDOMIZE
130 RANDOMIZE 42
140 PRINT "Random after RANDOMIZE 42: "; RND
150 RANDOMIZE
160 PRINT "Random after RANDOMIZE (time-based): "; RND
170 END