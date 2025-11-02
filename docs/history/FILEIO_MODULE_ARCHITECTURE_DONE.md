# FileIO Module Architecture for Sandboxing

## Status: COMPLETED (v1.0.370-1.0.400+)

**Implemented (v1.0.370-1.0.372):**
- ✅ FileIO interface created
- ✅ RealFileIO works (tested, all tests pass)
- ✅ Interpreter integration works
- ✅ FILES statement works in local UIs (TK/Curses/CLI)

**Not Working (v1.0.373):**
- ❌ SandboxedFileIO is stub - returns empty results
- ❌ FILES doesn't work in web UI
- ❌ Web UI still has security issue (no sandboxing yet)

**Root Cause:**
`ui.run_javascript()` returns `AwaitableResponse` which MUST be awaited. Can't use from synchronous interpreter code.

## Problem

Currently, FILES/LOAD/SAVE/etc statements access the filesystem directly via `glob.glob()` and Python's `open()`. This creates a **security issue for the web UI**:

- Web users can list server directories: `FILES "../../etc/passwd"`
- Web users could potentially read/write server files
- No sandboxing - direct access to server filesystem

The web UI needs to be **sandboxed** - file operations should work with:
- Browser localStorage
- Upload/download to client machine
- NOT the server's filesystem

## Current Insecure Behavior

**src/ui/ui_helpers.py - list_files():**
```python
def list_files(filespec: str = ""):
    # ...
    files = sorted(glob.glob(pattern))  # Direct server filesystem access!
```

**src/ui/web/nicegui_backend.py - cmd_files():**
```python
def cmd_files(self, filespec: str = ""):
    from src.ui.ui_helpers import list_files
    files = list_files(filespec)  # Server filesystem - BAD for web UI!
```

This allows web users to browse the server's filesystem - **SECURITY ISSUE**.

## Proposed Solution: FileIO Module

**Architecture:**
```
Interpreter.__init__(runtime, io_handler, file_io=None)
    file_io = FileIO module for file operations
              - If None: create RealFileIO (direct filesystem access)
              - If provided: use sandboxed implementation
```

**Different UIs pass different FileIO implementations:**
- **TK/Curses/CLI:** Pass `None` → Interpreter creates `RealFileIO` (local filesystem)
- **Web UI:** Pass `SandboxedFileIO` → Browser localStorage + upload/download

## FileIO Module Interface

```python
class FileIO:
    """Abstract interface for file operations.

    Implementations:
    - RealFileIO: Direct filesystem access (for local UIs)
    - SandboxedFileIO: Browser localStorage/upload/download (for web UI)
    """

    def list_files(self, filespec: str = "") -> List[Tuple[str, int, bool]]:
        """List files matching filespec.

        Returns:
            List of (filename, size_bytes, is_dir)
        """
        raise NotImplementedError

    def load_file(self, filename: str) -> str:
        """Load file contents.

        Returns:
            File contents as string

        Raises:
            FileNotFoundError: File not found
        """
        raise NotImplementedError

    def save_file(self, filename: str, content: str) -> None:
        """Save file contents.

        Args:
            filename: Name of file to save
            content: File contents
        """
        raise NotImplementedError

    def delete_file(self, filename: str) -> None:
        """Delete a file.

        Raises:
            FileNotFoundError: File not found
        """
        raise NotImplementedError

    def file_exists(self, filename: str) -> bool:
        """Check if file exists."""
        raise NotImplementedError
```

## RealFileIO Implementation (Local UIs)

