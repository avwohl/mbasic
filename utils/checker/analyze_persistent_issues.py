#!/usr/bin/env python3
"""
Analyze Historical Consistency Reports to Find Persistent Issues

This script analyzes all historical consistency reports (v1-v22) to identify
which issues keep appearing across multiple versions, despite wording changes.

It uses similarity matching to group related issues and ranks them by:
- Persistence (how many versions they appear in)
- Recency (are they still present in latest reports)
- Severity (high/medium/low)

Usage:
    python3 utils/checker/analyze_persistent_issues.py
"""

import json
import re
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass, field
from difflib import SequenceMatcher
import hashlib

@dataclass
class Issue:
    """Represents a single issue from a report"""
    version: int
    description: str
    files: List[str]
    severity: str
    details: str = ""
    issue_type: str = ""
    keywords: Set[str] = field(default_factory=set)

    def __post_init__(self):
        """Extract keywords from description and files"""
        # Key terms to look for
        key_terms = [
            'ERL', 'RENUM', 'FileIO', 'INPUT', 'PRINT', 'FOR', 'STEP',
            'renumber', 'renum', 'error', 'line', 'comment', 'docstring',
            'parse', 'runtime', 'immediate', 'mode', 'statement',
            'sandbox', 'file_io', 'filesystem', 'abstraction', 'integration'
        ]

        text = (self.description + " " + self.details + " " + " ".join(self.files)).lower()

        for term in key_terms:
            if term.lower() in text:
                self.keywords.add(term.upper())

        # Also extract file basenames as keywords
        for f in self.files:
            basename = Path(f).stem.replace('_', ' ').upper()
            if len(basename) > 2:  # Skip very short names
                self.keywords.add(basename)

@dataclass
class IssueCluster:
    """Groups similar issues across versions"""
    canonical_description: str
    all_descriptions: List[str]
    files_involved: Set[str]
    keywords: Set[str]
    versions_present: Set[int]
    severities: Counter
    example_details: str
    total_occurrences: int = 0

    def persistence_score(self, max_version: int = 22) -> float:
        """Calculate how persistent this issue is"""
        # Factors:
        # - Number of versions it appears in (weight: 0.5)
        # - Recency (appears in last 3 versions) (weight: 0.3)
        # - Severity (weight: 0.2)

        version_score = len(self.versions_present) / max(len(self.versions_present), 1)  # How many of the available versions

        recent_versions = {20, 21, 22}
        recency_score = len(self.versions_present & recent_versions) / 3

        severity_score = (
            self.severities.get('high', 0) * 1.0 +
            self.severities.get('medium', 0) * 0.5 +
            self.severities.get('low', 0) * 0.3
        ) / max(sum(self.severities.values()), 1)

        return (version_score * 0.5 + recency_score * 0.3 + severity_score * 0.2)

    def signature(self) -> str:
        """Generate a signature for this cluster"""
        # Use files and keywords to create a stable signature
        sig_parts = sorted(self.files_involved)[:3] + sorted(self.keywords)[:5]
        return " + ".join(sig_parts)

