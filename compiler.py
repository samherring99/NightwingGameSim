"""
GameBoy ROM compiler wrapper for NightwingGameSim.

Provides Python interface to compile.sh with error handling and result parsing.
"""

import subprocess
import shutil
from pathlib import Path
from dataclasses import dataclass
from typing import Optional
from config import config
from utils import (
    read_file_safe,
    write_file_safe,
    format_compilation_error,
    parse_compilation_errors
)


@dataclass
class CompilationResult:
    """Result of a compilation attempt."""
    success: bool
    output_path: Optional[Path] = None
    error_message: Optional[str] = None
    raw_errors: Optional[str] = None
    parsed_errors: Optional[list[dict]] = None


class Compiler:
    """Wrapper for GBDK GameBoy ROM compilation."""

    def __init__(self):
        """Initialize compiler with config paths."""
        self.wkdir = config.WKDIR
        self.work_file = config.WORK_FILE
        self.work_obj = config.WORK_OBJ
        self.work_err = config.WORK_ERR
        self.output_gb = config.OUTPUT_GB
        self.compile_script = config.COMPILE_SCRIPT

        # Ensure directories exist
        config.ensure_directories()

    def compile(self, c_code: str, output_name: str = "out.gb") -> CompilationResult:
        """
        Compile C code to GameBoy ROM.

        Args:
            c_code: C source code to compile
            output_name: Name for output .gb file

        Returns:
            CompilationResult with success status and details
        """
        # Validate compile script exists
        if not self.compile_script.exists():
            return CompilationResult(
                success=False,
                error_message=f"Compile script not found: {self.compile_script}"
            )

        # Write C code to working file
        success, message = write_file_safe(self.work_file, c_code)
        if not success:
            return CompilationResult(
                success=False,
                error_message=f"Failed to write source file: {message}"
            )

        if config.VERBOSE:
            print(f"Wrote {len(c_code)} bytes to {self.work_file}")

        # Clean up previous artifacts
        self._clean_working_directory()

        # Run compilation script
        try:
            if config.VERBOSE:
                print(f"Running {self.compile_script}...")

            result = subprocess.run(
                ["bash", str(self.compile_script)],
                cwd=config.PROJECT_ROOT,
                capture_output=True,
                text=True,
                timeout=30
            )

            if config.VERBOSE:
                if result.stdout:
                    print(f"Compiler stdout: {result.stdout}")
                if result.stderr:
                    print(f"Compiler stderr: {result.stderr}")

        except subprocess.TimeoutExpired:
            return CompilationResult(
                success=False,
                error_message="Compilation timed out after 30 seconds"
            )
        except Exception as e:
            return CompilationResult(
                success=False,
                error_message=f"Failed to run compiler: {e}"
            )

        # Check if compilation succeeded
        if self.output_gb.exists():
            # Success! Move to desired output name if different
            final_output = config.OUT_DIR / output_name

            try:
                if final_output != self.output_gb:
                    shutil.move(str(self.output_gb), str(final_output))
                else:
                    final_output = self.output_gb

                return CompilationResult(
                    success=True,
                    output_path=final_output
                )
            except Exception as e:
                return CompilationResult(
                    success=False,
                    error_message=f"Compilation succeeded but failed to move output: {e}"
                )

        # Compilation failed - read error output
        error_text = ""
        if self.work_err.exists():
            success, content = read_file_safe(self.work_err)
            if success:
                error_text = content

        # Also include stdout/stderr from script execution
        combined_errors = []
        if error_text:
            combined_errors.append(error_text)
        if result.stderr:
            combined_errors.append(result.stderr)
        if result.stdout and "error" in result.stdout.lower():
            combined_errors.append(result.stdout)

        raw_errors = "\n".join(combined_errors)
        formatted_errors = format_compilation_error(raw_errors)
        parsed_errors = parse_compilation_errors(raw_errors)

        return CompilationResult(
            success=False,
            error_message=formatted_errors if formatted_errors else "Compilation failed with no error output",
            raw_errors=raw_errors,
            parsed_errors=parsed_errors
        )

    def _clean_working_directory(self):
        """Clean up previous compilation artifacts."""
        artifacts = [
            self.work_obj,
            self.work_err,
            self.output_gb,
            self.wkdir / "out.gb",
        ]

        for artifact in artifacts:
            if artifact.exists():
                try:
                    artifact.unlink()
                    if config.VERBOSE:
                        print(f"Cleaned up {artifact}")
                except Exception as e:
                    if config.VERBOSE:
                        print(f"Warning: Could not remove {artifact}: {e}")

    def validate_gbdk_installation(self) -> tuple[bool, str]:
        """
        Validate GBDK is properly installed.

        Returns:
            Tuple of (is_valid: bool, message: str)
        """
        if not config.GBDK_LCC.exists():
            return False, (
                f"GBDK compiler not found at {config.GBDK_LCC}\n"
                f"Please install GBDK 4.2.0 or set GBDK_ROOT environment variable"
            )

        # Try to run lcc to check it works
        try:
            result = subprocess.run(
                [str(config.GBDK_LCC), "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return True, f"GBDK found at {config.GBDK_LCC}"
        except Exception as e:
            return False, f"GBDK found but failed to run: {e}"


# Global compiler instance
compiler = Compiler()


if __name__ == "__main__":
    # Test compilation with a simple program
    test_code = """
#include <gb/gb.h>
#include <stdio.h>

void main() {
    printf("Hello GameBoy!");
    waitpad(J_START);
}
"""

    print("Testing compiler...")
    print("=" * 60)

    # Validate GBDK
    valid, message = compiler.validate_gbdk_installation()
    print(f"GBDK Validation: {message}")
    print()

    if valid:
        print("Compiling test code...")
        result = compiler.compile(test_code, output_name="test.gb")

        if result.success:
            print(f"Success! ROM created at: {result.output_path}")
        else:
            print(f"Compilation failed:")
            print(result.error_message)
    else:
        print("Skipping compilation test (GBDK not available)")
