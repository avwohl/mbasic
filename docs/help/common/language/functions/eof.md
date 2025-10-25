# EOF

## Syntax

```basic
EOF«file number»
```

**Versions:** Disk

## Description

Returns -1 (true) if the end of a sequential file has been reached.     Use EOF to test for end-of-file while INPUTting,  to avoid "Input past end" errors.

## Example

```basic
10 OPEN "I",l,"DATA"
              20 C=O
              30 IF EOF(l) THEN 100
              40 INPUT #l,M(C)
              50 C=C+l:GOTO 30
BASIC-80 FUNCTIONS                                    Page 3-7
```

## See Also

*Related functions will be linked here*
