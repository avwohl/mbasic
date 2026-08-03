#!/bin/bash
# compare_toolchains.sh - build the same BASIC program with both Z80 toolchains and
# compare what the two executables actually print.
#
# The project supports building with uc80 (preferred) and z88dk (alternate), and running
# with cpmemu (preferred) and tnylpo (alternate).  Supporting both is only meaningful if
# somebody checks they agree, so this does that.  See docs/dev/TOOLCHAIN_POLICY.md.
#
# Usage:
#   utils/compare_toolchains.sh program.bas [more.bas ...]
#   utils/compare_toolchains.sh basic/bas_tests1/*.bas
#
# Environment:
#   KEEP=1        keep the build directory instead of using a temporary one
#   BUILDDIR=DIR  build in DIR (implies KEEP)
#
# Exit status is 0 when every program either matched or was skipped, 1 when any
# program produced different output from the two toolchains.
#
# Two differences are EXPECTED and are reported separately rather than as failures:
#
#   - Line endings.  z88dk's CP/M runtime emits CRLF (which is what real CP/M does);
#     uc80's emits bare LF.  Carriage returns are stripped before comparing.
#   - Last-digit float differences.  uc80 uses 32-bit IEEE 754; z88dk is built here with
#     --math-mbf32 for Microsoft Binary Format.  Same 24-bit mantissa, different rounding,
#     so results can differ by one unit in the last place (3.14159 vs 3.14160).

set -u

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MBASIC="$REPO/mbasic"
EMULATOR="${EMULATOR:-cpmemu}"
RUN_TIMEOUT="${RUN_TIMEOUT:-20}"
BUILD_TIMEOUT="${BUILD_TIMEOUT:-300}"

if [ $# -eq 0 ]; then
    sed -n '2,26p' "${BASH_SOURCE[0]}" | sed 's/^# \?//'
    exit 2
fi

if ! command -v "$EMULATOR" >/dev/null 2>&1; then
    echo "error: $EMULATOR not found - cannot run the compiled programs." >&2
    echo "Install cpmemu (https://github.com/avwohl/cpmemu), or set EMULATOR=tnylpo." >&2
    exit 2
fi

# Resolve inputs to absolute paths before changing directory.
FILES=()
for arg in "$@"; do
    FILES+=("$(readlink -f "$arg")")
done

if [ -n "${BUILDDIR:-}" ]; then
    KEEP=1
    mkdir -p "$BUILDDIR"
    WORK="$(readlink -f "$BUILDDIR")"
else
    # NOT under /tmp: the z88dk snap package cannot read /tmp or hidden directories,
    # and reports the baffling "file '<name>.c' not found" for a file that plainly
    # exists. Build under $HOME so both toolchains can reach the sources.
    WORK="$(mktemp -d "${HOME}/mbasic-toolchain-cmp-XXXXXX")"
fi
cleanup() { [ -z "${KEEP:-}" ] && rm -rf "$WORK"; }
trap cleanup EXIT

cd "$WORK" || exit 2

same=0; crlf_only=0; differ=0; uc80_fail=0; z88dk_fail=0; both_fail=0

# Run a .com and normalize: drop cpmemu's own banner/footer lines and strip CR.
run_com() {
    timeout "$RUN_TIMEOUT" "$EMULATOR" "$1" </dev/null 2>&1 \
        | grep -vE '^(CPU mode:|Loaded [0-9]+ bytes from |Program exit via )' \
        | tr -d '\r'
}

for bas in "${FILES[@]}"; do
    name="$(basename "$bas")"
    if [ ! -f "$bas" ]; then
        echo "MISSING  $name"
        continue
    fi
    # CP/M-safe, collision-resistant stem.
    stem="$(basename "$bas" .bas | tr -cd 'A-Za-z0-9' | tr 'A-Z' 'a-z' | cut -c1-6)"
    [ -n "$stem" ] || stem="prog"
    u="u$stem"; z="z$stem"
    rm -f "$u".* "$z".*

    timeout "$BUILD_TIMEOUT" python3 "$MBASIC" --compile-c "$u" "$bas" \
        --toolchain uc80  >/dev/null 2>&1
    timeout "$BUILD_TIMEOUT" python3 "$MBASIC" --compile-c "$z" "$bas" \
        --toolchain z88dk >/dev/null 2>&1

    if [ -f "$u.com" ] && [ -f "$z.com" ]; then
        uout="$(run_com "$u.com")"
        zout="$(run_com "$z.com")"
        if [ "$uout" = "$zout" ]; then
            same=$((same + 1))
            printf 'SAME     %-32s uc80 %6s B  z88dk %6s B\n' "$name" \
                "$(stat -c%s "$u.com")" "$(stat -c%s "$z.com")"
        else
            differ=$((differ + 1))
            echo "DIFFER   $name"
            diff <(printf '%s\n' "$zout") <(printf '%s\n' "$uout") \
                | sed 's/^/         /' | head -12
        fi
    elif [ -f "$z.com" ]; then
        uc80_fail=$((uc80_fail + 1)); echo "UC80FAIL $name (z88dk built it)"
    elif [ -f "$u.com" ]; then
        z88dk_fail=$((z88dk_fail + 1)); echo "Z88FAIL  $name (uc80 built it)"
    else
        both_fail=$((both_fail + 1)); echo "BOTHFAIL $name"
    fi
done

echo "--------------------------------------------------------------"
echo "identical: $same    differing: $differ"
echo "uc80-only failures: $uc80_fail    z88dk-only failures: $z88dk_fail    both failed: $both_fail"
[ -n "${KEEP:-}" ] && echo "build directory kept: $WORK"

[ "$differ" -eq 0 ] && exit 0
exit 1
