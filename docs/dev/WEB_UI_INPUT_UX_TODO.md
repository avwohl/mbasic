# Web UI INPUT Statement UX - TODO

## Status: ⏳ Design Decision Needed

## Problem

The web UI needs to handle BASIC's `INPUT` statement, but there's a UX challenge:

**User Feedback:**
> "im not sure about INPUT dialog boxes. a lot of games have text to read before the input"

BASIC games often have extensive narrative text before INPUT prompts. Modal dialog boxes block viewing that text, which is poor UX.

## Current Implementation

- **TK UI**: Uses modal `simpledialog.askstring()` dialog
- **Web UI**: Placeholder that returns empty string (not yet implemented)

## Options

### Option 1: Modal Dialog (TK approach)
**Pros:**
- Simple to implement
- Clear separation of input from output
- Works with synchronous interpreter

**Cons:**
- ❌ Blocks view of previous output
- ❌ Bad UX for games with narrative text
- Breaks immersion

### Option 2: Inline Input Field
**Pros:**
- ✅ Can see all previous output
- ✅ Better for games/long text scenarios
- ✅ More terminal-like experience
- Natural reading flow

**Cons:**
- More complex to implement
- Need to coordinate async UI with synchronous interpreter

### Option 3: Hybrid Approach
Show output in main pane, but input field appears:
- Below the output (inline style)
- In a collapsible panel
- In a side panel

## Technical Challenge

The interpreter expects `input()` to return a value synchronously:

```python
def input(self, prompt=""):
    result = ???  # Must block until user enters value
    return result
```

But web UI is async/event-driven. Solutions:

### Solution A: Background Thread (Current TK Approach)
- Run interpreter in background thread
- `input()` can block the thread
- UI remains responsive
- **This is what TK does with tick-based execution**

### Solution B: Event/Queue Coordination
```python
def input(self, prompt=""):
    self.input_queue.put(prompt)
    # Wait for result from queue
    result = self.result_queue.get()  # Blocks
    return result
```
- More complex coordination
- Still needs threading

### Solution C: Fully Async Interpreter
- Major refactor of interpreter
- Would need to yield at INPUT points
- Changes interpreter architecture significantly

## Recommendation

**Use Option 2 (Inline Input) with Solution A (Background Thread)**

1. Show output in readonly textarea (current implementation)
2. When INPUT needed:
   - Append prompt to output
   - Show input field below output area
   - Program execution pauses (already using ticks)
   - User types input
   - On Enter: submit input, hide field, continue execution
3. Interpreter already runs with tick-based execution
4. INPUT can use a blocking queue/event mechanism

**Implementation Plan:**
1. Add input field UI element (hidden by default)
2. Create input queue/event system
3. When INPUT called:
   - Pause tick execution
   - Show input field
   - Wait for user input via queue
   - Hide input field
   - Resume execution
4. This gives inline UX without major interpreter refactor

## Priority

**MEDIUM** - INPUT works (returns empty), but UX needs improvement for games

## See Also

- `src/ui/web/nicegui_backend.py:35` - Current INPUT implementation with TODO
- `src/ui/tk_ui.py:3421` - TK's modal dialog approach
