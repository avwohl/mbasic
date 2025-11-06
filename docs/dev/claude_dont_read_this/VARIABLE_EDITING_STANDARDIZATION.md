# Variable Editing Standardization Across UIs

**Created:** 2025-10-29
**Purpose:** Document and standardize how variable editing works across all MBASIC UIs

## Current Implementation Status

### CLI
- **View variables:** Immediate mode (`PRINT A`) or new WATCH command
- **Edit variables:** Immediate mode assignment (`A = 100`)
- **Status:** ✅ Works via immediate mode

### Curses
- **View variables:** Ctrl+W opens variables window
- **Edit variables:** Limited support (mentioned as ⚠️ in tracking)
- **Status:** ⚠️ Partial implementation

### Tk
- **View variables:** Ctrl+V opens variables window
- **Edit variables:** Double-click on variable in window
- **Status:** ✅ Full implementation

### Web
- **View variables:** Ctrl+V opens variables panel
- **Edit variables:** Double-click to edit
- **Status:** ✅ Full implementation

### Visual
- **View variables:** Not implemented
- **Edit variables:** Not implemented
- **Status:** ❌ Stub only

## Proposed Standard Behavior

### 1. Viewing Variables

**Standard Keybinding:** Ctrl+V (Variables)
- Opens a variables window/panel/view
- Shows all defined variables
- Updates in real-time during execution

**Display Format:**
```
Name    Type      Value
----    ----      -----
A       Integer   42
B$      String    "Hello"
C()     Array     (10 elements)
```

### 2. Editing Variables

**Standard Interaction:**
- **Double-click** (GUI): Opens edit dialog
- **Enter key** (Terminal): Starts inline editing
- **Context menu**: Right-click → Edit Value

**Edit Dialog Requirements:**
1. Show current value
2. Validate new value matches type
3. Cancel option (Esc key)
4. Confirm option (Enter key)

### 3. Variable Filtering

**Standard Features:**
- Search box to filter by name
- Case-insensitive search
- Real-time filtering as you type

### 4. Variable Sorting

**Standard Sort Options:**
- By Name (alphabetical)
- By Type (group by type)
- By Value (numeric/alphabetical)
- By Access Time (most recently accessed)
- By Write Time (most recently modified)

**Default:** By Name (ascending)

## Implementation Requirements

### For CLI
```basic
WATCH           - List all variables
WATCH A         - Show specific variable
WATCH A=10      - Set variable value (new feature)
```

### For Curses
Need to implement:
1. Inline editing in variables window
2. Validation of new values
3. Esc to cancel, Enter to confirm

### For Tk (Already Complete)
Current implementation is the standard

### For Web (Already Complete)
Current implementation follows the standard

## Type Validation Rules

### Integer Variables (%)
- Accept: Whole numbers -32768 to 32767
- Reject: Decimals, strings, out of range

### Single/Double Precision (!, #)
- Accept: Any numeric value
- Convert: Strings that parse as numbers
- Reject: Non-numeric strings

### String Variables ($)
- Accept: Any text
- Auto-quote if not provided
- Max length: 255 characters (MBASIC limit)

### Arrays
- Show dimensions and size
- Allow editing individual elements
- Format: `A(5) = value` to edit element

## Error Handling

### Invalid Value Entered
- Show error message: "Invalid value for type [type]"
- Restore original value
- Keep edit dialog open for retry

### Variable Not Found
- Show: "Variable [name] not defined"
- Offer to create it (in immediate mode only)

### Type Mismatch
- Show: "Type mismatch: expected [type], got [type]"
- Provide format hint

## Accessibility

### Keyboard Navigation
- **Tab**: Move between variables
- **Arrow keys**: Navigate list
- **Enter**: Start editing
- **Esc**: Cancel editing
- **Ctrl+F**: Focus search box

### Screen Reader Support
- Announce variable name, type, and value
- Announce when entering/exiting edit mode
- Read error messages

## Testing Requirements

### Test Cases
1. Edit integer variable with valid value
2. Edit integer variable with invalid value (string)
3. Edit string variable
4. Edit array element
5. Cancel edit operation
6. Edit during program execution (should work)
7. Edit undefined variable (should error)

### UI-Specific Tests
- **CLI**: Test WATCH A=10 syntax
- **Curses**: Test inline editing
- **Tk**: Test double-click dialog
- **Web**: Test async value updates

## Migration Plan

### Phase 1: Document Current State ✅
- Complete (this document)

### Phase 2: Implement CLI Enhancement
- Add `WATCH var=value` syntax
- Estimated: 1 hour

### Phase 3: Fix Curses Editing
- Add inline editing support
- Add validation
- Estimated: 2 hours

### Phase 4: Verify Tk/Web Compliance
- Ensure both follow standard
- Add any missing features
- Estimated: 1 hour

### Phase 5: Update Documentation
- Update help files
- Update UI tracking spreadsheet
- Estimated: 1 hour

## Benefits

1. **Consistency**: Same behavior across all UIs
2. **Discoverability**: Standard shortcuts work everywhere
3. **Productivity**: Quick variable inspection/modification
4. **Debugging**: Essential for effective debugging
5. **Learning**: Users learn once, use everywhere

## Related Documentation

- `UI_FEATURE_PARITY_TRACKING.md` - Overall UI feature tracking
- Individual UI help files in `docs/help/ui/`
- MBASIC variable documentation