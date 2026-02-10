"""
Tests for utils.py
"""

import pytest
from pathlib import Path
from utils import (
    extract_code_from_markdown,
    looks_like_c_code,
    clean_filename,
    format_compilation_error,
    parse_compilation_errors,
    truncate_text,
    count_lines
)


class TestCodeExtraction:
    """Tests for code extraction from markdown."""

    def test_extract_code_with_c_tag(self):
        """Test extraction from ```c code blocks."""
        text = """
        Here is some code:
        ```c
        #include <gb/gb.h>
        void main() {
            printf("Hello");
        }
        ```
        """
        code = extract_code_from_markdown(text)
        assert code is not None
        assert "#include <gb/gb.h>" in code
        assert "void main()" in code

    def test_extract_code_without_tag(self):
        """Test extraction from ``` code blocks."""
        text = """
        ```
        #include <stdio.h>
        int main() { return 0; }
        ```
        """
        code = extract_code_from_markdown(text)
        assert code is not None
        assert "#include <stdio.h>" in code

    def test_extract_code_no_backticks(self):
        """Test extraction when code has no backticks but looks like C."""
        text = """
        #include <gb/gb.h>
        #include <stdio.h>

        void main() {
            printf("Hello GameBoy!");
        }
        """
        code = extract_code_from_markdown(text)
        assert code is not None
        assert "#include <gb/gb.h>" in code

    def test_extract_code_none(self):
        """Test extraction returns None for non-code text."""
        text = "This is just regular text with no code."
        code = extract_code_from_markdown(text)
        assert code is None

    def test_extract_multiple_blocks_gets_first(self):
        """Test that first code block is extracted when multiple exist."""
        text = """
        First block:
        ```c
        int foo() { return 1; }
        ```

        Second block:
        ```c
        int bar() { return 2; }
        ```
        """
        code = extract_code_from_markdown(text)
        assert code is not None
        assert "foo" in code
        # Should get first block, not second
        assert "bar" not in code or code.index("foo") < code.index("bar")


class TestLooksLikeCCode:
    """Tests for C code detection heuristic."""

    def test_looks_like_c_positive(self):
        """Test detection of obvious C code."""
        code = """
        #include <gb/gb.h>
        void main() {
            UINT8 x = 0;
        }
        """
        assert looks_like_c_code(code) is True

    def test_looks_like_c_negative(self):
        """Test rejection of non-C text."""
        text = "This is just regular English text."
        assert looks_like_c_code(text) is False

    def test_looks_like_c_edge_case(self):
        """Test edge case with only one indicator."""
        text = "#include <stdio.h>"
        # Only 1 indicator, should be False (threshold is 2)
        assert looks_like_c_code(text) is False


class TestFilenameClean:
    """Tests for filename sanitization."""

    def test_clean_filename_basic(self):
        """Test basic filename cleaning."""
        assert clean_filename("hello world") == "hello world"
        assert clean_filename("test.txt") == "test.txt"

    def test_clean_filename_invalid_chars(self):
        """Test removal of invalid filename characters."""
        assert clean_filename("hello/world") == "hello_world"
        assert clean_filename("test:file") == "test_file"
        assert clean_filename("<>:\"/\\|?*") == "___________"

    def test_clean_filename_long(self):
        """Test truncation of long filenames."""
        long_name = "a" * 300
        cleaned = clean_filename(long_name)
        assert len(cleaned) <= 200

    def test_clean_filename_empty(self):
        """Test handling of empty string."""
        assert clean_filename("") == "unnamed"
        assert clean_filename("   ") == "unnamed"


class TestErrorFormatting:
    """Tests for compilation error formatting."""

    def test_format_error_basic(self):
        """Test basic error formatting."""
        error = "file.c:10:5: error: undeclared variable"
        formatted = format_compilation_error(error)
        assert "❌" in formatted
        assert "error" in formatted

    def test_format_error_warning(self):
        """Test warning formatting."""
        error = "file.c:5:1: warning: unused variable"
        formatted = format_compilation_error(error)
        assert "⚠️" in formatted

    def test_format_error_empty(self):
        """Test handling of empty error."""
        formatted = format_compilation_error("")
        assert "No error output" in formatted

    def test_parse_errors(self):
        """Test error parsing into structured data."""
        error_text = """file.c:10:5: error: undeclared variable 'foo'
file.c:12:1: warning: unused variable 'bar'"""

        errors = parse_compilation_errors(error_text)
        assert len(errors) == 2

        assert errors[0]['line'] == 10
        assert errors[0]['column'] == 5
        assert errors[0]['type'] == 'error'
        assert 'foo' in errors[0]['message']

        assert errors[1]['line'] == 12
        assert errors[1]['type'] == 'warning'


class TestTextUtilities:
    """Tests for text utility functions."""

    def test_truncate_short_text(self):
        """Test truncation doesn't affect short text."""
        text = "Short text"
        assert truncate_text(text, max_length=100) == text

    def test_truncate_long_text(self):
        """Test truncation of long text."""
        text = "a" * 2000
        truncated = truncate_text(text, max_length=100)
        assert len(truncated) < 200  # Should be truncated + ellipsis
        assert "[truncated]" in truncated

    def test_count_lines(self):
        """Test line counting."""
        assert count_lines("single line") == 1
        assert count_lines("line 1\nline 2\nline 3") == 3
        assert count_lines("") == 1  # Empty string is 1 line


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
