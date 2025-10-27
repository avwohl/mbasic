#!/usr/bin/env python3
"""
Tests for Recent Files Manager

Tests the recent_files module functionality including:
- Adding files
- Retrieving recent files
- Maximum file limit
- File existence filtering
- Clearing history
"""

import sys
from pathlib import Path
import tempfile
import shutil

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from ui.recent_files import RecentFilesManager


def test_basic_operations():
    """Test basic add, get, and clear operations."""
    print("Testing basic operations...")

    # Use temporary directory for testing
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        config_dir = tmpdir_path / '.test_mbasic'

        # Create test files
        test_files = []
        for i in range(5):
            f = tmpdir_path / f'test{i}.bas'
            f.write_text(f'10 PRINT "Test {i}"\n')
            test_files.append(str(f))

        # Create manager
        rfm = RecentFilesManager(config_dir=config_dir)

        # Add files
        for f in test_files:
            rfm.add_file(f)

        # Get recent files
        recent = rfm.get_recent_files()

        # Should be in reverse order (most recent first)
        assert len(recent) == 5, f"Expected 5 files, got {len(recent)}"
        assert recent[0] == test_files[-1], "Most recent file should be first"
        assert recent[-1] == test_files[0], "Oldest file should be last"

        # Clear
        rfm.clear()
        recent = rfm.get_recent_files()
        assert len(recent) == 0, "Recent files should be empty after clear"

    print("✓ Basic operations test passed")


def test_max_files_limit():
    """Test that max_files limit is enforced."""
    print("Testing max files limit...")

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        config_dir = tmpdir_path / '.test_mbasic'

        # Create more files than the limit
        test_files = []
        for i in range(15):
            f = tmpdir_path / f'test{i}.bas'
            f.write_text(f'10 PRINT "Test {i}"\n')
            test_files.append(str(f))

        # Create manager with max 10 files
        rfm = RecentFilesManager(max_files=10, config_dir=config_dir)

        # Add all files
        for f in test_files:
            rfm.add_file(f)

        # Should only keep last 10
        recent = rfm.get_recent_files()
        assert len(recent) == 10, f"Expected 10 files, got {len(recent)}"

        # Should be the last 10 files added
        assert recent[0] == test_files[-1], "Most recent should be last added"
        assert recent[-1] == test_files[5], "10th most recent should be test5.bas"

    print("✓ Max files limit test passed")


def test_duplicate_handling():
    """Test that adding the same file twice moves it to the top."""
    print("Testing duplicate handling...")

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        config_dir = tmpdir_path / '.test_mbasic'

        # Create test files
        test_files = []
        for i in range(5):
            f = tmpdir_path / f'test{i}.bas'
            f.write_text(f'10 PRINT "Test {i}"\n')
            test_files.append(str(f))

        # Create manager
        rfm = RecentFilesManager(config_dir=config_dir)

        # Add files
        for f in test_files:
            rfm.add_file(f)

        # Re-add the oldest file (test0.bas)
        rfm.add_file(test_files[0])

        # Get recent files
        recent = rfm.get_recent_files()

        # test0.bas should now be at the top
        assert recent[0] == test_files[0], "Re-added file should be at top"
        # Should still only have 5 files
        assert len(recent) == 5, f"Expected 5 files, got {len(recent)}"

    print("✓ Duplicate handling test passed")


def test_file_existence_filtering():
    """Test that non-existent files are filtered out."""
    print("Testing file existence filtering...")

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        config_dir = tmpdir_path / '.test_mbasic'

        # Create test files
        test_files = []
        for i in range(5):
            f = tmpdir_path / f'test{i}.bas'
            f.write_text(f'10 PRINT "Test {i}"\n')
            test_files.append(str(f))

        # Create manager
        rfm = RecentFilesManager(config_dir=config_dir)

        # Add files
        for f in test_files:
            rfm.add_file(f)

        # Delete some files
        Path(test_files[1]).unlink()
        Path(test_files[3]).unlink()

        # Get recent files - should filter out deleted ones
        recent = rfm.get_recent_files()

        # Should only have 3 files now
        assert len(recent) == 3, f"Expected 3 files, got {len(recent)}"
        assert test_files[1] not in recent, "Deleted file should not be in list"
        assert test_files[3] not in recent, "Deleted file should not be in list"

    print("✓ File existence filtering test passed")


def test_persistence():
    """Test that recent files persist across instances."""
    print("Testing persistence...")

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        config_dir = tmpdir_path / '.test_mbasic'

        # Create test files
        test_files = []
        for i in range(3):
            f = tmpdir_path / f'test{i}.bas'
            f.write_text(f'10 PRINT "Test {i}"\n')
            test_files.append(str(f))

        # Create first manager and add files
        rfm1 = RecentFilesManager(config_dir=config_dir)
        for f in test_files:
            rfm1.add_file(f)

        # Create second manager (should load from disk)
        rfm2 = RecentFilesManager(config_dir=config_dir)
        recent = rfm2.get_recent_files()

        # Should have the same files
        assert len(recent) == 3, f"Expected 3 files, got {len(recent)}"
        assert recent[0] == test_files[-1], "Files should persist across instances"

    print("✓ Persistence test passed")


def test_get_with_info():
    """Test getting recent files with additional information."""
    print("Testing get_recent_files_with_info...")

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        config_dir = tmpdir_path / '.test_mbasic'

        # Create test file
        test_file = tmpdir_path / 'test.bas'
        test_file.write_text('10 PRINT "Test"\n')

        # Create manager
        rfm = RecentFilesManager(config_dir=config_dir)
        rfm.add_file(str(test_file))

        # Get with info
        info = rfm.get_recent_files_with_info()

        assert len(info) == 1, "Should have 1 file"
        assert info[0]['path'] == str(test_file.resolve())
        assert info[0]['filename'] == 'test.bas'
        assert info[0]['exists'] == True
        assert 'timestamp' in info[0]

    print("✓ Get with info test passed")


def run_all_tests():
    """Run all tests."""
    print("=" * 60)
    print("RECENT FILES MANAGER TEST SUITE")
    print("=" * 60)
    print()

    try:
        test_basic_operations()
        test_max_files_limit()
        test_duplicate_handling()
        test_file_existence_filtering()
        test_persistence()
        test_get_with_info()

        print()
        print("=" * 60)
        print("ALL TESTS PASSED ✅")
        print("=" * 60)
        return 0

    except AssertionError as e:
        print()
        print("=" * 60)
        print(f"TEST FAILED ❌: {e}")
        print("=" * 60)
        return 1

    except Exception as e:
        print()
        print("=" * 60)
        print(f"UNEXPECTED ERROR ❌: {e}")
        print("=" * 60)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(run_all_tests())
