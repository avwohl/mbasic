#!/usr/bin/env python3
"""
Utilities for parsing YAML front matter in markdown files.

This module provides tools for:
- Parsing markdown files with YAML front matter
- Building search indexes from help documentation
- Searching help content by keywords, aliases, and categories
- Finding related topics based on metadata
"""

import frontmatter
from pathlib import Path
from typing import Dict, List, Optional, Set
import json


def parse_markdown_file(file_path: Path) -> Dict:
    """
    Parse markdown file with YAML front matter.

    Args:
        file_path: Path to markdown file

    Returns:
        Dictionary with:
            'metadata': dict - YAML front matter
            'content': str - Markdown content
            'path': Path - File path
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        post = frontmatter.load(f)

    return {
        'metadata': dict(post.metadata),
        'content': post.content,
        'path': file_path
    }


def build_search_index(help_root: Path) -> Dict:
    """
    Build search index from all markdown files with front matter.

    Args:
        help_root: Root directory containing help files

    Returns:
        Dictionary with:
            'files': List of file metadata dicts
            'keywords': Dict mapping keywords to file paths
            'aliases': Dict mapping aliases to file paths
            'categories': Dict mapping categories to file paths
            'by_type': Dict mapping document types to file paths
    """
    index = {
        'files': [],
        'keywords': {},
        'aliases': {},
        'categories': {},
        'by_type': {}
    }

    for md_file in help_root.rglob('*.md'):
        # Skip index files
        if md_file.name in ('index.md', 'INDEX.md'):
            continue

        try:
            parsed = parse_markdown_file(md_file)
            metadata = parsed['metadata']

            if not metadata:
                continue  # No front matter, skip

            rel_path = md_file.relative_to(help_root)
            rel_path_str = str(rel_path)

            # Add to files list
            file_entry = {
                'path': rel_path_str,
                'title': metadata.get('title', ''),
                'type': metadata.get('type', ''),
                'category': metadata.get('category', ''),
                'description': metadata.get('description', ''),
            }
            index['files'].append(file_entry)

            # Index keywords
            for keyword in metadata.get('keywords', []):
                keyword_lower = keyword.lower()
                if keyword_lower not in index['keywords']:
                    index['keywords'][keyword_lower] = []
                index['keywords'][keyword_lower].append(rel_path_str)

            # Index aliases
            for alias in metadata.get('aliases', []):
                index['aliases'][alias.upper()] = rel_path_str

            # Index by category
            category = metadata.get('category', '')
            if category:
                if category not in index['categories']:
                    index['categories'][category] = []
                index['categories'][category].append(rel_path_str)

            # Index by type
            doc_type = metadata.get('type', '')
            if doc_type:
                if doc_type not in index['by_type']:
                    index['by_type'][doc_type] = []
                index['by_type'][doc_type].append(rel_path_str)

        except Exception as e:
            print(f"Warning: Error parsing {md_file}: {e}")

    return index


def search_help(query: str, index: Dict) -> List[str]:
    """
    Search help index for query.

    Args:
        query: Search term
        index: Search index from build_search_index()

    Returns:
        List of matching file paths (relative to help root)
    """
    query_lower = query.lower()
    results: Set[str] = set()

    # Exact alias match (highest priority)
    if query.upper() in index['aliases']:
        results.add(index['aliases'][query.upper()])

    # Keyword match
    for keyword, files in index['keywords'].items():
        if query_lower in keyword:
            results.update(files)

    # Title match
    for entry in index['files']:
        if query_lower in entry['title'].lower():
            results.add(entry['path'])

    # Description match
    for entry in index['files']:
        description = entry.get('description', '')
        if description and query_lower in description.lower():
            results.add(entry['path'])

    # Category match
    for category, files in index['categories'].items():
        if query_lower in category.lower():
            results.update(files)

    return sorted(list(results))


def get_related_topics(file_path: str, help_root: Path) -> List[Dict]:
    """
    Get related topics for a file based on its front matter.

    Args:
        file_path: Relative path to help file
        help_root: Root directory containing help files

    Returns:
        List of related file metadata dicts with:
            'path': str - Relative path
            'title': str - Title from front matter
            'description': str - Description from front matter
    """
    full_path = help_root / file_path

    if not full_path.exists():
        return []

    parsed = parse_markdown_file(full_path)
    metadata = parsed['metadata']

    related_names = metadata.get('related', [])
    if not related_names:
        return []

    related_files = []
    parent_dir = full_path.parent

    for name in related_names:
        # Try to find file matching name
        # Try same directory first
        candidate = parent_dir / f"{name}.md"

        if candidate.exists():
            try:
                related_parsed = parse_markdown_file(candidate)
                related_files.append({
                    'path': str(candidate.relative_to(help_root)),
                    'title': related_parsed['metadata'].get('title', name),
                    'description': related_parsed['metadata'].get('description', '')
                })
            except Exception:
                pass  # Skip files we can't parse

    return related_files


def save_index(index: Dict, output_file: Path) -> None:
    """
    Save search index to JSON file.

    Args:
        index: Search index from build_search_index()
        output_file: Path to output JSON file
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(index, f, indent=2)


