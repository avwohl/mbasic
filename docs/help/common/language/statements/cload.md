# CLOAD     THIS COMMAND IS NOT INCLUDED IN THE DEC VT180 VERSION

## Purpose

To load a program or an array from cassette tape into memory.

## Remarks

CLOAD executes a NEW command before it loads the program from cassette tape. <filename> is, the string expression or the first character of the string expression that was specified when the program was CSAVEd. CLOAD? verifies tapes by comparing the program currently in memory with the file on tape that has the same filename. If they are the same, BASIC prints Ok. If not, BASIC prints NO GOOD. CLOAD* loads a numeric array that has been saved on tape.    The data on tape is loaded into the array called <array name> specified when the array was CSAVE*ed. CLOAD and CLOAD? are always entered at command level as direct· mode commands. CLOAD* may be entered at command level or used as a program statement.    Make   sure the array has been DIMensioned before it is loaded.   BASIC always returns to COmmand level after a CLOAD, CLOAD? or CLOAD* is executed.      Before a CLOAD is executed, make sure the cassette recorder is properly connected and in the Play mode, and the tape is possitioned correctly. See also CSAVE, Section 2.9. NOTE:           CLOAD and CSAVE are not           included      in    all implementations of BASIC.

## Example

```basic
CLOAD "MAX2"
                Loads file "M" into memory.
MICROSOFT BASIC COMMANDS AND STATEMENTS                 Page 2-8
```

## See Also

*Related statements will be linked here*
