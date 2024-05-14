#!/bin/bash

cd /path/to/NightwingGameSim/wkdir

/path/to/NightwingGameSim/gbdk/bin/lcc -Wa-l -Wl-m -Wl-j -c -o main.o file.c > err.txt
/path/to/NightwingGameSim/gbdk/bin/lcc -Wa-l -Wl-m -Wl-j -o out.gb main.o

mv out.gb /path/to/NightwingGameSim/out.gb

cd /path/to/NightwingGameSim/