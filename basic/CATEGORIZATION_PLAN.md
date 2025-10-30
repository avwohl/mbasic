# BASIC Programs Categorization Plan

## Proposed Categories

### 1. games/
Card games, arcade games, strategy games, etc.

### 2. utilities/
Calculators, converters, utilities, tools

### 3. demos/
Graphics demos, test programs, examples

### 4. education/
Math tests, educational programs

### 5. business/
Financial, budgeting, calendar, scheduling

### 6. telecommunications/
Modem, BBS, communication programs

### 7. electronics/
Circuit design, IC timers, electronic calculators

### 8. data_management/
Bibliography, database, file management

### 9. ham_radio/
QSO logs, ham radio utilities

### 10. incompatible/
Programs that require hardware/features not available (graphics, specific CP/M features, etc.)

## Categorization

### games/ (15 programs)
- bacarrat.bas - Baccarat card game
- blkjk.bas - Blackjack
- hangman.bas - Hangman word game
- roulette.bas - Roulette casino game
- spacewar.bas - Space combat
- startrek.bas - Star Trek game
- survival.bas - Survival game
- tankie.bas - Tank game
- lifscore.bas - Life score game
- star.bas - Star game
- simcvax.bas - Simulation game
- massa.bas - Game (needs inspection)
- feesten.bas - Game (needs inspection)
- kalfeest.bas - Game (needs inspection)
- ozdot.bas - Dot game

### utilities/ (20 programs)
- calendar.bas - Calendar
- calendr5.bas - Calendar utility
- bigcal2.bas - Big calendar
- convert.bas - Unit converter
- sort.bas - Sorting utility
- search.bas - Search utility
- ucase.bas - Uppercase converter
- charfreq.bas - Character frequency analyzer
- dow.bas - Day of week calculator
- uudecode.bas - UU decoder
- xextract.bas - Extract utility
- xfind.bas - Find utility
- xscan.bas - Scan utility
- cpkhex.bas - CP/K hex utility
- hex2data.bas - Hex to data converter
- fprime.bas - Prime finder
- million.bas - Number utility
- rotate.bas - Rotate utility
- un-prot.bas - Unprotect utility
- unprotct.bas - Unprotect utility

### demos/ (8 programs)
- test_curses_features.bas - Curses test
- test_curses_input.bas - Input test
- test_curses_simple.bas - Simple test
- test_immediate_input.bas - Immediate input test
- sample-c.bas - Sample C
- sample-s.bas - Sample S
- benchmk.bas - Benchmark
- interpreter-vs-compiler.bas - Interpreter comparison

### education/ (3 programs)
- mathtest.bas - Math test
- astrnmy2.bas - Astronomy
- windchil.bas - Wind chill calculator

### business/ (8 programs)
- budget.bas - Budget tracker
- finance.bas - Finance calculator
- interest.bas - Interest calculator
- mortgage.bas - Mortgage calculator
- diary.bas - Diary/journal
- cpm-pert.bas - PERT charts
- log10k.bas - Logarithm tables
- airmiles.bas - Air miles calculator

### telecommunications/ (6 programs)
- bmodem.bas - Modem program
- bmodem1.bas - Modem utility
- exitbbs1.bas - BBS exit utility
- xtel.bas - Telecom utility
- dialog11.bas - Dialog utility
- command.bas - Command utility

### electronics/ (14 programs)
- 555-ic.bas - 555 timer calculator
- 567-ic.bas - 567 IC calculator
- timer555.bas - 555 timer
- atten.bas - Attenuator calculator
- bearing.bas - Bearing calculator
- bc2.bas - Calculator
- rc5.bas - RC5 calculator
- lst8085.bas - 8085 assembly lister
- lstintel.bas - Intel assembly lister
- lsttdl.bas - TDL assembly lister
- tab8085.bas - 8085 table
- tabintel.bas - Intel table
- tabtdl.bas - TDL table
- tabzilog.bas - Zilog table

### data_management/ (13 programs)
- bibbld.bas - Bibliography builder
- biblio.bas - Bibliography
- bibsr2.bas - Bibliography search 2
- bibsrch.bas - Bibliography search
- cbasedit.bas - Database editor
- cmprbib.bas - Compare bibliography
- mfil.bas - File manager
- vocbld.bas - Vocabulary builder
- voclst.bas - Vocabulary list
- xlabels.bas - Labels utility
- sfamove.bas - File move
- sfaobdes.bas - File descriptor
- sfavoc.bas - File vocabulary

### ham_radio/ (9 programs)
- qso.bas - QSO logger
- qsoedit.bas - QSO editor
- qsofind.bas - QSO finder
- qsolist.bas - QSO lister
- rbsclock.bas - RBS clock
- rbspurge.bas - RBS purge
- rbsutl31.bas - RBS utility
- boka-ei.bas - Ham radio utility
- rsj.bas - Ham radio utility

### incompatible/ (18 programs)
Programs that require CP/M-specific features, graphics, or hardware not available:

- clock-cb.bas - Clock (hardware specific)
- digiklok.bas - Digital clock (hardware specific)
- e-sketch.bas - Etch-a-sketch (graphics)
- facelift.bas - Graphics program
- fills.bas - Graphics fills
- handplot.bas - Plotting (graphics)
- pokehi.bas - Poke commands (hardware specific)
- grabcom.bas - COM port (hardware)
- findctl.bas - Control chars (CP/M specific)
- fndtble.bas - CP/M specific
- buildsub.bas - CP/M submit files
- fprod.bas - CP/M specific
- fprod1.bas - CP/M specific
- xformer.bas - CP/M file transfer
- kpro2-sw.bas - Kaypro specific
- cpmprt51.bas - CP/M print
- ykw1.bas - Unknown/hardware
- ykw2.bas - Unknown/hardware

## Implementation Steps

1. Create category directories under `basic/`
2. Move files into appropriate categories
3. Update `docs/library/games.json` to be `docs/library/library.json`
4. Create category JSON files for each category
5. Update UI code to show category selection first
6. Update documentation
