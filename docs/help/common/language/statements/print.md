# PRINT

## Syntax

```basic
PRINT [<list of expressions>]
PRINT USING <string   exp>~<list   of expressions>
```

**Versions:** SK, Extended, Disk Extended, Disk

## Purpose

To output data at the terminal. To print strings or numbers    using    a   specified format •. Remarks        <list of expressions> is comprised of the string and            expressions or numeric expressions that are to

## Remarks

If <list of expressions> is omitted, a blank line is printed.     If <list of expressions> is included, the values of the expressions are printed at the terminal. The expressions in the list may be numeric and/or string expressions. (Strings must be enclosed in quotation marks.) Print Positions The position of each printed item is determined by the punctuation used to separate the items in the list. BASIC-SO divides the line into print zones of 14 spaces each.        In the list of expressions, a comma causes the next value to be printed at the beginning of the next zone. A semicolon causes the next value to be printed immediately after the last value. Typing one or more spaces between expressions has the same effect as typing a semicolon. If a comma or a semicolon terminates the list of expressions, the next PRINT statement begins printing on the same line, spacing accordingly. If the list of expressions terminates without a comma or a semicolon, a carriage return is printed at the end of the line. If the printed line is longer than the terminal width, BASIC-SO goes to the next physical line and continues printing. Printed numbers are always followed by a space. Positive   numbers are preceded by a space. Negative numbers are preceded by a minus sign. Single precision numbers that can be represented with 6 or fewer digits in the unscaled format no less accurately than they can be represen.ted in the scaled format, are output using the unscaled format.   For eX9mple, 10A(-6) is output as .000001 and 10A(-7) is output as lE-7.    Double preclslon numbers that can be represented with 16 or fewer digits in the unscaled format no less accurately than they can be represented in the scaled format, are output using the unscaled format.' For example, 10A(-16) is output as .0000000000000001 and 10A(-17)    is output as 10-17. BASIC-80 COMMANDS AND STATEMENTS                            Page 2-61 A question mark may be used in place of the word PRINT in a PRINT statement. Example 1:   10 X=5 20 PRINT X+5, X-5, X*(-5), X""5 30 END RUN 10            a            -25                    3125 Ok In this example, the commas in the        PRINT statement cause each value to be printed at the beginning of the next print zone. Example 2:   LIST 10 INPUT X 20 PRINT X "SQUARED IS" X""2 "AND" 7 30 PRINT X "CUBED IS" X""3 40 PRINT 50 GOTO 10 Ok RUN ? 9 9 SQUARED IS 81 AND 9 CUBED IS 729 ? 21 21 SQUARED IS 441 AND 21 CUBED IS 9261 ? In this example, the semicolon at the end of line 20 causes both PRINT statements to be printed on the same line, and line 40 causes a blank line to be printed before the next prompt. Example 3:   10 FOR X = 1 TO 5 20 J=J+5 30 K=K+10 40 ?J7K7 50 NEXT X Ok RUN 5 10 10 20 15        30   20   40   25   50 Ok In this example, the semicolons in the PRINT statement   cause   each value to be printed immediately after the preceding value.   (Don~t forget, a number is always followed by a space and positive numbers are preceded by a space.) In line 40, a question mark is used instead of the word PRINT. BASIC-80 COMMANDS AND STATEMENTS                           Page 2-62 2.~0     PRINT USING

## Example