```python
class RealFileIO(FileIO):
    """Real filesystem access for local UIs (TK, Curses, CLI)."""

    def list_files(self, filespec: str = "") -> List[Tuple[str, int, bool]]:
        import glob
        import os

        pattern = filespec if filespec else "*"
        files = sorted(glob.glob(pattern))

        result = []
        for filename in files:
            try:
                if os.path.isdir(filename):
                    result.append((filename, None, True))
                elif os.path.isfile(filename):
                    size = os.path.getsize(filename)
                    result.append((filename, size, False))
            except OSError:
                result.append((filename, None, False))

        return result

    def load_file(self, filename: str) -> str:
        with open(filename, 'r') as f:
            return f.read()

    def save_file(self, filename: str, content: str) -> None:
        with open(filename, 'w') as f:
            f.write(content)

    def delete_file(self, filename: str) -> None:
        import os
        os.remove(filename)

    def file_exists(self, filename: str) -> bool:
        import os
        return os.path.exists(filename)
```

## SandboxedFileIO Implementation (Web UI)

```python
class SandboxedFileIO(FileIO):
    """Sandboxed file operations for web UI.

    Uses browser localStorage for file storage.
    Files are stored per-user session.
    No access to server filesystem.
    """

    def __init__(self, backend):
        """
        Args:
            backend: NiceGUIBackend instance for localStorage access
        """
        self.backend = backend

    def list_files(self, filespec: str = "") -> List[Tuple[str, int, bool]]:
        """List files in browser localStorage.

        Returns list of files stored in this user's session.
        Filespec pattern matching is done client-side.
        """
        import fnmatch

        # Get all files from localStorage via JavaScript
        files_json = self.backend.run_javascript('''
            const files = [];
            for (let i = 0; i < localStorage.length; i++) {
                const key = localStorage.key(i);
                if (key.startsWith('mbasic_file_')) {
                    const filename = key.substring(12);  // Remove 'mbasic_file_' prefix
                    const content = localStorage.getItem(key);
                    files.push({
                        name: filename,
                        size: content.length
                    });
                }
            }
            return files;
        ''')

        pattern = filespec if filespec else "*"

        result = []
        for file_info in files_json:
            filename = file_info['name']
            if fnmatch.fnmatch(filename, pattern):
                result.append((filename, file_info['size'], False))

        return sorted(result)

    def load_file(self, filename: str) -> str:
        """Load file from browser localStorage."""
        content = self.backend.run_javascript(f'''
            return localStorage.getItem('mbasic_file_{filename}');
        ''')

        if content is None:
            raise FileNotFoundError(f"File not found: {filename}")

        return content

    def save_file(self, filename: str, content: str) -> None:
        """Save file to browser localStorage."""
        self.backend.run_javascript(f'''
            localStorage.setItem('mbasic_file_{filename}', {repr(content)});
        ''')

    def delete_file(self, filename: str) -> None:
        """Delete file from browser localStorage."""
        self.backend.run_javascript(f'''
            localStorage.removeItem('mbasic_file_{filename}');
        ''')

    def file_exists(self, filename: str) -> bool:
        """Check if file exists in browser localStorage."""
        exists = self.backend.run_javascript(f'''
            return localStorage.getItem('mbasic_file_{filename}') !== null;
        ''')
        return exists
```

## Interpreter Changes

