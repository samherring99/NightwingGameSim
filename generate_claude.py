"""
Claude-based GameBoy C code generator.

Uses Anthropic's Claude API to generate GBDK-compatible C code.
"""

import sys
from pathlib import Path
import anthropic
from config import config


def generate_code(prompt: str, system_prompt: str = None) -> str:
    """
    Generate GameBoy C code using Claude.

    Args:
        prompt: User request for what game/program to create
        system_prompt: Optional custom system prompt (uses default if None)

    Returns:
        Generated C code as string
    """
    # Validate API key
    if not config.ANTHROPIC_API_KEY:
        raise ValueError(
            "ANTHROPIC_API_KEY not set. "
            "Please set it in .env file or environment variable."
        )

    # Load system prompt from file if not provided
    if system_prompt is None:
        if config.SYSTEM_PROMPT_FILE.exists():
            system_prompt = config.SYSTEM_PROMPT_FILE.read_text()
        else:
            system_prompt = (
                "You are an expert GameBoy software developer who writes perfect C code "
                "using GBDK. Do not respond with any other text, just the full C code "
                "enclosed in backticks."
            )

    # Create Claude client
    client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)

    # Generate code
    if config.VERBOSE:
        print(f"Generating code with {config.CLAUDE_MODEL}...")

    message = client.messages.create(
        model=config.CLAUDE_MODEL,
        max_tokens=config.CLAUDE_MAX_TOKENS,
        temperature=config.CLAUDE_TEMPERATURE,
        system=system_prompt,
        messages=[{"role": "user", "content": f"Request: {prompt}"}]
    )

    return message.content[0].text


if __name__ == "__main__":
    # Example usage
    if len(sys.argv) > 1:
        prompt = " ".join(sys.argv[1:])
    else:
        prompt = "a creative and pretty visualization"

    try:
        code = generate_code(prompt)
        print(code)
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)