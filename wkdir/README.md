# wkdir/

Working directory for GameBoy ROM compilation.

This directory is used as a temporary workspace during the compilation process:
- Generated C code is written to `file.c`
- GBDK compiler outputs intermediate files (`main.o`, `err.txt`)
- Files are automatically cleaned up after compilation

**Note**: This directory should remain empty between builds. Contents are transient.
