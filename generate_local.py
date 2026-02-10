"""
Local Llama-based GameBoy C code generator.

Uses llama-cpp-python with a local GGUF model to generate GBDK-compatible C code.
"""

import sys
from pathlib import Path
from llama_cpp import Llama
from config import config


def load_model() -> Llama:
    """
    Load local Llama model.

    Returns:
        Initialized Llama model instance

    Raises:
        ValueError: If model path not configured or model file doesn't exist
    """
    if not config.LOCAL_MODEL_PATH:
        raise ValueError(
            "LOCAL_MODEL_PATH not set. "
            "Please download a Llama model and set the path in .env file.\n"
            "Example: Meta-Llama-3-8B-Instruct-Q4_K_M.gguf"
        )

    model_path = Path(config.LOCAL_MODEL_PATH)
    if not model_path.exists():
        raise ValueError(f"Model file not found: {model_path}")

    if config.VERBOSE:
        print(f"Loading model from {model_path}...")

    return Llama(
        model_path=str(model_path),
        n_gpu_layers=-1,  # Use GPU acceleration if available
        n_ctx=8192,       # Context window size
        verbose=config.VERBOSE
    )


def generate_code(prompt: str, system_prompt: str = None) -> str:
    """
    Generate GameBoy C code using local Llama model.

    Args:
        prompt: User request for what game/program to create
        system_prompt: Optional custom system prompt (uses default if None)

    Returns:
        Generated C code as string
    """
    # Load system prompt from file if not provided
    if system_prompt is None:
        if config.SYSTEM_PROMPT_FILE.exists():
            system_prompt = config.SYSTEM_PROMPT_FILE.read_text()
        else:
            system_prompt = (
                "Write me C code that compiles to a .gb file given the following description. "
                "Do not return any other text, just the full C code enclosed in backticks. "
                "The code should be error free and concise, do not make any assumptions. "
                "Everything should be in one file. Define any methods or variables you need. "
                "Use tiling to draw sprites. "
                "You'll want to use `#include <gb/gb.h>` in your headers and use `joypad()` to wait for user control. "
                "It will be compiled and ran on a Nintendo GameBoy, so be visually creative."
            )

    # Construct full prompt
    full_prompt = f"{system_prompt}\n\nDescription: {prompt}"

    # Load model
    llm = load_model()

    # Generate code
    if config.VERBOSE:
        print("Generating code with local Llama model...")

    output = llm(
        full_prompt,
        max_tokens=None,
        temperature=0.0,
        top_p=0.95,
    )

    return output['choices'][0]['text']


if __name__ == "__main__":
    # Example usage
    if len(sys.argv) > 1:
        prompt = " ".join(sys.argv[1:])
    else:
        prompt = "render a pyramid in isometric view"

    try:
        code = generate_code(prompt)
        print(code)
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)