"""
Real filesystem provider for local UIs (CLI, Curses, Tk).

Provides direct access to the host filesystem.
"""

from .base import FileHandle, FileSystemProvider
from typing import Union, Optional
import glob as glob_module
import os


class RealFileHandle(FileHandle):
    """File handle that wraps Python's built-in file object."""

    def __init__(self, file_obj, binary: bool = False):
        self.file_obj = file_obj
        self.binary = binary
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
        """Flush write buffers."""
        if not self.closed:
            self.file_obj.flush()

    def close(self):
        """Close the file."""
        if not self.closed:
            self.file_obj.close()
            self.closed = True

    def seek(self, offset: int, whence: int = 0):
        """Seek to position in file."""
        self.file_obj.seek(offset, whence)

    def tell(self) -> int:
        """Get current file position."""
        return self.file_obj.tell()

    def is_eof(self) -> bool:
        """Check if at end of file."""
        current_pos = self.file_obj.tell()
        # Try to read one byte
        byte = self.file_obj.read(1)
        if byte:
            # Not EOF, seek back
            self.file_obj.seek(current_pos)
            return False
        return True


class RealFileSystemProvider(FileSystemProvider):
    """
    Real filesystem provider with direct OS access.

    Used by CLI, Curses, and Tk UIs where the user has local access
    and full filesystem permissions are appropriate.
    """

    def __init__(self, base_path: Optional[str] = None):
        """
        Initialize real filesystem provider.

        Args:
            base_path: Optional base directory to restrict access.
                      If None, allows access to entire filesystem.
        """
        self.base_path = base_path
        self.open_files = {}  # Track open files for reset()

    def _resolve_path(self, filename: str) -> str:
        """
        Resolve filename to actual path.

        Args:
            filename: User-provided filename

        Returns:
            Absolute path

        Raises:
            PermissionError: If path is outside base_path
        """
        if self.base_path:
            # Resolve relative to base_path
            abs_path = os.path.abspath(os.path.join(self.base_path, filename))
            # Ensure it's within base_path
            if not abs_path.startswith(os.path.abspath(self.base_path)):
                raise PermissionError(f"Access denied: {filename} is outside allowed directory")
            return abs_path
        else:
            # No restriction, use as-is
            return filename

    def open(self, filename: str, mode: str, binary: bool = False) -> FileHandle:
        """
        Open a file.

        Args:
            filename: Name/path of file
            mode: "r" (read), "w" (write), "a" (append), "r+" (read/write)
            binary: If True, open in binary mode

        Returns:
            RealFileHandle instance

        Raises:
            OSError: If file cannot be opened
            PermissionError: If access is denied
        """
        path = self._resolve_path(filename)

        # Convert mode
        file_mode = mode
        if binary:
            file_mode += 'b'

        # Open file
        try:
            file_obj = open(path, file_mode)
            handle = RealFileHandle(file_obj, binary)
            # Track for reset()
            self.open_files[id(handle)] = handle
            return handle
        except (OSError, IOError) as e:
            raise OSError(f"Cannot open {filename}: {e.strerror if hasattr(e, 'strerror') else str(e)}")

    def exists(self, filename: str) -> bool:
        """Check if file exists."""
        try:
            path = self._resolve_path(filename)
            return os.path.exists(path)
        except PermissionError:
            return False

    def delete(self, filename: str):
        """Delete a file."""
        path = self._resolve_path(filename)
        if os.path.exists(path):
            os.remove(path)

    def list_files(self, pattern: Optional[str] = None) -> list:
        """
        List files matching pattern.

        Args:
            pattern: Optional glob pattern (e.g., "*.BAS")

        Returns:
            List of filenames
        """
        if self.base_path:
            search_path = os.path.join(self.base_path, pattern if pattern else '*')
        else:
            search_path = pattern if pattern else '*'

        files = glob_module.glob(search_path)
        # Return just filenames if base_path is set
        if self.base_path:
            return [os.path.basename(f) for f in files]
        return files

    def get_size(self, filename: str) -> int:
        """Get file size in bytes."""
        path = self._resolve_path(filename)
        return os.path.getsize(path)

    def reset(self):
        """Close all open files."""
        for handle in list(self.open_files.values()):
            try:
                handle.close()
            except:
                pass
        self.open_files.clear()
