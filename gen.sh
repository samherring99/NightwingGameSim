#!/bin/bash
# Quick wrapper to generate GameBoy games with local model

source ~/miniconda3/etc/profile.d/conda.sh
conda activate nightwing-gamesim

python generate.py "$@" --backend local