**src/interpreter.py:**
```python
class Interpreter:
    def __init__(self, runtime, io_handler, file_io=None, limits=None):
        """
        Args:
            runtime: Runtime instance
            io_handler: IOHandler for program I/O
            file_io: FileIO module for file operations
                     If None, creates RealFileIO (direct filesystem access)
            limits: Resource limits
        """
        self.runtime = runtime
        self.io = io_handler
        self.limits = limits

        # File I/O module - sandboxed or real filesystem
        if file_io is None:
            self.file_io = RealFileIO()  # Default: real filesystem
        else:
            self.file_io = file_io  # Use provided (possibly sandboxed)

    def execute_files(self, stmt):
        """Execute FILES statement."""
        filespec = ""
        if stmt.filespec:
            filespec = self.evaluate_expression(stmt.filespec)
            if not isinstance(filespec, str):
                raise RuntimeError("FILES requires string filespec")

        # Use file_io module (sandboxed or real)
        files = self.file_io.list_files(filespec)
        pattern = filespec if filespec else "*"

        if not files:
            self.io.output(f"No files matching: {pattern}")
            return

        for filename, size, is_dir in files:
            if is_dir:
                self.io.output(f"{filename:<30}        <DIR>")
            elif size is not None:
                self.io.output(f"{filename:<30} {size:>12} bytes")
            else:
                self.io.output(f"{filename:<30}            ?")

        self.io.output(f"\n{len(files)} File(s)")

    def execute_load(self, stmt):
        """Execute LOAD statement."""
        filename = self.evaluate_expression(stmt.filename)
        if not isinstance(filename, str):
            raise RuntimeError("LOAD requires string filename")

        # Use file_io module (sandboxed or real)
        try:
            content = self.file_io.load_file(filename)

            # Parse content into program
            # (This requires ProgramManager reference - see MOVE_STATEMENTS_TO_INTERPRETER_TODO.md)
            self.program_manager.clear()
            for line in content.split('\n'):
                line = line.strip()
                if line:
                    self.program_manager.add_line_from_text(line)

            self.io.output(f"Loaded: {filename}")
        except FileNotFoundError:
            raise RuntimeError(f"File not found: {filename}")

    def execute_save(self, stmt):
        """Execute SAVE statement."""
        filename = self.evaluate_expression(stmt.filename)
        if not isinstance(filename, str):
            raise RuntimeError("SAVE requires string filename")

        # Get program content from ProgramManager
        lines = []
        for line_num in sorted(self.program_manager.lines.keys()):
            lines.append(self.program_manager.lines[line_num])
        content = '\n'.join(lines)

        # Use file_io module (sandboxed or real)
        self.file_io.save_file(filename, content)
        self.io.output(f"Saved: {filename}")
```

## UI Backend Changes

**TK/Curses/CLI UIs:**
```python
# Pass None for file_io → uses RealFileIO (direct filesystem)
interpreter = Interpreter(runtime, io_handler, file_io=None, limits=limits)
```

**Web UI:**
```python
# Pass SandboxedFileIO → uses localStorage
sandboxed_file_io = SandboxedFileIO(self)  # 'self' is NiceGUIBackend
interpreter = Interpreter(runtime, io_handler, file_io=sandboxed_file_io, limits=limits)
```

## Benefits

1. **Security:** Web UI is sandboxed - no server filesystem access
2. **Consistency:** All UIs use same interpreter code for FILES/LOAD/SAVE
3. **Flexibility:** Easy to add new FileIO implementations (cloud storage, etc.)
4. **Clean architecture:** Interpreter doesn't know about sandboxing - UI decides
5. **Default safety:** `file_io=None` creates real FileIO only when appropriate

## Additional Features for Web UI

**Upload/Download Integration:**
```python
class SandboxedFileIO(FileIO):
    def upload_from_client(self, file_data: bytes, filename: str):
        """Upload file from client browser to localStorage."""
        content = file_data.decode('utf-8')
        self.save_file(filename, content)

    def download_to_client(self, filename: str):
        """Download file from localStorage to client browser."""
        content = self.load_file(filename)
        # Trigger browser download
        self.backend.download_file(filename, content.encode('utf-8'))
```

**File browser UI:**
- FILES statement shows localStorage files
- Web UI File > Open shows upload dialog + localStorage browser
- Web UI File > Save shows download option + localStorage save

## Migration Path

### Phase 1: Create FileIO Module
1. Create `src/file_io.py` with FileIO interface
2. Implement RealFileIO (filesystem access)
3. Implement SandboxedFileIO (localStorage)

### Phase 2: Update Interpreter
1. Add `file_io` parameter to Interpreter.__init__()
2. Update execute_files() to use file_io.list_files()
3. Update execute_load() to use file_io.load_file()
4. Update execute_save() to use file_io.save_file()

