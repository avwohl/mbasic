#!/usr/bin/env python3
"""Parse docs_todo file and extract issues for processing."""

import re
from pathlib import Path

def parse_todos(filepath):
    """Parse the todo file and return a list of issues."""
    with open(filepath, 'r') as f:
        content = f.read()

    issues = []
    current_issue = {}
    in_issue = False

    lines = content.split('\n')
    for i, line in enumerate(lines):
        if line.startswith('####'):
            # Save previous issue if exists
            if current_issue:
                issues.append(current_issue)
            # Start new issue
            current_issue = {
                'category': line.strip('# ').strip(),
                'description': '',
                'files': [],
                'details': '',
                'line_start': i + 1
            }
            in_issue = True
        elif line.startswith('**Description:**'):
            current_issue['description'] = line.replace('**Description:**', '').strip()
        elif line.startswith('**Affected files:**'):
            # Next lines will be file list
            pass
        elif line.startswith('- `') and in_issue:
            # Extract filename
            match = re.search(r'`([^`]+)`', line)
            if match:
                current_issue['files'].append(match.group(1))
        elif line.startswith('**Details:**'):
            # Collect details until next separator
            details_lines = []
            j = i + 1
            while j < len(lines) and not lines[j].startswith('---') and not lines[j].startswith('####'):
                details_lines.append(lines[j])
                j += 1
            current_issue['details'] = '\n'.join(details_lines).strip()
        elif line.startswith('---'):
            # Issue separator
            pass

    # Add last issue
    if current_issue:
        issues.append(current_issue)

    return issues

if __name__ == '__main__':
    todo_file = Path('/home/wohl/cl/mbasic/docs/history/docs_todo-v12.md')
    issues = parse_todos(todo_file)

    print(f"Total issues: {len(issues)}")
    print(f"\nFirst 5 issues:")
    for i, issue in enumerate(issues[:5], 1):
        print(f"\n{i}. {issue['category']}")
        print(f"   Description: {issue['description']}")
        print(f"   Files: {', '.join(issue['files'])}")
