# Writeable Flag Behavior

## Purpose
The `writeable` flag is a **performance optimization**, not a restriction. It indicates whether a string's data can be modified in place without affecting other strings.

## Key Principle
**The writeable flag should NEVER cause an operation to fail.** If a string is not writeable, the operation should transparently make a copy and proceed.

## Flag States

### writeable = 1
- String data is exclusively owned by this descriptor
- Can be modified in place
- Typical for newly allocated strings
- Example: `A$ = INPUT$` creates a writeable string

### writeable = 0
- String data is shared with other descriptors OR is constant
- Cannot be modified without affecting others
- Typical for:
  - Substrings created by LEFT$/RIGHT$/MID$
  - Strings that have been copied with `B$ = A$`
  - Source strings after substring operations

## Behavior for String Operations

### Direct Assignment (A$ = "new value")
- Always succeeds
- If writeable and new value fits: overwrites in place
- Otherwise: allocates new space

### MID$ Statement (MID$(A$, 3) = "XX")
- Always succeeds
- If writeable: modifies in place
- If not writeable:
  1. Makes a copy of the entire string
  2. Performs the MID$ assignment on the copy
  3. Updates descriptor to point to the copy

### Substring Operations (LEFT$/RIGHT$/MID$ functions)
- Create shared references when possible
- Mark source as not writeable (immutable)
- New substring is also not writeable

## Example Scenarios

### Scenario 1: Simple Assignment
```basic
10 A$ = "HELLO"       ' A$ is writeable
20 A$ = "HI"          ' Reuses A$'s space if it fits
```

### Scenario 2: Shared String Modification
```basic
10 A$ = "ABCDEFGH"    ' A$ is writeable
20 B$ = LEFT$(A$, 4)  ' B$ shares A$'s data, both become non-writeable
30 MID$(B$, 2) = "XX" ' B$ gets its own copy "AXXD", A$ unchanged
```

### Scenario 3: Constant String Modification
```basic
10 A$ = "CONSTANT"    ' A$ points to constant data, not writeable
20 MID$(A$, 1) = "X"  ' A$ gets heap copy, becomes writeable
```

## Implementation Pattern

```c
if (!dest->writeable) {
    /* Save original data */
    uint8_t *orig_data = dest->data;
    uint8_t orig_len = dest->len;

    /* Allocate new space */
    mb25_string_alloc(dest_id, required_size);

    /* Copy original data */
    memcpy(dest->data, orig_data, orig_len);

    /* Now writeable, proceed with modification */
}
/* Perform the operation */
```

## Benefits

1. **Transparent to BASIC programmer** - Operations always work
2. **Memory efficient** - Shares when possible, copies when necessary
3. **Performance optimization** - Avoids unnecessary copying
4. **Maintains semantics** - BASIC programs behave correctly

## Testing

See `test_mid_assign.c` for comprehensive tests of writeable flag behavior with:
- Writeable strings (modified in place)
- Shared strings (copy-on-write)
- Constant strings (copy to heap)
- Edge cases (beyond bounds, etc.)