class PersistentIssueAnalyzer:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.history_dir = self.project_root / "docs" / "history"
        self.issues = []
        self.clusters = []

    def load_all_reports(self) -> List[Issue]:
        """Load all historical consistency reports"""
        issues = []

        # Find all report files - check both history dir and /tmp for extracted ones
        report_pattern = re.compile(r'docs_inconsistencies_report-v(\d+)\.md')

        # Check history dir
        for report_file in self.history_dir.glob('docs_inconsistencies_report-v*.md'):
            match = report_pattern.search(report_file.name)
            if not match:
                continue

            version = int(match.group(1))
            print(f"Loading report v{version} from history...")

            # Parse the markdown report
            with open(report_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract issues from the report
            issues.extend(self.parse_report(content, version))

        # Also check /tmp for extracted historical reports
        tmp_dir = Path('/tmp')
        for report_file in tmp_dir.glob('report_v*.md'):
            match = re.search(r'report_v(\d+)\.md', report_file.name)
            if not match:
                continue

            version = int(match.group(1))
            # Skip if already loaded from history
            if any(i.version == version for i in issues):
                continue

            print(f"Loading report v{version} from /tmp...")

            # Parse the markdown report
            with open(report_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract issues from the report
            issues.extend(self.parse_report(content, version))

        return issues

    def parse_report(self, content: str, version: int) -> List[Issue]:
        """Parse issues from a single report"""
        issues = []

        # Split into sections
        sections = re.split(r'^#{2,4}\s+', content, flags=re.MULTILINE)

        current_severity = 'medium'

        for section in sections:
            lines = section.strip().split('\n')
            if not lines:
                continue

            header = lines[0].strip()

            # Detect severity sections
            if 'High Severity' in header or '🔴' in header:
                current_severity = 'high'
            elif 'Medium Severity' in header or '🟡' in header:
                current_severity = 'medium'
            elif 'Low Severity' in header or '🟢' in header:
                current_severity = 'low'

            # Parse individual issues
            issue_blocks = re.split(r'^---+$', '\n'.join(lines[1:]), flags=re.MULTILINE)

            for block in issue_blocks:
                if not block.strip():
                    continue

                issue = self.parse_issue_block(block, version, current_severity)
                if issue:
                    issues.append(issue)

        return issues

    def parse_issue_block(self, block: str, version: int, severity: str) -> Issue:
        """Parse a single issue from a block of text"""
        lines = block.strip().split('\n')

        description = ""
        files = []
        details = ""
        issue_type = ""

        in_details = False

        for line in lines:
            line = line.strip()

            # Extract description
            if line.startswith('**Description:**'):
                description = line.replace('**Description:**', '').strip()
            elif line.startswith('Description:'):
                description = line.replace('Description:', '').strip()

            # Extract affected files
            elif line.startswith('**Affected files:**') or line.startswith('Affected files:'):
                in_files = True
                continue
            elif line.startswith('- `') and '`' in line:
                # Extract filename from bullet point
                match = re.search(r'`([^`]+)`', line)
                if match:
                    files.append(match.group(1))

            # Extract details
            elif line.startswith('**Details:**') or line.startswith('Details:'):
                in_details = True
                continue
            elif in_details:
                details += line + " "

            # Extract issue type
            elif line.startswith('####'):
                issue_type = line.replace('#', '').strip()

        if description or files:
            return Issue(
                version=version,
                description=description,
                files=files,
                severity=severity,
                details=details[:500],  # Truncate long details
                issue_type=issue_type
            )

        return None

    def similarity_score(self, issue1: Issue, issue2: Issue) -> float:
        """Calculate similarity between two issues"""
        # Factors to consider:
        # 1. File overlap (weight: 0.4)
        # 2. Keyword overlap (weight: 0.3)
        # 3. Description similarity (weight: 0.3)

        # File overlap
        if issue1.files and issue2.files:
            files1 = set(issue1.files)
            files2 = set(issue2.files)
            file_overlap = len(files1 & files2) / len(files1 | files2) if files1 | files2 else 0
        else:
            file_overlap = 0

        # Keyword overlap
        if issue1.keywords and issue2.keywords:
            keyword_overlap = len(issue1.keywords & issue2.keywords) / len(issue1.keywords | issue2.keywords)
        else:
            keyword_overlap = 0

        # Description similarity (using SequenceMatcher)
        desc_similarity = SequenceMatcher(None, issue1.description, issue2.description).ratio()

        return (file_overlap * 0.4 + keyword_overlap * 0.3 + desc_similarity * 0.3)

    def cluster_issues(self, issues: List[Issue]) -> List[IssueCluster]:
        """Group similar issues into clusters"""
        clusters = []
        clustered_indices = set()

        for i, issue1 in enumerate(issues):
            if i in clustered_indices:
                continue

            # Start a new cluster
            cluster_issues = [issue1]
            clustered_indices.add(i)

            # Find similar issues
            for j, issue2 in enumerate(issues[i+1:], i+1):
                if j in clustered_indices:
                    continue

                if self.similarity_score(issue1, issue2) > 0.5:  # Threshold for similarity
                    cluster_issues.append(issue2)
                    clustered_indices.add(j)

            # Create cluster
            if len(cluster_issues) >= 2:  # Only keep clusters with multiple occurrences
                cluster = IssueCluster(
                    canonical_description=self.get_canonical_description(cluster_issues),
                    all_descriptions=[iss.description for iss in cluster_issues],
                    files_involved=set(f for iss in cluster_issues for f in iss.files),
                    keywords=set(k for iss in cluster_issues for k in iss.keywords),
                    versions_present=set(iss.version for iss in cluster_issues),
                    severities=Counter(iss.severity for iss in cluster_issues),
                    example_details=cluster_issues[0].details,
                    total_occurrences=len(cluster_issues)
                )
                clusters.append(cluster)

        return clusters

    def get_canonical_description(self, issues: List[Issue]) -> str:
        """Get the most representative description from a cluster"""
        # Use the most recent description as canonical
        sorted_issues = sorted(issues, key=lambda x: x.version, reverse=True)
        return sorted_issues[0].description

    def generate_report(self):
        """Generate analysis report"""
        print("\nLoading all historical reports...")
        self.issues = self.load_all_reports()
        versions_loaded = sorted(set(i.version for i in self.issues))
        print(f"Found {len(self.issues)} total issues across versions: {versions_loaded}")

        print("\nClustering similar issues...")
        self.clusters = self.cluster_issues(self.issues)
        print(f"Identified {len(self.clusters)} unique recurring issues")

        # Sort clusters by persistence score
        self.clusters.sort(key=lambda c: c.persistence_score(), reverse=True)

        # Generate report
        report_path = self.project_root / "docs" / "dev" / "PERSISTENT_ISSUES_ANALYSIS.md"

        with open(report_path, 'w') as f:
            f.write("# Persistent Issues Analysis\n\n")
            f.write(f"Analyzed {len(self.issues)} issues from consistency reports versions: {versions_loaded}\n")
            f.write(f"Identified {len(self.clusters)} unique recurring issues\n\n")

            f.write("## Top 10 Most Persistent Issues\n\n")
            f.write("These issues appear across multiple versions and should be prioritized for fixing:\n\n")

            for i, cluster in enumerate(self.clusters[:10], 1):
                score = cluster.persistence_score()
                f.write(f"### {i}. {cluster.canonical_description}\n\n")
                f.write(f"**Persistence Score:** {score:.2%}\n")
                f.write(f"**Appears in versions:** {sorted(cluster.versions_present)}\n")
                f.write(f"**Total occurrences:** {cluster.total_occurrences}\n")
                f.write(f"**Files involved:** {', '.join(sorted(cluster.files_involved)[:5])}\n")
                f.write(f"**Keywords:** {', '.join(sorted(cluster.keywords)[:8])}\n")
                f.write(f"**Severity distribution:** High={cluster.severities['high']}, "
                       f"Medium={cluster.severities['medium']}, Low={cluster.severities['low']}\n\n")

                if cluster.example_details:
                    f.write(f"**Example details:** {cluster.example_details[:200]}...\n\n")

                f.write("**Signature:** `" + cluster.signature() + "`\n\n")
                f.write("---\n\n")

            # Add summary statistics
            f.write("## Summary Statistics\n\n")

            # Issues still present in latest versions
            recent_clusters = [c for c in self.clusters if 22 in c.versions_present or 21 in c.versions_present]
            f.write(f"- Issues still active in v21/v22: {len(recent_clusters)}\n")

            # Most affected files
            all_files = Counter(f for c in self.clusters for f in c.files_involved)
            f.write("\n### Most Affected Files\n\n")
            for file, count in all_files.most_common(10):
                f.write(f"- `{file}`: appears in {count} issue clusters\n")

            # Most common keywords
            all_keywords = Counter(k for c in self.clusters for k in c.keywords)
            f.write("\n### Most Common Keywords\n\n")
            for keyword, count in all_keywords.most_common(15):
                f.write(f"- **{keyword}**: {count} clusters\n")

            f.write("\n## Recommended Priority Order\n\n")
            f.write("Based on persistence analysis, fix issues in this order:\n\n")

            for i, cluster in enumerate(self.clusters[:20], 1):
                f.write(f"{i}. **{cluster.signature()}** (Score: {cluster.persistence_score():.1%})\n")

        print(f"\nReport saved to: {report_path}")

        return report_path

def main():
    analyzer = PersistentIssueAnalyzer()
    analyzer.generate_report()

    # Also generate a JSON file for programmatic access
    json_data = {
        'clusters': [
            {
                'description': c.canonical_description,
                'signature': c.signature(),
                'score': c.persistence_score(),
                'versions': sorted(c.versions_present),
                'files': sorted(c.files_involved),
                'keywords': sorted(c.keywords)
            }
            for c in analyzer.clusters[:20]
        ]
    }

    json_path = analyzer.project_root / "docs" / "dev" / "persistent_issues.json"
    with open(json_path, 'w') as f:
        json.dump(json_data, f, indent=2)

    print(f"JSON data saved to: {json_path}")

if __name__ == "__main__":
    main()