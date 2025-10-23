#!/usr/bin/env python3
"""Find duplicate BASIC files by content"""

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

def normalize_basename(name):
    """Normalize basename for comparison (case-insensitive)"""
    return name.lower()

def find_duplicates(base_dir):
    """Find duplicate files by content hash"""
    hash_to_files = defaultdict(list)

    # Find all .bas/.BAS files
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.bas') or file.endswith('.BAS'):
                filepath = os.path.join(root, file)
                file_hash = get_file_hash(filepath)
                if file_hash:
                    hash_to_files[file_hash].append(filepath)

    # Find duplicates
    duplicates = {h: files for h, files in hash_to_files.items() if len(files) > 1}

    return duplicates, hash_to_files

def find_case_variants(base_dir):
    """Find files that differ only in case"""
    basename_to_files = defaultdict(list)

    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.bas') or file.endswith('.BAS'):
                filepath = os.path.join(root, file)
                # Store by normalized basename
                norm_name = normalize_basename(file)
                basename_to_files[norm_name].append(filepath)

    # Find case variants
    case_variants = {name: files for name, files in basename_to_files.items()
                     if len(files) > 1}

    return case_variants

def main():
    base_dir = 'basic'

    print("=" * 70)
    print("FINDING DUPLICATES BY CONTENT")
    print("=" * 70)

    duplicates, all_hashes = find_duplicates(base_dir)

    if duplicates:
        print(f"\nFound {len(duplicates)} sets of duplicate files:\n")

        for file_hash, files in sorted(duplicates.items()):
            print(f"\nDuplicate set (hash: {file_hash[:8]}...):")
            files_sorted = sorted(files)
            for i, f in enumerate(files_sorted):
                size = os.path.getsize(f)
                marker = " [KEEP]" if i == 0 else " [REMOVE]"
                print(f"  {marker} {f} ({size} bytes)")
    else:
        print("\n✓ No exact duplicate files found by content")

    print("\n" + "=" * 70)
    print("FINDING CASE VARIANTS (same name, different case)")
    print("=" * 70)

    case_variants = find_case_variants(base_dir)

    if case_variants:
        print(f"\nFound {len(case_variants)} files with case variants:\n")

        for norm_name, files in sorted(case_variants.items()):
            print(f"\nCase variants of '{norm_name}':")
            files_sorted = sorted(files)
            for i, f in enumerate(files_sorted):
                size = os.path.getsize(f)
                basename = os.path.basename(f)
                marker = " [KEEP]" if i == 0 else " [REMOVE?]"
                print(f"  {marker} {f} ({size} bytes, name: {basename})")
    else:
        print("\n✓ No case variant files found")

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Total files scanned: {len(all_hashes)}")
    print(f"Exact duplicate sets: {len(duplicates)}")
    print(f"Case variant sets: {len(case_variants)}")

    # Calculate how many files would be removed
    remove_count = sum(len(files) - 1 for files in duplicates.values())
    print(f"Files that could be removed (exact duplicates): {remove_count}")

if __name__ == '__main__':
    main()
