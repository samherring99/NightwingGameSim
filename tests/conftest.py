"""
Pytest configuration and shared fixtures for NightwingGameSim tests.
"""

import pytest
import sys
from pathlib import Path

# Add parent directory to path so tests can import project modules
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def sample_c_code():
    """Fixture providing valid sample C code for testing."""
    return """
#include <gb/gb.h>
#include <stdio.h>

void main() {
    printf("Hello GameBoy!");
    waitpad(J_START);
}
"""


@pytest.fixture
def invalid_c_code():
    """Fixture providing invalid C code for testing."""
    return """
This is not valid C code!
It should fail compilation.
foo bar baz
"""


@pytest.fixture
def sample_llm_output_with_code():
    """Fixture providing sample LLM output containing code."""
    return """
Here is the GameBoy game you requested:

```c
#include <gb/gb.h>
#include <stdio.h>

void main() {
    UINT8 x = 80, y = 72;

    printf("Game Start!");

    while(1) {
        UINT8 joypad_state = joypad();

        if (joypad_state & J_LEFT) {
            x--;
        }
        if (joypad_state & J_RIGHT) {
            x++;
        }

        plot(x, y, 1, M_NOFILL);
        delay(100);
    }
}
```

This creates a simple interactive program where you can move a cursor left and right.
"""


@pytest.fixture
def sample_compilation_error():
    """Fixture providing sample GBDK compilation error."""
    return """
file.c:10:5: error: undeclared variable 'foo'
file.c:12:1: warning: unused variable 'bar'
file.c:15:10: error: expected ';' before 'baz'
"""


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test (may be slow)"
    )
    config.addinivalue_line(
        "markers", "requires_gbdk: mark test as requiring GBDK installation"
    )
    config.addinivalue_line(
        "markers", "requires_api_key: mark test as requiring API keys"
    )
