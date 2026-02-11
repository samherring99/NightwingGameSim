"""
Configuration management for NightwingGameSim.

Handles environment-aware path resolution, API keys, and model paths.
Supports .env files for sensitive configuration.
"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()


class Config:
    """Centralized configuration for NightwingGameSim."""

    # Project paths
    PROJECT_ROOT = Path(__file__).parent.resolve()
    WKDIR = PROJECT_ROOT / "wkdir"
    OUT_DIR = PROJECT_ROOT / "out"
    SRC_DIR = PROJECT_ROOT / "src"
    DATA_DIR = PROJECT_ROOT / "data"
    TESTS_DIR = PROJECT_ROOT / "tests"
    EXAMPLES_DIR = PROJECT_ROOT / "examples"
    DOCS_DIR = PROJECT_ROOT / "docs"

    # GBDK paths
    GBDK_ROOT = PROJECT_ROOT / "gbdk"
    GBDK_BIN = GBDK_ROOT / "bin"
    GBDK_LCC = GBDK_BIN / "lcc"

    # Allow override via environment variable
    if os.getenv("GBDK_ROOT"):
        GBDK_ROOT = Path(os.getenv("GBDK_ROOT"))
        GBDK_BIN = GBDK_ROOT / "bin"
        GBDK_LCC = GBDK_BIN / "lcc"

    # Compilation settings
    COMPILE_SCRIPT = PROJECT_ROOT / "compile.sh"
    WORK_FILE = WKDIR / "file.c"
    WORK_OBJ = WKDIR / "main.o"
    WORK_ERR = WKDIR / "err.txt"
    OUTPUT_GB = OUT_DIR / "out.gb"

    # API Keys
    ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
    HUGGINGFACE_TOKEN: Optional[str] = os.getenv("HUGGINGFACE_TOKEN")

    # Model configuration
    CLAUDE_MODEL: str = os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-20241022")
    CLAUDE_MAX_TOKENS: int = int(os.getenv("CLAUDE_MAX_TOKENS", "4096"))
    CLAUDE_TEMPERATURE: float = float(os.getenv("CLAUDE_TEMPERATURE", "0.0"))

    # Local model paths
    LOCAL_MODEL_PATH: Optional[str] = os.getenv("LOCAL_MODEL_PATH")
    LOCAL_MODEL_DEFAULT = Path.home() / ".cache" / "huggingface" / "models" / "Meta-Llama-3-8B-Instruct.gguf"

    if not LOCAL_MODEL_PATH and LOCAL_MODEL_DEFAULT.exists():
        LOCAL_MODEL_PATH = str(LOCAL_MODEL_DEFAULT)

    # RAG configuration
    RAG_EMBED_MODEL: str = os.getenv("RAG_EMBED_MODEL", "BAAI/bge-small-en-v1.5")
    RAG_LLM_MODEL: str = os.getenv("RAG_LLM_MODEL", "meta-llama/Llama-3.2-3B-Instruct")

    # System prompts
    SYSTEM_PROMPT_FILE = PROJECT_ROOT / "system_prompt.txt"

    # Generation settings
    MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))
    VERBOSE: bool = os.getenv("VERBOSE", "false").lower() in ("true", "1", "yes")

    @classmethod
    def validate(cls) -> list[str]:
        """
        Validate configuration and return list of issues.

        Returns:
            List of validation error messages (empty if valid)
        """
        issues = []

        # Check GBDK installation
        if not cls.GBDK_LCC.exists():
            issues.append(
                f"GBDK compiler not found at {cls.GBDK_LCC}. "
                f"Please install GBDK 4.2.0 or set GBDK_ROOT environment variable."
            )

        # Check system prompt
        if not cls.SYSTEM_PROMPT_FILE.exists():
            issues.append(f"System prompt file not found at {cls.SYSTEM_PROMPT_FILE}")

        # Check data directory
        if not cls.DATA_DIR.exists():
            issues.append(f"Data directory not found at {cls.DATA_DIR}")

        return issues

    @classmethod
    def print_config(cls) -> None:
        """Print current configuration (excluding sensitive data)."""
        print("=" * 60)
        print("NightwingGameSim Configuration")
        print("=" * 60)
        print(f"Project Root: {cls.PROJECT_ROOT}")
        print(f"GBDK Root:    {cls.GBDK_ROOT}")
        print(f"GBDK Compiler: {cls.GBDK_LCC}")
        print(f"Working Dir:  {cls.WKDIR}")
        print(f"Output Dir:   {cls.OUT_DIR}")
        print(f"\nClaude Model: {cls.CLAUDE_MODEL}")
        print(f"API Key Set:  {'Yes' if cls.ANTHROPIC_API_KEY else 'No'}")
        print(f"Local Model:  {cls.LOCAL_MODEL_PATH if cls.LOCAL_MODEL_PATH else 'Not configured'}")
        print(f"\nMax Retries:  {cls.MAX_RETRIES}")
        print(f"Verbose:      {cls.VERBOSE}")
        print("=" * 60)

        # Show validation issues if any
        issues = cls.validate()
        if issues:
            print("\n⚠️  Configuration Issues:")
            for issue in issues:
                print(f"  - {issue}")
            print()

    @classmethod
    def ensure_directories(cls) -> None:
        """Create necessary directories if they don't exist."""
        for directory in [cls.WKDIR, cls.OUT_DIR, cls.SRC_DIR, cls.TESTS_DIR,
                         cls.EXAMPLES_DIR, cls.DOCS_DIR]:
            directory.mkdir(parents=True, exist_ok=True)


# Create a singleton instance
config = Config()


if __name__ == "__main__":
    # Test configuration when run directly
    config.print_config()
