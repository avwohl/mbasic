rem  convert basicode2 programs to mbasic
rem
rem  an CB80 program from
rem
rem	Henk Wevers
rem	Dutch Hobby computerclub
rem
rem







rem ------- filenames -------------------------


	file1$=command$+".bas"
	file2$=command$+".$$$"
	file3$=command$+".bak"
	file4$="keywords.dat"
	file5$="function.dat"

rem ------- dimensions ------------------------

	dim keyword$(255),function$(255)

rem -------------------------------------------

	on error goto fout.afhandeling

	for i%= 1 to 32:print:next
	print "convert version 1.0"
	print
	print "NO copyrights"
	print
	print "Copywrong by Henk Wevers"
	print "Dutch Hobby Computer Club"
	for i%= 1 to 15:print:next

	if match(".",command$,1)<> 0 then \
		print "wrong filename in commandstring !";chr$(7):stop

if end #3 then continue:
	open file3$ as 3
	delete 3
continue:
	if size(file4$) = 0 then file$=file4$:goto no.file
	open file4$ as 4
	keywords%=1
	if end #4 then end.keywords
read.keyword:
	read #4;line keyword$(keywords%)
	keywords%=keywords%+1
	goto read.keyword
end.keywords:
	close 4
	if size(file5$) = 0 then file$=file5$:goto no.file
	open file5$ as 5
	functions%=1
	if end #5 then end.functions
read.functions:
	read #5;line function$(functions%)
	functions%=functions%+1
	goto read.functions:
end.functions:
	close 5

	if size(file1$) = 0 then file$=file1$:goto no.file
	open file1$ as 1
	create file2$ as 2
	if end #1 then finished
read.a.line:
	read #1;line inline$
	print inline$;chr$(13);
	length%=len(inline$)
	if length% = 0 then goto read.a.line
	outline$=left$(inline$,1)
	quotes.flag%=0
	for 	position% = 2 to length%
		if length% < 3 then goto take.remainder
		char$=mid$(inline$,position%,1)
		if char$=chr$(34) and quotes.flag% = 0 then \
			quotes.flag%=1:goto next.char
		if char$=chr$(34) and quotes.flag% = 1 then \
			quotes.flag%=0:goto next.char

		if quotes.flag%=1 then goto next.char
		
		rem -------- try keywords ------------------
try.keyword:
		for 	i%= 1 to keywords%-1
			for	j% = 1 to len(keyword$(i%))
				if position%+j%-1 > length% then goto next.key
				keychar$=mid$(keyword$(i%),j%,1)
				trychar$=UCASE$(mid$(inline$,position%+j%-1,1))
				if keychar$ <> trychar$ then goto next.key
			next	j%
			goto keyword.match
next.key:
		next	i%
		goto try.function

keyword.match:
			char1$= mid$(inline$,position%-1,1)
			if char1$ =" " or char1$=":" then goto no.spac
			if right$(outline$,1)=" " then goto no.spac
			outline$=outline$+" "
no.spac:
			outline$=outline$+keyword$(i%)
			position%=position%+len(keyword$(i%))
			if position%>length% then goto next.line
			char$=mid$(inline$,position%,1)
			if (char$ =" " or char$=":" or char$=";" or char$=",")\
					 and keyword$(i%)<>"REM" then\
							 goto next.char
			if char$ =" " and keyword$(i%)="REM" then \
							goto take.remainder
			outline$=outline$+" "
			if keyword$(i%)="REM" then goto take.remainder
			position%=position%-1:goto next.char.1
		rem -------- try functions ------------------
try.function:
		for 	i%= 1 to functions%-1
			for	j% = 1 to len(function$(i%))
				if position%+j%-1 > length% then goto next.fun
				funchar$=mid$(function$(i%),j%,1)
				trychar$=UCASE$(mid$(inline$,position%+j%-1,1))
				if funchar$ <> trychar$ then goto next.fun
			next	j%
			goto function.match
next.fun:
		next	i%
		goto next.char

function.match:
			c$=mid$(inline$,position%-1,1) 
			if c$=" " or c$=","or c$=";" or c$=":" or c$="=" then \
					goto no.spac1
			if right$(outline$,1)=" " then goto no.spac1
			outline$=outline$+" "
no.spac1:
			outline$=outline$+function$(i%)
			position%=position%+len(function$(i%))
			if position%>length% then goto next.line
			position%=position%-1:goto next.char.1

next.char:
			outline$=outline$+char$
next.char.1:
		next position%

take.remainder:
			outline$=outline$+right$(inline$,length%-position%+1)
next.line:
			print using "&";#2;outline$
			print outline$
			goto read.a.line

finished:
			close 1,2
			test%=rename(file3$,file1$)
			if test%=0 then goto disk.error
			test%=rename(file1$,file2$)
			if test%=0 then goto disk.error
			print clear$:print:print "+++ succesfull +++"
			stop
disk.error:
			print clear$:print
			print:print "+++ OOPS ! disk-error":stop
no.file:
	print clear$
	print "++++ file ";file$;" not found ! ++++";chr$(7)
	print
	print
	stop
fout.afhandeling:
	print clear$
	print "++++ UGH !, error in proces ! ++++";chr$(7)
	print
	print "error code: ";err
	print
	print "quitting execution...... ":stop
