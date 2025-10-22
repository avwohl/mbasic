!
!  simcvax.bas  VAX BASIC V3.3
!
!  converts the index file SIMIBM.IDX into the
!  easily read file SIMIBM.LST (for the entire list)
!  or SIMIBM.LSTyymmdd (if the starting date is yymmdd)
!  or SIMIBM.LSTsubstring (if using substring search)
!
!
!  Gives the user the option to include in the list file only those
!  files added to the index after a specified date or only those
!  containing a given string.
!
!  Part of this program was translated from Dustin Fu's SIMCVT.FOR
!  to VAX BASIC V3.3
!
!   New code/Updates by:
!		Mark Harris
!		Digital Equipment Corp
!		Santa Clara, CA
!		Internet:	harris_ma@wr2for.dec.com
!		1/10/91		Added scan options
!		5/13/91		Fixed case sensitivity
!		6/1/91		Valid names for output file, misc aesthetics
!		7/1/91		Scan Monitor added
!		12/31/91	Timestamp
!		6/5/92		New scans, Memory for last search, etc
!
!   Original improvements by
!                     Don Chodrow
!                     Physics Department
!                     James Madison University
!                     Harrisonburg, VA 22807
!                     BITNET:      FAC_CHOD@JMUVAX1
!                     INTERNET:    dc@dirac.physics.jmu.edu
!
!
!  This program will convert the file SIMIBM.IDX into a readable form,
!  sending the output to the file SIMIBM.LST.  Because it is written in
!  BASIC instead of FORTRAN, there is no need to convert quotes to
!  apostrophes.
!
!  This program may be loaded into the VAX BASIC environment and run, or
!  it may be compiled and linked to produce an .exe file:
!
!           $ basic simcvax
!           $ link simcvax
!           $ run simcvax
!
   searchfile$ = "SIMIBM"
!
!
DIM #3,		TS_M%(1%),	&
		TS_D%(1%),	&
		TS_Y%(1%)
Open "SIMCVAX.DAT" as file 3%, 	&
		Organization VIRTUAL FIXED,	&
		Access MODIFY
!
If TS_M%(1)=0% Then
	TS_D%(1)=1%
	TS_Y%(1)=70%
	TS_M%(1)=1%
End If
!
SAVE_D%=TS_D%(1)
SAVE_Y%=TS_Y%(1)
SAVE_M%=TS_M%(1)
!
! These above will be the last run's values...
!
!TS_D%(1)=VAL(LEFT(DATE$(0),2%))
!TS_Y%(1)=VAL(MID(DATE$(0),8%,2%))
!TS_M%(1)=(pos("JanFebMarAprMayJunJulAugSepOctNovDec",MID(DATE$(0),4%,3%),1%)+2%)/3%
!Close 3%
! Now we have the SAVE_* values above as the date of LAST access...
!
print searchfile$+" - Public Domain and shareware listing as of ";date$(0)
print
!
!
print "Do you wish to locate a specific file or files with their FILENAME"
input "or Description containing a substring <Y/N, Default:N>",yesno$
yesno$ = left$(edit$(yesno$,32),1)
substring$=""
yesno$="N" unless yesno$="Y"
!
while substring$="" and yesno$="Y"
input "Substring to locate ", substring$
next
!
mask_substring$=""
For I%=1% TO len(substring$)
ATMP$=MID(edit$(substring$,32%),I%,1)
ATMP%=ascii(ATMP$)
mask_substring$=mask_substring$+ATMP$	&
	IF	(ATMP%>=65% and ATMP%<=90%) or	&
		(ATMP%>=48% and ATMP%<=57%)
Next I%
! mask_substring$ Returned
! Valid Characters are A-Z,1-9
!
print "Do you want to list only those files added to the index"
input "on or after a certain date <Y/N, Default:N>",yesno$
yesno$ = left$(edit$(yesno$,32),1)
starter$ = "0"
if (yesno$ = "Y") then
   yr%=0
   while (yr% <70) or (yr% > 99)
	print "Enter the last 2 digits of the starting year (";	&
		NUM1$(Save_y%);"): ";
	input yr%
	yr%=save_y% if yr%=0%
   next
   month% = 0
   while (month% < 1) or (month% > 12)
	print "Enter the number of the starting month, 1 to 12 (";	&
		NUM1$(Save_M%);") :";
	input month%
	month%=Save_m% if month%=0%
   next
   day% = 0
   while (day% < 1) or (day% > 31) or ((month%=2) and (day%>29%))
	Print "Enter the starting day, 1 to 31 (";	&
		NUM1$(Save_D%);") :";
	input day%
	day%=Save_D% if day%=0%
   next

   starter$ = str$(yr%)

   if (month% < 10) then
      starter$=starter$ + "0"+str$(month%)
   else
      starter$ = starter$ + str$(month%)
   end if

   if (day% < 10) then
      starter$ = starter$ + "0" + str$(day%)
   else
      starter$ = starter$ + str$(day%)
   end if
end if

outfile$ = searchfile$+".lst"
if starter$ <> "0" then
   outfile$ = searchfile$+".lst" + starter$
