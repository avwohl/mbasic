#!/usr/bin/env python3
"""
MBASIC 5.21 Interpreter - implementation of the `mbasic` command.

Installed as a console script via [project.scripts] in pyproject.toml; the
extensionless ./mbasic file at the repo root is a launcher that calls main()
here so source checkouts keep working.

Usage:
    ./mbasic                                  # Interactive mode (curses if installed, else cli)
    ./mbasic program.bas                      # Execute program
    ./mbasic --ui curses                      # Curses text UI (urwid, full-screen terminal)
    ./mbasic --ui cli                         # CLI backend (line-based)
    ./mbasic --ui tk                          # Tkinter GUI (graphical)
    ./mbasic --ui web                         # Web UI (browser-based)
    ./mbasic --ui web --port 3000             # Web UI on custom port
    ./mbasic --debug                          # Enable debug output
"""

import sys
import os
import argparse
import importlib
import importlib.util
from pathlib import Path

# Allow flat imports (parser, lexer, runtime, ...) from this package directory,
# and make the project root importable so 'src.*' package imports resolve when
# running from a source checkout.
_SRC_DIR = Path(__file__).resolve().parent
for _p in (str(_SRC_DIR), str(_SRC_DIR.parent)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from parser import TypeInfo

# Single source of truth for the package version: pyproject.toml reads the same
# attribute (see [tool.setuptools.dynamic]), so `mbasic --version` and the
# version pip records can never disagree.
from src.version import VERSION


# Single source of truth for UI backend metadata. Used by --list-backends, by
# load_backend()'s error messages, and by default-backend selection, so the
# installation instructions we print cannot drift apart from each other.
#
# 'requires' names the third-party package a backend needs. MBASIC itself has no
# required dependencies (`pip install mbasic` installs none), so every backend
# except cli may legitimately be missing on a working installation.
BACKENDS = {
    'cli': {
        'name': 'CLI',
        'description': 'Line-based command interface',
        'module': 'src.ui.cli',
        'class': 'CLIBackend',
        'requires': None,  # Python standard library only - always available
        'install': [],
    },
    'curses': {
        'name': 'Curses',
        'description': 'Full-screen terminal UI',
        'module': 'src.ui.curses_ui',
        'class': 'CursesBackend',
        'requires': 'urwid',
        'install': ['pip install "mbasic[curses]"', 'pip install "urwid>=2.0.0"'],
        'needs_tty': True,  # urwid reads keys straight from the terminal
    },
    'tk': {
        'name': 'Tkinter',
        'description': 'Graphical UI',
        'module': 'src.ui.tk_ui',
        'class': 'TkBackend',
        'requires': 'tkinter',
        'install': [
            'sudo apt-get install python3-tk     (Debian/Ubuntu)',
            'sudo dnf install python3-tkinter    (RHEL/Fedora)',
            'reinstall Python from python.org    (macOS/Windows)',
        ],
    },
    'web': {
        'name': 'Web',
        'description': 'Web-based UI (NiceGUI)',
        'module': 'src.ui.web',
        'class': 'NiceGUIBackend',
        'requires': 'nicegui',
        'install': ['pip install "mbasic[web]"', 'pip install "nicegui>=3.2.0"'],
    },
    # Internal stub, not offered by --ui.
    'visual': {
        'name': 'Visual',
        'description': 'Stub backend (internal)',
        'module': 'src.ui.visual',
        'class': 'VisualBackend',
        'requires': None,
        'install': [],
        'hidden': True,
    },
}

# Backends the user may select with --ui.
UI_CHOICES = [name for name, info in BACKENDS.items() if not info.get('hidden')]

# Preference order when --ui is not given: the full-screen UI if its dependency
# is installed, otherwise the dependency-free CLI.
DEFAULT_BACKEND_PREFERENCE = ('curses', 'cli')


def program_name():
    """Command name for help text: 'mbasic' when installed, './mbasic' from a checkout."""
    return Path(sys.argv[0]).name or 'mbasic'


def backend_available(backend_name):
    """Return True if the package a backend depends on can be imported."""
    info = BACKENDS.get(backend_name)
    if info is None:
        return False
    required = info.get('requires')
    if not required:
        return True
    try:
        return importlib.util.find_spec(required) is not None
    except (ImportError, ValueError):
        # find_spec raises if a parent package is itself missing or broken.
        return False


def stdio_is_interactive():
    """True when both stdin and stdout are attached to a terminal."""
    try:
        return sys.stdin.isatty() and sys.stdout.isatty()
    except (AttributeError, ValueError):
        return False


def choose_default_backend(quiet=False):
    """Pick the best usable backend when the user did not pass --ui.

    Falling back instead of failing matters because `pip install mbasic` pulls in
    no dependencies at all, so the preferred curses UI is absent on a minimal
    install and plain `mbasic` would otherwise exit with an error. The same
    applies when output is piped, where a full-screen UI cannot run at all.

    Args:
        quiet: Suppress the explanatory note (for modes that never start a UI)

    Returns:
        Name of the backend to use
    """
    skipped = []  # (backend info, reason, install hint lines)

    for name in DEFAULT_BACKEND_PREFERENCE:
        info = BACKENDS[name]

        if not backend_available(name):
            skipped.append((info, f"'{info['requires']}' is not installed", info['install']))
            continue
        if info.get('needs_tty') and not stdio_is_interactive():
            skipped.append((info, "this is not an interactive terminal", []))
            continue

        if skipped and not quiet:
            first, reason, hint = skipped[0]
            print(
                f"Note: the {first['name']} UI was skipped because {reason} - "
                f"starting the {info['name']} UI instead.",
                file=sys.stderr,
            )
            if hint:
                print("      To install it:", file=sys.stderr)
                for line in hint:
                    print(f"        {line}", file=sys.stderr)
            print(f"      Use --ui {name} to select a UI explicitly.\n", file=sys.stderr)
        return name

    # Should be unreachable: the cli backend has no dependencies and no tty need.
    return 'cli'


def missing_backend_message(backend_name, error):
    """Build the error text shown when an explicitly requested backend won't load."""
    info = BACKENDS.get(backend_name, {})
    lines = [f"Failed to load backend '{backend_name}': {error}", ""]

    if info.get('requires'):
        lines.append(
            f"The {info['name']} UI needs the '{info['requires']}' package, "
            f"which is not installed."
        )
    if info.get('install'):
        lines.append("Install it with:")
        lines.extend(f"    {line}" for line in info['install'])

    alternatives = [
        name for name in UI_CHOICES
        if name != backend_name and backend_available(name)
    ]
    if alternatives:
        lines.append("")
        lines.append(
            "Already installed: " + ", ".join(f"--ui {name}" for name in alternatives)
        )
    lines.append(f"Run '{program_name()} --list-backends' to see all UIs.")
    return "\n".join(lines)


def list_backends():
    """Print each selectable backend and whether its dependencies are installed."""
    print("Available MBASIC backends:\n")
    for name in UI_CHOICES:
        info = BACKENDS[name]
        available = backend_available(name)
        status = "✓ Available" if available else "✗ Not installed"
        print(f"  {name:10} {info['name']:12} {info['description']:30} {status}")
        if not available:
            for line in info['install']:
                print(f"{' ' * 14}{line}")

    default = choose_default_backend(quiet=True)
    print(f"\nUsage: {program_name()} --ui <name>")
    print(f"Default when --ui is not given: {default}")


def create_default_def_type_map():
    """Create default DEF type map (all SINGLE precision)"""
    def_type_map = {}
    for letter in 'abcdefghijklmnopqrstuvwxyz':
        def_type_map[letter] = TypeInfo.SINGLE
    return def_type_map


def compile_to_javascript(input_file, output_file, generate_html=False, debug=False):
    """Compile BASIC program to JavaScript

    Args:
        input_file: Path to BASIC source file
        output_file: Path to output JavaScript file
        generate_html: Also generate HTML wrapper
        debug: Enable debug output
    """
    try:
        # Import via src.* to match the codegen backend, for the same reason as
        # compile_to_c: these modules are importable under two names (flat,
        # because src/ is on sys.path, and as src.*), and Python treats those as
        # separate modules with separate class objects. Mixing them made every
        # `VarType.X` comparison in the backend false.
        from src.lexer import Lexer
        from src.parser import Parser
        from src.semantic_analyzer import SemanticAnalyzer
        from src.codegen_js_backend import JavaScriptBackend

        # Read source file
        with open(input_file, 'r') as f:
            source = f.read()

        if debug:
            print(f"Compiling {input_file} to JavaScript...", file=sys.stderr)

        # Lex
        lexer = Lexer(source)
        tokens = lexer.tokenize()

        if debug:
            print(f"  Lexed {len(tokens)} tokens", file=sys.stderr)

        # Parse
        parser = Parser(tokens)
        ast = parser.parse()

        if debug:
            print(f"  Parsed {len(ast.lines)} lines", file=sys.stderr)

        # Semantic analysis
        analyzer = SemanticAnalyzer()
        success = analyzer.analyze(ast)

        if not success:
            print("Semantic analysis failed", file=sys.stderr)
            sys.exit(1)

        if debug:
            print(f"  Semantic analysis complete", file=sys.stderr)

        # Generate JavaScript
        config = {
            'source_file': os.path.basename(input_file)
        }
        backend = JavaScriptBackend(analyzer.symbols, config)
        js_code = backend.generate(ast)

        # Write JavaScript file
        with open(output_file, 'w') as f:
            f.write(js_code)

        # Make executable
        os.chmod(output_file, 0o755)

        print(f"Generated JavaScript: {output_file}")

        # Generate HTML wrapper if requested
        if generate_html:
            html_file = output_file.replace('.js', '.html')
            generate_html_wrapper(output_file, html_file, os.path.basename(input_file))
            print(f"Generated HTML wrapper: {html_file}")

    except FileNotFoundError:
        print(f"Error: File not found: {input_file}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        if debug:
            import traceback
            traceback.print_exc()
        else:
            print(f"Compilation error: {e}", file=sys.stderr)
        sys.exit(1)


def uc80_lib_dir():
    """Locate the directory holding uc80's libc.lib and runtime.lib.

    uc80 offers no flag or environment variable for this, and the .lib files are
    build artifacts that do not always sit beside the Python package: in a source
    checkout they land in the repo's top-level lib/, two levels above src/uc80/.
    Try the plausible spots and let MBASIC_UC80_LIB override.

    Returns the directory, or None if no libc.lib was found.
    """
    candidates = []
    env = os.environ.get('MBASIC_UC80_LIB')
    if env:
        candidates.append(env)
    try:
        import uc80
        pkg = os.path.dirname(uc80.__file__)
        candidates.append(os.path.join(pkg, 'lib'))
        # Source checkout: <repo>/src/uc80/ -> <repo>/lib/
        candidates.append(os.path.join(os.path.dirname(os.path.dirname(pkg)), 'lib'))
    except ImportError:
        pass
    for path in candidates:
        if os.path.isfile(os.path.join(path, 'libc.lib')):
            return path
    return None


def sanitize_cpm_filename(name):
    """Sanitize filename for CP/M 8.3 format.

    CP/M filenames must:
    - Be max 8 characters (before extension)
    - Use only A-Z, 0-9 (no underscores, hyphens, etc.)
    - Lowercase. cpmemu, the preferred emulator, maps host names itself and does
      not need this; tnylpo does. A portable name costs nothing, so do it for both.

    Args:
        name: Input filename (without extension)

    Returns:
        Sanitized filename suitable for cpmemu/tnylpo/CP/M
    """
    import re
    # Remove extension if present
    name = os.path.splitext(name)[0]
    # Replace underscores/hyphens with nothing
    name = re.sub(r'[_\-]', '', name)
    # Keep only alphanumeric
    name = re.sub(r'[^a-zA-Z0-9]', '', name)
    # Truncate to 8 characters
    name = name[:8]
    # Lowercase (tnylpo requires this)
    name = name.lower()
    # Default if empty
    if not name:
        name = 'program'
    return name


def _run_tool(cmd, what, c_file, debug, install_hint=None):
    """Run one build tool, failing loudly and non-zero if it did not work."""
    import subprocess
    if debug:
        print(f"  Running: {' '.join(cmd)}", file=sys.stderr)
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
    except FileNotFoundError:
        # Without this the outer handler blames the BASIC source file, reporting
        # "File not found: <program>.bas" for a file that exists.
        print(f"Error: {cmd[0]} not found - cannot build the generated C.",
              file=sys.stderr)
        print(f"The C source was written to {c_file}.", file=sys.stderr)
        if install_hint:
            print(install_hint, file=sys.stderr)
        sys.exit(1)
    if result.returncode != 0:
        # Exit non-zero: no .com was produced, so a script must not treat this
        # as success.
        print(f"{what} failed - no executable was created.", file=sys.stderr)
        print(f"The generated C source is at {c_file}.", file=sys.stderr)
        print(f"{cmd[0]} reported:", file=sys.stderr)
        print((result.stderr or result.stdout).rstrip() or "(no output)",
              file=sys.stderr)
        sys.exit(1)
    return result


def build_with_uc80(c_file, com_file, runtime_dir, runtime_c, string_count, debug):
    """Build a CP/M .com with the preferred toolchain: uc80 -> um80 -> ul80.

    uc80 is a C-to-assembly translator only; it never invokes an assembler or
    linker, so the three steps are orchestrated here.  The subtleties (all of them
    learned the hard way, see docs/dev/TOOLCHAIN_POLICY.md):

    - MB25_NUM_STRINGS goes on the command line, not in the generated C.  uc80
      compiles every translation unit together, so a #define that disagreed with
      the runtime's view of the header silently corrupted the descriptor array.
    - The assembly shim is assembled SEPARATELY.  Handing a .mac to uc80 links
      cleanly but places the code in BSS, where crt0 zeroes it before main runs.
    - --printf flags accumulate rather than replace; float alone loses %d.
    - --no-embed-runtime is required because we link runtime.lib explicitly.
    """
    lib = uc80_lib_dir()
    if lib is None:
        print("Error: uc80's libc.lib was not found - cannot link the generated C.",
              file=sys.stderr)
        print(f"The C source was written to {c_file}.", file=sys.stderr)
        print("Install the toolchain with: pip install uc80 um80", file=sys.stderr)
        print("If uc80 is installed, its libraries may not be built yet - run "
              "'python3 -m uc80.lib.build_libs', or point MBASIC_UC80_LIB at the "
              "directory holding libc.lib.", file=sys.stderr)
        print("Or build with the alternate toolchain: --toolchain z88dk",
              file=sys.stderr)
        sys.exit(1)

    base = com_file[:-4] if com_file.endswith('.com') else com_file
    mac_file, rel_file = base + '.mac', base + '.rel'
    shim_mac = os.path.join(runtime_dir, 'mb25_uc80_shim.mac')
    shim_rel = base + '_shim.rel'

    uc80_cmd = ['uc80', f'-I{runtime_dir}']
    if string_count > 0:
        uc80_cmd.append(f'-DMB25_NUM_STRINGS={string_count}')
    uc80_cmd += [c_file, runtime_c,
                 '--printf', 'int', '--printf', 'float',
                 '--scanf', 'int', '--scanf', 'float',
                 '--no-embed-runtime', '-o', mac_file]
    _run_tool(uc80_cmd, 'uc80 compilation', c_file, debug,
              'Install it with: pip install uc80 um80')

    _run_tool(['um80', mac_file, '-o', rel_file], 'um80 assembly', c_file, debug,
              'Install it with: pip install um80')

    link_inputs = [rel_file]
    if string_count > 0:
        if not os.path.exists(shim_mac):
            print(f"Error: {shim_mac} not found - it supplies the string-pool "
                  "helpers that uc80 cannot express in C.", file=sys.stderr)
            sys.exit(1)
        _run_tool(['um80', shim_mac, '-o', shim_rel], 'um80 assembly of the uc80 shim',
                  c_file, debug)
        link_inputs.append(shim_rel)

    _run_tool(['ul80'] + link_inputs +
              [os.path.join(lib, 'libc.lib'), os.path.join(lib, 'runtime.lib'),
               '-o', com_file],
              'ul80 link', c_file, debug, 'Install it with: pip install um80')


def build_with_z88dk(c_file, com_file, runtime_dir, runtime_c, cpu, debug):
    """Build a CP/M .com with the alternate toolchain, z88dk.

    Still the route for Microsoft Binary Format floats and for real 8080 output.

    --math-mbf32 selects Microsoft Binary Format floats, matching MBASIC.  Both
    targets need it: without it the z80 link fails on any program with a float
    variable ("undefined symbol: init_floatpack").  -o names the output exactly,
    so ask for the .com name we advertise - otherwise z88dk writes an
    extensionless file and the --run step silently finds nothing.

    z88dk's own errors can be baffling: it reports "file '<name>.c' not found"
    for a file that plainly exists when it cannot reach the directory (the snap
    package cannot read /tmp or hidden directories, for example).
    """
    zcc_cmd = ['z88dk.zcc', '+cpm']
    if cpu == '8080':
        zcc_cmd.append('-clib=8080')
    zcc_cmd += ['--math-mbf32', f'-I{runtime_dir}', c_file, runtime_c,
                '-o', com_file, '-create-app']
    _run_tool(zcc_cmd, 'z88dk compilation', c_file, debug,
              'Install z88dk (https://z88dk.org) to build a CP/M .com binary.')


def compile_to_c(input_file, output_file, cpu='z80', run=False, debug=False,
                 toolchain='uc80', emulator='cpmemu'):
    """Compile BASIC program to C, then to a CP/M .com executable.

    Args:
        input_file: Path to BASIC source file
        output_file: Path to output (without extension - generates .c and .com)
        cpu: Target CPU - 'z80' (default) or '8080'
        run: Run the compiled program under the emulator after compilation
        debug: Enable debug output
        toolchain: 'uc80' (preferred) or 'z88dk' (alternate).  See
            docs/dev/TOOLCHAIN_POLICY.md.  '8080' forces z88dk - uc80 is Z80-only.
        emulator: 'cpmemu' (preferred) or 'tnylpo' (alternate)
    """
    import subprocess

    try:
        # Import via src.* to match the codegen backend. These modules are
        # importable under two names (flat, because src/ is on sys.path, and as
        # src.*), and Python treats those as separate modules with separate
        # class objects. Mixing them made every `var_info.var_type == VarType.X`
        # comparison in the backend false, so no variable declarations were
        # emitted and string variables were treated as numeric.
        from src.lexer import Lexer
        from src.parser import Parser
        from src.semantic_analyzer import SemanticAnalyzer
        from src.codegen_backend import Z88dkCBackend

        # Read source file
        with open(input_file, 'r') as f:
            source = f.read()

        if debug:
            print(f"Compiling {input_file} to C ({cpu})...", file=sys.stderr)

        # Lex
        lexer = Lexer(source)
        tokens = lexer.tokenize()

        if debug:
            print(f"  Lexed {len(tokens)} tokens", file=sys.stderr)

        # Parse
        parser = Parser(tokens)
        ast = parser.parse()

        if debug:
            print(f"  Parsed {len(ast.lines)} lines", file=sys.stderr)

        # Semantic analysis
        analyzer = SemanticAnalyzer()
        success = analyzer.analyze(ast)

        if not success:
            print("Semantic analysis failed", file=sys.stderr)
            for err in analyzer.errors:
                print(f"  {err}", file=sys.stderr)
            sys.exit(1)

        if analyzer.warnings:
            for warn in analyzer.warnings:
                print(f"Warning: {warn}", file=sys.stderr)

        if debug:
            print(f"  Semantic analysis complete", file=sys.stderr)

        # uc80 emits Z80 only.  Rather than produce a binary that hangs the moment
        # it hits an 8080 core, fall back to z88dk and say so.
        if cpu == '8080' and toolchain == 'uc80':
            print("Note: --cpu 8080 requires the z88dk toolchain (uc80 is Z80-only) "
                  "- building with z88dk.", file=sys.stderr)
            toolchain = 'z88dk'

        # Generate C code
        config = {
            'source_file': os.path.basename(input_file),
            'cpu_target': cpu,
            'dialect': toolchain,
        }
        backend = Z88dkCBackend(analyzer.symbols, config)
        c_code = backend.generate(ast)

        # --compile-c takes a base name, but users reasonably pass "out.c" and
        # got "out.c.c". Treat a trailing .c as the base name they meant.
        if output_file.endswith('.c'):
            output_file = output_file[:-2]

        # Write C file
        c_file = output_file + '.c'
        with open(c_file, 'w') as f:
            f.write(c_code)

        # Flush so this line cannot appear AFTER a z88dk error: stdout is block
        # buffered when redirected while stderr is not, which reversed the two
        # and made it look as though the C file was never written.
        print(f"Generated C: {c_file}", flush=True)

        # Compile with z88dk
        com_file = output_file + '.com'

        # Find runtime library path (beside src/ in a checkout, inside the
        # package when pip-installed)
        from src.resource_locator import find_c_runtime_dir
        runtime_path = find_c_runtime_dir()
        if runtime_path is None:
            print("Error: C runtime library (runtime/strings/mb25_string.c) not found - "
                  "cannot link the compiled program.", file=sys.stderr)
            print("Reinstall mbasic, or run --compile-c from a source checkout.",
                  file=sys.stderr)
            sys.exit(1)
        runtime_dir = str(runtime_path)
        runtime_c = os.path.join(runtime_dir, 'mb25_string.c')

        if toolchain == 'uc80':
            build_with_uc80(c_file, com_file, runtime_dir, runtime_c,
                            backend.string_count, debug)
        else:
            build_with_z88dk(c_file, com_file, runtime_dir, runtime_c, cpu, debug)

        # Flush for the same reason as "Generated C" above: the emulator started
        # below writes straight to fd 1, so an unflushed buffer prints this line
        # after the program's own output.
        print(f"Generated COM: {com_file}", flush=True)

        # Run with tnylpo if requested
        if run and os.path.exists(com_file):
            # tnylpo requires lowercase CP/M 8.3 filenames - sanitize if needed.
            # cpmemu maps host names itself, but a portable name costs nothing.
            basename = os.path.basename(output_file)
            safe_name = sanitize_cpm_filename(basename)
            run_file = com_file

            # If filename isn't CP/M safe, copy to safe name in current dir
            if safe_name != basename.lower():
                import shutil
                run_file = f'{safe_name}.com'
                shutil.copy(com_file, run_file)
                if debug:
                    print(f"  Copied to CP/M-safe name: {run_file}", file=sys.stderr)

            # Flush before handing the terminal to the emulator, which writes
            # straight to fd 1 - otherwise this banner surfaces after the
            # program's own output.
            print(f"\nRunning {run_file}...")
            print("-" * 40, flush=True)
            emu_cmd = [emulator]
            if emulator == 'cpmemu' and cpu == '8080':
                emu_cmd.append('--8080')
            emu_cmd.append(run_file)
            try:
                subprocess.run(emu_cmd, check=True)
            except FileNotFoundError:
                if emulator == 'cpmemu':
                    print("cpmemu not found - install it to run CP/M programs")
                    print("See https://github.com/avwohl/cpmemu (.deb/.rpm on the "
                          "releases page), or use --emulator tnylpo")
                else:
                    print("tnylpo not found - install tnylpo to run CP/M programs")
                    print("See docs/dev/TNYLPO_SETUP.md for installation instructions")
            except subprocess.CalledProcessError as e:
                print(f"Execution failed: {e}", file=sys.stderr)

    except FileNotFoundError:
        print(f"Error: File not found: {input_file}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        if debug:
            import traceback
            traceback.print_exc()
        else:
            print(f"Compilation error: {e}", file=sys.stderr)
        sys.exit(1)


def generate_html_wrapper(js_file, html_file, source_name):
    """Generate HTML wrapper for JavaScript output

    Args:
        js_file: Path to JavaScript file
        html_file: Path to output HTML file
        source_name: Name of BASIC source file (for title)
    """
    js_basename = os.path.basename(js_file)

    html_content = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>MBASIC Program: {source_name}</title>
  <style>
    body {{
      font-family: 'Courier New', monospace;
      background: black;
      color: #00ff00;
      padding: 20px;
      margin: 0;
    }}
    #output {{
      white-space: pre;
      line-height: 1.4;
    }}
    .header {{
      color: #ffff00;
      margin-bottom: 10px;
      border-bottom: 1px solid #333;
      padding-bottom: 10px;
    }}
  </style>
</head>
<body>
  <div class="header">MBASIC Program: {source_name}</div>
  <div id="output"></div>
  <script src="{js_basename}"></script>
</body>
</html>
"""

    with open(html_file, 'w') as f:
        f.write(html_content)


def load_backend(backend_name, io_handler, program_manager):
    """Load a UI backend dynamically using importlib

    Args:
        backend_name: Name of backend ('cli', 'curses', 'tk', 'web')
        io_handler: IOHandler instance for I/O operations
        program_manager: ProgramManager instance for program storage

    Returns:
        UIBackend instance

    Raises:
        ImportError: If backend module cannot be loaded (with helpful installation instructions)
        AttributeError: If backend doesn't have required classes
    """
    info = BACKENDS.get(backend_name)
    if info is None:
        raise ValueError(f"Unknown backend: {backend_name}")

    try:
        backend_module = importlib.import_module(info['module'])
        backend_class = getattr(backend_module, info['class'])
        return backend_class(io_handler, program_manager)

    except ImportError as e:
        # A missing optional dependency is an expected condition, not a crash:
        # tell the user exactly what to install and what they can use instead.
        raise ImportError(missing_backend_message(backend_name, e))
    except AttributeError as e:
        raise AttributeError(
            f"Backend '{backend_name}' does not have class '{info['class']}': {e}"
        )


def run_file(program_path, backend, debug_enabled=False):
    """Execute a BASIC program from file

    Args:
        program_path: Path to BASIC program file
        backend: UIBackend instance to use
        debug_enabled: Enable debug output
    """
    try:
        # Load the program using ProgramManager
        success, errors = backend.program.load_from_file(program_path)

        # Report any errors
        if errors:
            for line_num, error_msg in errors:
                print(f"Parse error at line {line_num}: {error_msg}", file=sys.stderr)

        if not success:
            print(f"Failed to load program: {program_path}", file=sys.stderr)
            sys.exit(1)

        # Enter interactive mode with program loaded
        # (Don't call cmd_run() here - it needs the event loop which starts in backend.start())
        backend.start()

    except FileNotFoundError:
        print(f"Error: File not found: {program_path}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        # Print traceback only in DEBUG mode
        if debug_enabled or os.environ.get('DEBUG'):
            import traceback
            traceback.print_exc()
        else:
            print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    """Main entry point with argument parsing"""
    parser = argparse.ArgumentParser(
        description='MBASIC 5.21 Interpreter',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  ./mbasic                                  # Interactive mode (curses if installed, else cli)
  ./mbasic program.bas                      # Run program and enter interactive mode
  ./mbasic --ui curses                      # Curses text UI (urwid, full-screen terminal)
  ./mbasic --ui cli                         # CLI backend (line-based)
  ./mbasic --ui tk                          # Tkinter GUI (graphical)
  ./mbasic --ui web                         # Web UI (browser-based)
  ./mbasic --ui web --port 3000             # Web UI on custom port
  ./mbasic --debug                          # Enable debug output
        """
    )

    parser.add_argument(
        'program',
        nargs='?',
        help='BASIC program file to load and run'
    )

    # The version number is this package's, not the language's: MBASIC 5.21 is
    # the dialect being implemented and never changes. Both are named here
    # because the docs use "MBASIC 5.21" everywhere and a bare "1.0.1006" would
    # look like it contradicts them.
    parser.add_argument(
        '--version', '-V',
        action='version',
        version=f'mbasic {VERSION} (implements MBASIC 5.21)',
        help="Show this interpreter's version and exit"
    )

    parser.add_argument(
        '--ui',
        '--backend',  # Keep --backend as alias for backwards compatibility
        dest='backend',
        choices=UI_CHOICES,
        default=None,  # Resolved below by choose_default_backend()
        help='UI to use (default: curses if urwid is installed, otherwise cli)'
    )

    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug output'
    )

    parser.add_argument(
        '--list-backends',
        action='store_true',
        help='List available backends and exit'
    )

    parser.add_argument(
        '--dump-keymap',
        action='store_true',
        help='Print keyboard shortcuts for the selected UI and exit'
    )

    parser.add_argument(
        '--port',
        type=int,
        default=8080,
        help='Port for web backend (default: 8080)'
    )

    parser.add_argument(
        '--compile-js', '--js',
        metavar='OUTPUT',
        dest='compile_js',
        help='Compile BASIC program to JavaScript (specify output file)'
    )

    parser.add_argument(
        '--html',
        action='store_true',
        help='Generate HTML wrapper for JavaScript output (use with --js)'
    )

    parser.add_argument(
        '--compile-c', '--cpm',
        metavar='OUTPUT',
        dest='compile_c',
        help='Compile BASIC program to C/Z80 for CP/M (specify output name without extension)'
    )

    parser.add_argument(
        '--cpu',
        choices=['z80', '8080'],
        default='z80',
        help='Target CPU for C compilation (default: z80)'
    )

    parser.add_argument(
        '--toolchain',
        choices=['uc80', 'z88dk'],
        default='uc80',
        help='C toolchain for --compile-c (default: uc80). z88dk is the alternate, '
             'and is used automatically for --cpu 8080 since uc80 is Z80-only.'
    )

    parser.add_argument(
        '--emulator',
        choices=['cpmemu', 'tnylpo'],
        default='cpmemu',
        help='CP/M emulator used by --run (default: cpmemu)'
    )

    parser.add_argument(
        '--run',
        action='store_true',
        help='Run compiled program under the CP/M emulator after compilation '
             '(use with --compile-c; see --emulator)'
    )

    args = parser.parse_args()

    # Resolve the UI backend. An explicit --ui is honoured exactly and fails with
    # installation instructions if its dependency is missing; with no --ui we pick
    # a backend that is actually installed, because `pip install mbasic` installs
    # no dependencies and the preferred curses UI would otherwise be unusable.
    if args.backend is None:
        starts_a_ui = not (args.list_backends or args.dump_keymap
                           or args.compile_js or args.compile_c)
        if starts_a_ui:
            args.backend = choose_default_backend()
        else:
            # Modes that only print or compile must not vary with the
            # environment. --dump-keymap in particular generates checked-in
            # documentation, so it always describes the preferred UI whether or
            # not urwid is installed and whether or not output is redirected.
            args.backend = DEFAULT_BACKEND_PREFERENCE[0]

    # Handle --list-backends first (exit after showing)
    if args.list_backends:
        list_backends()
        sys.exit(0)

    # Handle --dump-keymap (exit after showing)
    if args.dump_keymap:
        from src.ui.keybinding_loader import dump_keymap
        dump_keymap(args.backend)
        sys.exit(0)

    # Handle --compile-js (compile and exit)
    if args.compile_js:
        if not args.program:
            print("Error: --compile-js requires a BASIC program file", file=sys.stderr)
            sys.exit(1)

        compile_to_javascript(
            args.program,
            args.compile_js,
            generate_html=args.html,
            debug=args.debug
        )
        sys.exit(0)

    # Handle --compile-c (compile to C/Z80 and exit)
    if args.compile_c:
        if not args.program:
            print("Error: --compile-c requires a BASIC program file", file=sys.stderr)
            sys.exit(1)

        compile_to_c(
            args.program,
            args.compile_c,
            cpu=args.cpu,
            run=args.run,
            debug=args.debug,
            toolchain=args.toolchain,
            emulator=args.emulator
        )
        sys.exit(0)

    # An explicitly requested full-screen UI cannot run without a terminal. Say
    # so here rather than letting urwid fail deep inside its event loop.
    if BACKENDS.get(args.backend, {}).get('needs_tty') and not stdio_is_interactive():
        name = BACKENDS[args.backend]['name']
        print(f"Error: the {name} UI needs an interactive terminal, but stdin or "
              f"stdout is redirected.", file=sys.stderr)
        print(f"Use '{program_name()} --ui cli' for pipes, scripts and CI.",
              file=sys.stderr)
        sys.exit(1)

    # Create I/O handler based on backend choice
    if args.backend == 'cli':
        from iohandler.console import ConsoleIOHandler
        io_handler = ConsoleIOHandler(debug_enabled=args.debug)
    elif args.backend == 'curses':
        # Curses backend creates its own CursesIOHandler internally
        # Pass a dummy handler for initialization (will be replaced)
        from iohandler.console import ConsoleIOHandler
        io_handler = ConsoleIOHandler(debug_enabled=args.debug)
    elif args.backend == 'tk':
        # Tk backend uses console I/O for now (will implement TkIOHandler later)
        from iohandler.console import ConsoleIOHandler
        io_handler = ConsoleIOHandler(debug_enabled=args.debug)
    elif args.backend == 'visual':
        # Visual backend uses console I/O (stub)
        from iohandler.console import ConsoleIOHandler
        io_handler = ConsoleIOHandler(debug_enabled=args.debug)
        print("Note: Visual backend is a stub, using console I/O")
    else:
        # Fallback to console I/O
        from iohandler.console import ConsoleIOHandler
        io_handler = ConsoleIOHandler(debug_enabled=args.debug)

    # Create program manager
    from editing import ProgramManager
    program_manager = ProgramManager(create_default_def_type_map())

    # Web backend uses per-client architecture
    if args.backend == 'web':
        # Imported here rather than through load_backend(), so it needs the same
        # missing-dependency handling.
        try:
            from src.ui.web.nicegui_backend import start_web_ui
        except ImportError as e:
            print(f"Error loading backend: {missing_backend_message('web', e)}",
                  file=sys.stderr)
            sys.exit(1)
        try:
            start_web_ui(port=args.port)
        except KeyboardInterrupt:
            print("\n\nMBASIC Web UI: Exiting due to Ctrl+C\n")
            sys.exit(0)
        return

    # Load other backends dynamically
    try:
        backend = load_backend(args.backend, io_handler, program_manager)
    except (ImportError, AttributeError) as e:
        print(f"Error loading backend: {e}", file=sys.stderr)
        sys.exit(1)

    # Run program or enter interactive mode
    if args.program:
        run_file(args.program, backend, debug_enabled=args.debug)
    else:
        backend.start()


if __name__ == '__main__':
    main()
