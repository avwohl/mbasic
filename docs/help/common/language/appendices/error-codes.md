---
description: Complete reference of BASIC-80 error codes and their meanings
keywords:
- array
- codes
- command
- condition
- data
- dim
- else
- error
- execute
- field
title: Error Codes and Messages
type: reference
---

# Error Codes and Messages

Summary of BASIC-80 error codes and their meanings.

## General Errors

| Code | Number | Message | Description |
|------|--------|---------|-------------|
| **NF** | 1 | NEXT without FOR | A variable in a NEXT statement does not correspond to any previously executed, unmatched FOR statement variable. |
| **SN** | 2 | Syntax error | A line contains an incorrect sequence of characters (such as unmatched parenthesis, misspelled command or statement, incorrect punctuation, etc.). |
| **RG** | 3 | Return without GOSUB | A RETURN statement is encountered for which there is no previous, unmatched GOSUB statement. |
| **OD** | 4 | Out of data | A READ statement is executed when there are no DATA statements with unread data remaining in the program. |
| **FC** | 5 | Illegal function call | A parameter that is out of range is passed to a math or string function. This may also occur from:<br>• Negative or unreasonably large subscript<br>• Negative or zero argument with LOG<br>• Negative argument to SQR<br>• Negative mantissa with non-integer exponent<br>• Call to USR function with no address set<br>• Improper argument to MID$, LEFT$, RIGHT$, INP, OUT, WAIT, PEEK, POKE, TAB, SPC, STRING$, SPACE$, INSTR, or ON...GOTO |
| **OV** | 6 | Overflow | The result of a calculation is too large to be represented in BASIC-80's number format. (Underflow results in zero with no error.) |
| **OM** | 7 | Out of memory | A program is too large, has too many FOR loops or GOSUBs, too many variables, or expressions that are too complicated. |
| **UL** | 8 | Undefined line | A line reference in GOTO, GOSUB, IF...THEN...ELSE, or DELETE is to a nonexistent line. |
| **BS** | 9 | Subscript out of range | An array element is referenced with a subscript outside the array dimensions, or with the wrong number of subscripts. |
| **DD** | 10 | Redimensioned array | Two DIM statements are given for the same array, or a DIM statement is given after the default dimension of 10 has been established. |
| **/0** | 11 | Division by zero | A division by zero is encountered. Machine infinity with the sign of the numerator is supplied as the result, and execution continues. |
| **ID** | 12 | Illegal direct | A statement that is illegal in direct mode is entered as a direct mode command. |
| **TM** | 13 | Type mismatch | A string variable is assigned a numeric value or vice versa; a function expecting a numeric argument is given a string or vice versa. |
| **OS** | 14 | Out of string space | String variables have exceeded the amount of free memory remaining. |
| **LS** | 15 | String too long | An attempt is made to create a string more than 255 characters long. |
| **ST** | 16 | String formula too complex | A string expression is too long or complex. Break it into smaller expressions. |
| **CN** | 17 | Can't continue | An attempt is made to continue a program that has halted due to an error, has been modified during a break, or does not exist. |
| **UF** | 18 | Undefined user function | A USR function is called before the function definition (DEF statement) is given. |

## Extended and Disk Version Errors

| Code | Number | Message | Description |
|------|--------|---------|-------------|
| | 19 | No RESUME | An error trapping routine is entered but contains no RESUME statement. |
| | 20 | RESUME without error | A RESUME statement is encountered before an error trapping routine is entered. |
| | 21 | Unprintable error | An error message is not available for the error condition. Usually caused by ERROR with an undefined error code. |
| | 22 | Missing operand | An expression contains an operator with no operand following it. |
| | 23 | Line buffer overflow | An attempt is made to input a line that has too many characters. |
| | *24-25* | *(Reserved)* | Not defined in MBASIC 5.21. Reserved for future use. |
| | 26 | FOR without NEXT | A FOR was encountered without a matching NEXT. |
| | *27-28* | *(Reserved)* | Not defined in MBASIC 5.21. Reserved for future use. |
| | 29 | WHILE without WEND | A WHILE statement does not have a matching WEND. |
| | 30 | WEND without WHILE | A WEND was encountered without a matching WHILE. |
| | *31-49* | *(Reserved)* | Not defined in MBASIC 5.21. Reserved for future use. |

## Disk I/O Errors

| Code | Number | Message | Description |
|------|--------|---------|-------------|
| | 50 | Field overflow | A FIELD statement is attempting to allocate more bytes than were specified for the record length of a random file. |
| | 51 | Internal error | An internal malfunction has occurred in Disk BASIC-80. |
| | 52 | Bad file number | A statement references a file with a file number that is not OPEN or is out of range. |
| | 53 | File not found | A LOAD, KILL, or OPEN statement references a file that does not exist. |
| | 54 | Bad file mode | An attempt is made to use PUT, GET, or LOF with a sequential file, to LOAD a random file, or to OPEN with a mode other than I, O, or R. |
| | 55 | File already open | A sequential output mode OPEN is issued for a file that is already open, or a KILL is given for an open file. |
| | *56* | *(Reserved)* | Not defined in MBASIC 5.21. Reserved for future use. |
| | 57 | Disk I/O error | A fatal I/O error occurred on a disk operation that the OS cannot recover from. |
| | 58 | File already exists | The filename in a NAME statement is identical to an existing filename. |
| | *59-60* | *(Reserved)* | Not defined in MBASIC 5.21. Reserved for future use. |
| | 61 | Disk full | All disk storage space is in use. |
| | 62 | Input past end | An INPUT statement is executed after all data in the file has been read, or for an empty file. Use EOF to detect end of file. |
| | 63 | Bad record number | In a PUT or GET statement, the record number is either greater than 32767 or equal to zero. |
| | 64 | Bad file name | An illegal form is used for the filename (e.g., too many characters). |
| | *65* | *(Reserved)* | Not defined in MBASIC 5.21. Reserved for future use. |
| | 66 | Direct statement in file | A direct statement is encountered while LOADing an ASCII-format file. The LOAD is terminated. |
| | 67 | Too many files | An attempt is made to create a new file when all 255 directory entries are full. |

## Error Handling

To handle errors in your program, use:

- [ON ERROR GOTO](../statements/on-error-goto.md) - Set up error trap
- [ERR and ERL](../statements/err-erl-variables.md) - Get error number and line
- [ERROR](../statements/error.md) - Simulate an error
- [RESUME](../statements/resume.md) - Resume after error

## Example

```basic
10 ON ERROR GOTO 1000
20 INPUT "Enter a number"; N
30 PRINT "Square root is"; SQR(N)
40 END
1000 REM Error handler
1010 IF ERR = 5 THEN PRINT "Can't take square root of negative number"
1020 RESUME 20
```

## See Also

- [Error Handling Statements](../statements/index.md#error-handling)
- [ON ERROR GOTO](../statements/on-error-goto.md)
- [ERR and ERL Variables](../statements/err-erl-variables.md)