```basic
be printed, separated by semicolons.     <string
               exp> is a string literal (or variable) comprised
               of   special   formatting   ch?lracters.   These
               formatting characters (see below) determine the
               field and the format of the printed strings or
               numbers.
                          String Fields
               When PRINT USING is used to print strings, one
               of three formatting characters may be used to
               format the string field:
       "!"     Specifies that only the first character       in   the
               given string is to be printed.
"\n spaces\"     Specifies that 2+n characters from the string
               are to be printed. If the backslashes are typed
               with no spaces, two characters will be printed~
               with   one   space, three characters will be
               printed, and so on. If the string is longer
               than   the   field, the extra characters are
               ignored. If the field is lonnger than the
               string, the string will be left-justified in the
               field and padded with spaces on the right.
               Example:
               10 A$="LOOK":B$="OUT"
               30 PRINT USING "!"~A$~B$
               40 PRINT USING"\ \"~A$~B$
               50 PRINT USING"\    \"~A$~B$~"!!"
               RUN
               LO
               LOOKOUT
               LOOK OUT   !!
BASIC-80 COMMANDS AND STATEMENTS                    Page 2-63
    "&"    Specifies a variable length string field. When
           the field is specified with "&", the string is
           output exactly as input. Example:
           10 A$="LOOK" :B$="OUT"
           20 PRINT USING "!"~A$~
           30 PRINT USING "&"~B$
           RUN
           LOUT
                          Numeric Fields
           When PRINT USING is used to print numbers, the
           following special characters may be used to
           format the numeric field:
      #    A number sign is used to represent each digit
           position.   Digit positions are always filled.
           If the number to be printed has fewer digits
           than positions specified, the number will be
           right-justified (preceded by spaces)   in the
           field.
            A decimal point may be inserted at any position
            in the field.     If the format string specifies
            that a digit is to precede the decimal point,
            the digit will always be printed (as 0 if
            necessary). Numbers are rounded as necessary.
            PRINT USING    nit.iin~.78
             0.78
            PRINT USING    "##i.t#"~987.654
            987.65
            PRINT USING "ii.ii    "~10.2,5.3,66.789,.234
            10.20    5.30   66.79     0.23
            In the last example, three spaces were inserted
            at the end of the format string to separate the
            printed values on the line.
      +     A plus sign at the beginning or end of the
            format string will cause ·the sign of the number
            (plus or minus) to be printed before or after
            the number.
BASIC-80 COMMANDS AND STATEMENTS                        Page 2-64
           A minus sign at the end of the format field will
           cause negative numbers to be printed with a
           trailing minus sign.
            PRINT USING "+.....   ";-68.95,2.4,55.6,-.9
            -68.95    +2.40   +55.60    -0.90
            PRINT USING " •••• #-    ";-68.95,22.449,-7.01
            68.95-   22.45        7.01-
     **     A double asterisk at the beginning of the format
            string causes leading spaces in the numeric
            field to be filled with asterisks. The ** also
            specifies positions for two more digits.
            PRINT USING "** •• #   ";12.39,-0.9,765.1
            *12.4   *-0.9    765.1
     $$     A double dollar sign causes a dollar sign to be
            printed to the immediate left of the formatted
            number.   The $$ specifies two      more   digit
            positions, one of which is the dollar sign. The
            exponential format cannot be used with $$.
            Negative numbers cannot be used unless the minus
            sign trails to the right.
            PRINT USING "$$## •• '.";456.78
             $456.78
    **$    The **$ at the beginning of a format string
           combines the effects of the above two symbols.
           Leading spaces will be asterisk-filled and a
           dollar sign will be printed before the number.
           **$ specifies three more digit positions, one of
           which is the dollar sign.
            PRINT USING "**$ ••• '.";2.34
            ***$2.34
            A comma that is to the left of the decimal point
            in a formatting string causes a comma to be
            printed to the left of every third digit to the
            left of the decimal point. A comma that is at
            the en~ of the format string is printed as part
            of the string. A comma specifies another digit
            position. The comma has no effect if used with
            the exponential (AAAA) format.
            PRINT USING " •• '., ••• ";1234.5
            1,234.50
            PRINT USING " ••••••• ,";1234.5
            1234.50,
BASIC-80 COMMANDS AND STATEMENTS                   Page 2-65
           Four carats (or up-arrows) may be placed after
           the   digit   position   characters to specify
           exponential format. The four carats allow space
           for E+xx to be printed.       Any decimal point
           position may be specified.      The significant
           digits are left-justified, and the exponent is
           adjusted. Unless a leading + or trailing + or -
           is specified, one digit position will be used to
           the left of the decimal point to print a space
           or a minus sign.
            PRINT USING   "*#.#*~~~~";234.56
             2.35E+02
            PRINT USING   ".####~~~~-";888888
             .8889E+06
            PRINT USING "+.##AAAA";123
            +.12E+03
           An underscore in the format string causes the
           next   character to be output as a literal
           character.
            PRINT USING "_1##.#*_1 ";12.34
            112.341
            The literal character    itself   may   be   an
            underscore by placing "_" in the format string.
      %     If the number to be printed is larger than the
            specified numeric field, a percent sign is
            printed in front of the number.     If rounding
            causes the number to exceed the field, a percent
            sign will be printed in front of the rounded
            number.
            PRINT USING "##.##";111.22
            %111.22
            PRINT USING ".##";.999
            %1.00
            If the number of digits specified exceeds 24, an
            "Illegal function call" error will result.
BASIC-80 COMMANDS AND STATEMENTS                         Page 2-66
```

## See Also

*Related statements will be linked here*
