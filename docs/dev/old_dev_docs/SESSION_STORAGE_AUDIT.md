# Session Storage Audit - Web UI Backend

## Overview
This document audits the current session storage implementation in `NiceGUIBackend` to determine what needs to be serialized for Redis storage support.

**Current Implementation**: The entire `NiceGUIBackend` instance is stored in `app.storage.client['backend']` (line 3263)

## NiceGUIBackend Instance Variables

### From UIBackend (base class)
Located in `src/ui/base.py`:
- `self.io` - IOHandler instance (not used in web backend, passed as None)
- `self.program` - ProgramManager instance

### NiceGUIBackend-specific State

#### Configuration (Serializable ✅)
```python
self.max_recent_files = 10                    # int
self.auto_save_enabled = True                 # bool
self.auto_save_interval = 30                  # int
self.output_max_lines = 1000                  # int
```

#### UI Elements (Cannot Serialize ❌ - Recreate on Load)
```python
self.editor = None                            # CodeMirror5Editor instance
self.output = None                            # UI element
self.status_label = None                      # UI element
self.auto_line_label = None                   # UI element
self.current_line_label = None                # UI element
self.immediate_entry = None                   # UI element
self.recent_files_menu = None                 # UI element
self.input_row = None                         # UI element
self.input_label = None                       # UI element
self.input_field = None                       # UI element
self.input_submit_btn = None                  # UI element
```
**Action**: Don't serialize - these are recreated by `build_ui()`

#### Dialogs (Cannot Serialize ❌ - Recreate on Load)
```python
self.variables_dialog = VariablesDialog(self)
self.stack_dialog = StackDialog(self)
self.open_file_dialog = OpenFileDialog(self)
self.save_as_dialog = SaveAsDialog(self)
self.merge_file_dialog = MergeFileDialog(self)
self.about_dialog = AboutDialog(self)
self.find_replace_dialog = FindReplaceDialog(self)
self.smart_insert_dialog = SmartInsertDialog(self)
self.delete_lines_dialog = DeleteLinesDialog(self)
self.renumber_dialog = RenumberDialog(self)
```
**Action**: Don't serialize - recreated by `build_ui()`

#### Runtime State (Complex Serialization ⚠️)
```python
self.runtime = Runtime({}, {})                # Runtime instance
```
**Contents** (from `src/runtime.py:40`):
- `_variables` - Dict of variables with metadata (✅ serializable)
- `_arrays` - Dict of arrays (✅ serializable)
- `_variable_case_variants` - Dict (✅ serializable)
- `_array_element_tracking` - Dict (✅ serializable)
- `common_vars` - List (✅ serializable)
- `array_base` - int (✅ serializable)
- `option_base_executed` - bool (✅ serializable)
- `pc` - PC object (✅ serializable - has line_num and stmt_offset)
- `npc` - PC object or None (✅ serializable)
- `statement_table` - StatementTable (⚠️ contains AST nodes - may need special handling)
- `halted` - bool (✅ serializable)
- `execution_stack` - List of dicts (✅ serializable)
- `for_loop_vars` - Dict (✅ serializable)
- `line_text_map` - Dict (✅ serializable)
- `data_items` - List (✅ serializable)
- `data_pointer` - int (✅ serializable)
- `data_line_map` - Dict (✅ serializable)
- `user_functions` - Dict mapping to DefFnStatementNode (⚠️ AST nodes - may need pickle)
- `files` - Dict of file handles (❌ Cannot serialize - must close and track state)
- `field_buffers` - Dict (✅ serializable)
- `error_handler` - int or None (✅ serializable)
- `error_handler_is_gosub` - bool (✅ serializable)
- `rnd_last` - float (✅ serializable)
- `stopped` - bool (✅ serializable)
- `breakpoints` - Set of PC objects (✅ serializable)
- `break_requested` - bool (✅ serializable)
- `trace_on` - bool (✅ serializable)
- `trace_detail` - str (✅ serializable)

**Action**: Most of Runtime can be serialized, but need to handle:
- Open file handles in `runtime.files`
- AST nodes in `statement_table` and `user_functions` (may need pickle or JSON representation)

#### Interpreter (Cannot Serialize ❌ - Recreate with Runtime)
```python
self.interpreter = Interpreter(...)           # Interpreter instance
```
**Action**: Don't serialize - recreate from serialized runtime state

#### Sandboxed Filesystem (Special Handling ⚠️)
```python
self.sandboxed_fs = SandboxedFileSystemProvider(user_id=session_id)
```
**Contents** (from `src/filesystem/sandboxed_fs.py:82`):
- `user_id` - str (✅ serializable)
- `max_files` - int (✅ serializable)
- `max_file_size` - int (✅ serializable)
- `open_files` - Dict (❌ file handles - must close)
- Class-level `_user_filesystems` - Dict[str, Dict[str, bytes]] (✅ serializable but shared across sessions)

