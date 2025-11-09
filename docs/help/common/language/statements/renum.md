---
category: editing
description: Renumber program lines and update line references
keywords: ['renum', 'renumber', 'line numbers', 'goto', 'gosub', 'editing']
syntax: "RENUM
RENUM <new_start>
RENUM <new_start>,<old_start>
RENUM <new_start>,<old_start>,<increment>"
title: RENUM
type: statement
---

# RENUM

## Purpose

To renumber program lines and automatically update all line number references in GOTO, GOSUB, THEN, ELSE, ON...GOTO, ON...GOSUB, RESTORE, RUN, and ON ERROR GOTO statements.

## Syntax

**Versions:** Disk

RENUM has four forms:

```basic
RENUM                              ' Renumber all lines starting at 10, increment 10
RENUM <new_start>                  ' Renumber all lines starting at new_start
RENUM <new_start>,<old_start>      ' Renumber from old_start onwards
RENUM <new_start>,<old_start>,<increment>  ' Full control
```

Parameters can be omitted using commas:
```basic
RENUM 100,,20   ' new_start=100, old_start=0 (all lines), increment=20
RENUM ,50,20    ' new_start=10, old_start=50, increment=20
```

## Parameters

- **new_start**: First line number in the renumbered sequence (default: 10)
- **old_start**: First line to renumber - lines before this stay unchanged (default: 0 = all lines)
- **increment**: Gap between line numbers (default: 10)

## Remarks

### Automatic Reference Updates

RENUM automatically updates line number references in:
- **GOTO** and **GOSUB** statements
- **IF...THEN** line_number and **ELSE** line_number
- **ON...GOTO** and **ON...GOSUB** lists
- **RESTORE** line_number
- **RUN** line_number
- **ON ERROR GOTO** line_number

### Range Renumbering

When `old_start` is specified, only lines with numbers >= old_start are renumbered. Lines before old_start keep their original numbers.

This is useful when:
- Adding code sections between existing code
- Reorganizing parts of large programs
- Making room in a specific section

### Limitations

- Cannot create line numbers > 65529
- Cannot reorder lines (e.g., RENUM 15,30 when lines are 10,20,30)
- If line number reference doesn't exist, prints: "Undefined line xxxxx in yyyyy"
  - xxxxx = the bad reference (not changed)
  - yyyyy = the line containing it (may be renumbered)

## Example

### Example 1: Renumber Entire Program

Before:
```basic
10 PRINT "START"
25 GOTO 60
40 PRINT "SKIP THIS"
60 PRINT "END"
```

After `RENUM` (default: start at 10, increment 10):
```basic
10 PRINT "START"
20 GOTO 40  ' Automatically updated from GOTO 60
30 PRINT "SKIP THIS"
40 PRINT "END"
```

### Example 2: Different Starting Line

```basic
10 PRINT "ONE"
20 PRINT "TWO"
30 PRINT "THREE"

RENUM 100

100 PRINT "ONE"
110 PRINT "TWO"
120 PRINT "THREE"
```

### Example 3: Range Renumbering

Original program:
```basic
10 PRINT "INIT"
20 PRINT "SETUP"
30 PRINT "PROCESS A"
40 PRINT "PROCESS B"
50 PRINT "DONE"
```

Renumber from line 30 onwards to make room for more setup code:
```basic
RENUM 100,30,10

10 PRINT "INIT"
20 PRINT "SETUP"
100 PRINT "PROCESS A"
110 PRINT "PROCESS B"
120 PRINT "DONE"
```

Lines 10-20 unchanged, lines 30+ renumbered starting at 100.

### Example 4: Custom Increment

```basic
10 FOR I=1 TO 10
20   PRINT I
30 NEXT I

RENUM 1000,,50

1000 FOR I=1 TO 10
1050   PRINT I
1100 NEXT I
```

### Example 5: GOTO Reference Update

```basic
10 INPUT X
20 IF X<0 THEN GOTO 50
30 PRINT "POSITIVE"
40 END
50 PRINT "NEGATIVE"

RENUM 100,0,10

100 INPUT X
110 IF X<0 THEN GOTO 140
120 PRINT "POSITIVE"
130 END
140 PRINT "NEGATIVE"
```

GOTO 50 automatically updated to GOTO 140.

### Example 6: ON...GOTO Reference Update

```basic
10 INPUT CHOICE
20 ON CHOICE GOTO 100,200,300
100 PRINT "OPTION 1"
110 END
200 PRINT "OPTION 2"
210 END
300 PRINT "OPTION 3"
310 END

RENUM 1000,100,100

10 INPUT CHOICE
20 ON CHOICE GOTO 1000,1100,1200
1000 PRINT "OPTION 1"
1010 END
1100 PRINT "OPTION 2"
1110 END
1200 PRINT "OPTION 3"
1210 END
```

All three target lines in ON...GOTO list updated.

### Example 7: Making Room for Insertions

You have lines 10-100 but need to add many lines between 30-40:

```basic
RENUM 1000,40,10
```

Result:
- Lines 10-30 stay unchanged
- Lines 40+ renumbered to 1000, 1010, 1020...
- Now you can add lines 40-999 with room to spare

## Common Patterns

### Tidy up cramped program
```basic
RENUM 10,0,10      ' Reset to nice 10,20,30...
```

### Make room in middle of program
```basic
RENUM 1000,500,10  ' Lines 500+ move to 1000+
```

### Large increment for big programs
```basic
RENUM 100,0,100    ' 100, 200, 300... lots of room
```

## Error Messages

### "Illegal function call"
- Trying to create line number > 65529
- Trying to reorder lines (e.g., RENUM 15,30 with lines 10,20,30)

### "Undefined line xxxxx in yyyyy"
- Line number reference doesn't exist
- xxxxx = bad reference (unchanged)
- yyyyy = line containing it (may be renumbered)

## See Also
- [AUTO](auto.md) - To generate a line number automatically after every carriage return
- [DELETE](delete.md) - To delete program lines
- [EDIT](edit.md) - To enter Edit Mode at the specified line
- [LIST](list.md) - To list all or part of the program currently in memory at the terminal
- [LLIST](llist.md) - To list all or part of the program currently in memory at the line printer
