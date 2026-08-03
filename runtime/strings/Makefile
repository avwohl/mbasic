# Makefile for MBASIC 2025 String System
#
# Usage:
#   make            # Build the native (host) test executable
#   make test       # Build and run tests natively
#   make debug      # Build with debug enabled
#   make z80        # Cross-build for Z80/CP/M with uc80 + um80 + ul80
#   make z80-run    # Cross-build and run it under cpmemu
#   make z80-z88dk  # Same program via the alternate z88dk toolchain
#   make clean      # Clean build files
#
# The Z80 toolchain preference (uc80 + cpmemu preferred, z88dk + tnylpo
# supported alternates) is documented in ../../docs/dev/TOOLCHAIN_POLICY.md.

CC = gcc
CFLAGS = -Wall -Wextra -O2
DEBUG_FLAGS = -g -O0 -DDEBUG -DMB25_ENABLE_DEBUG=1
LDFLAGS =

# Source files
SOURCES = mb25_string.c
HEADERS = mb25_string.h
TEST_SOURCES = test_mb25_string.c

# Object files
OBJECTS = mb25_string.o
TEST_OBJECTS = test_mb25_string.o

# Executables
TEST_EXEC = test_mb25_string

# ---------------------------------------------------------------------------
# Z80/CP/M cross-build settings
# ---------------------------------------------------------------------------

# Must match the #define in test_mb25_string.c.  uc80 merges all translation
# units into one compilation, so a macro that differs between two .c files is an
# ODR-style conflict rather than two independent compilations - pass it with -D
# so every unit agrees.  Same reason for MB25_ENABLE_DEBUG: the test calls the
# debug entry points, so mb25_string.c has to be compiled with them enabled too.
Z80_NUM_STRINGS = 50
Z80_DEFINES = -DMB25_NUM_STRINGS=$(Z80_NUM_STRINGS) -DMB25_ENABLE_DEBUG=1

# uc80 build products.  The shim is a hand-written source file, not output.
UC80_MAC   = mb25_string_z80.mac
UC80_REL   = mb25_string_z80.rel
UC80_COM   = mb25_string_z80.com
SHIM_MAC   = mb25_uc80_shim.mac
SHIM_REL   = mb25_uc80_shim.rel

# z88dk build product (alternate toolchain), kept under its own name so both
# builds can sit side by side for size and behaviour comparison.
Z88DK_COM  = mb25_string_z88dk.com

# libc.lib and runtime.lib live in the uc80 package's lib/ directory.  There is
# no flag or environment variable for it, so derive it from the installed module
# path.  A source/editable checkout keeps the built .lib files one level above
# the package, hence the second candidate.
UCLIB = $(shell python3 -c "import uc80,os; d=os.path.dirname(uc80.__file__); c=[os.path.join(d,'lib'), os.path.join(os.path.dirname(os.path.dirname(d)),'lib')]; print(next((p for p in c if os.path.isfile(os.path.join(p,'libc.lib'))), c[0]))" 2>/dev/null)

# Default target
all: $(TEST_EXEC)

# Build the test executable
$(TEST_EXEC): $(TEST_OBJECTS) $(OBJECTS)
	$(CC) $(CFLAGS) -o $@ $^ $(LDFLAGS)

# Build object files
mb25_string.o: mb25_string.c mb25_string.h
	$(CC) $(CFLAGS) -DMB25_ENABLE_DEBUG=1 -c -o $@ mb25_string.c

test_mb25_string.o: test_mb25_string.c mb25_string.h
	$(CC) $(CFLAGS) -DMB25_ENABLE_DEBUG=1 -c -o $@ test_mb25_string.c

# Debug build
debug: CFLAGS += $(DEBUG_FLAGS)
debug: clean $(TEST_EXEC)

# Run tests
test: $(TEST_EXEC)
	@echo "Running MBASIC 2025 String System tests..."
	@./$(TEST_EXEC)

