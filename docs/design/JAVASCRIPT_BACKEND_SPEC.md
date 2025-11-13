# JavaScript Backend Specification

## Date
2025-11-13

## Overview

New compiler backend to generate JavaScript code from BASIC programs. Generated code runs in:
- **Browser**: Standalone HTML + JS files
- **Node.js**: Command-line execution via npm/node

## Goals

1. **Compatibility**: Match interpreter behavior as closely as possible
2. **Portability**: Single JS file works in both browser and Node.js
3. **Performance**: Fast execution, compile-time optimization
4. **Simplicity**: Readable generated code for debugging
5. **Self-contained**: Minimal external dependencies

## Architecture

### Overall Design

Similar to existing Z88dk C backend (`src/codegen_backend.py`):
- Parse BASIC → AST
- Walk AST and generate JavaScript code
- Include runtime library for BASIC built-in functions
- Generate standalone executable file

### File Structure

```
src/
  codegen_js_backend.py          # New backend (similar to codegen_backend.py)
  js_runtime.js                   # Runtime library template

output/
  program.js                      # Generated standalone JS
  program.html                    # Optional: wrapper for browser
```

## Code Generation Strategy

### Variables

BASIC variables map to JavaScript variables:

```javascript
// BASIC: A = 10
let a = 10;

// BASIC: NAME$ = "HELLO"
let name_str = "HELLO";

// BASIC: X% = 5
let x_int = 5;

// Type suffixes:
// $ → _str (string)
// % → _int (integer)
// ! → _sng (single precision, default)
// # → _dbl (double precision)
```

### Arrays

Use JavaScript arrays:

```javascript
// BASIC: DIM A(10)
let a = new Array(11).fill(0);  // 0-based or 1-based depending on OPTION BASE

// BASIC: DIM B$(5, 5)
let b_str = Array.from({length: 6}, () => new Array(6).fill(""));
```

### Control Flow

#### FOR/NEXT

Use variable-indexed approach (matching our new interpreter implementation):

```javascript
// BASIC:
// 10 FOR I = 1 TO 10 STEP 2
// 20   PRINT I
// 30 NEXT I

// JavaScript:
line_10:
{
  let _for_i_end = 10;
  let _for_i_step = 2;
  for (i = 1; ((_for_i_step > 0) ? (i <= _for_i_end) : (i >= _for_i_end)); i += _for_i_step) {
line_20:
    console.log(i);
line_30:
  }
}
```

**Key points**:
- Store end/step in temporaries (evaluated once at FOR time)
- Direction check: step > 0 or step < 0
- Natural JavaScript scoping handles variable reuse after GOTO

#### WHILE/WEND

Direct mapping to JavaScript while:

```javascript
// BASIC:
// 10 WHILE X < 10
// 20   X = X + 1
// 30 WEND

line_10:
while (x < 10) {
line_20:
  x = x + 1;
line_30:
}
```

#### GOSUB/RETURN

Use call stack:

```javascript
// Runtime function
const _gosub_stack = [];

function _gosub(line) {
  _gosub_stack.push(line);
}

function _return() {
  if (_gosub_stack.length === 0) {
    throw new Error("RETURN without GOSUB");
  }
  const target = _gosub_stack.pop();
  return target;
}

// BASIC:
// 10 GOSUB 100
// 20 END
// 100 PRINT "SUB"
// 110 RETURN

line_10:
  _gosub(20);
  goto_100();
line_20:
  process.exit(0);

function goto_100() {
line_100:
  console.log("SUB");
line_110:
  const ret = _return();
  if (ret === 20) goto line_20;
}
```

#### GOTO/ON GOTO

JavaScript doesn't have goto, so use labeled blocks + functions:

**Option 1: Functions for each line block**
```javascript
function line_10() {
  console.log("Line 10");
  line_20();  // goto 20
}

function line_20() {
  console.log("Line 20");
}

line_10();
```

**Option 2: Switch statement**
```javascript
let pc = 10;
while (true) {
  switch (pc) {
    case 10:
      console.log("Line 10");
      pc = 20;
      break;
    case 20:
      console.log("Line 20");
      pc = null;
      break;
    default:
      return;
  }
  if (pc === null) return;
}
```

**Recommendation**: Use Option 2 (switch) - cleaner for complex control flow.

### Built-in Functions

Implement BASIC functions in runtime library:

```javascript
// Math functions
function _abs(x) { return Math.abs(x); }
function _int(x) { return Math.floor(x); }
function _sqr(x) { return Math.sqrt(x); }
function _sin(x) { return Math.sin(x); }
function _cos(x) { return Math.cos(x); }
function _tan(x) { return Math.tan(x); }
function _atn(x) { return Math.atan(x); }
function _log(x) { return Math.log(x); }
function _exp(x) { return Math.exp(x); }
function _rnd(x) {
  // MBASIC RND behavior:
  // RND(1) or RND(any positive) = next random [0,1)
  // RND(0) = repeat last random
  // RND(negative) = seed with x
  if (x > 0 || x === undefined) {
    _rnd_last = Math.random();
  } else if (x < 0) {
    // Seed (JavaScript doesn't allow seeding Math.random, use simple LCG)
    _rnd_seed = Math.abs(x);
  }
  return _rnd_last;
}
let _rnd_last = 0.5;
let _rnd_seed = 0.5;

// String functions
function _left(str, n) { return str.substring(0, n); }
function _right(str, n) { return str.substring(str.length - n); }
function _mid(str, start, len) {
  if (len === undefined) return str.substring(start - 1);
  return str.substring(start - 1, start - 1 + len);
}
function _len(str) { return str.length; }
function _chr(n) { return String.fromCharCode(n); }
function _asc(str) { return str.charCodeAt(0); }
function _str(n) { return " " + n; }  // BASIC STR$ adds leading space for positive
function _val(str) { return parseFloat(str.trim()) || 0; }
function _instr(haystack, needle, start) {
  const pos = haystack.indexOf(needle, (start || 1) - 1);
  return pos === -1 ? 0 : pos + 1;
}
```

### I/O

#### PRINT

Browser: append to output div
Node.js: console.log

```javascript
function _print(str, newline = true) {
  if (typeof window !== 'undefined') {
    // Browser
    const output = document.getElementById('output');
    if (output) {
      output.textContent += str;
      if (newline) output.textContent += '\n';
    }
  } else if (typeof process !== 'undefined') {
    // Node.js
    if (newline) {
      console.log(str);
    } else {
      process.stdout.write(str);
    }
  }
}
```

#### INPUT

Browser: use prompt() or custom input form
Node.js: use readline-sync (optional dependency) or async readline

```javascript
// Browser (synchronous with prompt)
function _input_browser(prompt_text) {
  return window.prompt(prompt_text || "? ");
}

// Node.js (requires readline-sync package, or use async)
function _input_node(prompt_text) {
  const readline = require('readline-sync');
  return readline.question(prompt_text || "? ");
}

function _input(prompt_text) {
  if (typeof window !== 'undefined') {
    return _input_browser(prompt_text);
  } else {
    return _input_node(prompt_text);
  }
}
```

#### File I/O

Browser: localStorage or File API
Node.js: fs module

```javascript
// Simplified - full implementation would match BASIC file I/O semantics
function _open_file(filename, mode) {
  if (typeof window !== 'undefined') {
    // Browser: use localStorage
    // (limited, but works for simple cases)
  } else {
    // Node.js: use fs
    const fs = require('fs');
    // ... implement file operations
  }
}
```

### DATA/READ/RESTORE

Compile DATA statements to array:

```javascript
// BASIC:
// 10 DATA 1, 2, 3, "HELLO", 4
// 20 READ A, B, C, D$, E

const _data = [1, 2, 3, "HELLO", 4];
let _data_ptr = 0;

function _read() {
  if (_data_ptr >= _data.length) {
    throw new Error("Out of DATA");
  }
  return _data[_data_ptr++];
}

function _restore(line) {
  _data_ptr = 0;  // Or specific line offset
}

// Generated code:
line_20:
  a = _read();
  b = _read();
  c = _read();
  d_str = _read();
  e = _read();
```

### Error Handling

```javascript
function _error(msg, line) {
  throw new Error(`?${msg} in line ${line}`);
}

// Wrap program in try/catch
try {
  main();
} catch (e) {
  _print(`Error: ${e.message}`);
  if (typeof process !== 'undefined') {
    process.exit(1);
  }
}
```

## Output Formats

### 1. Standalone JavaScript (.js)

