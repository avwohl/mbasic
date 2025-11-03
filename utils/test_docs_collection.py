#!/usr/bin/env python3
"""
Test the document collection part of the consistency checker.
This doesn't require an API key - just shows what documents would be analyzed.
"""

import sys
from pathlib import Path

def collect_documents():
    """Collect all markdown files from docs directory."""
    docs_dir = Path(__file__).parent.parent / "docs"
    documents = {}
    total_size = 0

    print(f"Scanning: {docs_dir}\n")

    for md_file in sorted(docs_dir.rglob("*.md")):
        # Skip very large files
        file_size = md_file.stat().st_size
        if file_size > 100000:  # Skip files > 100KB
            print(f"⚠️  Skipping large file: {md_file.relative_to(docs_dir)} ({file_size:,} bytes)")
            continue

        try:
            rel_path = md_file.relative_to(docs_dir)
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
                documents[str(rel_path)] = content
                total_size += len(content)
                print(f"✓ {rel_path} ({len(content):,} chars)")
        except Exception as e:
            print(f"✗ Error reading {md_file}: {e}")

    return documents, total_size

def analyze_documents(documents):
    """Basic analysis of collected documents."""
    print("\n" + "="*50)
    print("Document Statistics")
    print("="*50)

    # Count by directory
    dirs = {}
    for path in documents.keys():
        dir_name = Path(path).parts[0] if '/' in path else 'root'
        dirs[dir_name] = dirs.get(dir_name, 0) + 1

    print("\nDocuments by directory:")
    for dir_name, count in sorted(dirs.items()):
        print(f"  {dir_name:20} {count:3} files")

    # Find common terms that might have inconsistencies
    print("\nPotential inconsistency checks:")

    # Check for license mentions
    license_mentions = {}
    for path, content in documents.items():
        if 'LICENSE' in content.upper() or 'BSD' in content or 'MIT' in content:
            for term in ['0BSD', 'MIT', 'BSD', 'Apache', 'GPL']:
                if term in content:
                    if term not in license_mentions:
                        license_mentions[term] = []
                    license_mentions[term].append(path)

    if license_mentions:
        print("\n  License mentions:")
        for license_type, files in license_mentions.items():
            print(f"    {license_type}: {len(files)} files")

    # Check for UI mentions
    ui_terms = ['Web UI', 'web UI', 'web interface', 'Curses UI', 'curses UI',
                'Terminal UI', 'terminal UI', 'Direct mode', 'direct mode']
    ui_mentions = {}
    for path, content in documents.items():
        for term in ui_terms:
            if term in content:
                if term not in ui_mentions:
                    ui_mentions[term] = []
                ui_mentions[term].append(path)

    if ui_mentions:
        print("\n  UI mentions:")
        for ui_type, files in sorted(ui_mentions.items()):
            print(f"    {ui_type}: {len(files)} files")

    # Check for version mentions
    version_patterns = ['5.21', '5.29', 'MBASIC', 'CP/M', 'Python 3']
    version_mentions = {}
    for path, content in documents.items():
        for pattern in version_patterns:
            if pattern in content:
                if pattern not in version_mentions:
                    version_mentions[pattern] = []
                version_mentions[pattern].append(path)

    if version_mentions:
        print("\n  Version/platform mentions:")
        for version, files in sorted(version_mentions.items()):
            print(f"    {version}: {len(files)} files")

def main():
    """Main entry point."""
    print("Documentation Collection Test")
    print("============================\n")

    try:
        documents, total_size = collect_documents()

        print(f"\n{'='*50}")
        print(f"Collected {len(documents)} documents")
        print(f"Total size: {total_size:,} characters")
        print(f"Average size: {total_size//len(documents):,} characters")

        analyze_documents(documents)

        print(f"\n{'='*50}")
        print("✅ Document collection successful!")
        print("\nTo run full consistency check:")
        print("  1. Set ANTHROPIC_API_KEY environment variable")
        print("  2. Run: python3 utils/check_docs_consistency.py")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()