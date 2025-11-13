# Work in Progress: JavaScript Backend

## Date Started
2025-11-13

## Task
Design and implement JavaScript compiler backend

## Status
Phase 0: Design and Specification - Complete

## Branch
js-backend

## Goals
Create a new compiler backend that generates JavaScript code from BASIC programs.
Generated code should run in:
- Browser (standalone HTML + JS)
- Node.js (command-line via npm/node)

## Current Phase: Design Complete

### Completed
- [x] Created design specification document
- [x] Defined code generation strategy
- [x] Planned control flow handling (switch-based PC)
- [x] Designed runtime library structure
- [x] Specified I/O handling for browser vs Node.js
- [x] Outlined implementation phases

### Next Steps
1. Create `src/codegen_js_backend.py` skeleton
2. Implement basic code generation (variables, expressions)
3. Implement control flow (FOR, GOTO, GOSUB)
4. Create runtime library template
5. Test with simple programs

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
