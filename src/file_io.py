"""
File I/O abstraction for MBASIC interpreter - PROGRAM file operations.

This module handles PROGRAM file operations (FILES, LOAD, SAVE, MERGE, KILL commands).
For RUNTIME file I/O (OPEN, CLOSE, INPUT#, PRINT# statements), see src/filesystem/base.py.

TWO SEPARATE FILESYSTEM ABSTRACTIONS:
1. FileIO (this file) - Program management operations
   - Used by: Interactive mode, UI file browsers
   - Operations: FILES (list files), LOAD/SAVE/MERGE (program files), KILL (delete files)
   - Purpose: Load .BAS programs into memory, save from memory to storage
   - Implementations:
     * RealFileIO: Direct filesystem access to disk (Tk, Curses, CLI)
     * SandboxedFileIO: In-memory virtual filesystem on Python server (Web UI - NOT browser storage)

2. FileSystemProvider (src/filesystem/base.py) - Runtime file I/O (OPEN/CLOSE/INPUT#/PRINT#)
   - Used by: Interpreter during program execution
   - Operations: OPEN/CLOSE, INPUT#/PRINT#/WRITE#, EOF(), LOC(), LOF()
   - Also provides: list_files() and delete() for runtime use within programs
   - Purpose: File I/O from within running BASIC programs
   - Implementations:
     * LocalFileSystemProvider: Direct filesystem access (Tk, Curses, CLI)
     * SandboxedFileSystemProvider: Python server memory (Web UI)

Note: Both abstractions serve different purposes and are used at different times.
There is intentional overlap: both provide list_files() and delete() methods.
FileIO is for interactive commands (FILES/KILL), FileSystemProvider is for
runtime access (though not all BASIC dialects support runtime file listing/deletion).
"""

from typing import List, Tuple
from abc import ABC, abstractmethod


class FileIO(ABC):
    """Abstract interface for file operations.

    Different UIs provide different implementations:
    - Local UIs (Tk/Curses/CLI): RealFileIO (direct filesystem)
    - Web UI: SandboxedFileIO (delegates to backend.sandboxed_fs, an in-memory filesystem)
    """

    @abstractmethod
    def list_files(self, filespec: str = "") -> List[Tuple[str, int, bool]]:
        """List files matching filespec pattern.

        Args:
            filespec: File pattern (e.g., "*.BAS", "*.txt")
                     Empty string means "*" (all files)

        Returns:
            List of (filename, size_bytes, is_dir) tuples
            size_bytes may be None if size cannot be determined
        """
        pass

    @abstractmethod
    def load_file(self, filename: str) -> str:
        """Load file contents.

        Args:
            filename: Name of file to load

        Returns:
            File contents as string

        Raises:
            FileNotFoundError: File does not exist
            IOError: File cannot be read
        """
        pass

    @abstractmethod
    def save_file(self, filename: str, content: str) -> None:
        """Save file contents.

        Args:
            filename: Name of file to save
            content: File contents to write

        Raises:
            IOError: File cannot be written
        """
        pass

    @abstractmethod
    def delete_file(self, filename: str) -> None:
        """Delete a file.

        Args:
            filename: Name of file to delete

        Raises:
            FileNotFoundError: File does not exist
        """
        pass

    @abstractmethod
    def file_exists(self, filename: str) -> bool:
        """Check if file exists.

        Args:
            filename: Name of file to check

        Returns:
            True if file exists, False otherwise
        """
        pass

    @abstractmethod
    def system_exit(self) -> None:
        """Exit to operating system / end session.

        Different implementations handle this differently:
        - Local UIs (CLI/Curses/TK): Exit the Python process (sys.exit(0))
        - Web UI: Raise an error (cannot exit server for one user)

        Raises:
            IOError: In sandboxed environments where exit is not allowed
        """
        pass


class RealFileIO(FileIO):
    """Real filesystem access for local UIs (TK, Curses, CLI).

    Uses Python's standard file operations to access the local filesystem.
    Users can read/write files in their current working directory.
    """

    def list_files(self, filespec: str = "") -> List[Tuple[str, int, bool]]:
        """List files in local filesystem matching pattern."""
        import glob
        import os

        # Default pattern if no argument
        pattern = filespec.strip().strip('"').strip("'") if filespec else "*"
        if not pattern:
            pattern = "*"

        # Get matching files
        files = sorted(glob.glob(pattern))

        # Build result list
        result = []
        for filename in files:
            try:
                if os.path.isdir(filename):
                    result.append((filename, None, True))
                elif os.path.isfile(filename):
                    size = os.path.getsize(filename)
                    result.append((filename, size, False))
                else:
                    result.append((filename, None, False))
            except OSError:
                result.append((filename, None, False))

        return result

    def load_file(self, filename: str) -> str:
        """Load file from local filesystem."""
        with open(filename, 'r', encoding='utf-8') as f:
            return f.read()

    def save_file(self, filename: str, content: str) -> None:
        """Save file to local filesystem."""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)

    def delete_file(self, filename: str) -> None:
        """Delete file from local filesystem."""
        import os
        os.remove(filename)

    def file_exists(self, filename: str) -> bool:
        """Check if file exists in local filesystem."""
        import os
        return os.path.exists(filename)

    def system_exit(self) -> None:
        """Exit to operating system."""
        import sys
        sys.exit(0)