def load_index(index_file: Path) -> Dict:
    """
    Load search index from JSON file.

    Args:
        index_file: Path to JSON index file

    Returns:
        Search index dictionary
    """
    with open(index_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_files_by_category(category: str, index: Dict) -> List[Dict]:
    """
    Get all files in a category.

    Args:
        category: Category name
        index: Search index

    Returns:
        List of file metadata dicts
    """
    file_paths = index['categories'].get(category, [])

    files = []
    for entry in index['files']:
        if entry['path'] in file_paths:
            files.append(entry)

    return files


def get_files_by_type(doc_type: str, index: Dict) -> List[Dict]:
    """
    Get all files of a specific type.

    Args:
        doc_type: Document type (statement, function, guide, etc.)
        index: Search index

    Returns:
        List of file metadata dicts
    """
    file_paths = index['by_type'].get(doc_type, [])

    files = []
    for entry in index['files']:
        if entry['path'] in file_paths:
            files.append(entry)

    return files


def main():
    """Command-line interface for building search indexes."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Build search index from help files with YAML front matter'
    )
    parser.add_argument('help_dir', type=Path,
                       help='Directory containing help files')
    parser.add_argument('-o', '--output', type=Path,
                       default=None,
                       help='Output JSON file (default: help_dir/search_index.json)')
    parser.add_argument('--search', type=str,
                       help='Search for a term (requires existing index)')

    args = parser.parse_args()

    if args.search:
        # Load existing index and search
        index_file = args.output or (args.help_dir / 'search_index.json')
        if not index_file.exists():
            print(f"Error: Index file {index_file} not found")
            print("Build index first without --search flag")
            return 1

        index = load_index(index_file)
        results = search_help(args.search, index)

        print(f"\nSearch results for '{args.search}':")
        print("=" * 60)

        if results:
            for path in results:
                # Find metadata
                for entry in index['files']:
                    if entry['path'] == path:
                        print(f"\n  {entry['title']}")
                        print(f"  → {path}")
                        if entry.get('description'):
                            print(f"    {entry['description']}")
                        break
        else:
            print("  No results found")

        print()

    else:
        # Build index
        print(f"Building search index for {args.help_dir}...")
        index = build_search_index(args.help_dir)

        output_file = args.output or (args.help_dir / 'search_index.json')
        save_index(index, output_file)

        print(f"\nIndex built successfully!")
        print(f"  Files indexed: {len(index['files'])}")
        print(f"  Keywords: {len(index['keywords'])}")
        print(f"  Aliases: {len(index['aliases'])}")
        print(f"  Categories: {len(index['categories'])}")
        print(f"  Types: {len(index['by_type'])}")
        print(f"\nSaved to: {output_file}")
        print(f"\nTo search: {parser.prog} {args.help_dir} --search <term>")

    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())
