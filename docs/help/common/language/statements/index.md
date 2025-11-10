---
search:
  exclude: true
---

# BASIC-80 Commands and Statements

All BASIC-80 commands and statements are described in this reference.

## Alphabetical Listing

### A
- [AUTO](auto.md) - Automatic line numbering

### C
- [CALL](call.md) - Call assembly language subroutine
- [CHAIN](chain.md) - Chain to another program
- [CLEAR](clear.md) - Clear program variables and set memory limits
- [CLOAD](cload.md) - Load program from cassette (not in VT180)
- [CLOSE](close.md) - Close file(s)
- [COMMON](common.md) - Define variables to pass to chained program
- [CONT](cont.md) - Continue program execution
- [CSAVE](csave.md) - Save program to cassette (not in VT180)

### D
- [DATA](data.md) - Store data values in program
- [DEF FN](def-fn.md) - Define user function
- [DEF USR](def-usr.md) - Define assembly language subroutine address (not implemented)
- [DEFINT/SNG/DBL/STR](defint-sng-dbl-str.md) - Set default variable types
- [DELETE](delete.md) - Delete program lines
- [DIM](dim.md) - Dimension arrays

### E
- [EDIT](edit.md) - Edit program line
- [END](end.md) - End program execution
- [ERASE](erase.md) - Erase arrays from memory
- [ERR and ERL](err-erl-variables.md) - Error number and line variables
- [ERROR](error.md) - Simulate error condition

### F
- [FIELD](field.md) - Allocate space for random file I/O
- [FOR...NEXT](for-next.md) - Loop structure

### G
- [GET](get.md) - Read record from random file
- [GOSUB...RETURN](gosub-return.md) - Call subroutine
- [GOTO](goto.md) - Branch to line number

