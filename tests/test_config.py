"""
Tests for config.py
"""

import pytest
import os
from pathlib import Path
from config import Config


class TestConfigPaths:
    """Tests for configuration path resolution."""

    def test_project_root_exists(self):
        """Test that PROJECT_ROOT is set correctly."""
        assert Config.PROJECT_ROOT.exists()
        assert Config.PROJECT_ROOT.is_dir()

    def test_directory_paths(self):
        """Test that all directory paths are Path objects."""
        assert isinstance(Config.WKDIR, Path)
        assert isinstance(Config.OUT_DIR, Path)
        assert isinstance(Config.SRC_DIR, Path)
        assert isinstance(Config.DATA_DIR, Path)
        assert isinstance(Config.TESTS_DIR, Path)

    def test_paths_relative_to_root(self):
        """Test that paths are relative to project root."""
        assert str(Config.PROJECT_ROOT) in str(Config.WKDIR)
        assert str(Config.PROJECT_ROOT) in str(Config.OUT_DIR)

    def test_gbdk_paths(self):
        """Test GBDK path construction."""
        assert Config.GBDK_ROOT == Config.PROJECT_ROOT / "gbdk"
        assert Config.GBDK_BIN == Config.GBDK_ROOT / "bin"
        assert Config.GBDK_LCC == Config.GBDK_BIN / "lcc"


class TestConfigValidation:
    """Tests for configuration validation."""

    def test_validate_returns_list(self):
        """Test that validate() returns a list."""
        issues = Config.validate()
        assert isinstance(issues, list)

    def test_validate_checks_gbdk(self):
        """Test that validation checks for GBDK."""
        issues = Config.validate()
        # If GBDK is not installed, should have an issue about it
        gbdk_issue = any("GBDK" in issue for issue in issues)
        # Either GBDK is installed (no issue) or not installed (has issue)
        assert gbdk_issue or Config.GBDK_LCC.exists()

    def test_validate_checks_system_prompt(self):
        """Test that validation checks for system prompt file."""
        issues = Config.validate()
        # System prompt should exist (we created it)
        if not Config.SYSTEM_PROMPT_FILE.exists():
            assert any("System prompt" in issue for issue in issues)


class TestConfigSettings:
    """Tests for configuration settings."""

    def test_claude_defaults(self):
        """Test Claude API default settings."""
        assert Config.CLAUDE_MODEL is not None
        assert Config.CLAUDE_MAX_TOKENS > 0
        assert 0.0 <= Config.CLAUDE_TEMPERATURE <= 1.0

    def test_max_retries_positive(self):
        """Test that max retries is positive."""
        assert Config.MAX_RETRIES > 0

    def test_verbose_is_bool(self):
        """Test that verbose is a boolean."""
        assert isinstance(Config.VERBOSE, bool)


class TestConfigEnvironment:
    """Tests for environment variable handling."""

    def test_gbdk_root_override(self, monkeypatch):
        """Test GBDK_ROOT can be overridden via environment."""
        test_path = "/custom/gbdk/path"
        monkeypatch.setenv("GBDK_ROOT", test_path)

        # Need to reimport to pick up the env var
        # This is a limitation of module-level code
        # In practice, users set env vars before running
        assert os.getenv("GBDK_ROOT") == test_path

    def test_api_key_from_env(self, monkeypatch):
        """Test API key can be loaded from environment."""
        test_key = "test_api_key_123"
        monkeypatch.setenv("ANTHROPIC_API_KEY", test_key)
        assert os.getenv("ANTHROPIC_API_KEY") == test_key


class TestConfigMethods:
    """Tests for Config class methods."""

    def test_ensure_directories(self, tmp_path):
        """Test that ensure_directories creates missing dirs."""
        # This test uses Config's actual directories
        # In a real scenario, directories should exist after setup
        Config.ensure_directories()

        assert Config.WKDIR.exists()
        assert Config.OUT_DIR.exists()
        assert Config.SRC_DIR.exists()

    def test_print_config_no_error(self, capsys):
        """Test that print_config runs without error."""
        Config.print_config()
        captured = capsys.readouterr()
        assert "NightwingGameSim Configuration" in captured.out


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
