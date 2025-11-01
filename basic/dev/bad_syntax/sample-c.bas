Rem   Sample program in CBASIC-2 to count to 10,000

%NOLIST   Rem	Suppress listing for better compiler speed

Rem   NOTE that the obvious way of testing for even multiples of 1000
Rem	(in the loop in version 2 of the program), using the INT function,
Rem	will not work with CBASIC-2 (every number gets printed), and that
Rem	using floating-point variables (no "%" added to names), with which
Rem	the INT function will work, gives a program that is INCREDIBLY slow:
Rem	over 7 minutes (!) on my North Star. This is the reason for the
Rem	somewhat convoluted logic in the version appearing below.

Rem   Define constants (as integer variables for speed):
    Start.number% = 1
    End.number% = 10000
    Interval% = 1000

  Print Chr$ (7); "Counting program in CBASIC-2"
  Print
  Input "Press <RETURN> to start: "; LINE Go$
  Print
  Print "Counting ..."
  Print

  FOR Number% = Start.number% TO End.number%
Rem   (Remove next two "Rem's" for version 2 of the program)
Rem IF (Number% / Interval%) * Interval% = Number% THEN \
Rem   Print Number%
  NEXT Number%
  Print

  Print Chr$ (7); "Finished -- Good-bye"
  Print

END
