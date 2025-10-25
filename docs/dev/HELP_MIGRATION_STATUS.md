# Help System Migration Status

Status as of 2025-10-25

## Completed

### ✅ Chapter 3: Functions (40 functions)
- **Location**: `docs/help/common/language/functions/`
- **Files**: 40 individual function reference pages + index
- **Extraction**: Automated via `utils/extract_functions.py`
- **Quality**: Good - minor OCR errors in examples
- **Index**: Comprehensive alphabetical and categorical organization

**Functions extracted**:
- Mathematical (12): ABS, ATN, COS, EXP, FIX, INT, LOG, RND, SGN, SIN, SQR, TAN
- String (13): ASC, CHR$, HEX$, INSTR, LEFT$, LEN, MID$, RIGHT$, SPACE$, SPC, STR$, STRING$, VAL
- Type conversion (6): CDBL, CINT, CVD/CVI/CVS, MKD$/MKI$/MKS$
- File I/O (5): EOF, INPUT$, LOC, LPOS, POS
- System (4): FRE, INKEY$, INP, USR, VARPTR

### ✅ Chapter 2: Statements and Commands (63 statements)
- **Location**: `docs/help/common/language/statements/`
- **Files**: 63 individual statement/command reference pages + index
- **Extraction**: Automated via `utils/extract_statements.py`
- **Quality**: Good - some statements are very long (e.g., PRINT, PRINT USING)
- **Index**: Comprehensive alphabetical and categorical organization

**Statements extracted** (organized by category):
- Program Control (8): CHAIN, CLEAR, COMMON, CONT, END, NEW, STOP, RUN
- Flow Control (6): FOR-NEXT, GOSUB-RETURN, GOTO, IF-THEN-ELSE, ON-GOSUB/GOTO, WHILE-WEND
- Input/Output (5): INPUT, LINE INPUT, LPRINT, PRINT, WRITE
- File I/O (9): CLOSE, FIELD, GET, INPUT#, LINE INPUT#, OPEN, PRINT#, PUT, WRITE#
- File Management (7): CLOAD, CSAVE, KILL, LOAD, MERGE, NAME, SAVE
- Data (2): DATA, READ
- Arrays (3): DIM, ERASE, OPTION BASE
- Variables (3): LET, SWAP, DEFINT/SNG/DBL/STR
- Functions (1): DEF FN
- Error Handling (4): ERR/ERL, ERROR, ON ERROR GOTO, RESUME
- String (1): MID$
- Memory/Hardware (4): CALL, OUT, POKE, WAIT
- Program Editing - CLI only (6): AUTO, DELETE, EDIT, LIST, LLIST, RENUM
- System (5): NULL, RANDOMIZE, REM, TRON/TROFF, WIDTH

## Remaining Content to Migrate

### Chapter 1: General Information

This content should be organized into conceptual help pages rather than extracted programmatically.

**Recommended structure**:

1. **basics.md** - Overview
   - Section 1.2: Modes of Operation (Direct vs Program mode)
   - Section 1.3: Line Format and Line Numbers

2. **data-types.md** - Data Types and Variables
   - Section 1.5: Constants (numeric, string)
   - Section 1.5.1: Single and Double Precision
   - Section 1.6: Variables
   - Section 1.6.1: Variable Names and Declaration Characters
   - Section 1.6.2: Array Variables
   - Section 1.7: Type Conversion

3. **operators.md** - Operators and Expressions
   - Section 1.8: Operators
   - Section 1.8.1: Arithmetic Operators
   - Section 1.8.1.1: Integer Division and Modulus
   - Section 1.8.1.2: Overflow and Division by Zero
   - Section 1.8.2: Relational Operators
   - Section 1.8.3: Logical Operators

4. **character-set.md** - Character Set and Special Characters
   - Section 1.4: Character Set
   - Section 1.4.1: Control Characters

5. **error-handling.md** - Error Messages and Handling
   - Section 1.10: Error Messages (overview)
   - Link to Appendix F for full error code list

