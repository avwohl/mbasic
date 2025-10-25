# READ

## Syntax

```basic
READ <list of variables>
```

## Purpose

To read values from a DATA statement and assign them to variables.  (See DATA, Section 2.10.)

## Remarks

A READ statement must always be       used   in conjunction   with   a   DATA statement.   READ statements assign variables to DATA statement values on a one-to-one basis. READ statement variables may be numeric or string, and the values read must agree with the variable types specified. If they do not agree, a "Syntax error" will result. A single READ statement may access one or more DATA   statements (they will be accessed in order), or several READ statements may access the same DATA statment.       If the number of variables in <list of variables> exceeds the number of elements in the DATA statement(s), an OUT OF DATA message is printed. If the number of variables specified is fewer than the number of elements in the DATA statement(s), subsequent READ statements will begin reading data at the first unread element.      If    there  are   no subsequent READ statements, the extra data is ignored. To reread DATA statements from the start, use the RESTORE statement (see RESTORE, Section 2.57) Example 1: 80 FOR I=l TO 10 90 READ A(I) 100 NEXT I 110 DATA 3.08,5.19,3.12,3.98,4.24 120 DATA 5.08,5.55,4.00,3.16,3.37 This program segment READs the values from the DATA   statements   into the array A.      After execution, the value of A(l) will be 3. 08, and so on. BASIC-80 COMMANDS AND STATEMENTS                    Page 2-71 Example 2:   LIST 10 PRINT "CITY", "STATE", " ZIP" 20 READ C$,S$,Z 30 DATA "DENVER,", COLORADO, 80211 40 PRINT C$,S$,Z Ok RUN CITY         STATE         ZIP DENVER,      COLORADO      80211 Ok This program READs string and numeric data   from the DATA statement in line 30. BASIC-80 COMMANDS AND STATEMENTS                       Page 2-72

## See Also

*Related statements will be linked here*