# ---------------------------------------------------------------------------
# Z80/CP/M cross build - preferred path: uc80 + um80 + ul80, run under cpmemu
# ---------------------------------------------------------------------------
#
# uc80 is a C-to-assembly translator only: it never invokes the assembler or the
# linker, so the build orchestrates three tools by hand.

z80: check-uc80 $(UC80_COM)
	@echo "Z80 binary created: $(UC80_COM) (uc80 + um80 + ul80)"
	@echo "Run it with: cpmemu $(UC80_COM)   (or: make z80-run)"

# Step 1: C -> .mac.  All translation units in ONE invocation.
# --printf flags accumulate rather than replace, and --printf float alone would
# drop the integer conversions the test suite prints.  --no-embed-runtime is
# required because we link runtime.lib below; without it the runtime is embedded
# as well and every runtime symbol is multiply defined.
$(UC80_MAC): $(TEST_SOURCES) $(SOURCES) $(HEADERS)
	@echo "Compiling for Z80/CP/M with uc80..."
	uc80 $(Z80_DEFINES) -I . $(TEST_SOURCES) $(SOURCES) \
		--printf int --printf float --no-embed-runtime -o $@

# Step 2: .mac -> .rel
$(UC80_REL): $(UC80_MAC)
	um80 $< -o $@

# Step 3: the hand-written assembly shim, assembled SEPARATELY.
# Never pass a .mac to uc80 alongside the C sources: uc80 strips the CSEG
# directive and appends the file after its own BSS directive, so the code lands
# in BSS and is zeroed by crt0 before main() runs.  It links without complaint
# and then returns garbage at run time.
$(SHIM_REL): $(SHIM_MAC)
	um80 $< -o $@

# Step 4: link.  The shim supplies the pool-sizing helpers that compiled BASIC
# programs call; assembling and linking it here keeps it verified.
$(UC80_COM): $(UC80_REL) $(SHIM_REL)
	@if [ ! -f "$(UCLIB)/libc.lib" ]; then \
		echo "Error: uc80 libraries not found (looked for $(UCLIB)/libc.lib)."; \
		echo "Locate them with:"; \
		echo "  python3 -c \"import uc80,os;print(os.path.join(os.path.dirname(uc80.__file__),'lib'))\""; \
		exit 1; \
	fi
	ul80 $(UC80_REL) $(SHIM_REL) "$(UCLIB)/libc.lib" "$(UCLIB)/runtime.lib" -o $@

# Build for Z80 and run it under the cpmemu CP/M emulator.  cpmemu maps host
# files directly, so no disk image is needed and the .com can live here.
z80-run: z80
	@if command -v cpmemu >/dev/null 2>&1; then \
		cpmemu $(UC80_COM); \
	else \
		echo "Error: cpmemu not installed. See https://github.com/avwohl/cpmemu"; \
		exit 1; \
	fi

check-uc80:
	@for tool in uc80 um80 ul80; do \
		command -v $$tool >/dev/null 2>&1 || { \
			echo "Error: $$tool not found. Install the uc80 toolchain:"; \
			echo "  pip install uc80 um80        # https://github.com/avwohl/uc80"; \
			exit 1; }; \
	done

# ---------------------------------------------------------------------------
# Z80/CP/M cross build - alternate path: z88dk (zcc)
# ---------------------------------------------------------------------------
#
# Kept because z88dk still does three things uc80 cannot: Microsoft Binary
# Format floats (--math-mbf32), true Intel 8080 output, and INP/OUT/WAIT port
# I/O.  Use it when you need one of those; otherwise 'make z80' is the default.
z80-z88dk:
	@echo "Building for Z80 target with z88dk (alternate toolchain)..."
	@if command -v zcc >/dev/null 2>&1; then \
		zcc +cpm -O2 -o $(basename $(Z88DK_COM)) mb25_string.c test_mb25_string.c; \
		echo "Z80 binary created: $(Z88DK_COM)"; \
	else \
		echo "Error: zcc not found. The default Z80 build is 'make z80' (uc80);"; \
		echo "install z88dk only if you need this alternate path."; \
		exit 1; \
	fi

