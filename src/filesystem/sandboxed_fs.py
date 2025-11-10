"""
Sandboxed in-memory filesystem provider for web UI.

Provides isolated, per-user virtual filesystem with no real disk access.
Each user gets their own private filesystem stored in memory.
"""

from .base import FileHandle, FileSystemProvider
from typing import Union, Optional, Dict
import io
import fnmatch


class InMemoryFileHandle(FileHandle):
    """File handle for in-memory files."""

    def __init__(self, file_obj: Union[io.StringIO, io.BytesIO], filename: str, mode: str, fs_provider):
        self.file_obj = file_obj
        self.filename = filename
        self.mode = mode
        self.fs_provider = fs_provider
        self.closed = False

    def read(self, size: int = -1) -> Union[str, bytes]:
        """Read from file."""
        return self.file_obj.read(size)

    def readline(self) -> Union[str, bytes]:
        """Read one line from file."""
        return self.file_obj.readline()

    def write(self, data: Union[str, bytes]) -> int:
        """Write to file."""
        return self.file_obj.write(data)

    def flush(self):
        """Flush write buffers (no-op for in-memory files).

        Calls the underlying StringIO/BytesIO flush() method, which is a no-op.
        In-memory file writes are already in memory, so flush() has no practical effect.
        Content is only logically "saved" to the virtual filesystem on close().
        """
        # StringIO and BytesIO always have flush() methods (no-ops)
        self.file_obj.flush()

    def close(self):
        """Close the file and save to virtual filesystem."""
        if not self.closed:
            if 'w' in self.mode or 'a' in self.mode or '+' in self.mode:
                # Save content back to virtual filesystem
                self.file_obj.seek(0)
                content = self.file_obj.read()
                self.fs_provider._save_file_content(self.filename, content)

            self.file_obj.close()
            self.closed = True
            # Remove from open files tracking
            if id(self) in self.fs_provider.open_files:
                del self.fs_provider.open_files[id(self)]

    def seek(self, offset: int, whence: int = 0):
        """Seek to position in file."""
        self.file_obj.seek(offset, whence)

    def tell(self) -> int:
        """Get current file position."""
        return self.file_obj.tell()

    def is_eof(self) -> bool:
        """Check if at end of file."""
        current_pos = self.file_obj.tell()
        byte = self.file_obj.read(1)
        if byte:
            self.file_obj.seek(current_pos)
            return False
        return True


