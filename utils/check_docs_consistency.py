#!/usr/bin/env python3
"""
Documentation Consistency Checker

This script uses the Claude API to analyze all documentation files in the docs/
directory and identify inconsistencies between them.

Usage:
    python3 utils/check_docs_consistency.py

Requires:
    - ANTHROPIC_API_KEY environment variable
    - anthropic package (pip install anthropic)
"""

import os
import sys
import json
from pathlib import Path
from typing import List, Dict, Any
import hashlib
import time

try:
    import anthropic
except ImportError:
    print("Error: anthropic package not installed")
    print("Run: pip install anthropic")
    sys.exit(1)

class DocumentationAnalyzer:
    def __init__(self, api_key: str = None):
        """Initialize the analyzer with Claude API."""
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")

        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.docs_dir = Path(__file__).parent.parent / "docs"
        self.cache_file = Path(__file__).parent / ".docs_analysis_cache.json"

    def collect_documents(self) -> Dict[str, str]:
        """Collect all markdown files from docs directory."""
        documents = {}

        for md_file in self.docs_dir.rglob("*.md"):
            # Skip very large files or binary files
            if md_file.stat().st_size > 100000:  # Skip files > 100KB
                print(f"Skipping large file: {md_file}")
                continue

            try:
                rel_path = md_file.relative_to(self.docs_dir)
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    documents[str(rel_path)] = content
                    print(f"Collected: {rel_path}")
            except Exception as e:
                print(f"Error reading {md_file}: {e}")

        return documents

    def chunk_documents(self, documents: Dict[str, str], max_chunk_size: int = 50000) -> List[Dict[str, Any]]:
        """
        Chunk documents into manageable sizes for API calls.
        Groups related documents together when possible.
        """
        chunks = []
        current_chunk = {"files": {}, "size": 0}

        # Sort by directory to keep related docs together
        sorted_docs = sorted(documents.items(), key=lambda x: x[0])

        for filepath, content in sorted_docs:
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
                        # Save this part
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

    def analyze_chunk(self, chunk: Dict[str, Any], chunk_num: int, total_chunks: int) -> str:
        """Send a chunk to Claude for analysis."""
        print(f"\nAnalyzing chunk {chunk_num}/{total_chunks} ({len(chunk['files'])} files)...")

        # Prepare the document content
        doc_content = []
        for filepath, content in chunk['files'].items():
            doc_content.append(f"=== File: {filepath} ===\n{content}\n")

        prompt = f"""You are analyzing documentation files for inconsistencies.

Here are {len(chunk['files'])} documentation files to analyze:

{''.join(doc_content)}

Please identify any inconsistencies in these documents, including but not limited to:
1. Contradictory information (e.g., different license types mentioned)
2. Missing references (e.g., one doc lists all UIs but misses one mentioned elsewhere)
3. Outdated information that conflicts with newer documentation
4. Inconsistent terminology or naming
5. Version number mismatches
6. Command/path inconsistencies
7. Feature availability conflicts

Format your response as a JSON array of inconsistencies. Each item should have:
- "type": category of inconsistency
- "severity": "high", "medium", or "low"
- "files": list of affected files
- "description": clear description of the inconsistency
- "details": specific quotes or examples

If no inconsistencies are found, return an empty JSON array: []

Return ONLY the JSON array, no other text."""

        try:
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4000,
                temperature=0,
                messages=[{"role": "user", "content": prompt}]
            )

            # Extract JSON from response
            response_text = response.content[0].text.strip()

            # Try to parse as JSON
            try:
                result = json.loads(response_text)
                return result
            except json.JSONDecodeError:
                # If not valid JSON, try to extract JSON from the response
                import re
                json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
                else:
                    print(f"Warning: Could not parse JSON from response")
                    return []

        except Exception as e:
            print(f"Error analyzing chunk: {e}")
            return []

    def analyze_all_documents(self) -> List[Dict[str, Any]]:
        """Analyze all documentation for inconsistencies."""
        print("Collecting documentation files...")
        documents = self.collect_documents()

        if not documents:
            print("No documentation files found!")
            return []

        print(f"\nFound {len(documents)} documentation files")
        print(f"Total size: {sum(len(c) for c in documents.values())} characters")

        print("\nChunking documents for analysis...")
        chunks = self.chunk_documents(documents)
        print(f"Created {len(chunks)} chunks")

        all_inconsistencies = []

        for i, chunk in enumerate(chunks, 1):
            inconsistencies = self.analyze_chunk(chunk, i, len(chunks))
            if inconsistencies:
                all_inconsistencies.extend(inconsistencies)

            # Rate limiting
            if i < len(chunks):
                time.sleep(1)  # Be nice to the API

        return all_inconsistencies

    def cross_analyze_results(self, inconsistencies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Send all found inconsistencies to Claude for a final cross-analysis
        to identify patterns and group related issues.
        """
        if not inconsistencies:
            return []

        print("\nPerforming cross-analysis of all findings...")

        prompt = f"""Here are all the inconsistencies found in the documentation:

{json.dumps(inconsistencies, indent=2)}

Please:
1. Group related inconsistencies together
2. Remove any duplicates
3. Identify any patterns or systemic issues
4. Prioritize the most important issues

Return a JSON array with the consolidated and prioritized inconsistencies.
Each item should have:
- "type": category of inconsistency
- "severity": "high", "medium", or "low"
- "files": list of all affected files
- "description": clear description of the issue
- "details": consolidated details and examples
- "recommendation": suggested fix

Return ONLY the JSON array."""

        try:
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4000,
                temperature=0,
                messages=[{"role": "user", "content": prompt}]
            )

            response_text = response.content[0].text.strip()

            try:
                return json.loads(response_text)
            except json.JSONDecodeError:
                import re
                json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
                return inconsistencies  # Return original if parsing fails

        except Exception as e:
            print(f"Error in cross-analysis: {e}")
            return inconsistencies

    def save_report(self, inconsistencies: List[Dict[str, Any]], filename: str = "docs_inconsistencies_report.md"):
        """Save the analysis report to a markdown file."""
        report_path = Path(__file__).parent / filename

        with open(report_path, 'w') as f:
            f.write("# Documentation Inconsistencies Report\n\n")
            f.write(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            if not inconsistencies:
                f.write("✅ No inconsistencies found!\n")
            else:
                f.write(f"Found {len(inconsistencies)} inconsistencies:\n\n")

                # Group by severity
                high = [i for i in inconsistencies if i.get('severity') == 'high']
                medium = [i for i in inconsistencies if i.get('severity') == 'medium']
                low = [i for i in inconsistencies if i.get('severity') == 'low']

                if high:
                    f.write("## 🔴 High Severity\n\n")
                    for item in high:
                        self._write_issue(f, item)

                if medium:
                    f.write("## 🟡 Medium Severity\n\n")
                    for item in medium:
                        self._write_issue(f, item)

                if low:
                    f.write("## 🟢 Low Severity\n\n")
                    for item in low:
                        self._write_issue(f, item)

        print(f"\nReport saved to: {report_path}")
        return report_path

    def _write_issue(self, f, item: Dict[str, Any]):
        """Write a single issue to the report file."""
        f.write(f"### {item.get('type', 'Inconsistency')}\n\n")
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


def main():
    """Main entry point."""
    print("Documentation Consistency Checker")
    print("==================================\n")

    # Check for API key
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("Error: ANTHROPIC_API_KEY environment variable not set")
        print("\nTo set it:")
        print("  export ANTHROPIC_API_KEY='your-api-key-here'")
        print("\nGet your API key from: https://console.anthropic.com/")
        sys.exit(1)

    try:
        analyzer = DocumentationAnalyzer()

        # Analyze all documents
        inconsistencies = analyzer.analyze_all_documents()

        if inconsistencies:
            # Cross-analyze to consolidate findings
            final_results = analyzer.cross_analyze_results(inconsistencies)

            # Save report
            report_path = analyzer.save_report(final_results)

            print(f"\n{'='*50}")
            print(f"Analysis complete!")
            print(f"Found {len(final_results)} inconsistencies")
            print(f"Report saved to: {report_path}")
        else:
            print("\n✅ No inconsistencies found in the documentation!")

    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()