# Makefile for MBASIC 2025 String System
#
# Usage:
#   make -f Makefile.mb25_string         # Build everything
#   make -f Makefile.mb25_string test    # Build and run tests
#   make -f Makefile.mb25_string debug   # Build with debug enabled
#   make -f Makefile.mb25_string clean   # Clean build files

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

# Build for Z80 target (requires z88dk)
z80:
	@echo "Building for Z80 target..."
	@if command -v zcc >/dev/null 2>&1; then \
		zcc +cpm -O2 -o mb25_string_z80 mb25_string.c test_mb25_string.c; \
		echo "Z80 binary created: mb25_string_z80.com"; \
	else \
		echo "Error: z88dk not installed. Install z88dk to build for Z80."; \
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
	rm -f *.com *.bin *.hex  # Z80 output files
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
	@echo "  all       - Build test executable (default)"
	@echo "  test      - Build and run tests"
	@echo "  debug     - Build with debug symbols"
	@echo "  z80       - Build for Z80/CP/M target (requires z88dk)"
	@echo "  benchmark - Run performance benchmarks"
	@echo "  memcheck  - Check for memory leaks (requires valgrind)"
	@echo "  analyze   - Run static analysis (requires cppcheck)"
	@echo "  format    - Format code (requires clang-format)"
	@echo "  docs      - Generate documentation (requires doxygen)"
	@echo "  clean     - Remove build artifacts"
	@echo "  install   - Copy files to parent directory"
	@echo "  help      - Show this help message"

.PHONY: all test debug z80 benchmark memcheck analyze format docs clean install help