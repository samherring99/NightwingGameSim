# 🎮 NightwingGameSim

**Generate working GameBoy ROM files from text prompts using LLMs**

NightwingGameSim is an AI-powered pipeline that transforms natural language descriptions into fully functional GameBoy games. Simply describe what you want, and the system generates C code, compiles it with GBDK, and outputs a playable `.gb` ROM file.

```bash
$ python generate.py "Create a simple pong game"
SUCCESS!
ROM file: out/create_a_simple_pong_game.gb
```

## Features

- **Single-command generation** - From prompt to playable game in one command
- **Multiple AI backends** - Claude API, local Llama, or RAG with documentation
- **Automatic retry logic** - Retries compilation failures with error feedback
- **Source archiving** - Optionally save generated C code for inspection
- **Smart error handling** - Parses and formats GBDK compiler errors
- **Configurable** - Flexible configuration via `.env` files

## 📋 Table of Contents

- [Requirements](#-requirements)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Usage](#-usage)
- [Configuration](#-configuration)
- [Architecture](#-architecture)
- [Examples](#-examples)
- [Troubleshooting](#-troubleshooting)
- [Development](#-development)
- [Contributing](#-contributing)

## 🔧 Requirements

### Essential
- **Python 3.10+**
- **GBDK 4.2.0** - GameBoy Development Kit for compiling C to .gb files
  - Download: [gbdk-2020 v4.2.0](https://github.com/gbdk-2020/gbdk-2020/releases/tag/4.2.0)
- **GameBoy Emulator** (for testing) - BGB, mGBA, SameBoy, etc.

### Backend-Specific
- **Claude backend**: Anthropic API key ([get one here](https://console.anthropic.com/))
- **Local backend**: Llama model file (GGUF format, ~4-8GB)
- **RAG backend**: Llama model + documentation in `data/` directory

## 📦 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/NightwingGameSim.git
cd NightwingGameSim
```

### 2. Install Python Dependencies

```bash
# Using pip
pip install -r requirements.txt

# Or using a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Install GBDK

Download and extract GBDK 4.2.0:

```bash
# Linux/Mac
cd /path/to/NightwingGameSim
wget https://github.com/gbdk-2020/gbdk-2020/releases/download/4.2.0/gbdk-linux64.tar.gz
tar -xzf gbdk-linux64.tar.gz
mv gbdk gbdk  # Should create ./gbdk directory

# Or set GBDK_ROOT environment variable to existing installation
export GBDK_ROOT=/path/to/your/gbdk
```

### 4. Configure Environment

Copy the example environment file and add your API keys:

```bash
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

### 5. Verify Installation

```bash
python generate.py --validate-only
```

You should see:
```
✓ Configuration valid!
```

## Quick Start

### Generate Your First Game

```bash
# Using Claude API (default)
python generate.py "Create a simple snake game"

# Using local Llama model
python generate.py "Make a pong game" --backend local

# Save the generated source code
python generate.py "Tic-tac-toe game" --save-source
```

### Play Your Game

Load the generated `.gb` file in any GameBoy emulator:

```bash
# Example with mgba
mgba out/your_game.gb

# Example with BGB (Windows)
bgb.exe out/your_game.gb
```

## 📖 Usage

### Basic Syntax

```bash
python generate.py [OPTIONS] "Your game description"
```

### Options

| Option | Description |
|--------|-------------|
| `--backend` | AI backend: `claude`, `local`, or `rag` (default: `claude`) |
| `--output`, `-o` | Custom output filename (default: auto-generated) |
| `--save-source` | Save generated C code to `src/` directory |
| `--max-retries` | Maximum compilation retry attempts (default: 3) |
| `--prompt-file` | Read prompt from file |
| `--verbose`, `-v` | Enable verbose output |
| `--validate-only` | Validate configuration without generating |

### Examples

```bash
# Basic generation
python generate.py "A breakout/brick breaker game"

# Custom output name
python generate.py "Space invaders" --output space_invaders.gb

# Use local model with verbose output
python generate.py "Tetris clone" --backend local --verbose

# Read prompt from file
python generate.py --prompt-file examples/my_game_idea.txt

# Save source and retry up to 5 times
python generate.py "Maze game" --save-source --max-retries 5
```

## Configuration

### Environment Variables (.env)

Create a `.env` file in the project root:

```bash
# API Keys
ANTHROPIC_API_KEY=your_claude_api_key_here

# GBDK (optional if using ./gbdk)
GBDK_ROOT=/path/to/gbdk

# Claude Settings
CLAUDE_MODEL=claude-3-5-sonnet-20241022
CLAUDE_MAX_TOKENS=4096
CLAUDE_TEMPERATURE=0.0

# Local Model
LOCAL_MODEL_PATH=/path/to/model.gguf

# Generation Settings
MAX_RETRIES=3
VERBOSE=false
```

### Directory Structure

```
NightwingGameSim/
├── generate.py          # Main CLI interface
├── config.py            # Configuration management
├── compiler.py          # GBDK compilation wrapper
├── utils.py             # Utility functions
├── generate_claude.py   # Claude API backend
├── generate_local.py    # Local Llama backend
├── generate_rag.py      # RAG backend
├── compile.sh           # GBDK compilation script
├── system_prompt.txt    # Default GBDK system prompt
├── wkdir/               # Compilation workspace (temporary)
├── out/                 # Compiled .gb ROM files
├── src/                 # Generated C source archives
├── data/                # Documentation for RAG
├── tests/               # Test suite
├── examples/            # Example games
└── docs/                # Extended documentation
```

## Architecture

### Pipeline Flow

```
User Prompt
    ↓
[LLM Backend] (Claude/Local/RAG)
    ↓
Generated C Code
    ↓
[Extract Code] (utils.py)
    ↓
[GBDK Compiler] (compile.sh via compiler.py)
    ↓
GameBoy ROM (.gb)
```

### Components

- **`generate.py`** - Main CLI orchestrator
- **`config.py`** - Centralized configuration with .env support
- **`compiler.py`** - Python wrapper for GBDK with error parsing
- **`utils.py`** - Code extraction, file operations, error formatting
- **Backends**:
  - `generate_claude.py` - Anthropic Claude API
  - `generate_local.py` - llama-cpp-python (local inference)
  - `generate_rag.py` - LlamaIndex with documentation retrieval

### System Prompt

The `system_prompt.txt` file contains detailed GBDK constraints and capabilities:
- GameBoy hardware limitations (160x144px, monochrome)
- Available functions: `plot()`, `line()`, `box()`, `circle()`, `gprintf()`
- Input handling via `joypad()` buttons
- Required headers: `<gb/gb.h>`, `<gb/drawing.h>`, `<stdio.h>`

## Examples

### Example 1: Simple Visualization

```bash
python generate.py "A rotating cube in wireframe"
```

### Example 2: Interactive Game

```bash
python generate.py "A catch game where falling items drop and the player moves left/right to catch them"
```

### Example 3: Puzzle Game

```bash
python generate.py "Memory match game with 8 cards that flip over" --save-source
```

## Troubleshooting

### GBDK Not Found

```
ERROR: GBDK compiler not found at: /path/to/gbdk/bin/lcc
```

**Solution**: Install GBDK 4.2.0 or set `GBDK_ROOT` environment variable

### Compilation Errors

```
Compilation failed:
file.c:10:5: error: undeclared variable 'foo'
```

**Solution**:
- Check generated source in `src/` (use `--save-source`)
- Increase `--max-retries` to let the system retry
- Modify `system_prompt.txt` to add more constraints

### API Key Issues

```
ERROR: ANTHROPIC_API_KEY not set
```

**Solution**: Add your API key to `.env` file:
```bash
ANTHROPIC_API_KEY=sk-ant-...
```

### Model Not Found (Local Backend)

```
ERROR: Model file not found: /path/to/model.gguf
```

**Solution**: Download a Llama model and set `LOCAL_MODEL_PATH` in `.env`:
```bash
# Example: Download from HuggingFace
huggingface-cli download \
  TheBloke/Llama-2-7B-Chat-GGUF \
  llama-2-7b-chat.Q4_K_M.gguf \
  --local-dir ./models
```

## Development

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html

# Run specific test file
pytest tests/test_compiler.py -v
```

### Code Quality

```bash
# Format code
black *.py

# Lint code
ruff check *.py

# Type checking
mypy *.py
```

### Benchmarking

The `prompt_iter_loop.py` script tests different prompt strategies:

```bash
python prompt_iter_loop.py
```

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

See `CONTRIBUTING.md` for detailed guidelines.

## License

This project is licensed under the MIT License - see the `LICENSE` file for details.

## Acknowledgments

- **GBDK** - GameBoy Development Kit ([gbdk-2020](https://github.com/gbdk-2020/gbdk-2020))
- **Anthropic** - Claude API
- **llama.cpp** - Local LLM inference
- **LlamaIndex** - RAG framework

## Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/NightwingGameSim/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/NightwingGameSim/discussions)

---

**Made with ❤️ by nightwing**