class SandboxedFileSystemProvider(FileSystemProvider):
    """
    Sandboxed in-memory filesystem for web UI.

    Features:
    - All files stored in memory (no disk access).
    - Per-user isolation (user_id-based).
    - Size limits to prevent memory exhaustion.
    - File count limits.
    - Read-only example files can be pre-loaded.

    Security:
    - No access to real filesystem.
    - No path traversal (../ etc.).
    - Resource limits enforced.
    - Per-user isolation via user_id keys in class-level storage.
      IMPORTANT: Caller must ensure user_id is securely generated/validated
      to prevent cross-user access (e.g., use session IDs, not user-provided values).
    """

    # Class-level storage for all users
    # Structure: {user_id: {filename: content}}
    _user_filesystems: Dict[str, Dict[str, Union[str, bytes]]] = {}

    # Global read-only examples (shared across all users)
    _example_files: Dict[str, Union[str, bytes]] = {}

    def __init__(self, user_id: str, max_files: int = 50, max_file_size: int = 1024 * 1024):
        """
        Initialize sandboxed filesystem for a user.

        Args:
            user_id: Unique identifier for this user/session
                    SECURITY: Must be securely generated/validated (e.g., session IDs)
                    to prevent cross-user access. Do NOT use user-provided values.
                    NOTE: This class does NOT validate user_id - validation is the
                    caller's responsibility. Passing an untrusted/user-provided value
                    creates a security vulnerability (cross-user filesystem access).
            max_files: Maximum number of files allowed
            max_file_size: Maximum size per file in bytes (default 1MB)
        """
        # NOTE: user_id is accepted as-is without validation. Caller must ensure
        # it is securely generated (e.g., from session management, crypto-secure IDs)
        # and NOT from user-provided input.
        self.user_id = user_id
        self.max_files = max_files
        self.max_file_size = max_file_size
        self.open_files = {}  # Track open file handles

        # Initialize user's filesystem if not exists
        if user_id not in self._user_filesystems:
            self._user_filesystems[user_id] = {}

    @property
    def _files(self) -> Dict[str, Union[str, bytes]]:
        """Get this user's filesystem."""
        return self._user_filesystems[self.user_id]

    @classmethod
    def add_example_file(cls, filename: str, content: Union[str, bytes]):
        """
        Add a read-only example file available to all users.

        Args:
            filename: Name of example file
            content: File content
        """
        cls._example_files[filename] = content

    @classmethod
    def clear_user_filesystem(cls, user_id: str):
        """
        Clear all files for a specific user.

        Args:
            user_id: User whose files to clear
        """
        if user_id in cls._user_filesystems:
            del cls._user_filesystems[user_id]

    def _normalize_filename(self, filename: str) -> str:
        """
        Normalize and validate filename.

        Args:
            filename: User-provided filename

        Returns:
            Normalized filename

        Raises:
            PermissionError: If filename is invalid or contains path traversal
        """
        # Remove any path components (no directories allowed)
        filename = filename.replace('\\', '/').split('/')[-1]

        # Block dangerous filenames
        if filename in ('', '.', '..') or filename.startswith('.'):
            raise PermissionError(f"Invalid filename: {filename}")

        return filename.upper()  # CP/M style: uppercase filenames

    def _save_file_content(self, filename: str, content: Union[str, bytes]):
        """Save file content to virtual filesystem."""
        # Check size limit
        content_size = len(content) if isinstance(content, (str, bytes)) else 0
        if content_size > self.max_file_size:
            raise OSError(f"File too large: {content_size} bytes (max {self.max_file_size})")

        self._files[filename] = content

    def open(self, filename: str, mode: str, binary: bool = False) -> FileHandle:
        """
        Open a file in the virtual filesystem.

        Args:
            filename: Name of file
            mode: "r" (read), "w" (write), "a" (append), "r+" (read/write)
            binary: If True, use binary mode

        Returns:
            InMemoryFileHandle instance

        Raises:
            OSError: If file cannot be opened
            PermissionError: If file limits exceeded
        """
        filename = self._normalize_filename(filename)

        # Check file count limit for new files
        if mode in ('w', 'a', 'r+') and filename not in self._files:
            if len(self._files) >= self.max_files:
                raise OSError(f"Too many files (max {self.max_files})")

        # Determine if file exists
        exists_in_user = filename in self._files
        exists_in_examples = filename in self._example_files
        exists = exists_in_user or exists_in_examples

        # Handle different modes
        if mode == 'r':
            # Read mode - file must exist
            if not exists:
                raise OSError(f"File not found: {filename}")

            # Prefer user's file over example
            content = self._files.get(filename) or self._example_files.get(filename)

            # Create in-memory file
            if binary:
                if isinstance(content, str):
                    content = content.encode('utf-8')
                file_obj = io.BytesIO(content)
            else:
                if isinstance(content, bytes):
                    content = content.decode('utf-8', errors='ignore')
                file_obj = io.StringIO(content)

        elif mode == 'w':
            # Write mode - create new or truncate existing
            if binary:
                file_obj = io.BytesIO()
            else:
                file_obj = io.StringIO()

        elif mode == 'a':
            # Append mode - create or append
            if exists:
                content = self._files.get(filename) or self._example_files.get(filename)
                if binary:
                    if isinstance(content, str):
                        content = content.encode('utf-8')
                    file_obj = io.BytesIO(content)
                else:
                    if isinstance(content, bytes):
                        content = content.decode('utf-8', errors='ignore')
                    file_obj = io.StringIO(content)
                file_obj.seek(0, 2)  # Seek to end
            else:
                if binary:
                    file_obj = io.BytesIO()
                else:
                    file_obj = io.StringIO()

        elif mode == 'r+':
            # Read/write mode - file must exist
            if not exists:
                raise OSError(f"File not found: {filename}")

            content = self._files.get(filename) or self._example_files.get(filename)

            if binary:
                if isinstance(content, str):
                    content = content.encode('utf-8')
                file_obj = io.BytesIO(content)
            else:
                if isinstance(content, bytes):
                    content = content.decode('utf-8', errors='ignore')
                file_obj = io.StringIO(content)

        else:
            raise OSError(f"Invalid mode: {mode}")

        # Create handle
        handle = InMemoryFileHandle(file_obj, filename, mode, self)
        self.open_files[id(handle)] = handle
        return handle

    def exists(self, filename: str) -> bool:
        """Check if file exists."""
        try:
            filename = self._normalize_filename(filename)
            return filename in self._files or filename in self._example_files
        except PermissionError:
            return False

    def delete(self, filename: str):
        """Delete a file (only user's files, not examples)."""
        filename = self._normalize_filename(filename)

        # Can only delete user's own files
        if filename in self._files:
            del self._files[filename]
        else:
            raise OSError(f"File not found or read-only: {filename}")

    def list_files(self, pattern: Optional[str] = None) -> list:
        """
        List files matching pattern.

        Args:
            pattern: Optional glob pattern (e.g., "*.BAS")

        Returns:
            List of filenames (user's files + examples)
        """
        # Combine user files and examples
        all_files = set(self._files.keys()) | set(self._example_files.keys())

        if pattern:
            pattern = self._normalize_filename(pattern)
            # Use fnmatch for glob-style matching
            return sorted([f for f in all_files if fnmatch.fnmatch(f, pattern)])
        else:
            return sorted(list(all_files))

    def get_size(self, filename: str) -> int:
        """Get file size in bytes."""
        filename = self._normalize_filename(filename)

        content = self._files.get(filename) or self._example_files.get(filename)
        if content is None:
            raise OSError(f"File not found: {filename}")

        if isinstance(content, str):
            return len(content.encode('utf-8'))
        return len(content)

    def reset(self):
        """Close all open files."""
        for handle in list(self.open_files.values()):
            try:
                handle.close()
            except:
                pass
        self.open_files.clear()

    def get_stats(self) -> dict:
        """
        Get filesystem statistics.

        Returns:
            dict with file_count, total_size, max_files, max_file_size
        """
        total_size = sum(self.get_size(f) for f in self._files.keys())
        return {
            'file_count': len(self._files),
            'total_size': total_size,
            'max_files': self.max_files,
            'max_file_size': self.max_file_size,
            'user_id': self.user_id
        }
