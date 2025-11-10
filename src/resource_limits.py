"""Resource limits for BASIC program execution (runtime enforcement).

This module provides centralized resource tracking and enforcement for BASIC
programs during execution (CPU time, memory, loop depth, etc.). Different UIs
can create appropriate limit configurations (web UI uses tight limits, local
UIs use generous limits).

Note: This is distinct from resource_locator.py which locates package data files.

Usage:
    # Web UI
    limits = create_web_limits()
    interpreter = Interpreter(runtime, io, limits=limits)

    # Local UI
    limits = create_local_limits()
    interpreter = Interpreter(runtime, io, limits=limits)

    # Testing/Development
    limits = create_unlimited_limits()
    interpreter = Interpreter(runtime, io, limits=limits)
"""

import time
from typing import Dict, Optional, Any


class ResourceLimits:
    """Track and enforce resource limits for BASIC program execution.

    This class is passed from the UI to the interpreter to provide
    environment-specific resource constraints (web = tight limits,
    local = generous limits).
    """

    def __init__(self,
                 # Stack limits
                 max_gosub_depth: int = 100,
                 max_for_depth: int = 50,
                 max_while_depth: int = 50,

                 # Memory limits
                 max_total_memory: int = 10*1024*1024,  # 10MB default
                 max_array_size: int = 1*1024*1024,      # 1MB per array
                 max_string_length: int = 255,            # 255 bytes (MBASIC 5.21 compatibility)

                 # File system limits
                 max_open_files: int = 10,
                 max_file_size: int = 512*1024,          # 512KB per file
                 max_total_files: int = 20,

                 # Execution limits
                 max_execution_time: float = 60.0,       # 60 seconds
                 max_statements_per_tick: int = 1000,    # For tick-based execution
                 ):
        """Initialize resource limits.

        Args:
            max_gosub_depth: Maximum GOSUB call nesting depth
            max_for_depth: Maximum FOR loop nesting depth
            max_while_depth: Maximum WHILE loop nesting depth
            max_total_memory: Maximum total memory for all variables/arrays (bytes)
            max_array_size: Maximum size for a single array (bytes)
            max_string_length: Maximum byte length for a string variable (UTF-8 encoded).
                              MBASIC 5.21 limit is 255 bytes (mandatory for spec compliance).
            max_open_files: Maximum number of simultaneously open files
            max_file_size: Maximum size for a single file (bytes)
            max_total_files: Maximum number of files that can be created
            max_execution_time: Maximum execution time in seconds
            max_statements_per_tick: Maximum statements per tick (for tick-based UIs)
        """
        # Store limits
        self.max_gosub_depth = max_gosub_depth
        self.max_for_depth = max_for_depth
        self.max_while_depth = max_while_depth
        self.max_total_memory = max_total_memory
        self.max_array_size = max_array_size
        self.max_string_length = max_string_length
        self.max_open_files = max_open_files
        self.max_file_size = max_file_size
        self.max_total_files = max_total_files
        self.max_execution_time = max_execution_time
        self.max_statements_per_tick = max_statements_per_tick

        # Track current usage
        self.current_memory_usage = 0
        self.current_gosub_depth = 0
        self.current_for_depth = 0
        self.current_while_depth = 0
        self.current_open_files = 0
        self.execution_start_time: Optional[float] = None

        # Track individual allocations for detailed reporting
        self.allocations: Dict[str, int] = {}  # name -> size in bytes

    # Stack depth tracking

    def push_gosub(self, line_num: int) -> None:
        """Track GOSUB call.

        Args:
            line_num: Line number being called

        Raises:
            RuntimeError: If GOSUB depth limit exceeded
        """
        self.current_gosub_depth += 1
        if self.current_gosub_depth > self.max_gosub_depth:
            raise RuntimeError(f"GOSUB stack overflow (limit: {self.max_gosub_depth})")

    def pop_gosub(self) -> None:
        """Track RETURN from GOSUB."""
        self.current_gosub_depth = max(0, self.current_gosub_depth - 1)

    def push_for_loop(self, var_name: str) -> None:
        """Track FOR loop entry.

        Args:
            var_name: Loop variable name

        Raises:
            RuntimeError: If FOR loop nesting limit exceeded
        """
        self.current_for_depth += 1
        if self.current_for_depth > self.max_for_depth:
            raise RuntimeError(f"FOR loop nesting too deep (limit: {self.max_for_depth})")

    def pop_for_loop(self) -> None:
        """Track NEXT (loop exit)."""
        self.current_for_depth = max(0, self.current_for_depth - 1)

    def push_while_loop(self) -> None:
        """Track WHILE loop entry.

        Raises:
            RuntimeError: If WHILE loop nesting limit exceeded
        """
        self.current_while_depth += 1
        if self.current_while_depth > self.max_while_depth:
            raise RuntimeError(f"WHILE loop nesting too deep (limit: {self.max_while_depth})")

    def pop_while_loop(self) -> None:
        """Track WEND (loop exit)."""
        self.current_while_depth = max(0, self.current_while_depth - 1)

    # Memory tracking

    def estimate_size(self, value: Any, var_type: Any) -> int:
        """Estimate memory size of a value in bytes.

        Args:
            value: The actual value (number, string, array)
            var_type: TypeInfo (INTEGER, SINGLE, DOUBLE, STRING) or VarType enum

        Returns:
            Estimated size in bytes
        """
        # Import here to avoid circular dependency
        from src.ast_nodes import TypeInfo

        if var_type == TypeInfo.INTEGER:
            return 2  # 2 bytes for 16-bit integer
        elif var_type == TypeInfo.SINGLE:
            return 4  # 4 bytes for single-precision float
        elif var_type == TypeInfo.DOUBLE:
            return 8  # 8 bytes for double-precision float
        elif var_type == TypeInfo.STRING:
            # String: UTF-8 byte length + 4-byte length prefix
            if isinstance(value, str):
                return len(value.encode('utf-8')) + 4
            return 4  # Empty string
        else:
            return 8  # Default to double

    def check_array_allocation(self, var_name: str, dimensions: list, element_type: Any) -> int:
        """Check if array allocation would exceed limits.

        Args:
            var_name: Variable name
            dimensions: List of dimension sizes [10, 20] for DIM A(10, 20)
            element_type: TypeInfo for array elements

        Raises:
            RuntimeError: If allocation would exceed limits

        Returns:
            Estimated size in bytes
        """
        # Calculate total elements for limit checking
        # Note: DIM A(N) creates N+1 elements (0 to N) in MBASIC 5.21 due to 0-based indexing
        # We account for this convention in our size calculation to ensure limit checks match
        # the actual memory allocation size. The execute_dim() method in interpreter.py uses the
        # same convention when creating arrays, ensuring consistency between limit checks and allocation.
        total_elements = 1
        for dim_size in dimensions:
            total_elements *= (dim_size + 1)  # +1 for 0-based indexing (0 to N)

        # Estimate element size
        element_size = self.estimate_size(None, element_type)

        # Total array size
        array_size = total_elements * element_size

        # Check against per-array limit
        if array_size > self.max_array_size:
            raise RuntimeError(
                f"Array {var_name} too large: {array_size} bytes "
                f"(limit: {self.max_array_size} bytes, "
                f"{total_elements} elements × {element_size} bytes/element)"
            )

        # Check against total memory limit
        # Account for freeing old allocation if re-dimensioning
        old_size = self.allocations.get(var_name, 0)
        new_total = self.current_memory_usage - old_size + array_size
        if new_total > self.max_total_memory:
            raise RuntimeError(
                f"Out of memory: would use {new_total} bytes "
                f"(limit: {self.max_total_memory} bytes, "
                f"current: {self.current_memory_usage} bytes)"
            )

        return array_size

    def allocate_array(self, var_name: str, dimensions: list, element_type: Any) -> None:
        """Allocate memory for an array.

        Args:
            var_name: Variable name
            dimensions: List of dimension sizes
            element_type: TypeInfo for array elements

        Raises:
            RuntimeError: If allocation would exceed limits
        """
        # Check if allocation is allowed
        array_size = self.check_array_allocation(var_name, dimensions, element_type)

        # Free old allocation if re-dimensioning
        if var_name in self.allocations:
            old_size = self.allocations[var_name]
            self.current_memory_usage -= old_size

        # Record new allocation
        self.allocations[var_name] = array_size
        self.current_memory_usage += array_size

    def allocate_variable(self, var_name: str, value: Any, var_type: Any) -> None:
        """Track variable assignment.

        Args:
            var_name: Variable name
            value: The value being assigned
            var_type: TypeInfo
        """
        var_size = self.estimate_size(value, var_type)

        # Free old allocation
        if var_name in self.allocations:
            old_size = self.allocations[var_name]
            self.current_memory_usage -= old_size

        # Record new allocation
        self.allocations[var_name] = var_size
        self.current_memory_usage += var_size

    def free_variable(self, var_name: str) -> None:
        """Free memory for a variable (e.g., when CLEAR or NEW is called).

        Args:
            var_name: Variable name to free
        """
        if var_name in self.allocations:
            size = self.allocations[var_name]
            self.current_memory_usage -= size
            del self.allocations[var_name]

    def clear_all(self) -> None:
        """Free all memory (NEW command)."""
        self.allocations.clear()
        self.current_memory_usage = 0
        self.current_gosub_depth = 0
        self.current_for_depth = 0
        self.current_while_depth = 0

    def check_string_length(self, string_value: str) -> None:
        """Check if string exceeds maximum byte length.

        Args:
            string_value: The string to check

        Raises:
            RuntimeError: If string exceeds byte length limit

        Note:
            String limits are measured in bytes (UTF-8 encoded), not character count.
            This matches MBASIC 5.21 behavior which limits string storage size.
        """
        if isinstance(string_value, str):
            byte_length = len(string_value.encode('utf-8'))
            if byte_length > self.max_string_length:
                raise RuntimeError(
                    f"String too long: {byte_length} bytes "
                    f"(limit: {self.max_string_length} bytes)"
                )

    # Execution time tracking

    def start_execution(self) -> None:
        """Mark start of program execution."""
        self.execution_start_time = time.time()

    def check_execution_time(self) -> None:
        """Check if execution time limit exceeded.

        Raises:
            RuntimeError: If time limit exceeded
        """
        if self.execution_start_time is None:
            return

        elapsed = time.time() - self.execution_start_time
        if elapsed > self.max_execution_time:
            raise RuntimeError(
                f"Execution time limit exceeded: {elapsed:.1f}s "
                f"(limit: {self.max_execution_time}s)"
            )

    # Reporting

    def get_usage_report(self) -> str:
        """Get a human-readable usage report.

        Returns:
            Multi-line report of current resource usage
        """
        lines = []
        lines.append("Resource Usage:")
        lines.append(
            f"  Memory: {self.current_memory_usage:,} / {self.max_total_memory:,} bytes "
            f"({self.current_memory_usage / self.max_total_memory * 100:.1f}%)"
        )
        lines.append(f"  GOSUB depth: {self.current_gosub_depth} / {self.max_gosub_depth}")
        lines.append(f"  FOR depth: {self.current_for_depth} / {self.max_for_depth}")
        lines.append(f"  WHILE depth: {self.current_while_depth} / {self.max_while_depth}")

        if self.execution_start_time:
            elapsed = time.time() - self.execution_start_time
            lines.append(f"  Execution time: {elapsed:.1f}s / {self.max_execution_time}s")

        if self.allocations:
            lines.append("  Top allocations:")
            top = sorted(self.allocations.items(), key=lambda x: x[1], reverse=True)[:5]
            for name, size in top:
                lines.append(f"    {name}: {size:,} bytes")

        return "\n".join(lines)