class SandboxedFileIO(FileIO):
    """Sandboxed file operations for web UI.

    Acts as an adapter to backend.sandboxed_fs (SandboxedFileSystemProvider from
    src/filesystem/sandboxed_fs.py), which provides an in-memory virtual filesystem.

    IMPORTANT: This class mixes two concerns for web UI convenience:
    - Program file operations (load/save .BAS files for editing) - NOT IMPLEMENTED
    - Runtime file listing (FILES command to show in-memory data files) - IMPLEMENTED

    This design allows the FILES command to work in web UI by listing runtime data
    files created by BASIC OPEN/PRINT# statements. However, LOAD/SAVE for programs
    require different UI mechanisms (upload/download) and are not implemented.

    Storage location: In-memory virtual filesystem stored in server memory (NOT browser
                    localStorage or server disk files).
    Why server memory? Web UI runs Python interpreter on server, not in browser.
    Security: No access to server filesystem - all files are sandboxed in memory.
    Lifetime: Files exist only during the server session (cleared on restart).
              This is intentional - ephemeral storage prevents cross-user data leakage
              in the multi-user web environment. Users must download programs via
              browser's File → Save to persist them locally.

    Implementation status:
    - list_files(): IMPLEMENTED - queries the sandboxed_fs filesystem for in-memory data
                    files created by BASIC programs (OPEN/PRINT#/CLOSE). Returns empty list
                    if backend.sandboxed_fs doesn't exist. Catches exceptions and returns
                    (filename, None, False) for files that can't be stat'd.
    - load_file(): STUB - raises IOError (for .BAS program files - requires async refactor
                   to integrate with web UI file upload mechanisms)
    - save_file(): STUB - raises IOError (for .BAS program files - requires async refactor
                   to integrate with web UI file download mechanisms)
    - delete_file(): STUB - raises IOError (for .BAS program files - requires async refactor)
    - file_exists(): STUB - raises IOError (for .BAS program files - requires async refactor)

    Note: list_files() accesses runtime data files (created by OPEN statements), while
    load/save/delete are designed for .BAS program files (edited via UI). This mismatch
    is intentional - it allows FILES command to work while keeping program file handling
    deferred to proper async UI mechanisms.
    """

    def __init__(self, backend):
        """Initialize sandboxed file I/O.

        Args:
            backend: NiceGUIBackend instance that has a sandboxed_fs attribute
                    (SandboxedFileSystemProvider instance)
        """
        self.backend = backend

    def list_files(self, filespec: str = "") -> List[Tuple[str, int, bool]]:
        """List files in sandboxed filesystem.

        Uses the backend's sandboxed filesystem provider.
        Returns empty list if backend.sandboxed_fs doesn't exist.
        Catches exceptions during listing and size retrieval, returning (filename, None, False)
        for files that can't be stat'd. Note: Does not catch exceptions from list_files()
        itself - only from size lookups within the loop.
        """
        # Use the sandboxed filesystem from the backend
        if hasattr(self.backend, 'sandboxed_fs'):
            pattern = filespec.strip().strip('"').strip("'") if filespec else None
            try:
                files = self.backend.sandboxed_fs.list_files(pattern)
            except Exception:
                # If list_files() itself fails, return empty list
                return []

            # Convert to expected format: (filename, size, is_dir)
            result = []
            for filename in files:
                try:
                    size = self.backend.sandboxed_fs.get_size(filename)
                    result.append((filename, size, False))
                except Exception:
                    result.append((filename, None, False))
            return result
        return []

    def load_file(self, filename: str) -> str:
        """Load file from server memory virtual filesystem.

        STUB: Raises error (requires async refactor).
        """
        raise IOError("LOAD not yet implemented in web UI - requires async refactor")

    def save_file(self, filename: str, content: str) -> None:
        """Save file to server memory virtual filesystem.

        STUB: Raises error (requires async refactor).
        """
        raise IOError("SAVE not yet implemented in web UI - requires async refactor")

    def delete_file(self, filename: str) -> None:
        """Delete file from server memory virtual filesystem.

        STUB: Raises error (requires async refactor).
        """
        raise IOError("DELETE not yet implemented in web UI - requires async refactor")

    def file_exists(self, filename: str) -> bool:
        """Check if file exists in server memory virtual filesystem.

        STUB: Raises error (requires async refactor).
        """
        raise IOError("File existence check not yet implemented in web UI - requires async refactor")

    def system_exit(self) -> None:
        """Cannot exit in multi-user web environment.

        Raises IOError since exiting would terminate the server for all users.
        """
        raise IOError("SYSTEM command not available in web UI - would terminate server for all users")
