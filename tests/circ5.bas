10 PRINT "Starting test with";5;"nested GOSUBs"
20 GOSUB 1000
30 PRINT "Back to main - SUCCESS!"
40 END
1000 PRINT "Enter level 1"
1010 GOSUB 1100
1020 PRINT "Return from level 1"
1030 RETURN
1100 PRINT "Enter level 2"
1110 GOSUB 1200
1120 PRINT "Return from level 2"
1130 RETURN
1200 PRINT "Enter level 3"
1210 GOSUB 1300
1220 PRINT "Return from level 3"
1230 RETURN
1300 PRINT "Enter level 4"
1310 GOSUB 1400
1320 PRINT "Return from level 4"
1330 RETURN
1400 PRINT "Enter level 5"
1420 PRINT "Return from level 5"
1430 RETURN
