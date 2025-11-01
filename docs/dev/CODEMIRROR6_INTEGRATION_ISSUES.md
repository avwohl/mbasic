# CodeMirror 6 Integration Issues with NiceGUI

## Problem Summary

Attempted to integrate CodeMirror 6 into the MBASIC Web UI (NiceGUI-based) to provide statement-level highlighting features:
- Find highlighting (yellow background)
- Breakpoint markers (red line background)
- Current statement highlighting (green background during step debugging)

The integration failed due to module loading conflicts between CodeMirror 6's ES6 module system and NiceGUI's existing import map infrastructure.

## Technical Details

### What We Tried

1. **Standard Import Map** (v1.0.360)
   - Added `<script type="importmap">` with CodeMirror modules
   - **Issue**: Browser error "Multiple import maps are not allowed"
   - NiceGUI already creates its own import map, browsers only allow one

2. **Import Map Shim**
   - Changed to `<script type="importmap-shim">` to work with NiceGUI's es-module-shims
   - Used jsdelivr `+esm` format to bundle dependencies
   - **Issue**: Still had missing transitive dependencies (@marijn/find-cluster-break, etc.)

3. **Manual Dependency Listing**
   - Added all known CodeMirror dependencies to import map:
     - @codemirror/view, @codemirror/state, @codemirror/commands
     - style-mod, w3c-keyname, @lezer/common, @lezer/highlight, crelt
   - **Issue**: Still missing dependencies, CSS MIME type errors

### Root Causes

1. **Module System Conflict**: NiceGUI uses es-module-shims with its own import map for internal modules (nicegui-aggrid, etc.). CodeMirror 6 requires ES6 modules with complex dependency trees that conflict with this system.

2. **Transitive Dependencies**: CodeMirror 6 has many nested dependencies that must all be mapped. The dependency tree is deep and changes between versions.

3. **CSS Loading**: CDN-served CSS files had MIME type mismatches (text/plain vs text/css) due to browser security policies.

## Attempted Workarounds

- Using `+esm` format from jsdelivr (should bundle deps automatically, but didn't work with shims)
- Manually listing all dependencies (incomplete list)
- Using importmap-shim instead of importmap (still conflicts)

## Current Status

Reverted CodeMirror 6 integration. The code is still in the repository but disabled:
- `src/ui/web/codemirror_editor.py` - Python wrapper (exists but not used)
- `src/ui/web/codemirror_editor.js` - Vue component (exists but not used)
- `src/ui/web/codemirror_editor.css` - Styles (exists but not used)

The highlighting features (find, breakpoints, current statement) are still implemented in the backend Python code (nicegui_backend.py) and were working with CodeMirror in testing, but the module loading prevents the page from loading at all.

## Recommended Solutions

### Option 1: Use Simple Textarea (Current Approach)
**Pros**:
- No dependencies, works immediately
- Reliable, no module loading issues
- Can still add highlighting via background div overlays

**Cons**:
- More limited editor features (no syntax highlighting, code folding, etc.)
- Manual implementation of editor features

### Option 2: CodeMirror 5 (Legacy)
**Pros**:
- Uses simple `<script>` tags, no ES modules
- Well-tested, stable
- Similar API to CM6

**Cons**:
- Deprecated/unmaintained
- Larger bundle size
- Missing modern features

### Option 3: Monaco Editor
**Pros**:
- Modern, actively maintained (VS Code's editor)
- Rich features
- Has AMD/require.js loader that might work better

**Cons**:
- Larger bundle (~3MB minified)
- More complex API
- May have similar module loading issues

### Option 4: Ace Editor
**Pros**:
- Simple script inclusion
- Lightweight
- Good BASIC syntax support available

**Cons**:
- Less modern than CM6
- Smaller community

### Option 5: Download CodeMirror 6 Bundle
**Pros**:
- Serve CM6 as local static files via NiceGUI
- Full control over module resolution
- All dependencies bundled

**Cons**:
- Need to create/maintain custom bundle
- Increases repository size
- Build step required

## Recommended Path Forward

**Short term**: Continue with textarea approach. The highlighting features are already implemented and tested - they just need a working editor widget.

**Long term**: Option 5 (local CM6 bundle) or Option 4 (Ace) would provide the best balance of features and compatibility. Would need to:
1. Create a bundled version of CodeMirror 6 with all dependencies
2. Serve it as static files via `app.add_static_files()`
3. Load as a single script without import maps

## Files Affected

- `src/ui/web/nicegui_backend.py:1085-1097` - Import map code (now commented out)
- `src/ui/web/nicegui_backend.py:19` - CodeMirrorEditor import (still present)
- `src/ui/web/nicegui_backend.py:1119-1122` - Editor creation (using CodeMirrorEditor)
- `src/ui/web/codemirror_editor.py` - Full Python wrapper implementation
- `src/ui/web/codemirror_editor.js` - Full Vue component implementation
- `src/ui/web/codemirror_editor.css` - Styles for highlighting

## Next Steps

Need to decide:
1. Keep CodeMirror integration and create local bundle?
2. Switch to different editor (Ace, Monaco, CM5)?
3. Stick with textarea and implement minimal highlighting overlay?

The highlighting backend code is complete and working - just need a compatible editor widget.
