#!/usr/bin/env python3
"""
Documentation and Code Consistency Checker (Enhanced Version)

This script uses the Claude API to analyze documentation files AND source code
to identify inconsistencies between:
- Documentation files
- Code and comments
- Python and JSON files

New features:
- Checks .py and .json files in addition to .md
- Analyzes code vs comment conflicts
- Reads src tree before docs tree for better context
- Asks for clarification when uncertain about conflicts

Usage:
    python3 utils/check_docs_consistency2.py

Requires:
    - ANTHROPIC_API_KEY environment variable
    - anthropic package (pip install anthropic)
"""

import os
import sys
import json
from pathlib import Path
from typing import List, Dict, Any, Tuple
import hashlib
import time
import ast

USE_MODEL='claude-sonnet-4-5'

try:
    import anthropic
except ImportError:
    print("Error: anthropic package not installed")
    print("Run: pip install anthropic")
    sys.exit(1)

class EnhancedConsistencyAnalyzer:
    def __init__(self, api_key: str = None):
        """Initialize the analyzer with Claude API."""
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")

        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.project_root = Path(__file__).parent.parent
        self.docs_dir = self.project_root / "docs"
        self.src_dir = self.project_root / "src"
        self.utils_dir = self.project_root / "utils"
        self.tests_dir = self.project_root / "tests"
        self.cache_file = Path(__file__).parent / ".consistency_cache.json"

        # Scan these doc subdirectories
        self.scan_subdirs = ['help', 'library', 'stylesheets', 'user']

        # Track code context for better analysis
        self.code_context = {}
        self.comment_conflicts = []

    def collect_source_files(self) -> Dict[str, str]:
        """Collect Python and JSON files from src tree and other directories."""
        source_files = {}

        # Directories to scan for source code
        code_dirs = [
            (self.src_dir, "src"),
#            (self.utils_dir, "utils"),
#            (self.tests_dir, "tests"),
            (self.project_root, "root")  # For root-level .py files
        ]

        print("Scanning source code directories...")

        for directory, label in code_dirs:
            if not directory.exists():
                print(f"Skipping non-existent directory: {directory}")
                continue

            print(f"Scanning {label} directory for .py and .json files...")

            # For root directory, only get direct .py files (not recursive)
            if label == "root":
                patterns = [('*.py', False), ('*.json', False)]
            else:
                patterns = [('**/*.py', True), ('**/*.json', True)]

            for pattern, is_recursive in patterns:
                if is_recursive:
                    files = directory.rglob(pattern)
                else:
                    files = directory.glob(pattern)

                for file_path in files:
                    # Skip certain files/directories
                    parts = file_path.parts
                    if any(part in ['.git', '__pycache__', '.venv', 'venv',
                           'build', 'dist', '.egg-info'] for part in parts):
                        continue

                    # Skip very large files
                    if file_path.stat().st_size > 200000:  # Skip files > 200KB
                        print(f"Skipping large file: {file_path}")
                        continue

                    try:
                        rel_path = file_path.relative_to(self.project_root)
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            source_files[str(rel_path)] = content
                            print(f"Collected source: {rel_path}")

                            # Extract code context for Python files
                            if file_path.suffix == '.py':
                                self._extract_code_context(str(rel_path), content)

                    except Exception as e:
                        print(f"Error reading {file_path}: {e}")

        return source_files

    def _extract_code_context(self, filepath: str, content: str):
        """Extract functions, classes, and their docstrings/comments for analysis."""
        try:
            tree = ast.parse(content)

            context = {
                'functions': {},
                'classes': {},
                'module_docstring': ast.get_docstring(tree),
                'comments': self._extract_comments(content)
            }

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    context['functions'][node.name] = {
                        'docstring': ast.get_docstring(node),
                        'lineno': node.lineno
                    }
                elif isinstance(node, ast.ClassDef):
                    context['classes'][node.name] = {
                        'docstring': ast.get_docstring(node),
                        'lineno': node.lineno,
                        'methods': {}
                    }
                    # Get methods
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            context['classes'][node.name]['methods'][item.name] = {
                                'docstring': ast.get_docstring(item),
                                'lineno': item.lineno
                            }

            self.code_context[filepath] = context

        except SyntaxError as e:
            print(f"Syntax error in {filepath}: {e}")
            self.code_context[filepath] = {'error': str(e)}

    def _extract_comments(self, content: str) -> List[Dict[str, Any]]:
        """Extract inline comments from Python code."""
        comments = []
        lines = content.split('\n')

        for i, line in enumerate(lines, 1):
            # Find inline comments
            if '#' in line:
                # Check if it's not inside a string
                in_string = False
                escape_next = False
                quote_char = None

                for j, char in enumerate(line):
                    if escape_next:
                        escape_next = False
                        continue

                    if char == '\\':
                        escape_next = True
                        continue

                    if char in ['"', "'"]:
                        if not in_string:
                            in_string = True
                            quote_char = char
                        elif char == quote_char:
                            in_string = False
                            quote_char = None

                    if char == '#' and not in_string:
                        comment = line[j:].strip()
                        code_before = line[:j].strip()
                        comments.append({
                            'line': i,
                            'comment': comment,
                            'code': code_before
                        })
                        break

        return comments

    def collect_documents(self) -> Dict[str, str]:
        """Collect markdown files from specified subdirectories."""
        documents = {}

        # Scan the specified subdirectories
        for subdir in self.scan_subdirs:
            subdir_path = self.docs_dir / subdir
            if not subdir_path.exists():
                print(f"Skipping non-existent directory: {subdir}")
                continue

            print(f"Scanning documentation directory: {subdir}")
            for md_file in subdir_path.rglob("*.md"):
                # Skip very large files
                if md_file.stat().st_size > 100000:  # Skip files > 100KB
                    print(f"Skipping large file: {md_file}")
                    continue

                try:
                    rel_path = md_file.relative_to(self.project_root)
                    with open(md_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        documents[str(rel_path)] = content
                        print(f"Collected doc: {rel_path}")
                except Exception as e:
                    print(f"Error reading {md_file}: {e}")

        return documents

    def analyze_code_comment_conflicts(self, source_files: Dict[str, str]) -> List[Dict[str, Any]]:
        """Analyze Python files for code vs comment conflicts."""
        conflicts = []

        print("\nAnalyzing code vs comment consistency...")

        for filepath, content in source_files.items():
            if not filepath.endswith('.py'):
                continue
            print(f"Read {filepath}")

            # Prepare prompt for Claude
            prompt = f"""Analyze this Python file for conflicts between code and comments.
Look for:
1. Comments that describe behavior different from what the code actually does
2. Outdated comments from refactoring where code changed but comments didn't
3. Comments that are correct but the code has a bug
4. Docstrings that don't match function/class behavior
5. TODO/FIXME comments that may have been addressed but not removed

File: {filepath}

```python
{content}
```

For each conflict found, return a JSON object with:
- "type": "code_bug" or "comment_outdated" or "unclear" (if you can't determine which)
- "line": approximate line number
- "code_snippet": the relevant code
- "comment": the conflicting comment/docstring
- "explanation": why they conflict
- "suggested_fix": your recommendation (or "NEEDS_HUMAN_REVIEW" if unclear)

Return a JSON array of conflicts. Return empty array [] if no conflicts found.
IMPORTANT: If you cannot determine whether the code or comment is correct, mark type as "unclear" and suggested_fix as "NEEDS_HUMAN_REVIEW".

OUTPUT REQUIREMENTS:
- Return ONLY the raw JSON array starting with [ and ending with ]
- DO NOT wrap the JSON in markdown code blocks (no ``` or ```json)
- No markdown formatting whatsoever
- No explanatory text before or after the JSON
- Just the pure JSON array text"""

            try:
                response = self.client.messages.create(
                    model=USE_MODEL,
                    max_tokens=4000,
                    temperature=0,
                    messages=[{"role": "user", "content": prompt}]
                )

                response_text = response.content[0].text.strip()

                # Try to extract JSON from response
                file_conflicts = None

                # First, strip markdown code block formatting if present
                import re
                # Remove ```json or ``` at start and ``` at end
                cleaned_text = response_text.strip()
                if cleaned_text.startswith('```json'):
                    cleaned_text = cleaned_text[7:].lstrip('\n')  # Remove ```json and newline
                elif cleaned_text.startswith('```'):
                    cleaned_text = cleaned_text[3:].lstrip('\n')  # Remove ``` and newline
                if cleaned_text.endswith('```'):
                    cleaned_text = cleaned_text[:-3].rstrip('\n')  # Remove trailing ``` and newline
                cleaned_text = cleaned_text.strip()

                try:
                    # Try direct JSON parsing on cleaned text
                    file_conflicts = json.loads(cleaned_text)
                except json.JSONDecodeError:
                    # Try to extract JSON array from response text
                    json_match = re.search(r'\[.*\]', cleaned_text, re.DOTALL)
                    if json_match:
                        try:
                            file_conflicts = json.loads(json_match.group())
                        except json.JSONDecodeError:
                            pass

                    if not file_conflicts:
                        # Show what we got for debugging
                        print(f"Warning: Could not parse Claude's response for {filepath}")
                        if len(response_text) < 200:
                            print(f"  Response was: {response_text}")
                        else:
                            print(f"  Response started with: {response_text[:200]}...")

                # Add found conflicts if any
                if file_conflicts:
                    for conflict in file_conflicts:
                        conflict['file'] = filepath
                    conflicts.extend(file_conflicts)

            except Exception as e:
                print(f"Error analyzing {filepath}: {e}")

            # Rate limiting
            time.sleep(0.5)

        return conflicts

    def chunk_all_content(self, source_files: Dict[str, str], documents: Dict[str, str],
                         max_chunk_size: int = 50000) -> List[Dict[str, Any]]:
        """Chunk both source files and documents for analysis."""
        chunks = []

        # Combine all content
        all_content = {}

        # Add source files first (priority)
        for path, content in source_files.items():
            all_content[f"CODE:{path}"] = content

        # Then add documentation
        for path, content in documents.items():
            all_content[f"DOC:{path}"] = content

        current_chunk = {"files": {}, "size": 0}

        # Sort to keep related files together
        sorted_content = sorted(all_content.items(), key=lambda x: x[0])

        for filepath, content in sorted_content:
            doc_size = len(content)

            # If this doc alone is too big, split it
            if doc_size > max_chunk_size:
                # Save current chunk if it has content
                if current_chunk["files"]:
                    chunks.append(current_chunk)
                    current_chunk = {"files": {}, "size": 0}

                # Split the large document
                lines = content.split('\n')
                partial_content = []
                partial_size = 0
                part_num = 1

                for line in lines:
                    line_size = len(line) + 1
                    if partial_size + line_size > max_chunk_size and partial_content:
                        part_name = f"{filepath} (part {part_num})"
                        chunks.append({
                            "files": {part_name: '\n'.join(partial_content)},
                            "size": partial_size
                        })
                        partial_content = [line]
                        partial_size = line_size
                        part_num += 1
                    else:
                        partial_content.append(line)
                        partial_size += line_size

                # Save last part
                if partial_content:
                    part_name = f"{filepath} (part {part_num})"
                    chunks.append({
                        "files": {part_name: '\n'.join(partial_content)},
                        "size": partial_size
                    })

            # If adding this doc would exceed chunk size, start new chunk
            elif current_chunk["size"] + doc_size > max_chunk_size:
                if current_chunk["files"]:
                    chunks.append(current_chunk)
                current_chunk = {"files": {filepath: content}, "size": doc_size}

            # Add to current chunk
            else:
                current_chunk["files"][filepath] = content
                current_chunk["size"] += doc_size

        # Don't forget the last chunk
        if current_chunk["files"]:
            chunks.append(current_chunk)

        return chunks

    def analyze_chunk(self, chunk: Dict[str, Any], chunk_num: int, total_chunks: int) -> List[Dict[str, Any]]:
        """Send a chunk to Claude for comprehensive analysis."""
        print(f"\nAnalyzing chunk {chunk_num}/{total_chunks} ({len(chunk['files'])} files)...")

        # Separate code and doc files
        code_files = {}
        doc_files = {}

        for filepath, content in chunk['files'].items():
            if filepath.startswith("CODE:"):
                code_files[filepath[5:]] = content
            elif filepath.startswith("DOC:"):
                doc_files[filepath[4:]] = content

        # Prepare the content
        content_parts = []

        if code_files:
            content_parts.append("=== SOURCE CODE FILES ===")
            for filepath, content in code_files.items():
                file_type = "Python" if filepath.endswith('.py') else "JSON" if filepath.endswith('.json') else "Other"
                content_parts.append(f"\n--- {file_type} File: {filepath} ---\n{content}")

        if doc_files:
            content_parts.append("\n=== DOCUMENTATION FILES ===")
            for filepath, content in doc_files.items():
                content_parts.append(f"\n--- Doc File: {filepath} ---\n{content}")

        prompt = f"""You are analyzing code and documentation for inconsistencies.

{'\n'.join(content_parts)}

Please identify ALL types of inconsistencies:

1. Documentation inconsistencies:
   - Contradictory information between docs
   - Missing references or incomplete lists
   - Outdated information
   - Version mismatches
   - Command/path inconsistencies

2. Code vs Documentation inconsistencies:
   - Features documented but not implemented
   - Features implemented but not documented
   - Different behavior described vs implemented
   - API mismatches

3. Code vs Comment conflicts:
   - Comments describing different behavior than code
   - Outdated comments from refactoring
   - Docstrings not matching implementation

4. JSON configuration inconsistencies:
   - Config values that don't match documentation
   - Missing or extra config options
   - Type mismatches

Format your response as a JSON array. Each item should have:
- "type": category of inconsistency
- "severity": "high", "medium", or "low"
- "files": list of affected files
- "description": clear description of the inconsistency
- "details": specific quotes or code examples
- "conflict_type": (for code/comment conflicts) "code_bug", "comment_outdated", or "unclear"
- "needs_clarification": true if human review needed to determine which is correct

Return ONLY the raw JSON array, no markdown formatting (no ``` or ```json), no other text. Empty array [] if no issues."""

        try:
            response = self.client.messages.create(
                model=USE_MODEL,
                max_tokens=4000,
                temperature=0,
                messages=[{"role": "user", "content": prompt}]
            )

            response_text = response.content[0].text.strip()

            # Strip markdown code block formatting if present
            import re
            cleaned_text = response_text.strip()
            if cleaned_text.startswith('```json'):
                cleaned_text = cleaned_text[7:].lstrip('\n')  # Remove ```json and newline
            elif cleaned_text.startswith('```'):
                cleaned_text = cleaned_text[3:].lstrip('\n')  # Remove ``` and newline
            if cleaned_text.endswith('```'):
                cleaned_text = cleaned_text[:-3].rstrip('\n')  # Remove trailing ``` and newline
            cleaned_text = cleaned_text.strip()

            try:
                result = json.loads(cleaned_text)
                return result
            except json.JSONDecodeError:
                json_match = re.search(r'\[.*\]', cleaned_text, re.DOTALL)
                if json_match:
                    try:
                        return json.loads(json_match.group())
                    except json.JSONDecodeError:
                        print(f"Warning: Could not parse JSON from response")
                        return []
                else:
                    print(f"Warning: Could not parse JSON from response")
                    return []

        except Exception as e:
            print(f"Error analyzing chunk: {e}")
            return []

    def ask_for_clarification(self, conflicts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Prompt user for clarification on unclear conflicts."""
        clarified = []

        unclear_conflicts = [c for c in conflicts if c.get('needs_clarification') or c.get('conflict_type') == 'unclear']

        if unclear_conflicts:
            print("\n" + "="*60)
            print("CLARIFICATION NEEDED")
            print("="*60)
            print("\nThe following conflicts need human review to determine if the code or comment is correct:\n")

            for i, conflict in enumerate(unclear_conflicts, 1):
                print(f"\n[{i}] File: {', '.join(conflict.get('files', []))}")
                print(f"    Description: {conflict.get('description')}")
                print(f"    Details: {conflict.get('details', 'N/A')[:200]}...")

                response = input("\n    Which is correct? (c)ode, (d)ocument/comment, (u)nclear, (s)kip: ").lower()

                if response == 'c':
                    conflict['conflict_type'] = 'comment_outdated'
                    conflict['clarification'] = 'Code is correct, comment needs update'
                elif response == 'd':
                    conflict['conflict_type'] = 'code_bug'
                    conflict['clarification'] = 'Comment/doc is correct, code needs fix'
                elif response == 'u':
                    conflict['conflict_type'] = 'unclear'
                    conflict['clarification'] = 'Requires further investigation'
                else:
                    conflict['clarification'] = 'Skipped by user'

                clarified.append(conflict)

        # Add the clear conflicts as well
        clear_conflicts = [c for c in conflicts if not c.get('needs_clarification') and c.get('conflict_type') != 'unclear']
        clarified.extend(clear_conflicts)

        return clarified

    def save_report(self, all_inconsistencies: List[Dict[str, Any]],
                   code_conflicts: List[Dict[str, Any]],
                   filename: str = "consistency_report2.md"):
        """Save the enhanced analysis report."""
        report_path = Path(__file__).parent / filename

        with open(report_path, 'w') as f:
            f.write("# Enhanced Consistency Report (Code + Documentation)\n\n")
            f.write(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Analyzed: Source code (.py, .json) and Documentation (.md)\n\n")

            # Code vs Comment Conflicts Section
            if code_conflicts:
                f.write("## 🔧 Code vs Comment Conflicts\n\n")

                # Separate by type
                code_bugs = [c for c in code_conflicts if c.get('conflict_type') == 'code_bug']
                outdated_comments = [c for c in code_conflicts if c.get('conflict_type') == 'comment_outdated']
                unclear = [c for c in code_conflicts if c.get('conflict_type') == 'unclear']

                if code_bugs:
                    f.write("### 🐛 Likely Code Bugs (Comment appears correct)\n\n")
                    for item in code_bugs:
                        self._write_code_conflict(f, item)

                if outdated_comments:
                    f.write("### 📝 Outdated Comments (Code appears correct)\n\n")
                    for item in outdated_comments:
                        self._write_code_conflict(f, item)

                if unclear:
                    f.write("### ❓ Unclear - Needs Investigation\n\n")
                    for item in unclear:
                        self._write_code_conflict(f, item)

            # General Inconsistencies Section
            if all_inconsistencies:
                f.write("\n## 📋 General Inconsistencies\n\n")

                # Group by severity
                high = [i for i in all_inconsistencies if i.get('severity') == 'high']
                medium = [i for i in all_inconsistencies if i.get('severity') == 'medium']
                low = [i for i in all_inconsistencies if i.get('severity') == 'low']

                if high:
                    f.write("### 🔴 High Severity\n\n")
                    for item in high:
                        self._write_issue(f, item)

                if medium:
                    f.write("### 🟡 Medium Severity\n\n")
                    for item in medium:
                        self._write_issue(f, item)

                if low:
                    f.write("### 🟢 Low Severity\n\n")
                    for item in low:
                        self._write_issue(f, item)

            if not code_conflicts and not all_inconsistencies:
                f.write("✅ No inconsistencies found!\n")
            else:
                total = len(code_conflicts) + len(all_inconsistencies)
                f.write(f"\n## Summary\n\n")
                f.write(f"- Total issues found: {total}\n")
                f.write(f"- Code/Comment conflicts: {len(code_conflicts)}\n")
                f.write(f"- Other inconsistencies: {len(all_inconsistencies)}\n")

        print(f"\nReport saved to: {report_path}")
        return report_path

    def _write_code_conflict(self, f, item: Dict[str, Any]):
        """Write a code vs comment conflict to the report."""
        f.write(f"#### File: `{item.get('file', 'Unknown')}`\n\n")

        if item.get('line'):
            f.write(f"**Line:** {item['line']}\n\n")

        if item.get('code_snippet'):
            f.write("**Code:**\n```python\n")
            f.write(f"{item['code_snippet']}\n")
            f.write("```\n\n")

        if item.get('comment'):
            f.write(f"**Comment/Docstring:** {item['comment']}\n\n")

        f.write(f"**Conflict:** {item.get('explanation', 'No explanation')}\n\n")

        if item.get('suggested_fix'):
            f.write(f"**Suggested Fix:** {item['suggested_fix']}\n\n")

        if item.get('clarification'):
            f.write(f"**User Clarification:** {item['clarification']}\n\n")

        f.write("---\n\n")

    def _write_issue(self, f, item: Dict[str, Any]):
        """Write a general issue to the report file."""
        f.write(f"#### {item.get('type', 'Inconsistency')}\n\n")
        f.write(f"**Description:** {item.get('description', 'No description')}\n\n")

        if 'files' in item:
            f.write("**Affected files:**\n")
            for file in item['files']:
                f.write(f"- `{file}`\n")
            f.write("\n")

        if 'details' in item:
            f.write("**Details:**\n")
            f.write(f"{item['details']}\n\n")

        if 'recommendation' in item:
            f.write("**Recommendation:**\n")
            f.write(f"{item['recommendation']}\n\n")

        f.write("---\n\n")

    def analyze_all(self) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Main analysis workflow."""
        # First, analyze source code
        print("\n" + "="*60)
        print("PHASE 1: Collecting and Analyzing Source Code")
        print("="*60)

        source_files = self.collect_source_files()
        print(f"\nCollected {len(source_files)} source files")

        # Analyze code/comment conflicts
        code_conflicts = self.analyze_code_comment_conflicts(source_files)

        if code_conflicts:
            # Ask for clarification on unclear conflicts
            code_conflicts = self.ask_for_clarification(code_conflicts)

        # Then, analyze documentation
        print("\n" + "="*60)
        print("PHASE 2: Collecting Documentation")
        print("="*60)

        documents = self.collect_documents()
        print(f"\nCollected {len(documents)} documentation files")

        # Combine and chunk all content
        print("\n" + "="*60)
        print("PHASE 3: Cross-Analysis of Code and Documentation")
        print("="*60)

        chunks = self.chunk_all_content(source_files, documents)
        print(f"\nCreated {len(chunks)} chunks for analysis")

        all_inconsistencies = []

        for i, chunk in enumerate(chunks, 1):
            inconsistencies = self.analyze_chunk(chunk, i, len(chunks))
            if inconsistencies:
                all_inconsistencies.extend(inconsistencies)

            # Rate limiting
            if i < len(chunks):
                time.sleep(1)

        return all_inconsistencies, code_conflicts


def main():
    """Main entry point."""
    print("Enhanced Consistency Checker v2.0")
    print("==================================\n")
    print("This version checks:")
    print("  - Python source files (.py)")
    print("  - JSON configuration files (.json)")
    print("  - Documentation files (.md)")
    print("  - Code vs Comment conflicts")
    print("\nAnalysis order: src → utils → tests → docs\n")

    # Check for API key
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("Error: ANTHROPIC_API_KEY environment variable not set")
        print("\nTo set it:")
        print("  export ANTHROPIC_API_KEY='your-api-key-here'")
        print("\nGet your API key from: https://console.anthropic.com/")
        sys.exit(1)

    try:
        analyzer = EnhancedConsistencyAnalyzer()

        # Run comprehensive analysis
        all_inconsistencies, code_conflicts = analyzer.analyze_all()

        # Save the report
        report_path = analyzer.save_report(all_inconsistencies, code_conflicts)

        print(f"\n{'='*60}")
        print(f"Analysis complete!")
        print(f"Found {len(code_conflicts)} code/comment conflicts")
        print(f"Found {len(all_inconsistencies)} other inconsistencies")
        print(f"Report saved to: {report_path}")

    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
