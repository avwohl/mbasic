#!/usr/bin/env python3
"""
Detokenize all BASIC files in bas_tok and save to bas_out
"""
import subprocess
import sys
from pathlib import Path


def detokenize_file(input_path, output_path):
    """Detokenize a single file"""
    try:
        result = subprocess.run(
            ['python3', 'utils/detokenizer.py', str(input_path)],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0:
            # Write output to file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(result.stdout)
            return True, None
        else:
            return False, result.stderr
    except Exception as e:
        return False, str(e)


def main():
    tok_dir = Path('bas_tok')
    out_dir = Path('bas_out')

    if not tok_dir.exists():
        print("Error: bas_tok/ directory not found")
        return 1

    # Ensure output directory exists
    out_dir.mkdir(exist_ok=True)

    # Find all tokenized files
    tok_files = sorted(list(tok_dir.glob('*.bas')) + list(tok_dir.glob('*.BAS')))

    print(f"Detokenizing {len(tok_files)} files from bas_tok/ to bas_out/\n")
    print("=" * 80)

    success_count = 0
    error_count = 0

    for tok_file in tok_files:
        output_file = out_dir / tok_file.name

        success, error = detokenize_file(tok_file, output_file)

        if success:
            print(f"✓ {tok_file.name:30} -> bas_out/{tok_file.name}")
            success_count += 1
        else:
            print(f"✗ {tok_file.name:30} ERROR")
            if error:
                print(f"  {error[:100]}")
            error_count += 1

    print("\n" + "=" * 80)
    print(f"Successfully detokenized: {success_count}")
    print(f"Errors: {error_count}")

    return 0 if error_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