**Action**: Store `user_id` and recreate provider. The filesystem data is already in class-level storage keyed by user_id.

#### Execution State (Partially Serializable ⚠️)
```python
self.running = False                          # bool ✅
self.paused = False                           # bool ✅
self.output_text = '...'                      # str ✅
self.current_file = None                      # str or None ✅
self.recent_files = []                        # list[str] ✅
self.exec_io = None                           # SimpleWebIOHandler ❌ (has callbacks)
self.input_future = None                      # asyncio.Future ❌ (cannot serialize)
self.last_save_content = ''                   # str ✅
self.exec_timer = None                        # Timer object ❌ (recreate if needed)
self.auto_save_timer = None                   # Timer object ❌ (recreate if needed)
```

#### Output Batching (Don't Serialize ❌)
```python
self.output_batch = []                        # list - ephemeral ✅
self.output_batch_timer = None                # Timer ❌
self.output_update_count = 0                  # int ✅ (but ephemeral)
```
**Action**: Don't serialize - performance optimization only

#### Find/Replace State (Serializable ✅)
```python
self.last_find_text = ''                      # str ✅
self.last_find_position = 0                   # int ✅
self.last_case_sensitive = False              # bool ✅
```

#### Settings Manager (Singleton - Don't Serialize ❌)
```python
self.settings_manager = get_settings_manager()
```
**Action**: Don't serialize - singleton retrieved on init

#### Editor State (Serializable ✅)
```python
self.last_edited_line_index = None           # int or None ✅
self.last_edited_line_text = None            # str or None ✅
```

## Summary

### Must Serialize (Core Session State)
1. **Program content**: Via `self.program` (ProgramManager)
2. **Runtime state**: `self.runtime` (mostly serializable, handle file objects)
3. **Execution state**: `running`, `paused`, `output_text`, `current_file`, `recent_files`
4. **Configuration**: `max_recent_files`, `auto_save_enabled`, etc.
5. **Find/Replace state**: Last search terms
6. **Sandboxed FS user_id**: To reconnect to correct filesystem

### Cannot Serialize (Recreate on Load)
1. **UI elements**: All `self.editor`, `self.output`, etc.
2. **Dialogs**: All dialog instances
3. **Interpreter**: Recreate from runtime state
4. **IOHandler callbacks**: Recreate with UI reference
5. **Async futures**: `self.input_future` - abandon or handle gracefully
6. **Timers**: `self.exec_timer`, `self.auto_save_timer` - recreate if needed
7. **Settings manager**: Get from singleton

### Special Handling Required
1. **Open file handles**: Close before serialization, track state to reopen
2. **AST nodes**: In `statement_table` and `user_functions` - may need pickle
3. **Sandboxed filesystem**: Data is in class-level storage, just store user_id
4. **Session ID**: Need consistent session_id across requests (use NiceGUI's session management)

## Serialization Strategy

### Option 1: Pickle Everything (Simplest)
**Pros**: Handles AST nodes, complex objects automatically
**Cons**: Not human-readable, security concerns, version compatibility issues

### Option 2: JSON + Pickle Hybrid (Recommended)
**Pros**: Most data in JSON (inspectable, safe), pickle only for AST nodes
**Cons**: Slightly more complex

### Option 3: Full JSON with AST Reconstruction (Most Robust)
**Pros**: No pickle, fully inspectable, most secure
**Cons**: Need to serialize/deserialize AST nodes manually

## Recommended Approach

1. **Extract serializable state** into a dict structure:
```python
state = {
    'version': '1.0',  # For future compatibility
    'session_id': self.sandboxed_fs.user_id,
    'program_lines': self.program.get_lines_as_dict(),
    'runtime_state': self._serialize_runtime(),
    'execution': {
        'running': self.running,
        'paused': self.paused,
        'output_text': self.output_text,
        'current_file': self.current_file,
        'recent_files': self.recent_files,
        'last_save_content': self.last_save_content,
    },
    'config': {
        'max_recent_files': self.max_recent_files,
        'auto_save_enabled': self.auto_save_enabled,
        'auto_save_interval': self.auto_save_interval,
    },
    'find_replace': {
        'last_find_text': self.last_find_text,
        'last_find_position': self.last_find_position,
        'last_case_sensitive': self.last_case_sensitive,
    },
    'editor_state': {
        'content': self.editor.value if self.editor else '',
        'cursor_position': None,  # Future: track cursor
    }
}
```

2. **Close any open file handles** before serialization

3. **Store in Redis** via NiceGUI's storage system (handles serialization)

4. **On load**:
   - Retrieve state dict
   - Recreate Runtime from serialized state
   - Recreate Interpreter with restored Runtime
   - Recreate UI elements via `build_ui()`
   - Restore editor content and other state

## Next Steps
1. Implement `_serialize_runtime()` method
2. Implement `_deserialize_runtime()` method
3. Create state extraction method
4. Create state restoration method
5. Test round-trip serialization (save/load state)