```javascript
#!/usr/bin/env node
// Generated by MBASIC-2025 JavaScript Backend
// Source: program.bas

(function() {
  'use strict';

  // Runtime library
  const _gosub_stack = [];
  function _print(str) { /* ... */ }
  // ... more runtime functions

  // Variables
  let a = 0;
  let name_str = "";

  // Program
  function main() {
    let pc = 10;
    while (pc !== null) {
      switch (pc) {
        case 10:
          _print("HELLO WORLD");
          pc = null;
          break;
      }
    }
  }

  // Run
  try {
    main();
  } catch (e) {
    console.error(e.message);
    if (typeof process !== 'undefined') process.exit(1);
  }
})();
```

Can run with:
- Browser: `<script src="program.js"></script>`
- Node: `node program.js` or `chmod +x program.js && ./program.js`

### 2. HTML Wrapper (.html)

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>MBASIC Program</title>
  <style>
    body { font-family: monospace; background: black; color: white; padding: 20px; }
    #output { white-space: pre; }
  </style>
</head>
<body>
  <div id="output"></div>
  <script src="program.js"></script>
</body>
</html>
```

## Implementation Plan

### Phase 1: Basic Structure
- [ ] Create `src/codegen_js_backend.py`
- [ ] Copy structure from `codegen_backend.py`
- [ ] Implement JavaScript code generator class
- [ ] Generate variables and simple expressions

### Phase 2: Control Flow
- [ ] Implement switch-based PC execution
- [ ] FOR/NEXT loops
- [ ] WHILE/WEND
- [ ] GOTO/ON GOTO
- [ ] GOSUB/RETURN

### Phase 3: Built-in Functions
- [ ] Math functions
- [ ] String functions
- [ ] Type conversions

### Phase 4: I/O
- [ ] PRINT statements
- [ ] INPUT statements
- [ ] DATA/READ/RESTORE

### Phase 5: Runtime Library
- [ ] Create `src/js_runtime.js` template
- [ ] Browser compatibility
- [ ] Node.js compatibility
- [ ] Environment detection

### Phase 6: Testing
- [ ] Test with simple programs
- [ ] Test control flow (FOR, GOTO, GOSUB)
- [ ] Test Super Star Trek (the ultimate test!)
- [ ] Browser testing
- [ ] Node.js testing

### Phase 7: Integration
- [ ] Add to mbasic CLI: `mbasic --compile-js program.bas`
- [ ] Generate HTML wrapper option
- [ ] Documentation

## Advantages over Z88dk Backend

1. **No external dependencies**: JavaScript is built-in to browsers and Node.js
2. **Cross-platform**: Works on Windows, Mac, Linux, any browser
3. **Fast compile**: No C compiler needed
4. **Easy debugging**: Generated JS is readable
5. **Interactive**: Can embed in web pages
6. **Modern**: Leverage JavaScript ecosystem (npm packages, web APIs)

## Challenges

1. **No true GOTO**: Must use switch statement or function calls
2. **INPUT in browser**: Need UI for input (prompt is blocking and ugly)
3. **File I/O**: Different APIs for browser vs Node
4. **Random seed**: Math.random() can't be seeded (need custom RNG)
5. **Performance**: Interpreted JS slower than compiled C (but still fast enough)

## Future Enhancements

1. **Graphics**: Canvas API in browser for CIRCLE, LINE, PSET
2. **Sound**: Web Audio API for SOUND, PLAY
3. **Async I/O**: Non-blocking INPUT with callbacks
4. **WebAssembly**: Compile to WASM for better performance
5. **TypeScript**: Generate TypeScript for type safety
6. **Minification**: Compress generated code for smaller files
7. **Source maps**: Map JS back to BASIC line numbers for debugging

## Files to Create

- `src/codegen_js_backend.py` - Main backend implementation
- `src/js_runtime.js` - Runtime library template
- `docs/user/JAVASCRIPT_BACKEND_GUIDE.md` - User documentation
- `test_compile_js/` - Test directory (like test_compile/)

## References

- Existing Z88dk backend: `src/codegen_backend.py`
- Runtime implementation: `src/runtime.py`
- Interpreter: `src/interpreter.py`
- AST nodes: `src/ast_nodes.py`

## Success Criteria

A JavaScript backend is successful when:
1. ✅ Compiles simple BASIC programs to working JavaScript
2. ✅ Runs in both browser and Node.js
3. ✅ Handles all control flow (FOR, GOTO, GOSUB)
4. ✅ Supports built-in functions (math, strings)
5. ✅ Super Star Trek compiles and runs correctly
6. ✅ Generated code is readable and maintainable
