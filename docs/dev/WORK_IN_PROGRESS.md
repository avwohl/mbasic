# Work in Progress: JavaScript Backend

## Date Started
2025-11-13

## Task
Design and implement JavaScript compiler backend

## Status
Phase 1-5: Implementation - Complete

## Branch
js-backend

## Goals
Create a new compiler backend that generates JavaScript code from BASIC programs.
Generated code should run in:
- Browser (standalone HTML + JS)
- Node.js (command-line via npm/node)

## Completed

### Phase 0: Design
- [x] Created design specification document (docs/design/JAVASCRIPT_BACKEND_SPEC.md)
- [x] Defined code generation strategy
- [x] Planned control flow handling (switch-based PC)
- [x] Designed runtime library structure
- [x] Specified I/O handling for browser vs Node.js

### Phase 1-4: Implementation
- [x] Created `src/codegen_js_backend.py` (800+ lines)
- [x] Implemented variable declarations and array initialization
- [x] Implemented expression generation (arithmetic, logic, strings, arrays)
- [x] Implemented all statement types:
  - [x] PRINT (with separators)
  - [x] LET (including array assignment)
  - [x] FOR/NEXT (variable-indexed with state tracking)
  - [x] GOTO/ON GOTO
  - [x] GOSUB/RETURN
  - [x] IF/THEN/ELSE
  - [x] WHILE/WEND
  - [x] READ/DATA/RESTORE
  - [x] END
- [x] Implemented runtime library:
  - [x] Print functions (browser and Node.js)
  - [x] Math functions (ABS, INT, SQR, SIN, COS, TAN, ATN, LOG, EXP)
  - [x] String functions (LEFT$, RIGHT$, MID$, LEN, CHR$, ASC, STR$, VAL)
  - [x] RND function with seeding
  - [x] GOSUB/RETURN stack
  - [x] FOR/NEXT state tracking
  - [x] DATA/READ/RESTORE support
- [x] Added CLI integration (`--compile-js` and `--html` flags)
- [x] Implemented HTML wrapper generation
- [x] Tested with hello world program - successful compilation!

### Phase 5: Enhanced Features (Complete)
- [x] Implemented INPUT statement (browser: prompt, Node.js: readline)
- [x] Implemented RANDOMIZE statement (with and without seed)
- [x] Implemented STOP statement
- [x] Implemented SWAP statement
- [x] Implemented DEF FN / FN calls
- [x] Implemented TAB() and SPC() functions
- [x] Implemented INSTR() function
- [x] Implemented SPACE$() and STRING$() functions
- [x] Implemented HEX$(), OCT$(), POS() functions
- [x] Implemented FIX(), SGN(), CINT(), CSNG(), CDBL() functions
- [x] Fixed GOSUB return address calculation
- [x] Fixed FOR loop skip when condition not met
- [x] Fixed NEXT without variable
- [x] Fixed DATA value collection (extract from AST nodes)
- [x] Fixed GOTO/GOSUB/IF attribute names (line_number vs target/then_line)
- [x] Tested compilation with multiple programs

### Next Steps
1. Test with more complex programs
2. Test Super Star Trek (ultimate test!)
3. Optimize generated code
4. Consider implementing MID$ assignment
5. Consider implementing PRINT USING

## Key Design Decisions

1. **Control Flow**: Use switch statement with PC variable (like VM)
   - Reason: JavaScript has no goto, switch provides clean jumping

2. **FOR Loops**: Variable-indexed approach (matching new interpreter)
   - Reason: Consistency with interpreter, handles Super Star Trek pattern

3. **Runtime Detection**: Check for `window` vs `process`
   - Reason: Single JS file works in both environments

4. **GOSUB/RETURN**: Call stack array
   - Reason: Simple, matches BASIC semantics

## Files to Create

- `src/codegen_js_backend.py` - Main backend
- `src/js_runtime.js` - Runtime library template
- `test_compile_js/` - Test directory
- `docs/user/JAVASCRIPT_BACKEND_GUIDE.md` - User docs

## References

- Design spec: `docs/design/JAVASCRIPT_BACKEND_SPEC.md`
- Existing C backend: `src/codegen_backend.py`
- Runtime: `src/runtime.py`
- Interpreter: `src/interpreter.py`

## Testing Strategy

1. Start with hello world
2. Test control flow (FOR, GOTO, GOSUB)
3. Test built-in functions
4. Test I/O (PRINT, INPUT, DATA/READ)
5. Ultimate test: Super Star Trek

## Notes

- Following same pattern as Z88dk backend for consistency
- JavaScript backend will be easier to use (no C compiler needed)
- Can embed in web pages for interactive BASIC
- Good for teaching/learning BASIC in browser