# Preset Configurations

def create_web_limits() -> ResourceLimits:
    """Create resource limits suitable for web environment (restrictive).

    MBASIC 5.21 compatibility: Enforces 255-byte string length limit (required for spec compliance).

    Returns:
        ResourceLimits configured for web environment with tight constraints
    """
    return ResourceLimits(
        max_gosub_depth=50,
        max_for_depth=25,
        max_while_depth=25,
        max_total_memory=5*1024*1024,      # 5MB
        max_array_size=512*1024,            # 512KB per array
        max_string_length=255,              # 255 bytes (MBASIC 5.21 compatibility)
        max_open_files=5,
        max_file_size=256*1024,             # 256KB per file
        max_total_files=10,
        max_execution_time=30.0,            # 30 seconds
        max_statements_per_tick=500,
    )


def create_local_limits() -> ResourceLimits:
    """Create resource limits suitable for local CLI (generous).

    MBASIC 5.21 compatibility: Enforces 255-byte string length limit (required for spec compliance).

    Returns:
        ResourceLimits configured for local environment with generous constraints
    """
    return ResourceLimits(
        max_gosub_depth=500,
        max_for_depth=100,
        max_while_depth=100,
        max_total_memory=100*1024*1024,     # 100MB
        max_array_size=10*1024*1024,        # 10MB per array
        max_string_length=255,              # 255 bytes (MBASIC 5.21 compatibility)
        max_open_files=20,
        max_file_size=10*1024*1024,         # 10MB per file
        max_total_files=100,
        max_execution_time=300.0,           # 5 minutes
        max_statements_per_tick=10000,
    )


def create_unlimited_limits() -> ResourceLimits:
    """Create effectively unlimited limits (for testing).

    WARNING: This configuration INTENTIONALLY BREAKS MBASIC 5.21 COMPATIBILITY by setting
    max_string_length to 1MB (instead of the required 255 bytes). This is for testing/development
    only - programs may pass tests with unlimited limits that would fail with MBASIC-compatible
    limits. For MBASIC 5.21 spec compliance, use create_local_limits() or create_web_limits()
    which enforce the mandatory 255-byte string limit.

    Returns:
        ResourceLimits configured with very high limits for testing/development
    """
    return ResourceLimits(
        max_gosub_depth=10000,
        max_for_depth=1000,
        max_while_depth=1000,
        max_total_memory=1024*1024*1024,    # 1GB
        max_array_size=100*1024*1024,       # 100MB per array
        max_string_length=1024*1024,        # 1MB strings (for testing/development - not MBASIC compatible)
        max_open_files=100,
        max_file_size=100*1024*1024,        # 100MB per file
        max_total_files=1000,
        max_execution_time=3600.0,          # 1 hour
        max_statements_per_tick=100000,
    )
