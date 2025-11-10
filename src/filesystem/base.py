"""
Filesystem abstraction for MBASIC interpreter - RUNTIME file I/O.

This module handles RUNTIME file I/O (OPEN, CLOSE, INPUT#, PRINT# statements).
For PROGRAM file operations (FILES, LOAD, SAVE, MERGE commands), see src/file_io.py.

TWO FILESYSTEM ABSTRACTIONS (with some intentional overlap):
1. FileIO (src/file_io.py) - Program management operations
   - Used by: Interactive mode, UI file browsers
   - Operations: FILES (list), LOAD/SAVE/MERGE (program files), KILL (delete)
   - Purpose: Load .BAS programs into memory, save from memory to disk

2. FileSystemProvider (this file) - Runtime file I/O
   - Used by: Interpreter during program execution
   - Operations: OPEN/CLOSE, INPUT#/PRINT#/WRITE#, EOF(), LOC(), LOF()
   - Also provides: list_files() and delete() for runtime use
   - Purpose: File I/O from within running BASIC programs

Note: There is intentional overlap between the two abstractions.
Both provide list_files() and delete() methods, but serve different contexts:
FileIO is for interactive commands (FILES/KILL), FileSystemProvider is for
runtime access (though not all BASIC dialects support runtime file operations).

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

    @abstractmethod
    def flush(self):
        """Flush write buffers."""
        pass


class FileSystemProvider(ABC):
    """
    Abstract filesystem provider.

    Different UIs can provide different implementations:
    - LocalFileSystemProvider: Direct filesystem access (CLI, Tk, Curses)
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