# Performance benchmark
benchmark: $(TEST_EXEC)
	@echo "Running performance benchmark..."
	@time ./$(TEST_EXEC) | grep -A10 "Performance"

# Memory check with valgrind (if available)
memcheck: debug
	@if command -v valgrind >/dev/null 2>&1; then \
		echo "Running memory check with valgrind..."; \
		valgrind --leak-check=full --show-leak-kinds=all ./$(TEST_EXEC); \
	else \
		echo "Valgrind not installed. Skipping memory check."; \
	fi

# Generate documentation with Doxygen (if available)
docs:
	@if command -v doxygen >/dev/null 2>&1; then \
		echo "Generating documentation..."; \
		echo "PROJECT_NAME = \"MBASIC 2025 String System\"" > Doxyfile.tmp; \
		echo "INPUT = mb25_string.h mb25_string.c" >> Doxyfile.tmp; \
		echo "OUTPUT_DIRECTORY = docs" >> Doxyfile.tmp; \
		echo "GENERATE_HTML = YES" >> Doxyfile.tmp; \
		echo "GENERATE_LATEX = NO" >> Doxyfile.tmp; \
		doxygen Doxyfile.tmp; \
		rm Doxyfile.tmp; \
		echo "Documentation generated in docs/html/"; \
	else \
		echo "Doxygen not installed. Cannot generate documentation."; \
	fi

# Static analysis with cppcheck (if available)
analyze:
	@if command -v cppcheck >/dev/null 2>&1; then \
		echo "Running static analysis..."; \
		cppcheck --enable=all --suppress=missingIncludeSystem mb25_string.c test_mb25_string.c; \
	else \
		echo "cppcheck not installed. Skipping static analysis."; \
	fi

# Format code with clang-format (if available)
format:
	@if command -v clang-format >/dev/null 2>&1; then \
		echo "Formatting code..."; \
		clang-format -i mb25_string.c mb25_string.h test_mb25_string.c; \
		echo "Code formatted."; \
	else \
		echo "clang-format not installed. Cannot format code."; \
	fi

# Clean build artifacts
clean:
	rm -f $(OBJECTS) $(TEST_OBJECTS) $(TEST_EXEC)
	rm -f *.com *.bin *.hex *.sym  # Z80 output files
	# Named individually: a blanket 'rm -f *.mac' would delete the hand-written
	# shim source, which is not a build product.
	rm -f $(UC80_MAC) $(UC80_REL) $(SHIM_REL)
	rm -rf docs/html docs/latex  # Documentation
	rm -f core *.core  # Core dumps
	rm -f vgcore.*  # Valgrind core files

# Install (copies to parent directory)
install: $(OBJECTS)
	cp mb25_string.h mb25_string.c ../
	@echo "Installed to parent directory"

# Help target
help:
	@echo "MBASIC 2025 String System Makefile"
	@echo ""
	@echo "Targets:"
	@echo "  all        - Build test executable (default)"
	@echo "  test       - Build and run tests"
	@echo "  debug      - Build with debug symbols"
	@echo "  z80        - Build for Z80/CP/M with uc80 + um80 + ul80"
	@echo "  z80-run    - Build for Z80/CP/M and run it under cpmemu"
	@echo "  z80-z88dk  - Build for Z80/CP/M with z88dk (alternate toolchain)"
	@echo "  benchmark  - Run performance benchmarks"
	@echo "  memcheck   - Check for memory leaks (requires valgrind)"
	@echo "  analyze    - Run static analysis (requires cppcheck)"
	@echo "  format     - Format code (requires clang-format)"
	@echo "  docs       - Generate documentation (requires doxygen)"
	@echo "  clean      - Remove build artifacts"
	@echo "  install    - Copy files to parent directory"
	@echo "  help       - Show this help message"
	@echo ""
	@echo "Toolchain policy: ../../docs/dev/TOOLCHAIN_POLICY.md"

.PHONY: all test debug z80 z80-run z80-z88dk check-uc80 benchmark memcheck analyze format docs clean install help