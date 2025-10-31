#!/bin/bash
exec 2>mbasic_stderr.log
python3 mbasic --backend curses test_end_stderr.bas
