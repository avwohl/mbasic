"""Debug logging utility for MBASIC.

Provides centralized debug output controlled by MBASIC_DEBUG environment variable.
When enabled, errors and debug info are output to both the UI and stderr for
easy visibility when debugging with Claude Code or other tools.

Usage:
    from debug_logger import debug_log_error, is_debug_mode

    if is_debug_mode():
        debug_log_error("Error details", exception, context_info)
"""

import os
import sys
import traceback
from typing import Optional, Dict, Any


def is_debug_mode() -> bool:
    """Check if debug mode is enabled via environment variable.

    Returns:
        True if MBASIC_DEBUG is set to a truthy value
    """
    debug_var = os.environ.get('MBASIC_DEBUG', '').lower()
    return debug_var in ('1', 'true', 'yes', 'on')


def get_debug_level() -> int:
    """Get debug verbosity level.

    Returns:
        Debug level (0=off, 1=errors only, 2=verbose)
        Controlled by MBASIC_DEBUG_LEVEL environment variable
        Default is 1 when MBASIC_DEBUG is enabled
    """
    if not is_debug_mode():
        return 0

    level_var = os.environ.get('MBASIC_DEBUG_LEVEL', '1')
    try:
        return int(level_var)
    except ValueError:
        return 1


def debug_log_error(message: str,
                   exception: Optional[Exception] = None,
                   context: Optional[Dict[str, Any]] = None) -> str:
    """Log an error in debug mode.

    Outputs error details to stderr (visible to Claude/developer) and
    returns a formatted error message for the UI.

    Args:
        message: Human-readable error message
        exception: Optional exception object
        context: Optional dictionary of context information

    Returns:
        Formatted error message string suitable for display in UI
    """
    if not is_debug_mode():
        # Not in debug mode - just return the simple message
        if exception:
            return f"{message}: {exception}"
        return message

    # Debug mode - create detailed output
    from src.version import VERSION
    lines = []
    lines.append("=" * 70)
    lines.append("MBASIC DEBUG ERROR")
    lines.append(f"Version: {VERSION}")
    lines.append("=" * 70)
    lines.append(f"Message: {message}")

    if exception:
        lines.append(f"Exception: {type(exception).__name__}: {exception}")
        lines.append("")
        lines.append("Traceback:")
        lines.append(traceback.format_exc())

    if context:
        lines.append("")
        lines.append("Context:")
        for key, value in context.items():
            lines.append(f"  {key}: {value}")

    lines.append("=" * 70)

    debug_output = "\n".join(lines)

    # Output to stderr (visible to Claude/developer)
    print(debug_output, file=sys.stderr)
    sys.stderr.flush()

    # Return formatted message for UI
    ui_message = f"{message}"
    if exception:
        ui_message += f": {exception}"

    return ui_message


def debug_log(message: str, context: Optional[Dict[str, Any]] = None, level: int = 1) -> None:
    """Log a debug message (not an error).

    Args:
        message: Debug message
        context: Optional context information
        level: Debug level required (1=normal, 2=verbose). Only logs if get_debug_level() >= level
    """
    if get_debug_level() < level:
        return

    lines = [f"DEBUG: {message}"]
    if context:
        for key, value in context.items():
            lines.append(f"  {key}: {value}")

    print("\n".join(lines), file=sys.stderr)
    sys.stderr.flush()
