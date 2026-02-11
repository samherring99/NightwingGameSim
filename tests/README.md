# tests/

Test suite for NightwingGameSim.

## Structure
- `test_config.py` - Configuration system tests
- `test_compiler.py` - Compilation pipeline tests
- `test_generators.py` - LLM generation tests
- `test_integration.py` - End-to-end tests
- `test_utils.py` - Utility function tests

## Running Tests
```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=nightwing_gamesim --cov-report=html

# Run specific test file
pytest tests/test_config.py -v
```
