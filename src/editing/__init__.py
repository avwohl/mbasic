"""Program management and editing for MBASIC interpreter.

This module provides program line storage, parsing, and editing operations
extracted from InteractiveMode to enable reuse in different UI contexts.
"""

from .manager import ProgramManager

__all__ = ['ProgramManager']
