"""
Utility functions for NightwingGameSim.

Common helpers for code extraction, file operations, and error formatting.
"""

import re
from pathlib import Path
from typing import Optional, Tuple


def extract_code_from_markdown(text: str) -> Optional[str]:
    """
    Extract C code from markdown code blocks.

    Handles both:
    - Triple backtick fenced blocks: ```c or ```
    - Inline code with language specification

    Args:
        text: LLM output text potentially containing code blocks

    Returns:
        Extracted C code or None if no code block found
    """
    # Try to find code in triple backticks with optional language tag
    patterns = [
        r'```c\n(.*?)```',      # ```c ... ```
        r'```C\n(.*?)```',      # ```C ... ```
        r'```\n(.*?)```',       # ``` ... ```
        r'```(.*?)```',         # ```...``` (no newline)
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.DOTALL)
        if match:
            code = match.group(1).strip()
            if code:
                return code

    # If no code blocks found, check if entire text looks like C code
    if looks_like_c_code(text):
        return text.strip()

    return None


def looks_like_c_code(text: str) -> bool:
    """
    Heuristic check if text appears to be C code.

    Args:
        text: Text to check

    Returns:
        True if text appears to be C code
    """
    c_indicators = [
        '#include',
        'int main(',
        'void ',
        'uint8_t',
        'UINT8',
        '<gb/gb.h>',
    ]

    text_lower = text.lower()
    matches = sum(1 for indicator in c_indicators if indicator.lower() in text_lower)

    # If at least 2 C indicators found, assume it's C code
    return matches >= 2


def clean_filename(name: str) -> str:
    """
    Clean a string to make it a valid filename.

    Args:
        name: String to clean

    Returns:
        Cleaned filename-safe string
    """
    # Remove or replace invalid characters
    cleaned = re.sub(r'[<>:"/\\|?*]', '_', name)
    # Remove leading/trailing whitespace and dots
    cleaned = cleaned.strip('. ')
    # Limit length
    if len(cleaned) > 200:
        cleaned = cleaned[:200]
    # Ensure not empty
    if not cleaned:
        cleaned = "unnamed"
    return cleaned


def format_compilation_error(error_text: str) -> str:
    """
    Format GBDK compilation errors for better readability.

    Args:
        error_text: Raw error output from GBDK compiler

    Returns:
        Formatted, human-readable error messages
    """
    if not error_text or not error_text.strip():
        return "No error output (compilation may have failed silently)"

    lines = error_text.strip().split('\n')
    formatted = []

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Highlight error and warning lines
        if 'error:' in line.lower():
            formatted.append(f"{line}")
        elif 'warning:' in line.lower():
            formatted.append(f" {line}")
        else:
            formatted.append(f"   {line}")

    return '\n'.join(formatted)


def parse_compilation_errors(error_text: str) -> list[dict]:
    """
    Parse GBDK error output into structured error information.

    Args:
        error_text: Raw error output from GBDK compiler

    Returns:
        List of error dictionaries with keys: line, column, type, message
    """
    errors = []

    # Pattern for GBDK error format: file.c:line:column: error: message
    pattern = r'(\w+\.c):(\d+):(\d+):\s*(error|warning):\s*(.+)'

    for match in re.finditer(pattern, error_text):
        errors.append({
            'file': match.group(1),
            'line': int(match.group(2)),
            'column': int(match.group(3)),
            'type': match.group(4),
            'message': match.group(5).strip()
        })

    return errors


def read_file_safe(file_path: Path) -> Tuple[bool, str]:
    """
    Safely read a file with error handling.

    Args:
        file_path: Path to file to read

    Returns:
        Tuple of (success: bool, content_or_error: str)
    """
    try:
        content = file_path.read_text(encoding='utf-8')
        return True, content
    except FileNotFoundError:
        return False, f"File not found: {file_path}"
    except PermissionError:
        return False, f"Permission denied: {file_path}"
    except Exception as e:
        return False, f"Error reading {file_path}: {e}"


def write_file_safe(file_path: Path, content: str) -> Tuple[bool, str]:
    """
    Safely write a file with error handling.

    Args:
        file_path: Path to file to write
        content: Content to write

    Returns:
        Tuple of (success: bool, message: str)
    """
    try:
        # Ensure parent directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)

        file_path.write_text(content, encoding='utf-8')
        return True, f"Written to {file_path}"
    except PermissionError:
        return False, f"Permission denied: {file_path}"
    except Exception as e:
        return False, f"Error writing {file_path}: {e}"


def truncate_text(text: str, max_length: int = 1000) -> str:
    """
    Truncate text to max length with ellipsis.

    Args:
        text: Text to truncate
        max_length: Maximum length

    Returns:
        Truncated text with ellipsis if needed
    """
    if len(text) <= max_length:
        return text
    return text[:max_length] + "...\n[truncated]"


def count_lines(text: str) -> int:
    """
    Count lines in text.

    Args:
        text: Text to count lines in

    Returns:
        Number of lines
    """
    return len(text.splitlines())


if __name__ == "__main__":
    # Test utilities
    test_code = """
    Here is some C code:
    ```c
    #include <gb/gb.h>

    void main() {
        printf("Hello GameBoy!");
    }
    ```
    """

    extracted = extract_code_from_markdown(test_code)
    print("Extracted code:")
    print(extracted)

    # Test error formatting
    test_error = """file.c:10:5: error: undeclared variable 'foo'
    file.c:12:1: warning: unused variable 'bar'"""

    print("\nFormatted errors:")
    print(format_compilation_error(test_error))

    print("\nParsed errors:")
    print(parse_compilation_errors(test_error))
