"""
Filesystem abstraction for MBASIC interpreter.

Provides pluggable filesystem implementations to isolate and secure
file I/O operations, especially for web-based multi-user environments.
"""

from abc import ABC, abstractmethod
from typing import Union, Optional


class FileHandle(ABC):
    """Abstract file handle that wraps file operations."""

    @abstractmethod
    def read(self, size: int = -1) -> Union[str, bytes]:
        """Read from file."""
        pass

    @abstractmethod
    def readline(self) -> Union[str, bytes]:
        """Read one line from file."""
        pass

    @abstractmethod
    def write(self, data: Union[str, bytes]) -> int:
        """Write to file."""
        pass

    @abstractmethod
    def close(self):
        """Close the file."""
        pass

    @abstractmethod
    def seek(self, offset: int, whence: int = 0):
        """Seek to position in file."""
        pass

    @abstractmethod
    def tell(self) -> int:
        """Get current file position."""
        pass

    @abstractmethod
    def is_eof(self) -> bool:
        """Check if at end of file."""
        pass


class FileSystemProvider(ABC):
    """
    Abstract filesystem provider.

    Different UIs can provide different implementations:
    - RealFileSystemProvider: Direct filesystem access (CLI, Tk, Curses)
    - SandboxedFileSystemProvider: In-memory or restricted access (Web)
    """

    @abstractmethod
    def open(self, filename: str, mode: str, binary: bool = False) -> FileHandle:
        """
        Open a file.

        Args:
            filename: Name/path of file
            mode: "r" (read), "w" (write), "a" (append), "r+" (read/write)
            binary: If True, open in binary mode

        Returns:
            FileHandle instance

        Raises:
            OSError: If file cannot be opened
            PermissionError: If access is denied
        """
        pass

    @abstractmethod
    def exists(self, filename: str) -> bool:
        """Check if file exists."""
        pass

    @abstractmethod
    def delete(self, filename: str):
        """Delete a file."""
        pass

    @abstractmethod
    def list_files(self, pattern: Optional[str] = None) -> list:
        """
        List files matching pattern.

        Args:
            pattern: Optional glob pattern (e.g., "*.BAS")

        Returns:
            List of filenames
        """
        pass

    @abstractmethod
    def get_size(self, filename: str) -> int:
        """Get file size in bytes."""
        pass

    @abstractmethod
    def reset(self):
        """
        Reset/close all open files.

        Called when program ends or RESET statement executed.
        """
        pass
