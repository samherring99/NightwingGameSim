#!/bin/bash
# Wrapper to run with system libraries instead of conda's

# Force system libstdc++ and other system libs
export LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu:/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH

# Activate venv
source venv/bin/activate

# Run the command
exec "$@"
