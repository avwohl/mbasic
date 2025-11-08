#!/usr/bin/env python3
"""Check which documentation issues have been fixed."""

import re
from pathlib import Path

def parse_issues(filepath):
    """Parse the todo file into individual issues."""
    with open(filepath, 'r') as f:
        content = f.read()

    issues = []
    sections = content.split('---\n')

    for section in sections:
        section = section.strip()
        if not section or section.startswith('###'):
            continue

        # Extract key parts
        issue = {'raw': section}

        # Category (####)
        cat_match = re.search(r'^####\s+(.+)$', section, re.MULTILINE)
        if cat_match:
            issue['category'] = cat_match.group(1).strip()

        # Description
        desc_match = re.search(r'\*\*Description:\*\*\s+(.+?)(?:\n|$)', section)
        if desc_match:
            issue['description'] = desc_match.group(1).strip()

        # Affected files
        files = re.findall(r'^- `([^`]+)`', section, re.MULTILINE)
        issue['files'] = files

        # Details
        details_match = re.search(r'\*\*Details:\*\*\s*\n(.+)', section, re.DOTALL)
        if details_match:
            issue['details'] = details_match.group(1).strip()

        if issue.get('files'):
            issues.append(issue)

    return issues

def check_issue_fixed(issue):
    """Quick heuristic check if an issue might be fixed."""
    # This is a simple heuristic - we check if certain key phrases from the issue
    # description suggest it's a common type of issue that's likely been batch-fixed
    desc = issue.get('description', '').lower()

    # Issues that mention these are often already fixed:
    likely_fixed_indicators = [
        'unclear purpose',
        'needs clarification',
        'has unclear',
        'referenced',
        'missing documentation for.*module',  # cross-ref issues
    ]

    for indicator in likely_fixed_indicators:
        if re.search(indicator, desc):
            return 'LIKELY_FIXED'

    return 'NEEDS_CHECK'

def main():
    todo_file = Path('/home/wohl/cl/mbasic/docs/history/docs_todo-v12.md')
    issues = parse_issues(todo_file)

    print(f"Total issues parsed: {len(issues)}\n")

    # Group by file
    by_file = {}
    for issue in issues:
        for file in issue['files']:
            if file not in by_file:
                by_file[file] = []
            by_file[file].append(issue)

    print("Issues by file (sorted by count):")
    for file, file_issues in sorted(by_file.items(), key=lambda x: -len(x[1]))[:10]:
        print(f"  {len(file_issues):3d}  {file}")

    # Check which might be fixed
    likely_fixed = 0
    needs_check = 0

    for issue in issues:
        status = check_issue_fixed(issue)
        if status == 'LIKELY_FIXED':
            likely_fixed += 1
        else:
            needs_check += 1

    print(f"\nHeuristic analysis:")
    print(f"  Likely fixed: {likely_fixed}")
    print(f"  Needs checking: {needs_check}")

if __name__ == '__main__':
    main()
