# Documentation Consistency Checker

This utility uses the Claude API to analyze all documentation files in the `docs/` directory and identify inconsistencies between them.

## What it finds

- **License inconsistencies**: Different license types mentioned (e.g., 0BSD vs MIT)
- **Missing references**: Lists that don't include all items (e.g., UI lists missing Web UI)
- **Outdated information**: Old info that conflicts with newer documentation
- **Terminology issues**: Inconsistent naming or terminology
- **Version mismatches**: Different version numbers in different docs
- **Path/command inconsistencies**: Different paths or commands for same thing

## Setup

1. **Install the anthropic package:**
   ```bash
   pip install anthropic
   ```

2. **Set your Claude API key:**
   ```bash
   export ANTHROPIC_API_KEY='your-api-key-here'
   ```

   Get your API key from: https://console.anthropic.com/

## Usage

Run from the project root:
```bash
python3 utils/check_docs_consistency.py
```

## Output

The script will:
1. Scan all `.md` files in the `docs/` directory
2. Chunk them into manageable sizes for API analysis
3. Send each chunk to Claude for inconsistency detection
4. Cross-analyze all findings to remove duplicates and identify patterns
5. Save a report to `utils/docs_inconsistencies_report.md`

## Report Format

The report groups inconsistencies by severity:
- 🔴 **High**: Critical inconsistencies that could confuse users
- 🟡 **Medium**: Notable issues that should be fixed
- 🟢 **Low**: Minor inconsistencies or style issues

Each issue includes:
- Type of inconsistency
- Affected files
- Description of the problem
- Specific details/examples
- Recommended fix

## How it works

1. **Document Collection**: Recursively finds all `.md` files in `docs/`
2. **Chunking**: Groups related documents together, respecting API token limits
3. **Analysis**: Each chunk is analyzed by Claude for inconsistencies
4. **Cross-Analysis**: All findings are consolidated to remove duplicates
5. **Reporting**: Creates a prioritized markdown report

## Rate Limiting

The script includes a 1-second delay between API calls to avoid rate limiting.

## Caching

Currently no caching is implemented. Each run performs a full analysis.