#!/usr/bin/env python3
"""
Test if GOSUB stack is a circular buffer that drops oldest entries
"""

def create_test(num_gosubs, filename):
    """
    Create a test that does num_gosubs nested GOSUBs.
    Each level prints a message before and after its GOSUB.
    If stack is circular with size 8, we should see strange behavior after 8 levels.
    """
    lines = []

    # Main program
    lines.append('10 PRINT "Starting test with";{};"nested GOSUBs"'.format(num_gosubs))
    lines.append('20 GOSUB 1000')
    lines.append('30 PRINT "Back to main - SUCCESS!"')
    lines.append('40 END')

    # Create nested GOSUB chain
    for i in range(num_gosubs):
        base = 1000 + i * 100
        lines.append(f'{base} PRINT "Enter level {i+1}"')
        if i < num_gosubs - 1:
            lines.append(f'{base+10} GOSUB {base+100}')
        lines.append(f'{base+20} PRINT "Return from level {i+1}"')
        lines.append(f'{base+30} RETURN')

    program = '\n'.join(lines) + '\n'

    # Write with CRLF line endings
    with open(filename, 'wb') as f:
        f.write(program.replace('\n', '\r\n').encode('ascii'))

if __name__ == '__main__':
    # Test various depths around 8
    for depth in [5, 8, 9, 10, 12, 15]:
        filename = f'tests/circ{depth}.bas'
        create_test(depth, filename)
        print(f"Created {filename} with {depth} nested GOSUBs")
