# Storage Abstraction Layer Design

## Design Philosophy

**Leverage NiceGUI's built-in storage** rather than creating a parallel system:
- NiceGUI already handles in-memory vs Redis via `app.storage.client`
- NiceGUI already handles session management and cookies
- NiceGUI already handles Redis connection pooling

**Our job**: Make the backend state serializable so NiceGUI can store it.

## Key Insight

Currently (line 3263):
```python
app.storage.client['backend'] = backend  # Stores entire NiceGUIBackend instance
```

**Problem**: NiceGUIBackend contains non-serializable objects (UI elements, timers, async futures, file handles)

**Solution**: Don't store the backend instance - store serializable session state dict instead:
```python
app.storage.client['session_state'] = backend.serialize_state()
# Later:
state = app.storage.client.get('session_state')
if state:
    backend.restore_state(state)
```

## Architecture

### No New Classes Needed!

Instead of creating `StorageBackend`, `InMemoryStorage`, `RedisStorage` classes, we simply:

1. **Add serialization methods to NiceGUIBackend**:
   - `serialize_state() -> dict`
   - `restore_state(state: dict) -> None`

2. **Use NiceGUI's storage as-is**:
   - Default: `app.storage.client` uses in-memory dict
   - With `NICEGUI_REDIS_URL`: `app.storage.client` uses Redis automatically

3. **Configuration**: Single environment variable
   ```bash
   export NICEGUI_REDIS_URL="redis://localhost:6379/0"  # Enable Redis
   # If not set: uses in-memory storage (default)
   ```

## Implementation Plan

### Phase 1: Add Serialization to NiceGUIBackend

#### Step 1: Create Session State Class (Optional but Recommended)
```python
from dataclasses import dataclass, asdict
from typing import Optional, List, Dict, Any
import json

@dataclass
class SessionState:
    """Serializable session state for NiceGUIBackend."""
    version: str = "1.0"
    session_id: str = ""

    # Program content
    program_lines: Dict[int, str] = None

    # Runtime state (serialized separately)
    runtime_state: Dict[str, Any] = None

    # Execution state
    running: bool = False
    paused: bool = False
    output_text: str = ""
    current_file: Optional[str] = None
    recent_files: List[str] = None
    last_save_content: str = ""

    # Configuration
    max_recent_files: int = 10
    auto_save_enabled: bool = True
    auto_save_interval: int = 30

    # Find/Replace state
    last_find_text: str = ""
    last_find_position: int = 0
    last_case_sensitive: bool = False

    # Editor state
    editor_content: str = ""
    editor_cursor: Optional[int] = None

    def to_dict(self) -> dict:
        """Convert to dictionary for storage."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> 'SessionState':
        """Create from dictionary."""
        return cls(**data)

    def to_json(self) -> str:
        """Serialize to JSON."""
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_str: str) -> 'SessionState':
        """Deserialize from JSON."""
        return cls.from_dict(json.loads(json_str))
```

#### Step 2: Add Methods to NiceGUIBackend

