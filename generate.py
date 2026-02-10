#!/usr/bin/env python3
"""
NightwingGameSim - Unified GameBoy ROM Generator

Generate working GameBoy .gb files from text prompts using LLMs.
"""

import sys
import argparse
from pathlib import Path
from typing import Optional
from datetime import datetime

from config import config
from compiler import compiler
from utils import extract_code_from_markdown, write_file_safe, clean_filename


def generate_with_claude(prompt: str) -> str:
    """Generate code using Claude API."""
    from generate_claude import generate_code
    return generate_code(prompt)


def generate_with_local(prompt: str) -> str:
    """Generate code using local Llama model."""
    from generate_local import generate_code
    return generate_code(prompt)


def generate_with_rag(prompt: str) -> str:
    """Generate code using RAG pipeline."""
    from generate_rag import generate_code
    return generate_code(prompt)


def main():
    """Main entry point for NightwingGameSim."""
    parser = argparse.ArgumentParser(
        description="Generate GameBoy ROM files from text prompts",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "Create a simple pong game"
  %(prog)s "Make a snake game" --backend local
  %(prog)s "Tic-tac-toe" --output tictactoe.gb --save-source
  %(prog)s --prompt-file examples/my_game.txt --max-retries 5

Backends:
  claude - Use Anthropic's Claude API (requires ANTHROPIC_API_KEY)
  local  - Use local Llama model (requires LOCAL_MODEL_PATH)
  rag    - Use RAG with documentation (requires LOCAL_MODEL_PATH)
        """
    )

    parser.add_argument(
        "prompt",
        nargs="*",
        help="Text prompt describing the game to create"
    )

    parser.add_argument(
        "--backend",
        choices=["claude", "local", "rag"],
        default="claude",
        help="LLM backend to use (default: claude)"
    )

    parser.add_argument(
        "--output", "-o",
        type=str,
        help="Output .gb filename (default: auto-generated from prompt)"
    )

    parser.add_argument(
        "--save-source",
        action="store_true",
        help="Save generated C source code to src/ directory"
    )

    parser.add_argument(
        "--max-retries",
        type=int,
        default=config.MAX_RETRIES,
        help=f"Maximum compilation retry attempts (default: {config.MAX_RETRIES})"
    )

    parser.add_argument(
        "--prompt-file",
        type=Path,
        help="Read prompt from file instead of command line"
    )

    parser.add_argument(
        "--system-prompt",
        type=Path,
        help="Custom system prompt file (default: system_prompt.txt)"
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )

    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Only validate configuration, don't generate"
    )

    args = parser.parse_args()

    # Set verbose mode
    if args.verbose:
        config.VERBOSE = True

    # Print header
    print("=" * 70)
    print("NightwingGameSim - GameBoy ROM Generator".center(70))
    print("=" * 70)
    print()

    # Validate configuration
    if config.VERBOSE or args.validate_only:
        config.print_config()

    issues = config.validate()
    if issues:
        print("⚠️  Configuration Issues:")
        for issue in issues:
            print(f"  - {issue}")
        print()

        if args.validate_only:
            sys.exit(1 if issues else 0)

    if args.validate_only:
        print("✓ Configuration valid!")
        sys.exit(0)

    # Get prompt
    if args.prompt_file:
        if not args.prompt_file.exists():
            print(f"Error: Prompt file not found: {args.prompt_file}")
            sys.exit(1)
        prompt = args.prompt_file.read_text().strip()
        print(f"📄 Loaded prompt from: {args.prompt_file}")
    elif args.prompt:
        prompt = " ".join(args.prompt)
    else:
        print("Error: No prompt provided. Use positional argument or --prompt-file")
        parser.print_help()
        sys.exit(1)

    print(f"Prompt: {prompt}")
    print(f"Backend: {args.backend}")
    print()

    # Select generator based on backend
    generators = {
        "claude": generate_with_claude,
        "local": generate_with_local,
        "rag": generate_with_rag,
    }

    generator = generators[args.backend]

    # Generation and compilation loop with retries
    for attempt in range(1, args.max_retries + 1):
        print(f"Attempt {attempt}/{args.max_retries}: Generating code...")

        try:
            # Generate code
            llm_output = generator(prompt)

            if config.VERBOSE:
                print(f"Raw LLM output ({len(llm_output)} chars):")
                print("-" * 70)
                print(llm_output[:500] + "..." if len(llm_output) > 500 else llm_output)
                print("-" * 70)

            # Extract C code
            c_code = extract_code_from_markdown(llm_output)

            if not c_code:
                print("Error: Could not extract C code from LLM output")
                if attempt < args.max_retries:
                    print(f"   Retrying... ({attempt + 1}/{args.max_retries})")
                    continue
                else:
                    print("   Max retries reached. Giving up.")
                    sys.exit(1)

            print(f"✓ Extracted {len(c_code)} bytes of C code")

            # Save source if requested
            if args.save_source:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                safe_name = clean_filename(prompt[:50])
                source_filename = f"{timestamp}_{safe_name}.c"
                source_path = config.SRC_DIR / source_filename

                success, message = write_file_safe(source_path, c_code)
                if success:
                    print(f"Saved source: {source_path}")
                else:
                    print(f" Warning: Could not save source: {message}")

            # Compile
            print("Compiling...")

            # Determine output filename
            if args.output:
                output_name = args.output if args.output.endswith('.gb') else f"{args.output}.gb"
            else:
                safe_name = clean_filename(prompt[:50])
                output_name = f"{safe_name}.gb"

            result = compiler.compile(c_code, output_name=output_name)

            if result.success:
                print()
                print("=" * 70)
                print("SUCCESS!".center(70))
                print("=" * 70)
                print(f"ROM file: {result.output_path}")
                print(f"Size: {result.output_path.stat().st_size:,} bytes")
                print()
                print("To play your game:")
                print(f"  - Use a GameBoy emulator (BGB, mGBA, SameBoy)")
                print(f"  - Load file: {result.output_path}")
                print("=" * 70)
                sys.exit(0)

            else:
                print(f"Compilation failed:")
                print()
                print(result.error_message)
                print()

                if attempt < args.max_retries:
                    print(f"Retrying with error feedback... ({attempt + 1}/{args.max_retries})")
                    # TODO: In future, send error feedback to LLM for correction
                    continue
                else:
                    print("Max retries reached. Compilation unsuccessful.")
                    if result.raw_errors:
                        error_file = config.OUT_DIR / "last_error.txt"
                        write_file_safe(error_file, result.raw_errors)
                        print(f"📝 Full error log saved to: {error_file}")
                    sys.exit(1)

        except KeyboardInterrupt:
            print("\n\n Interrupted by user")
            sys.exit(130)

        except Exception as e:
            print(f"Error during generation: {e}")
            if config.VERBOSE:
                import traceback
                traceback.print_exc()

            if attempt < args.max_retries:
                print(f"Retrying... ({attempt + 1}/{args.max_retries})")
                continue
            else:
                print("Max retries reached.")
                sys.exit(1)

    print("All attempts exhausted.")
    sys.exit(1)


if __name__ == "__main__":
    main()