end if
if substring$ <> "" then
   outfile$ = searchfile$+".lst" + left(mask_substring$,8)
end if

start% = val%(starter$)
outfile$=edit$(outfile$,32)

open searchfile$+".IDX" for input as file #1
open outfile$ for output as file #2
print
print "File being created: ";outfile$
margin #2,80%
number_of_matches%=0%
number_of_records%=0%
latest_entry=0
Scan_tick=1000.00

print #2, ""+searchfile$+" PUBLIC DOMAIN AND SHAREWARE LISTING AS OF ";date$(0)
if starter$ <> "0" then
   print #2, " "
   print #2, "This list contains files dated ";starter$;" or later."
end if
if substring$ <> "" then
   print #2, " "
   print #2, "This list contains files with names and/or descriptions"
   print #2, "containing the substring : ";substring$
end if
print #2," "
print #2, "NOTE: Type B is Binary; Type A is ASCII"

fs1$ = " "      ! initialize
dir1$ = " "     ! initialize

qq$ = "'LLLLLLLLLLLL 'L ####### ###### "
qq$ = qq$ + "'LLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLL"
!
!  qq$ is the PRINT USING format string
!

when error use closer  ! terminate program when end of file #1 is reached

  while 1 = 1  ! "endless" loop, terminated by end of file #1 "error"
		linput #1, rawdata$
		C1%=POS(RAWDATA$,",",1%)
		C2%=POS(RAWDATA$,",",C1%+1%)
		C3%=POS(RAWDATA$,",",C2%+1%)
		C4%=POS(RAWDATA$,",",C3%+1%)
		C5%=POS(RAWDATA$,",",C4%+1%)
		C6%=POS(RAWDATA$,",",C5%+1%)
		C7%=POS(RAWDATA$,",",C6%+1%)
		DQ%=POS(RAWDATA$,'"',C7%+2%)
		!
		fs2$=MID(RAWDATA$,2%,C1%-3%)
		dir2$=MID(RAWDATA$,C1%+2%,C2%-C1%-3%)
		filnam$=MID(RAWDATA$,C2%+2%,C3%-C2%-3%)
		rev$=MID(RAWDATA$,C3%+1%,C4%-C3%-1%)
		file_length$=MID(RAWDATA$,C4%+1%,C5%-C4%-1%)
		bits$=MID(RAWDATA$,C5%+1%,C6%-C5%-1%)
		dt$=MID(RAWDATA$,C6%+1%,C7%-C6%-1%)
		descr$=MID(RAWDATA$,C7%+2%,DQ%-C7%-2%)
	! We get as strings to allow for format errors
	rev=val(rev$)
	file_length=val(file_length$)
	bits%=val(bits$)
	dt=val(dt$)
    Number_of_records%=Number_of_records%+1
    if (Number_of_records%/Scan_tick) = INT(Number_of_records%/Scan_tick) THEN	&
		PRINT Number_of_records%;"files searched. ";
		IF Number_of_matches%=0% then	&
			MF$="No"
		ELSE
			MF$=NUM1$(Number_of_matches%)
		END IF
		PRINT MF$;" matches found, continuing..."
    END IF
    latest_entry=dt if dt > latest_entry
    if ((dt >= start%) and ( substring$="" )) or	&
       (((start% <> 0%) and (substring$ <> "")) and	&
        (dt>=start%) and 	&
	(pos(edit$(filnam$,32),edit$(substring$,32),1) or 	&
			pos(edit$(descr$,32),edit$(substring$,32),1))) or	&
	((pos(edit$(filnam$,32),edit$(substring$,32),1) or	&
			pos(edit$(descr$,32),edit$(substring$,32),1)) and	&
		start%=0) then
      if ((fs1$ <> fs2$) or (dir1$ <> dir2$)) then
          print #2," "
          print #2,"Directory ";fs2$;dir2$
          print #2," Filename   Type Length   Date    Description"
          print #2,"=============================================="
          dir1$ = dir2$
          fs1$ = fs2$
      end if

      if (bits% = 8) then
         style$ = "B"
      else
         style$ = "A"
      end if

      print #2 using qq$ ; filnam$,style$,file_length,dt,descr$
      number_of_matches%=number_of_matches%+1%
    end if
  next  ! end of "endless" loop

end when

handler closer
   if err = 11% then
      close #1
      close #2
      !
   end if
end handler
!print err,ert$(err)
!
ld$=num1$(latest_entry)
mtmp%=val(mid(ld$,3%,2%))
mtmp$=mid("JanFebMarAprMayJunJulAugSepOctNovDec",mtmp%*3%-2%,3%)
dtmp$=mid(ld$,5%,2%)
ytmp$=mID(ld$,1%,2%)
print searchfile$;" has submissions through ";mtmp$;" ";dtmp$;", 19";ytmp$
print 		"Of";Number_of_records%;	&
		"entries, the number of Matches found is";Number_of_matches%
!
TS_D%(1)=val(dtmp$)
TS_Y%(1)=val(ytmp$)
TS_M%(1)=mtmp%
!
close #3
end
