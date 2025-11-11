#!/usr/bin/env python3
"""
Find ALL instances of a specific issue across code and documentation.

This tool is designed to exhaustively find every instance of an issue
to ensure complete resolution per the convergence proposal.

Usage:
    python3 utils/checker/find_all_issue_instances.py "ERL renum"
"""

import sys
import re
from pathlib import Path
from typing import List, Set, Dict, Tuple
import subprocess

class ExhaustiveIssueFinder:
    def __init__(self, issue_description: str):
        self.issue = issue_description
        self.project_root = Path(__file__).parent.parent.parent
        self.results = []

    def generate_search_patterns(self) -> List[str]:
        """Generate multiple search patterns from the issue description."""
        patterns = []

        # For ERL/RENUM specific case
        if "ERL" in self.issue.upper() and "RENUM" in self.issue.upper():
            patterns.extend([
                r"ERL.*renum",
                r"renum.*ERL",
                r"error.*line.*renum",
                r"renumber.*error.*line",
                r"ERL.*renumber",
                r"if\s+ERL\s*[<>=]+\s*\d+",
                r"ERL\s*\+\s*\d+",
                r"ERL\s*\*\s*\d+",
                r"_renum_erl",
                r"renumber.*comparison",
                r"INTENTIONAL.*DEVIATION",
                r"conservative.*renum",
            ])

        # For FileIO case
        elif "FILEIO" in self.issue.upper() or "FILE_IO" in self.issue.upper():
            patterns.extend([
                r"FileIO",
                r"file_io",
                r"filesystem.*abstraction",
                r"SandboxedFileIO",
                r"RealFileIO",
                r"planned.*filesystem",
                r"FileIO.*integration",
                r"FileIO.*status",
            ])

        # Generic patterns based on words in issue
        words = self.issue.split()
        for word in words:
            if len(word) > 2:  # Skip short words
                patterns.append(re.escape(word))
                # Add variations
                patterns.append(word.lower())
                patterns.append(word.upper())
                patterns.append(word.replace('_', '.*'))

        return list(set(patterns))  # Remove duplicates

    def search_with_grep(self, pattern: str) -> List[Tuple[str, int, str]]:
        """Use ripgrep to find matches."""
        results = []
        try:
            # Use ripgrep for speed
            cmd = [
                'rg', '-n', '-i', '--no-heading',
                pattern,
                str(self.project_root)
            ]

            # Exclude certain directories
            cmd.extend(['--glob', '!.git/**'])
            cmd.extend(['--glob', '!__pycache__/**'])
            cmd.extend(['--glob', '!*.pyc'])
            cmd.extend(['--glob', '!build/**'])
            cmd.extend(['--glob', '!dist/**'])

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)

            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if line:
                        parts = line.split(':', 2)
                        if len(parts) >= 3:
                            filepath = parts[0]
                            line_no = int(parts[1])
                            content = parts[2]
                            results.append((filepath, line_no, content))

        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            # Fallback to Python-based search if ripgrep not available
            results.extend(self.python_search(pattern))

        return results

    def python_search(self, pattern: str) -> List[Tuple[str, int, str]]:
        """Fallback Python-based search."""
        results = []
        regex = re.compile(pattern, re.IGNORECASE)

        for ext in ['*.py', '*.md', '*.json']:
            for filepath in self.project_root.rglob(ext):
                if '.git' in str(filepath) or '__pycache__' in str(filepath):
                    continue

                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        for i, line in enumerate(f, 1):
                            if regex.search(line):
                                results.append((str(filepath), i, line.strip()))
                except Exception:
                    continue

        return results

    def find_all_instances(self) -> Dict[str, List[Tuple[int, str]]]:
        """Find all instances of the issue."""
        all_matches = {}
        patterns = self.generate_search_patterns()

        print(f"\nSearching for: {self.issue}")
        print(f"Generated {len(patterns)} search patterns")

        for pattern in patterns:
            print(f"  Searching: {pattern[:50]}...")
            matches = self.search_with_grep(pattern)

            for filepath, line_no, content in matches:
                if filepath not in all_matches:
                    all_matches[filepath] = []

                # Avoid duplicates
                if not any(ln == line_no for ln, _ in all_matches[filepath]):
                    all_matches[filepath].append((line_no, content))

        # Sort by line number within each file
        for filepath in all_matches:
            all_matches[filepath].sort(key=lambda x: x[0])

        return all_matches

    def generate_report(self) -> str:
        """Generate a report of all found instances."""
        matches = self.find_all_instances()

        report = []
        report.append(f"# All Instances of: {self.issue}")
        report.append(f"\nFound in {len(matches)} files\n")

        # Group by directory
        by_dir = {}
        for filepath in sorted(matches.keys()):
            dir_name = str(Path(filepath).parent.relative_to(self.project_root))
            if dir_name not in by_dir:
                by_dir[dir_name] = []
            by_dir[dir_name].append(filepath)

        for dir_name in sorted(by_dir.keys()):
            report.append(f"\n## Directory: {dir_name}")

            for filepath in by_dir[dir_name]:
                rel_path = Path(filepath).relative_to(self.project_root)
                report.append(f"\n### {rel_path}")
                report.append(f"Lines: {len(matches[filepath])}")

                for line_no, content in matches[filepath][:10]:  # Show first 10
                    report.append(f"  {line_no}: {content[:100]}")

                if len(matches[filepath]) > 10:
                    report.append(f"  ... and {len(matches[filepath]) - 10} more")

        # Summary
        total_instances = sum(len(m) for m in matches.values())
        report.append(f"\n## Summary")
        report.append(f"- Total files: {len(matches)}")
        report.append(f"- Total instances: {total_instances}")

        # Most affected files
        report.append(f"\n## Most Affected Files")
        sorted_files = sorted(matches.items(), key=lambda x: len(x[1]), reverse=True)
        for filepath, instances in sorted_files[:10]:
            rel_path = Path(filepath).relative_to(self.project_root)
            report.append(f"- {rel_path}: {len(instances)} instances")

        return '\n'.join(report)

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 find_all_issue_instances.py \"issue description\"")
        print("Example: python3 find_all_issue_instances.py \"ERL renum\"")
        sys.exit(1)

    issue = ' '.join(sys.argv[1:])
    finder = ExhaustiveIssueFinder(issue)
    report = finder.generate_report()

    # Save report
    output_file = Path(f"/tmp/issue_instances_{issue.replace(' ', '_').lower()}.md")
    with open(output_file, 'w') as f:
        f.write(report)

    print(f"\nReport saved to: {output_file}")
    print(report)

if __name__ == "__main__":
    main()