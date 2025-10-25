# WAIT

## Syntax

```basic
WAIT <port number>, • I[,J]
where I and J are integer expressions
```

## Purpose

To suspend program execution while      monitoring the status of a machine input port.

## Remarks

The WAIT statement causes execution to       be suspended until a specified machine input port develops a specified bit pattern. The data read at the port is exclusive OR~ed with the integer expression J, and then AND~ed with 1.   If the result is zero, BASIC-80 loops back and reads the data at the port again. If the result is nonzero,   execution continues with the next statement. If J is omitted, it is assumed to be zero CAUTION:      It is possible to enter an infinite loop with the WAIT statement, in which case it will be necessary to manually restart the machine.

## Example

```basic
100 WAIT 32,2
BASIC-80 COMMANDS AND STATEMENTS                       Page 2-82
```

## See Also

*Related statements will be linked here*