### Phase 3: Update UIs
1. TK/Curses/CLI: Pass `file_io=None` (uses RealFileIO)
2. Web UI: Create and pass SandboxedFileIO instance

### Phase 4: Remove Old Code
1. Remove cmd_files/cmd_load/cmd_save from UI backends
2. Remove delegation code from interpreter
3. Remove ui_helpers.list_files() (now in FileIO)

## Files to Create

- `src/file_io.py` - FileIO interface, RealFileIO, SandboxedFileIO

## Files to Modify

- `src/interpreter.py` - Add file_io parameter, use for FILES/LOAD/SAVE
- `src/ui/web/nicegui_backend.py` - Create and pass SandboxedFileIO
- `src/ui/tk_ui.py` - Pass file_io=None
- `src/ui/curses_ui.py` - Pass file_io=None
- `src/ui/cli.py` - Pass file_io=None

## Security Considerations

**Web UI Sandboxing:**
- Files only visible to current browser session
- No access to server filesystem
- No path traversal attacks possible
- localStorage has ~5-10MB limit (plenty for BASIC programs)

**Local UI Security:**
- Direct filesystem access is fine (user's own machine)
- Standard filesystem permissions apply
- No change from current behavior

## Async/Await Problem - Solutions

### Problem
`ui.run_javascript()` in NiceGUI returns `AwaitableResponse` that MUST be awaited:
```python
# This doesn't work (synchronous):
result = ui.run_javascript('localStorage.getItem("key")')  # Returns AwaitableResponse object

# This works (async):
result = await ui.run_javascript('localStorage.getItem("key")')  # Returns actual value
```

But the interpreter is synchronous and can't await.

### Solution Options

**Option 1: Make Interpreter Async**
- Make all execute_* methods async
- Make tick() async
- All UIs would need to await interpreter calls
- **Pros:** Clean, proper async/await
- **Cons:** MASSIVE refactor, breaks all UIs

**Option 2: Use asyncio.run() in SandboxedFileIO**
- Wrap async calls in `asyncio.run()`
- Run event loop from sync code
- **Pros:** Minimal changes to interpreter
- **Cons:** Might conflict with NiceGUI's event loop, risky

**Option 3: Pre-fetch and Cache**
- Backend fetches localStorage on page load
- Cache results in backend.file_cache dict
- SandboxedFileIO reads from cache
- **Pros:** Synchronous, no async issues
- **Cons:** Cache can get stale, need to invalidate

**Option 4: Use Different JavaScript Bridge**
- Find/create synchronous JavaScript execution method
- Might not exist in NiceGUI
- **Pros:** Clean sync code
- **Cons:** Might be impossible

**Option 5: Wait/Poll Pattern**
- Start JavaScript execution (don't await)
- Poll for result in loop with timeout
- **Pros:** Works with sync code
- **Cons:** Hacky, inefficient

### Recommended: Option 3 (Pre-fetch and Cache)

Implement a cache in the backend:
```python
class NiceGUIBackend:
    def __init__(self):
        self.localStorage_cache = {}  # filename -> content cache

    async def refresh_localStorage_cache(self):
        """Called periodically to refresh cache from browser."""
        files_json = await ui.run_javascript('''...get localStorage...''')
        self.localStorage_cache = {...parse results...}

class SandboxedFileIO:
    def list_files(self, filespec):
        # Read from backend.localStorage_cache (synchronous)
        return [f for f in self.backend.localStorage_cache.keys()]
```

**Implementation:**
1. Add `localStorage_cache` dict to NiceGUIBackend
2. Add async method to refresh cache from browser
3. Call refresh before running programs
4. SandboxedFileIO reads from cache (sync)

## Priority

High - this is a **security issue** for web UI (currently using RealFileIO which exposes server filesystem)

## Date Created

2025-11-01

## Date Updated

2025-11-01 - Discovered async/await issue, converted SandboxedFileIO to stub