```python
class NiceGUIBackend(UIBackend):

    def serialize_state(self) -> dict:
        """Serialize backend state for storage.

        Returns:
            dict: Serializable state dictionary
        """
        # Close any open files before serialization
        self._close_all_files()

        state = SessionState(
            session_id=self.sandboxed_fs.user_id,
            program_lines=self._serialize_program(),
            runtime_state=self._serialize_runtime(),
            running=self.running,
            paused=self.paused,
            output_text=self.output_text,
            current_file=self.current_file,
            recent_files=self.recent_files.copy(),
            last_save_content=self.last_save_content,
            max_recent_files=self.max_recent_files,
            auto_save_enabled=self.auto_save_enabled,
            auto_save_interval=self.auto_save_interval,
            last_find_text=self.last_find_text,
            last_find_position=self.last_find_position,
            last_case_sensitive=self.last_case_sensitive,
            editor_content=self.editor.value if self.editor else "",
        )

        return state.to_dict()

    def restore_state(self, state_dict: dict) -> None:
        """Restore backend state from storage.

        Args:
            state_dict: State dictionary from serialize_state()
        """
        state = SessionState.from_dict(state_dict)

        # Restore program
        self._restore_program(state.program_lines)

        # Restore runtime
        self._restore_runtime(state.runtime_state)

        # Recreate interpreter with restored runtime
        self._recreate_interpreter()

        # Restore execution state
        self.running = state.running
        self.paused = state.paused
        self.output_text = state.output_text
        self.current_file = state.current_file
        self.recent_files = state.recent_files
        self.last_save_content = state.last_save_content

        # Restore configuration
        self.max_recent_files = state.max_recent_files
        self.auto_save_enabled = state.auto_save_enabled
        self.auto_save_interval = state.auto_save_interval

        # Restore find/replace
        self.last_find_text = state.last_find_text
        self.last_find_position = state.last_find_position
        self.last_case_sensitive = state.last_case_sensitive

        # Restore editor content (if UI is built)
        if self.editor:
            self.editor.set_value(state.editor_content)

        # Update UI to reflect restored state
        self._update_ui_from_state()

    def _serialize_program(self) -> Dict[int, str]:
        """Serialize program lines."""
        return {line.line_number: line.text
                for line in self.program.get_lines()}

    def _serialize_runtime(self) -> dict:
        """Serialize runtime state."""
        # Close open files first
        open_file_numbers = list(self.runtime.files.keys())
        for file_num in open_file_numbers:
            try:
                self.runtime.files[file_num].close()
            except:
                pass
        self.runtime.files.clear()

        # For now, use pickle for AST nodes (statement_table, user_functions)
        # TODO: Consider JSON representation of AST for better compatibility
        import pickle

        return {
            'variables': self.runtime._variables,
            'arrays': self.runtime._arrays,
            'variable_case_variants': self.runtime._variable_case_variants,
            'array_element_tracking': self.runtime._array_element_tracking,
            'common_vars': self.runtime.common_vars,
            'array_base': self.runtime.array_base,
            'option_base_executed': self.runtime.option_base_executed,
            'pc': {'line': self.runtime.pc.line_num, 'stmt': self.runtime.pc.stmt_offset} if self.runtime.pc else None,
            'npc': {'line': self.runtime.npc.line_num, 'stmt': self.runtime.npc.stmt_offset} if self.runtime.npc else None,
            'statement_table': pickle.dumps(self.runtime.statement_table).hex(),  # Hex encoding for JSON
            'halted': self.runtime.halted,
            'execution_stack': self.runtime.execution_stack,
            'for_loop_vars': self.runtime.for_loop_vars,
            'line_text_map': self.runtime.line_text_map,
            'data_items': self.runtime.data_items,
            'data_pointer': self.runtime.data_pointer,
            'data_line_map': self.runtime.data_line_map,
            'user_functions': pickle.dumps(self.runtime.user_functions).hex(),
            'field_buffers': self.runtime.field_buffers,
            'error_handler': self.runtime.error_handler,
            'error_handler_is_gosub': self.runtime.error_handler_is_gosub,
            'rnd_last': self.runtime.rnd_last,
            'stopped': self.runtime.stopped,
            'breakpoints': [{'line': bp.line_num, 'stmt': bp.stmt_offset} for bp in self.runtime.breakpoints],
            'break_requested': self.runtime.break_requested,
            'trace_on': self.runtime.trace_on,
            'trace_detail': self.runtime.trace_detail,
        }

    def _restore_runtime(self, state: dict) -> None:
        """Restore runtime from serialized state."""
        import pickle
        from src.pc import PC

        self.runtime._variables = state['variables']
        self.runtime._arrays = state['arrays']
        self.runtime._variable_case_variants = state['variable_case_variants']
        self.runtime._array_element_tracking = state['array_element_tracking']
        self.runtime.common_vars = state['common_vars']
        self.runtime.array_base = state['array_base']
        self.runtime.option_base_executed = state['option_base_executed']
        self.runtime.pc = PC(state['pc']['line'], state['pc']['stmt']) if state['pc'] else PC.halted_pc()
        self.runtime.npc = PC(state['npc']['line'], state['npc']['stmt']) if state['npc'] else None
        self.runtime.statement_table = pickle.loads(bytes.fromhex(state['statement_table']))
        self.runtime.halted = state['halted']
        self.runtime.execution_stack = state['execution_stack']
        self.runtime.for_loop_vars = state['for_loop_vars']
        self.runtime.line_text_map = state['line_text_map']
        self.runtime.data_items = state['data_items']
        self.runtime.data_pointer = state['data_pointer']
        self.runtime.data_line_map = state['data_line_map']
        self.runtime.user_functions = pickle.loads(bytes.fromhex(state['user_functions']))
        self.runtime.field_buffers = state['field_buffers']
        self.runtime.error_handler = state['error_handler']
        self.runtime.error_handler_is_gosub = state['error_handler_is_gosub']
        self.runtime.rnd_last = state['rnd_last']
        self.runtime.stopped = state['stopped']
        self.runtime.breakpoints = {PC(bp['line'], bp['stmt']) for bp in state['breakpoints']}
        self.runtime.break_requested = state['break_requested']
        self.runtime.trace_on = state['trace_on']
        self.runtime.trace_detail = state['trace_detail']
```

