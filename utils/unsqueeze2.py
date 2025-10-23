#!/usr/bin/env python3
"""
Unsqueeze utility for CP/M squeezed files (.?Q? extension, typically .BQS for BASIC).

Implements the Huffman decoding algorithm used by the SQ/USQ utilities from CP/M.
Based on the original USQ.C implementation by Dick Greenlaw and others.

Format (from usq.c):
1. Magic number: 0xFF76 (16-bit)
2. Checksum: 16-bit
3. Original filename: null-terminated string
4. Number of nodes: 16-bit
5. Tree: array of nodes, each with left and right children (16-bit signed each)
6. Compressed data

Tree node values:
- Positive: index of child node in tree array
- Negative: -(value + 1) where value is 0-255 (character) or 256 (EOF marker)
"""

import sys
import struct
from pathlib import Path

# Squeeze file magic number
SQUEEZE_MAGIC = 0xFF76

# Special codes
SPEOF = 256  # Special code for EOF
NUMVALS = 257  # Number of values (0-255 + EOF)

def read_int16(f):
    """Read a 16-bit little-endian signed integer."""
    data = f.read(2)
    if len(data) < 2:
        return None
    val = struct.unpack('<H', data)[0]
    # Convert to signed
    if val >= 0x8000:
        val = val - 0x10000
    return val

def read_uint16(f):
    """Read a 16-bit little-endian unsigned integer."""
    data = f.read(2)
    if len(data) < 2:
        return None
    return struct.unpack('<H', data)[0]

def read_byte(f):
    """Read a single byte."""
    data = f.read(1)
    if len(data) < 1:
        return None
    return data[0]

def unsqueeze_file(input_path, output_path=None):
    """Unsqueeze a single file."""
    input_path = Path(input_path)

    with open(input_path, 'rb') as f:
        # Read and verify magic number
        magic = read_uint16(f)
        if magic != SQUEEZE_MAGIC:
            raise ValueError(f"Not a squeezed file: magic={hex(magic) if magic else 'None'}, expected={hex(SQUEEZE_MAGIC)}")

        # Read checksum (stored but not verified in this implementation)
        checksum = read_uint16(f)

        # Read original filename (null-terminated)
        original_name = b''
        while True:
            byte = read_byte(f)
            if byte is None or byte == 0:
                break
            original_name += bytes([byte])

        original_name = original_name.decode('ascii', errors='replace')
        print(f"  Original name: {original_name}")

        # Determine output path
        if output_path is None:
            # Use original filename from the squeezed file
            output_path = input_path.parent / original_name

        # Read number of nodes in tree
        numnodes = read_int16(f)
        if numnodes is None or numnodes < 0 or numnodes >= NUMVALS:
            raise ValueError(f"Invalid tree size: {numnodes}")

        print(f"  Tree nodes: {numnodes}")

        # Read Huffman tree
        # Tree is stored as array of nodes, each with left and right children
        tree = []
        for i in range(numnodes):
            left = read_int16(f)
            right = read_int16(f)
            if left is None or right is None:
                raise ValueError(f"Unexpected EOF reading tree at node {i}")
            tree.append((left, right))

        # If empty tree, set up SPEOF-only tree
        if not tree:
            tree = [(-(SPEOF + 1), -(SPEOF + 1))]

        # Decompress data
        print(f"  Decompressing data...")

        output_data = bytearray()
        bit_buffer = 0
        bits_in_buffer = 0

        while True:
            # Start at root (node 0)
            node_idx = 0

            while True:
                if node_idx >= len(tree):
                    raise ValueError(f"Invalid tree traversal: node {node_idx} out of range")

                # Read next bit
                if bits_in_buffer == 0:
                    byte = read_byte(f)
                    if byte is None:
                        # End of file
                        break
                    bit_buffer = byte
                    bits_in_buffer = 8

                # Get bit (LSB first)
                bit = bit_buffer & 1
                bit_buffer >>= 1
                bits_in_buffer -= 1

                # Get child based on bit
                child = tree[node_idx][bit]  # 0 = left, 1 = right

                if child < 0:
                    # Leaf node - extract value
                    value = -(child + 1)

                    if value == SPEOF:
                        # End of compressed data
                        break

                    if value < 0 or value > 255:
                        raise ValueError(f"Invalid character value: {value}")

                    output_data.append(value)
                    break  # Back to root
                else:
                    # Internal node - continue traversing
                    node_idx = child

            # Check if we hit SPEOF
            if node_idx >= len(tree) or (node_idx < len(tree) and
                                         tree[node_idx][0] < 0 and
                                         -(tree[node_idx][0] + 1) == SPEOF):
                break
            if bits_in_buffer == 0 and read_byte(f) is None:
                break

        # Decode DLE (Data Link Escape) run-length encoding
        # DLE (0x90) followed by count means repeat previous character count times
        # DLE followed by DLE means literal DLE
        print(f"  Decoded {len(output_data)} Huffman bytes, applying DLE decoding...")

        DLE = 0x90
        decoded_data = bytearray()
        i = 0
        prev_char = 0

        while i < len(output_data):
            char = output_data[i]

            if char == DLE:
                if i + 1 < len(output_data):
                    next_char = output_data[i + 1]
                    if next_char == DLE:
                        # DLE DLE = literal DLE
                        decoded_data.append(DLE)
                        i += 2
                    else:
                        # DLE count = repeat previous character
                        count = next_char
                        for _ in range(count):
                            decoded_data.append(prev_char)
                        i += 2
                else:
                    # DLE at end of file - just add it
                    decoded_data.append(char)
                    i += 1
            else:
                decoded_data.append(char)
                prev_char = char
                i += 1

        # Write output
        with open(output_path, 'wb') as out:
            out.write(decoded_data)

        print(f"  Final output: {len(decoded_data)} bytes")
        return output_path

def main():
    if len(sys.argv) < 2:
        print("Usage: unsqueeze2.py <input.bqs> [output.bas]")
        print("Or: unsqueeze2.py <directory>  (process all .bqs files)")
        sys.exit(1)

    input_arg = Path(sys.argv[1])

    if input_arg.is_dir():
        # Process all .bqs files in directory
        bqs_files = list(input_arg.glob('*.bqs'))
        print(f"Found {len(bqs_files)} .bqs files to unsqueeze\n")

        success = 0
        failed = 0

        for bqs_file in sorted(bqs_files):
            print(f"Unsqueezing {bqs_file.name}...")
            try:
                output_path = unsqueeze_file(bqs_file)
                print(f"  ✓ Success: {output_path.name}\n")
                success += 1
            except Exception as e:
                print(f"  ✗ Failed: {e}\n")
                failed += 1

        print(f"\nSummary: {success} succeeded, {failed} failed")

    else:
        # Single file
        output_path = sys.argv[2] if len(sys.argv) > 2 else None
        try:
            result = unsqueeze_file(input_arg, output_path)
            print(f"Successfully unsqueezed to: {result}")
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

if __name__ == '__main__':
    main()