### I
- [IF...THEN...ELSE](if-then-else-if-goto.md) - Conditional statement
- [INPUT](input.md) - Input from keyboard
- [INPUT#](input_hash.md) - Input from file
- [LINE INPUT](line-input.md) - Input entire line from keyboard
- [LINE INPUT#](inputi.md) - Input entire line from file

### K
- [KILL](kill.md) - Delete file from disk

### L
- [LET](let.md) - Assign value to variable
- [LIST](list.md) - List program lines
- [LLIST](llist.md) - List program to printer
- [LOAD](load.md) - Load program from disk
- [LPRINT](lprint-lprint-using.md) - Print to line printer

### M
- [MERGE](merge.md) - Merge program from disk
- [MID$](mid-assignment.md) - Replace characters in string

### N
- [NAME](name.md) - Rename disk file
- [NEW](new.md) - Delete program in memory
- [NULL](null.md) - Set null character count

### O
- [ON ERROR GOTO](on-error-goto.md) - Error trapping
- [ON...GOSUB/GOTO](on-gosub-on-goto.md) - Computed branch
- [OPEN](open.md) - Open file for I/O
- [OPTION BASE](option-base.md) - Set array lower bound
- [OUT](out.md) - Send byte to I/O port

### P
- [POKE](poke.md) - Write byte to memory location
- [PRINT](print.md) - Print to screen
- [PRINT#](printi-printi-using.md) - Print to file
- [PUT](put.md) - Write record to random file

### R
- [RANDOMIZE](randomize.md) - Seed random number generator
- [READ](read.md) - Read DATA values
- [REM](rem.md) - Remark/comment
- [RENUM](renum.md) - Renumber program lines
- [RESUME](resume.md) - Resume after error

### S
- [SAVE](save.md) - Save program to disk
- [STOP](stop.md) - Stop program execution
- [SWAP](swap.md) - Exchange two variables

### T
- [TRON/TROFF](tron-troff.md) - Trace on/off

### W
- [WAIT](wait.md) - Wait for I/O port condition
- [WHILE...WEND](while-wend.md) - While loop structure
- [WIDTH](width.md) - Set output line width
- [WRITE](write.md) - Write data to screen
- [WRITE#](writei.md) - Write data to file

## By Category

### Program Control
- [CHAIN](chain.md) - Chain to another program
- [CLEAR](clear.md) - Clear variables and memory
- [COMMON](common.md) - Pass variables to chained program
- [CONT](cont.md) - Continue execution
- [END](end.md) - End program
- [NEW](new.md) - Delete program
- [STOP](stop.md) - Stop execution

### Flow Control
- [FOR...NEXT](for-next.md) - Loop structure
- [GOSUB...RETURN](gosub-return.md) - Subroutine call
- [GOTO](goto.md) - Unconditional branch
- [IF...THEN...ELSE](if-then-else-if-goto.md) - Conditional
- [ON...GOSUB/GOTO](on-gosub-on-goto.md) - Computed branch
- [WHILE...WEND](while-wend.md) - While loop

### Input/Output
- [INPUT](input.md) - Keyboard input
- [LINE INPUT](line-input.md) - Line input from keyboard
- [LPRINT](lprint-lprint-using.md) - Print to printer
- [PRINT](print.md) - Print to screen
- [WRITE](write.md) - Write data to screen

### File I/O
- [CLOSE](close.md) - Close files
- [FIELD](field.md) - Define random file buffer
- [GET](get.md) - Read random file record
- [INPUT#](input_hash.md) - Input from file
- [LINE INPUT#](inputi.md) - Line input from file
- [OPEN](open.md) - Open file
- [PRINT#](printi-printi-using.md) - Print to file
- [PUT](put.md) - Write random file record
- [WRITE#](writei.md) - Write to file

### File Management
- [CLOAD](cload.md) - Load from cassette
- [CSAVE](csave.md) - Save to cassette
- [KILL](kill.md) - Delete file
- [LOAD](load.md) - Load program
- [MERGE](merge.md) - Merge program
- [NAME](name.md) - Rename file
- [SAVE](save.md) - Save program

### Data Handling
- [DATA](data.md) - Store data in program
- [READ](read.md) - Read DATA values

### Arrays
- [DIM](dim.md) - Dimension arrays
- [ERASE](erase.md) - Erase arrays
- [OPTION BASE](option-base.md) - Set array base

### Variables and Assignment
- [LET](let.md) - Variable assignment
- [SWAP](swap.md) - Exchange variables
- [DEFINT/SNG/DBL/STR](defint-sng-dbl-str.md) - Default types

### Functions
- [DEF FN](def-fn.md) - Define user function
- [DEF USR](def-usr.md) - Define assembly subroutine address (not implemented)

### Error Handling
- [ERR and ERL](err-erl-variables.md) - Error variables
- [ERROR](error.md) - Simulate error
- [ON ERROR GOTO](on-error-goto.md) - Error trap
- [RESUME](resume.md) - Resume after error

### String Manipulation
- [MID$](mid-assignment.md) - Replace substring

### Memory and Hardware
- [CALL](call.md) - Call machine language
- [OUT](out.md) - Output to port
- [POKE](poke.md) - Write to memory
- [WAIT](wait.md) - Wait for port

### Program Editing
- [AUTO](auto.md) - Automatic line numbering
- [DELETE](delete.md) - Delete program lines
- [EDIT](edit.md) - Edit program line (CLI line editor)
- [LIST](list.md) - List program lines
- [LLIST](llist.md) - List program to printer
- [RENUM](renum.md) - Renumber program lines

### System
- [NULL](null.md) - Set null character count
- [RANDOMIZE](randomize.md) - Seed RNG
- [REM](rem.md) - Comment
- [TRON/TROFF](tron-troff.md) - Trace mode
- [WIDTH](width.md) - Set line width

### Modern Extensions (MBASIC only)
- [HELPSETTING](helpsetting.md) - Display help for settings
- [LIMITS](limits.md) - Show interpreter limits
- [SET](setsetting.md) - Configure interpreter settings
- [SHOW SETTINGS](showsettings.md) - Display current settings

## See Also

- [Functions](../functions/index.md) - BASIC-80 intrinsic functions
- [Error Codes](../appendices/error-codes.md) - Error messages and codes
- [Examples](../../examples.md) - Example programs
