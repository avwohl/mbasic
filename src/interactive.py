"""
MBASIC 5.21 Interactive Command Mode

Implements the interactive REPL with:
- Line entry and editing
- Direct commands (RUN, LIST, SAVE, LOAD, NEW, etc.)
- Immediate mode execution
"""

import sys
import re
from pathlib import Path
from lexer import tokenize
from parser import Parser
from runtime import Runtime
from interpreter import Interpreter
import ast_nodes


class InteractiveMode:
    """MBASIC 5.21 interactive command mode"""

    def __init__(self):
        self.lines = {}  # line_number -> line_text
        self.current_file = None

    def start(self):
        """Start interactive mode"""
        print("MBASIC 5.21 Interpreter")
        print("Ready")
        print()

        while True:
            try:
                # Read input
                line = input()

                # Process line
                if not line.strip():
                    continue

                self.process_line(line)

            except EOFError:
                # Ctrl+D to exit
                print()
                break
            except KeyboardInterrupt:
                # Ctrl+C
                print()
                print("Break")
                continue
            except Exception as e:
                print(f"?{type(e).__name__}: {e}")

    def process_line(self, line):
        """Process a line of input (numbered line or direct command)"""
        line = line.strip()

        # Check if it's a numbered line
        match = re.match(r'^(\d+)\s*(.*)', line)
        if match:
            line_num = int(match.group(1))
            rest = match.group(2)

            if not rest:
                # Delete line
                if line_num in self.lines:
                    del self.lines[line_num]
            else:
                # Add/replace line
                self.lines[line_num] = line
        else:
            # Direct command
            self.execute_command(line)

    def execute_command(self, cmd):
        """Execute a direct command"""
        cmd_stripped = cmd.strip()

        # Parse command and arguments (preserve case for arguments)
        parts = cmd_stripped.split(None, 1)
        command = parts[0].upper() if parts else ""
        args = parts[1] if len(parts) > 1 else ""

        # Dispatch to command handler
        if command == "RUN":
            self.cmd_run()
        elif command == "LIST":
            self.cmd_list(args)
        elif command == "NEW":
            self.cmd_new()
        elif command == "SAVE":
            self.cmd_save(args)
        elif command == "LOAD":
            self.cmd_load(args)
        elif command == "AUTO":
            self.cmd_auto(args)
        elif command == "FILES":
            self.cmd_files(args)
        elif command == "SYSTEM" or command == "BYE":
            self.cmd_system()
        elif command == "DELETE":
            self.cmd_delete(args)
        elif command == "RENUM":
            self.cmd_renum(args)
        elif command == "":
            pass  # Empty command
        else:
            # Try to execute as immediate mode statement
            try:
                self.execute_immediate(cmd)
            except Exception as e:
                print(f"?Syntax error: {command}")

    def cmd_run(self):
        """RUN - Execute the program"""
        if not self.lines:
            print("?No program")
            return

        try:
            # Build program text
            program_text = self.get_program_text()

            # Parse
            tokens = list(tokenize(program_text))
            parser = Parser(tokens)
            ast = parser.parse()

            # Execute
            runtime = Runtime(ast)
            interpreter = Interpreter(runtime)
            interpreter.run()

        except Exception as e:
            print(f"?{type(e).__name__}: {e}")

    def cmd_list(self, args):
        """LIST [start][-][end] - List program lines"""
        if not self.lines:
            return

        # Parse range
        start = None
        end = None

        if args:
            # Handle various formats: LIST 100, LIST 100-200, LIST -200, LIST 100-
            if '-' in args:
                parts = args.split('-', 1)
                if parts[0]:
                    start = int(parts[0])
                if parts[1]:
                    end = int(parts[1])
            else:
                # Single line or start
                start = int(args)
                end = start

        # Get sorted line numbers
        line_numbers = sorted(self.lines.keys())

        # Filter by range
        for line_num in line_numbers:
            if start is not None and line_num < start:
                continue
            if end is not None and line_num > end:
                continue

            print(self.lines[line_num])

    def cmd_new(self):
        """NEW - Clear program"""
        self.lines.clear()
        self.current_file = None
        print("Ready")

    def cmd_save(self, filename):
        """SAVE "filename" - Save program to file"""
        if not filename:
            print("?Syntax error")
            return

        # Remove quotes if present
        filename = filename.strip().strip('"').strip("'")

        if not filename:
            print("?Syntax error")
            return

        try:
            # Add .bas extension if not present
            if not filename.endswith('.bas'):
                filename += '.bas'

            program_text = self.get_program_text()

            with open(filename, 'w') as f:
                f.write(program_text)

            self.current_file = filename
            print(f"Saved to {filename}")

        except Exception as e:
            print(f"?{type(e).__name__}: {e}")

    def cmd_load(self, filename):
        """LOAD "filename" - Load program from file"""
        if not filename:
            print("?Syntax error")
            return

        # Remove quotes if present
        filename = filename.strip().strip('"').strip("'")

        if not filename:
            print("?Syntax error")
            return

        try:
            # Add .bas extension if not present
            if not filename.endswith('.bas'):
                filename += '.bas'

            with open(filename, 'r') as f:
                program_text = f.read()

            # Clear current program
            self.lines.clear()

            # Parse and load lines
            for line in program_text.split('\n'):
                line = line.strip()
                if not line:
                    continue

                match = re.match(r'^(\d+)\s', line)
                if match:
                    line_num = int(match.group(1))
                    self.lines[line_num] = line

            self.current_file = filename
            print(f"Loaded from {filename}")
            print("Ready")

        except FileNotFoundError:
            print(f"?File not found: {filename}")
        except Exception as e:
            print(f"?{type(e).__name__}: {e}")

    def cmd_delete(self, args):
        """DELETE start-end - Delete range of lines"""
        if not args or '-' not in args:
            print("?Syntax error")
            return

        try:
            parts = args.split('-', 1)
            start = int(parts[0]) if parts[0] else min(self.lines.keys())
            end = int(parts[1]) if parts[1] else max(self.lines.keys())

            # Delete lines in range
            to_delete = [n for n in self.lines.keys() if start <= n <= end]
            for line_num in to_delete:
                del self.lines[line_num]

        except Exception as e:
            print(f"?Syntax error")

    def cmd_renum(self, args):
        """RENUM [new_start][,increment] - Renumber program lines and update references"""
        new_start = 10
        increment = 10

        if args:
            parts = args.split(',')
            if parts[0]:
                new_start = int(parts[0])
            if len(parts) > 1 and parts[1]:
                increment = int(parts[1])

        # Build mapping from old line numbers to new line numbers
        old_lines = sorted(self.lines.keys())
        line_map = {}

        new_num = new_start
        for old_num in old_lines:
            line_map[old_num] = new_num
            new_num += increment

        # Renumber lines and update line references
        new_lines = {}

        for old_num in old_lines:
            line_text = self.lines[old_num]
            match = re.match(r'^(\d+)(\s.*)', line_text)
            if not match:
                continue

            new_line_num = line_map[old_num]
            rest_of_line = match.group(2)

            # Update line number references in GOTO, GOSUB, THEN, ELSE, RESTORE, RUN
            # Patterns to match:
            # GOTO 100, GOSUB 100, THEN 100, ELSE 100, RESTORE 100, RUN 100
            # ON x GOTO 10,20,30  ON x GOSUB 10,20,30

            # Replace line numbers after these keywords
            updated_line = rest_of_line

            # Handle GOTO, GOSUB, THEN, ELSE, RESTORE, RUN followed by a line number
            for keyword in ['GOTO', 'GOSUB', 'THEN', 'ELSE', 'RESTORE', 'RUN', 'goto', 'gosub', 'then', 'else', 'restore', 'run']:
                # Pattern: keyword followed by optional spaces and a line number
                pattern = r'\b' + keyword + r'\s+(\d+)\b'

                def replace_linenum(match_obj):
                    old_linenum = int(match_obj.group(1))
                    if old_linenum in line_map:
                        new_linenum = line_map[old_linenum]
                        return keyword + ' ' + str(new_linenum)
                    return match_obj.group(0)

                updated_line = re.sub(pattern, replace_linenum, updated_line, flags=re.IGNORECASE)

            # Handle ON...GOTO and ON...GOSUB with comma-separated line numbers
            # Pattern: ON expr GOTO/GOSUB num,num,num
            def replace_on_statement(match_obj):
                prefix = match_obj.group(1)  # "ON expr GOTO " or "ON expr GOSUB "
                line_numbers = match_obj.group(2)  # "10,20,30"

                # Split and replace each line number
                nums = line_numbers.split(',')
                new_nums = []
                for num in nums:
                    num = num.strip()
                    if num.isdigit():
                        old_num = int(num)
                        if old_num in line_map:
                            new_nums.append(str(line_map[old_num]))
                        else:
                            new_nums.append(num)
                    else:
                        new_nums.append(num)

                return prefix + ','.join(new_nums)

            # Match ON ... GOTO/GOSUB with line number list
            updated_line = re.sub(
                r'\b(ON\s+\S+\s+(?:GOTO|GOSUB)\s+)([\d,\s]+)',
                replace_on_statement,
                updated_line,
                flags=re.IGNORECASE
            )

            # Create the new line
            new_line_text = str(new_line_num) + updated_line
            new_lines[new_line_num] = new_line_text

        self.lines = new_lines
        print("Renumbered")

    def cmd_auto(self, args):
        """AUTO [start][,increment] - Automatic line numbering mode

        AUTO - Start at 10, increment by 10
        AUTO 100 - Start at 100, increment by 10
        AUTO 100,5 - Start at 100, increment by 5
        AUTO ,5 - Start at 10, increment by 5
        """
        start = 10
        increment = 10

        if args:
            parts = args.split(',')
            # Handle "AUTO start" or "AUTO start,increment"
            if parts[0].strip():
                try:
                    start = int(parts[0].strip())
                except ValueError:
                    print("?Syntax error")
                    return
            # Handle "AUTO ,increment" or "AUTO start,increment"
            if len(parts) > 1 and parts[1].strip():
                try:
                    increment = int(parts[1].strip())
                except ValueError:
                    print("?Syntax error")
                    return

        # Enter AUTO mode
        current_line = start

        try:
            while True:
                # Check if line already exists
                if current_line in self.lines:
                    # Show asterisk for existing line
                    prompt = f"*{current_line} "
                else:
                    # Show line number for new line
                    prompt = f"{current_line} "

                # Read input
                try:
                    line_text = input(prompt)
                except EOFError:
                    # Ctrl+D exits AUTO mode
                    print()
                    break

                # Check if line is empty (just pressing Enter)
                if not line_text or not line_text.strip():
                    # Empty line exits AUTO mode
                    break

                # Add the line with its number
                full_line = str(current_line) + " " + line_text.strip()
                self.lines[current_line] = full_line

                # Move to next line number
                current_line += increment

        except KeyboardInterrupt:
            # Ctrl+C exits AUTO mode
            print()
            return

    def cmd_system(self):
        """SYSTEM - Exit to operating system"""
        print("Goodbye")
        sys.exit(0)

    def cmd_files(self, filespec):
        """FILES [filespec] - Display directory listing

        FILES - List all .bas files in current directory
        FILES "*.BAS" - List files matching pattern
        FILES "A:*.*" - List files on drive A (not supported, lists current dir)
        """
        import glob
        import os

        # Default pattern if no argument
        if not filespec:
            pattern = "*.bas"
        else:
            # Remove quotes if present
            pattern = filespec.strip().strip('"').strip("'")

            # If pattern is empty after stripping, use default
            if not pattern:
                pattern = "*.bas"

        # In MBASIC, FILES shows disk directory. We'll list matching files in current directory
        # Get matching files
        try:
            files = sorted(glob.glob(pattern))

            if not files:
                print(f"No files matching: {pattern}")
                return

            # Display files (MBASIC shows them in columns)
            # Simple format: one per line with size
            for filename in files:
                try:
                    size = os.path.getsize(filename)
                    # MBASIC shows file sizes in bytes or blocks
                    # We'll show bytes
                    print(f"{filename:<20} {size:>8} bytes")
                except OSError:
                    print(f"{filename:<20}        ? bytes")

            # Show count
            print(f"\n{len(files)} File(s)")

        except Exception as e:
            print(f"?{type(e).__name__}: {e}")

    def execute_immediate(self, statement):
        """Execute a statement in immediate mode (no line number)"""
        # For now, just try to execute PRINT statements
        # Build a minimal program with line 0
        program_text = "0 " + statement

        try:
            tokens = list(tokenize(program_text))
            parser = Parser(tokens)
            ast = parser.parse()

            runtime = Runtime(ast)
            interpreter = Interpreter(runtime)
            interpreter.run()
        except Exception as e:
            print(f"?{type(e).__name__}: {e}")

    def get_program_text(self):
        """Get program as text"""
        lines = []
        for line_num in sorted(self.lines.keys()):
            lines.append(self.lines[line_num])
        return '\n'.join(lines) + '\n'