**Notes**:
- Section 1.1 (INITIALIZATION) is OS/UI-specific, not shared language reference
- Section 1.9 (INPUT EDITING) is CLI-specific, not applicable to curses UI

### Appendices

**Recommended structure** (in `docs/help/common/language/appendices/`):

1. **error-codes.md** - Appendix F: Error Codes and Messages
   - Complete list of error codes with descriptions
   - Can be extracted programmatically from PDF

2. **ascii-codes.md** - Appendix H: ASCII Character Codes
   - ASCII table
   - Can be extracted from PDF or created manually

3. **math-functions.md** - Appendix G: Mathematical Functions
   - Trig identities, formulas
   - Can be extracted from PDF

4. **disk-io.md** - Appendix B: Disk I/O Guide
   - File handling concepts
   - Random vs sequential files
   - Shared across all UIs

5. **assembly-language.md** - Appendix C: Assembly Language Interface
   - CALL and USR details
   - Advanced topic, low priority

**Low Priority / Skip**:
- Appendix A: New Features in Release 5.0 (historical reference only)
- Appendix D: CP/M specific (historical, not applicable)
- Appendix E: Converting Programs (migration guide, historical)

## Extraction Quality Notes

### What Works Well
- PDF extraction with `pdftotext -layout` preserves structure
- Automated parsing finds 95%+ of content correctly
- Section markers (Format:, Versions:, Purpose:, etc.) parse reliably
- Function and statement names extract correctly

### Known Issues
- Some OCR errors in special characters (e.g., `»` instead of `)`)
- Spacing and indentation in examples not always perfect
- Page markers occasionally leak into content
- Very long statements (PRINT, OPEN) have complex multi-section layouts

### Manual Cleanup Needed
- Fix OCR character errors in examples
- Remove stray page markers
- Improve formatting of complex multi-section statements
- Add cross-reference links between related topics

## Next Steps

1. **Create Chapter 1 conceptual help pages** (manual)
   - basics.md
   - data-types.md
   - operators.md
   - character-set.md
   - error-handling.md (overview, link to appendix)

2. **Extract and create appendices** (semi-automated)
   - error-codes.md (extract from Appendix F)
   - ascii-codes.md (extract from Appendix H or create table)
   - math-functions.md (extract from Appendix G)
   - disk-io.md (extract from Appendix B)
   - assembly-language.md (extract from Appendix C, low priority)

3. **Create top-level language index**
   - `docs/help/common/language/index.md`
   - Links to functions, statements, concepts, appendices

4. **Add cross-references**
   - Link related functions/statements in "See Also" sections
   - Link from concepts to relevant statements/functions
   - Link from error-handling to error-codes appendix

5. **Manual quality improvements** (ongoing)
   - Fix OCR errors in examples
   - Improve formatting of complex statements
   - Add practical examples where helpful
   - Test help navigation from curses UI

## Statistics

- **Total extracted**: 103 help files (40 functions + 63 statements)
- **Lines migrated**: ~7,000+ lines from PDF into structured markdown
- **Extraction scripts**: 2 (extract_functions.py, extract_statements.py)
- **Automation success rate**: ~95% (most content extracts correctly)
- **Remaining manual work**: ~5-10 conceptual pages + 3-5 appendices

## Integration with Help System

The extracted help files are already integrated with the curses UI help browser:

1. **Ctrl+A** opens help table of contents (`docs/help/ui/curses/index.md`)
2. Navigate to "Language Reference" link
3. Browse functions and statements with Tab/Enter
4. Use U to go back in navigation history

**Help browser features**:
- Markdown rendering with MarkdownRenderer
- Link navigation (Tab, Enter)
- Back button (U)
- Scroll with arrow keys
- Close with ESC/Q

## Summary

**Completed**: Functions and statements extraction (core language reference)
**Remaining**: Conceptual topics (Chapter 1) and appendices
**Quality**: Good enough for immediate use, can be improved iteratively
**Next focus**: Create conceptual help pages for data types, operators, error handling