### Phase 2: Modify Page Handler

Current code (line 3243-3266):
```python
@ui.page('/', viewport='width=device-width, initial-scale=1.0')
def main_page():
    """Create a new backend instance for each client."""
    # ... create program_manager ...
    backend = NiceGUIBackend(None, program_manager)
    app.storage.client['backend'] = backend  # OLD WAY
    backend.build_ui()
```

New code:
```python
@ui.page('/', viewport='width=device-width, initial-scale=1.0')
def main_page():
    """Create/restore backend for each client."""
    from src.editing.manager import ProgramManager
    from src.ast_nodes import TypeInfo

    # Try to restore existing session state
    saved_state = app.storage.client.get('session_state')

    if saved_state:
        # Restore from existing session
        # Create default program_manager (will be overwritten by restore)
        def_type_map = {letter: TypeInfo.SINGLE for letter in 'abcdefghijklmnopqrstuvwxyz'}
        program_manager = ProgramManager(def_type_map)
        backend = NiceGUIBackend(None, program_manager)
        backend.restore_state(saved_state)
    else:
        # New session - create fresh backend
        def_type_map = {letter: TypeInfo.SINGLE for letter in 'abcdefghijklmnopqrstuvwxyz'}
        program_manager = ProgramManager(def_type_map)
        backend = NiceGUIBackend(None, program_manager)

    # Build UI (creates UI elements)
    backend.build_ui()

    # Save state on page exit/refresh (NiceGUI handles this)
    def save_on_disconnect():
        app.storage.client['session_state'] = backend.serialize_state()

    ui.context.client.on_disconnect(save_on_disconnect)
```

### Phase 3: Configuration

Add to `ui.run()` call:
```python
import os

ui.run(
    title='MBASIC 5.21 - Web IDE',
    port=port,
    # Enable secure session cookies (required for app.storage.user)
    storage_secret=os.environ.get('MBASIC_STORAGE_SECRET', 'dev-default-change-in-production'),
    reload=False,
    show=True
)
```

Set environment variable to enable Redis:
```bash
export NICEGUI_REDIS_URL="redis://localhost:6379/0"
export MBASIC_STORAGE_SECRET="your-secret-key-here"
```

If `NICEGUI_REDIS_URL` is not set, NiceGUI automatically uses in-memory storage.

## Benefits of This Design

1. **Zero new abstractions**: No new storage backend classes
2. **Leverages NiceGUI**: Uses built-in Redis support
3. **Minimal code changes**: Just add serialize/restore methods
4. **Backward compatible**: Works without Redis by default
5. **Configuration-driven**: Single env var to switch modes
6. **Automatic failover**: NiceGUI handles Redis connection errors

## Testing Strategy

1. **Test serialization round-trip**: serialize -> deserialize -> verify state
2. **Test in-memory mode**: Multiple tabs, verify isolation
3. **Test Redis mode**: Multiple tabs, verify persistence
4. **Test load balancing**: Multiple processes, verify session follows user

## Open Questions

1. **When to serialize?**
   - On every request? (Too slow)
   - On disconnect? (May lose data if crash)
   - Periodically? (Compromise - every 5 seconds?)
   - On state change? (Complex to track)

2. **Session lifetime in Redis?**
   - NiceGUI default: 24 hours
   - Configurable via `app.storage.client` TTL?

3. **Large program handling?**
   - Serialize entire program or just diffs?
   - Compression?

## Next Steps

1. Implement `SessionState` dataclass
2. Implement `serialize_state()` and `restore_state()` methods
3. Modify page handler to save/restore state
4. Add `storage_secret` to `ui.run()`
5. Test both modes (in-memory and Redis)
