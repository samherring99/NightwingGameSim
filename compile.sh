#!/bin/bash

# NightwingGameSim - GameBoy ROM Compilation Script
# Uses GBDK (GameBoy Development Kit) to compile C code to .gb ROM files

set -e  # Exit on error

# Determine project root (directory containing this script)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="${SCRIPT_DIR}"

# Configure paths
WKDIR="${PROJECT_ROOT}/wkdir"
OUT_DIR="${PROJECT_ROOT}/out"

# GBDK paths - check environment variable first, fall back to local installation
if [ -n "${GBDK_ROOT}" ]; then
    LCC="${GBDK_ROOT}/bin/lcc"
else
    LCC="${PROJECT_ROOT}/gbdk/bin/lcc"
fi

# Validate GBDK installation
if [ ! -f "${LCC}" ]; then
    echo "ERROR: GBDK compiler not found at: ${LCC}"
    echo "Please install GBDK 4.2.0 or set GBDK_ROOT environment variable"
    exit 1
fi

# Validate working directory
if [ ! -d "${WKDIR}" ]; then
    echo "ERROR: Working directory not found: ${WKDIR}"
    exit 1
fi

# Ensure output directory exists
mkdir -p "${OUT_DIR}"

# Change to working directory
cd "${WKDIR}"

# Compile C source to object file
echo "Compiling file.c..."
"${LCC}" -Wa-l -Wl-m -Wl-j -c -o main.o file.c > err.txt 2>&1

# Link object file to GameBoy ROM
echo "Linking to out.gb..."
"${LCC}" -Wa-l -Wl-m -Wl-j -o out.gb main.o

# Move output to project out directory
mv out.gb "${OUT_DIR}/out.gb"

echo "Compilation successful: ${OUT_DIR}/out.gb"

# Return to project root
cd "${PROJECT_ROOT}"