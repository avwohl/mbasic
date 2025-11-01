#!/usr/bin/env python3
"""
Test FileIO module - RealFileIO and basic interface.

This tests the RealFileIO implementation. SandboxedFileIO requires
browser/JavaScript context which can't be easily tested in CLI.
"""

import sys
import os
import tempfile
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from file_io import FileIO, RealFileIO


def test_real_file_io():
    """Test RealFileIO implementation with real filesystem."""

    print("Testing RealFileIO...")

    # Create temporary directory for testing
    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)

        # Create test files
        Path("test1.bas").write_text("10 PRINT \"TEST1\"\n20 END\n")
        Path("test2.bas").write_text("10 PRINT \"TEST2\"\n")
        Path("readme.txt").write_text("This is a readme file\n")
        os.makedirs("subdir", exist_ok=True)
        Path("subdir/test3.bas").write_text("10 PRINT \"TEST3\"\n")

        file_io = RealFileIO()

        # Test 1: list_files with no pattern (all files)
        print("\n1. List all files:")
        files = file_io.list_files("")
        for name, size, is_dir in files:
            if is_dir:
                print(f"  {name:<30} <DIR>")
            else:
                print(f"  {name:<30} {size} bytes")
        assert len(files) == 4, f"Expected 4 items, got {len(files)}"
        print("  ✓ List all files works")

        # Test 2: list_files with pattern
        print("\n2. List *.bas files:")
        files = file_io.list_files("*.bas")
        for name, size, is_dir in files:
            print(f"  {name:<30} {size} bytes")
        assert len(files) == 2, f"Expected 2 .bas files, got {len(files)}"
        print("  ✓ Pattern matching works")

        # Test 3: load_file
        print("\n3. Load file:")
        content = file_io.load_file("test1.bas")
        print(f"  Loaded {len(content)} bytes")
        assert "TEST1" in content
        assert content.endswith("\n")
        print("  ✓ Load file works")

        # Test 4: save_file
        print("\n4. Save file:")
        new_content = "10 PRINT \"NEW FILE\"\n20 END\n"
        file_io.save_file("new.bas", new_content)
        assert Path("new.bas").exists()
        loaded = file_io.load_file("new.bas")
        assert loaded == new_content
        print("  ✓ Save file works")

        # Test 5: file_exists
        print("\n5. File exists check:")
        assert file_io.file_exists("test1.bas") == True
        assert file_io.file_exists("nonexistent.bas") == False
        print("  ✓ File exists works")

        # Test 6: delete_file
        print("\n6. Delete file:")
        file_io.save_file("temp.bas", "temporary")
        assert file_io.file_exists("temp.bas")
        file_io.delete_file("temp.bas")
        assert not file_io.file_exists("temp.bas")
        print("  ✓ Delete file works")

        print("\n✅ All RealFileIO tests passed!")


def test_files_statement_integration():
    """Test that FILES statement would work with RealFileIO."""

    print("\n\nTesting FILES statement integration...")

    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)

        # Create test files
        Path("prog1.bas").write_text("10 PRINT 1\n")
        Path("prog2.bas").write_text("10 PRINT 2\n")
        Path("data.txt").write_text("some data\n")

        file_io = RealFileIO()

        # Simulate what execute_files() does
        filespec = ""  # Empty = all files
        files = file_io.list_files(filespec)
        pattern = filespec if filespec else "*"

        print(f"\nDirectory listing for: {pattern}")
        print("-" * 50)

        if not files:
            print(f"No files matching: {pattern}")
        else:
            for filename, size, is_dir in files:
                if is_dir:
                    print(f"{filename:<30}        <DIR>")
                elif size is not None:
                    print(f"{filename:<30} {size:>12} bytes")
                else:
                    print(f"{filename:<30}            ?")
            print(f"\n{len(files)} File(s)")

        assert len(files) == 3
        print("\n✓ FILES statement integration works")


if __name__ == "__main__":
    try:
        test_real_file_io()
        test_files_statement_integration()
        print("\n" + "="*60)
        print("ALL TESTS PASSED ✅")
        print("="*60)
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
