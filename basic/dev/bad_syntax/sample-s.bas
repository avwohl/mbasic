Rem   Sample program in S-BASIC to count to 10,000

$LIST	Rem   Suppress listing for better compiler speed

Rem   NOTE that the obvious way of testing for even multiples of 1000
Rem	(in the loop in version 2 of the program), using the INT function,
Rem	will not work with SBASIC using integer variables, just as with
Rem	CBASIC-2 (every number gets printed), and that, as with CBASIC-2,
Rem	using floating-point variables, with which the INT function will work,
Rem	gives a program that is almost as slow as the equivalent SAMPLE/C.BAS
Rem	(over 3.5 minutes (!), in this case). So once again, the same
Rem	type of trick was used, in the version appearing below.

$CONSTANT   Start.number = 1
$CONSTANT   End.number = 10000
$CONSTANT   Interval = 1000

VAR Number = Integer
VAR Start = Char

   Print Chr$ (7); "Counting program in S-BASIC"
   Print
   Input2 "Press <RETURN> to start: "; Start
   Print
   Print "Counting ..."
   Print

   FOR Number = Start.number TO End.number
Rem   (Remove next two "Rem's" for version 2 of the program)
Rem   IF (Number / Interval) * Interval = Number THEN \
Rem	 Print Number
   NEXT Number
   Print

   Print Chr$ (7); "Finished -- Good-bye"
   Print

END
