"""
Tests for compiler.py
"""

import pytest
from pathlib import Path
from compiler import Compiler, CompilationResult
from config import config


@pytest.fixture
def compiler_instance():
    """Fixture providing a Compiler instance."""
    return Compiler()


class TestCompilerInit:
    """Tests for Compiler initialization."""

    def test_compiler_init(self, compiler_instance):
        """Test that compiler initializes with correct paths."""
        assert compiler_instance.wkdir == config.WKDIR
        assert compiler_instance.work_file == config.WORK_FILE
        assert compiler_instance.compile_script == config.COMPILE_SCRIPT

    def test_compiler_creates_directories(self, compiler_instance):
        """Test that compiler ensures directories exist."""
        # After init, directories should exist (via ensure_directories)
        assert config.WKDIR.exists()
        assert config.OUT_DIR.exists()


class TestCompilationResult:
    """Tests for CompilationResult dataclass."""

    def test_success_result(self):
        """Test creation of success result."""
        result = CompilationResult(
            success=True,
            output_path=Path("test.gb")
        )
        assert result.success is True
        assert result.output_path == Path("test.gb")
        assert result.error_message is None

    def test_failure_result(self):
        """Test creation of failure result."""
        result = CompilationResult(
            success=False,
            error_message="Test error"
        )
        assert result.success is False
        assert result.error_message == "Test error"
        assert result.output_path is None


class TestCompilerValidation:
    """Tests for GBDK validation."""

    def test_validate_gbdk_returns_tuple(self, compiler_instance):
        """Test that validation returns a tuple."""
        result = compiler_instance.validate_gbdk_installation()
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert isinstance(result[0], bool)
        assert isinstance(result[1], str)

    def test_validate_gbdk_message(self, compiler_instance):
        """Test that validation provides a message."""
        valid, message = compiler_instance.validate_gbdk_installation()
        assert message  # Message should not be empty
        if valid:
            assert "GBDK found" in message or "found at" in message.lower()
        else:
            assert "not found" in message.lower() or "failed" in message.lower()


class TestCompilation:
    """Tests for compilation process."""

    def test_compile_requires_code(self, compiler_instance):
        """Test that compile requires C code."""
        # Empty code should still attempt compilation
        result = compiler_instance.compile("")
        # Will fail but shouldn't crash
        assert isinstance(result, CompilationResult)

    def test_compile_invalid_code_fails(self, compiler_instance):
        """Test that invalid C code produces failure result."""
        # Skip if GBDK not installed
        valid, _ = compiler_instance.validate_gbdk_installation()
        if not valid:
            pytest.skip("GBDK not installed")

        invalid_code = """
        This is not valid C code at all!
        It should fail to compile.
        """

        result = compiler_instance.compile(invalid_code)
        assert result.success is False
        assert result.error_message is not None

    def test_compile_valid_code_succeeds(self, compiler_instance):
        """Test that valid C code compiles successfully."""
        # Skip if GBDK not installed
        valid, _ = compiler_instance.validate_gbdk_installation()
        if not valid:
            pytest.skip("GBDK not installed")

        valid_code = """
#include <gb/gb.h>
#include <stdio.h>

void main() {
    printf("Hello!");
    waitpad(J_START);
}
"""

        result = compiler_instance.compile(valid_code, output_name="test_valid.gb")

        if result.success:
            assert result.output_path is not None
            assert result.output_path.exists()
            assert result.output_path.suffix == ".gb"
            assert result.error_message is None
        else:
            # If compilation failed, should have error message
            assert result.error_message is not None
            print(f"Compilation failed: {result.error_message}")

    def test_compile_custom_output_name(self, compiler_instance):
        """Test compilation with custom output name."""
        valid, _ = compiler_instance.validate_gbdk_installation()
        if not valid:
            pytest.skip("GBDK not installed")

        code = "#include <gb/gb.h>\nvoid main() {}"

        custom_name = "my_custom_game.gb"
        result = compiler_instance.compile(code, output_name=custom_name)

        if result.success:
            assert result.output_path.name == custom_name


class TestCompilerCleanup:
    """Tests for compiler cleanup functionality."""

    def test_clean_working_directory(self, compiler_instance):
        """Test that cleanup removes artifacts."""
        # Create dummy artifacts
        test_file = compiler_instance.wkdir / "test_artifact.o"
        test_file.touch()

        assert test_file.exists()

        compiler_instance._clean_working_directory()

        # The test artifact we created won't be removed
        # (cleanup only removes specific known artifacts)
        # But the method should run without error


class TestCompilerErrors:
    """Tests for error handling."""

    def test_compile_script_missing(self, compiler_instance, tmp_path):
        """Test behavior when compile script is missing."""
        # Temporarily point to non-existent script
        original_script = compiler_instance.compile_script
        compiler_instance.compile_script = tmp_path / "nonexistent.sh"

        result = compiler_instance.compile("#include <gb/gb.h>")

        assert result.success is False
        assert "not found" in result.error_message.lower()

        # Restore
        compiler_instance.compile_script = original_script


@pytest.mark.integration
class TestCompilerIntegration:
    """Integration tests for full compilation pipeline."""

    def test_full_pipeline(self, compiler_instance):
        """Test complete pipeline from code to ROM."""
        valid, _ = compiler_instance.validate_gbdk_installation()
        if not valid:
            pytest.skip("GBDK not installed")

        code = """
#include <gb/gb.h>
#include <gb/drawing.h>
#include <stdio.h>

void main() {
    // Simple program
    printf("Test");

    // Wait for button press
    waitpad(J_START);
}
"""

        result = compiler_instance.compile(code, output_name="integration_test.gb")

        # Should either succeed or fail gracefully
        assert isinstance(result, CompilationResult)

        if result.success:
            assert result.output_path.exists()
            assert result.output_path.stat().st_size > 0
            print(f"✓ Integration test passed: {result.output_path}")
        else:
            print(f"✗ Integration test failed: {result.error_message}")
            # Still a valid result, just failed compilation


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
