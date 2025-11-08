#!/usr/bin/env python3
"""Bulk process documentation issues from docs_todo file."""

import re
from pathlib import Path
from collections import defaultdict

def parse_all_issues(filepath):
    """Parse all issues from the todo file."""
    with open(filepath, 'r') as f:
        content = f.read()

    # Split by --- separator
    sections = content.split('\n---\n')
    issues = []

    for section in sections:
        section = section.strip()
        if not section or section.startswith('###'):
            continue

        issue = {'raw': section}

        # Extract category
        cat_match = re.search(r'^####\s+(.+)$', section, re.MULTILINE)
        if cat_match:
            issue['category'] = cat_match.group(1).strip()

        # Extract description
        desc_match = re.search(r'\*\*Description:\*\*\s+(.+?)(\n|$)', section)
        if desc_match:
            issue['description'] = desc_match.group(1).strip()

        # Extract affected files
        files = re.findall(r'^-\s+`([^`]+)`', section, re.MULTILINE)
        issue['files'] = files

        # Extract details
        details_match = re.search(r'\*\*Details:\*\*\s*\n(.+)', section, re.DOTALL)
        if details_match:
            issue['details'] = details_match.group(1).strip()

        if issue.get('files'):
            issues.append(issue)

    return issues

def categorize_issues(issues):
    """Categorize issues by type and likely status."""
    categories = {
        'already_fixed': [],
        'simple_comment_fix': [],
        'terminology_consistency': [],
        'needs_manual_review': []
    }

    for issue in issues:
        desc = issue.get('description', '').lower()
        details = issue.get('details', '').lower()

        # Check for indicators that suggest issue is already fixed
        if any(phrase in desc for phrase in [
            'unclear purpose',
            'needs clarification',
            'missing documentation for.*module referenced',
        ]):
            categories['already_fixed'].append(issue)

        # Simple redundant comment issues
        elif 'redundant' in desc or 'duplicates information' in details:
            categories['simple_comment_fix'].append(issue)

        # Terminology inconsistencies
        elif 'inconsistent terminology' in desc or 'terminology' in desc:
            categories['terminology_consistency'].append(issue)

        else:
            categories['needs_manual_review'].append(issue)

    return categories

def generate_summary_report(issues):
    """Generate a summary report of all issues."""
    # Group by file
    by_file = defaultdict(list)
    for issue in issues:
        for file in issue.get('files', []):
            by_file[file].append(issue)

    print("="*70)
    print("DOCUMENTATION ISSUES SUMMARY")
    print("="*70)
    print(f"\nTotal issues: {len(issues)}")

    print(f"\nTop 15 files by issue count:")
    for file, file_issues in sorted(by_file.items(), key=lambda x: -len(x[1]))[:15]:
        print(f"  {len(file_issues):3d}  {file}")

    # Categorize
    categories = categorize_issues(issues)
    print(f"\nCategorization (heuristic):")
    print(f"  Likely already fixed: {len(categories['already_fixed'])}")
    print(f"  Simple comment fixes: {len(categories['simple_comment_fix'])}")
    print(f"  Terminology fixes: {len(categories['terminology_consistency'])}")
    print(f"  Needs manual review: {len(categories['needs_manual_review'])}")

    return categories

def main():
    todo_file = Path('/home/wohl/cl/mbasic/docs/history/docs_todo-v12.md')
    issues = parse_all_issues(todo_file)

    categories = generate_summary_report(issues)

    # Show sample of each category
    print("\n" + "="*70)
    print("SAMPLE ISSUES BY CATEGORY")
    print("="*70)

    for cat_name, cat_issues in categories.items():
        if cat_issues:
            print(f"\n{cat_name.upper().replace('_', ' ')} ({len(cat_issues)} issues):")
            for issue in cat_issues[:2]:  # Show first 2 of each category
                print(f"  - {issue.get('description', 'N/A')[:80]}")
                print(f"    Files: {', '.join(issue.get('files', [])[:2])}")

if __name__ == '__main__':
    main()
