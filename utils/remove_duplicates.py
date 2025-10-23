#!/usr/bin/env python3
"""Remove duplicate BASIC files, keeping preferred versions"""

import os
import hashlib
from pathlib import Path
from collections import defaultdict

def get_file_hash(filepath):
    """Calculate MD5 hash of file content"""
    try:
        with open(filepath, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return None

def priority_score(filepath):
    """
    Calculate priority score for keeping a file.
    Higher score = more likely to keep.
    """
    score = 0
    path_parts = filepath.split(os.sep)

    # Prefer files NOT in test directories (keep working files over tests)
    if 'bas_tests' in path_parts:
        score -= 100
    if 'bas_tests1' in path_parts:
        score -= 100

    # Prefer files NOT in bad_syntax (keep good files)
    if 'bad_syntax' in path_parts:
        score -= 50

    # Prefer files NOT in bad_not521
    if 'bad_not521' in path_parts:
        score -= 50

    # Prefer files in the root basic/ directory
    if len(path_parts) == 2 and path_parts[0] == 'basic':
        score += 100

    # Prefer lowercase filenames (convention)
    basename = os.path.basename(filepath)
    if basename == basename.lower():
        score += 10

    return score

def find_duplicates(base_dir):
    """Find duplicate files by content hash"""
    hash_to_files = defaultdict(list)

    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.bas') or file.endswith('.BAS'):
                filepath = os.path.join(root, file)
                file_hash = get_file_hash(filepath)
                if file_hash:
                    hash_to_files[file_hash].append(filepath)

    duplicates = {h: files for h, files in hash_to_files.items() if len(files) > 1}
    return duplicates

def remove_duplicates(base_dir, dry_run=True):
    """Remove duplicate files, keeping the best version"""
    duplicates = find_duplicates(base_dir)

    if not duplicates:
        print("No duplicates found!")
        return

    removed_count = 0
    kept_count = 0

    for file_hash, files in sorted(duplicates.items()):
        # Sort by priority (highest first)
        files_with_scores = [(f, priority_score(f)) for f in files]
        files_sorted = sorted(files_with_scores, key=lambda x: (-x[1], x[0]))

        # Keep the first (highest priority) file
        keep_file = files_sorted[0][0]
        kept_count += 1

        print(f"\nDuplicate set (hash: {file_hash[:8]}...):")
        print(f"  [KEEP]   {keep_file} (score: {files_sorted[0][1]})")

        # Remove the rest
        for filepath, score in files_sorted[1:]:
            if dry_run:
                print(f"  [REMOVE] {filepath} (score: {score})")
            else:
                try:
                    os.remove(filepath)
                    print(f"  [REMOVED] {filepath} (score: {score})")
                    removed_count += 1
                except Exception as e:
                    print(f"  [ERROR] Failed to remove {filepath}: {e}")

    print("\n" + "=" * 70)
    if dry_run:
        print("DRY RUN - No files were actually removed")
    print(f"Files kept: {kept_count}")
    print(f"Files {'would be' if dry_run else ''} removed: {sum(len(files) - 1 for files in duplicates.values())}")

def main():
    import sys

    base_dir = 'basic'
    dry_run = '--execute' not in sys.argv

    if dry_run:
        print("=" * 70)
        print("DRY RUN MODE - No files will be removed")
        print("Run with --execute to actually remove files")
        print("=" * 70)
    else:
        print("=" * 70)
        print("EXECUTION MODE - Files will be removed!")
        print("=" * 70)

    remove_duplicates(base_dir, dry_run=dry_run)

if __name__ == '__main__':
    main()
