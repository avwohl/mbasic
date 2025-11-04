"""
Filesystem abstraction for MBASIC.

Provides pluggable filesystem implementations for different UI backends.
"""

from .base import FileHandle, FileSystemProvider
from .real_fs import RealFileSystemProvider
from .sandboxed_fs import SandboxedFileSystemProvider

__all__ = [
    'FileHandle',
    'FileSystemProvider',
    'RealFileSystemProvider',
    'SandboxedFileSystemProvider',
]
