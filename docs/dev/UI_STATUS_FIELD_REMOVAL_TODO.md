# UI Status Field Removal - TODO

## Summary
The interpreter's status field has been removed and replaced with a simpler microprocessor-style model. The curses UI has been updated, but other UIs need the same changes.

## Completed
- ✅ **Curses UI** (src/ui/curses_ui.py) - Updated in v1.0.458-461

## Pending Updates

### TK UI (src/ui/tk_ui.py)
**Status checks to replace:**
```python
# OLD                                    # NEW
state.status == 'error'                  state.error_info is not None
state.status == 'waiting_for_input'      state.input_prompt is not None
state.status == 'done'                   runtime.halted and pc.halted()
state.status == 'paused'                 runtime.halted and not error_info
state.status == 'at_breakpoint'          runtime.halted and not error_info
state.status == 'running'                not runtime.halted and not error_info
```

**Runtime cleanup:**
- Create runtime once at startup (like curses UI does at line 1192)
- Never set `self.runtime = None`
- Remove all `if self.runtime:` and `if self.runtime else None` checks
- Runtime always exists after startup

### Web UI (src/ui/web_ui.py)
**Same status field changes as TK UI above**

**Runtime cleanup:**
- Create runtime once at startup
- Never set to None
- Remove unnecessary None checks

### CLI UI (cli.py or similar)
**Same status field changes as TK UI above**

**Runtime cleanup:**
- Create runtime once at startup
- Never set to None
- Remove unnecessary None checks

## Changes Required

### 1. Status Field Removal
The `InterpreterState.status` field no longer exists. Replace all status checks with:
- `runtime.halted` - program stopped (paused/done/breakpoint)
- `state.input_prompt` - waiting for INPUT
- `state.error_info` - error occurred

### 2. Runtime Management
- Create runtime once: `self.runtime = Runtime({}, {})`
- Never set to `None`
- Just call `runtime.reset_for_run()` when needed (on RUN command)
- Remove all defensive checks like `if self.runtime:` and `if self.runtime else None`

## Reference Implementation
See curses UI commits:
- v1.0.458: Status field removal
- v1.0.459-460: Runtime cleanup
- v1.0.461: Remove all runtime None checks

## Testing After Changes
1. Test RUN command
2. Test stepping (step statement, step line)
3. Test breakpoints
4. Test INPUT statements
5. Test error handling
6. Test CONT after breakpoint
