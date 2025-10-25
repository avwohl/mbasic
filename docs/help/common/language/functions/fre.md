# FRE

## Syntax

```basic
FRE(O) FRE (X$)
```

## Description

Arguments to FRE are dummy arguments.       FRE returns the number of bytes in memory not being used by BASIC-80. FRE("") forGes a garbage collection       before returning   the   number   of free bytes.     BE PATIENT: garbage collection may take 1 to 1-1/2 minutes.    BASIC   will not initiate garbage collection until all free memory has been used up.   Therefore, using FRE("") periodically will result in shorter delays for each        garbage collection.

## Example

```basic
PRINT FRE(O)
               14542
              Ok
```

## See Also

*Related functions will be linked here*
