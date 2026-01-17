# ICGL Style Guide

## File and Code Naming Conventions

### Python Files

- **Modules/Files**: `snake_case.py`
  - Examples: `server.py`, `logging_config.py`, `knowledge_base.py`
  
### Classes and Types

- **Classes**: `PascalCase`
  - Examples: `KnowledgeBase`, `AgentResult`, `ConnectionManager`
  
- **Dataclasses/Pydantic Models**: `PascalCase`
  - Examples: `ProposalRequest`, `SignRequest`, `LLMConfig`

### Functions and Variables

- **Functions**: `snake_case()`
  - Examples: `get_icgl()`, `run_analysis_task()`, `generate_consensus_mindmap()`
  
- **Variables**: `snake_case`
  - Examples: `active_synthesis`, `global_telemetry`, `ui_path`
  
- **Constants**: `UPPER_SNAKE_CASE`
  - Examples: `LOG_FORMAT`, `BASE_DIR`, `API_BASE`

### Private Members

- **Private functions/variables**: Prefix with single underscore `_`
  - Examples: `_icgl_instance`, `_analyze()`, `_check_orphan_adr()`

## Import Organization

1. Standard library imports
2. Third-party imports
3. Local application imports

Separate each group with a blank line.

```python
# Standard library
import os
import sys
from pathlib import Path

# Third-party
from fastapi import FastAPI
from pydantic import BaseModel

# Local
from ..kb import KnowledgeBase
from ..utils.logging_config import get_logger
```

## Documentation

### Docstrings

Use triple-quoted docstrings for all public functions and classes:

```python
def get_icgl() -> ICGL:
    \"\"\"Get or create the ICGL engine singleton (thread-safe).\"\"\"
    ...
```

For complex functions, use detailed docstrings:

```python
def setup_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
    console: bool = True
) -> None:
    \"\"\"
    Configure logging for the entire application.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file path
        console: Whether to also output to console
    \"\"\"
```

## Type Hints

Always use type hints for function parameters and return values:

```python
def process_data(data: Dict[str, Any], limit: int = 10) -> List[str]:
    ...
```

Use `typing` module for complex types:

- `Optional[T]` for nullable values
- `List[T]`, `Dict[K, V]` for collections
- `Union[T1, T2]` for multiple types

## Code Organization

### File Structure

- Keep files focused (single responsibility)
- Aim for <500 lines per file
- Split large files into logical modules

### Module Organization

```python
\"\"\"Module docstring\"\"\"

# Imports
...

# Constants
...

# Type definitions / Dataclasses
...

# Helper functions
...

# Main classes
...

# Public API / Entry points
...
```

## Logging

Use centralized logging instead of `print()`:

```python
from icgl.utils.logging_config import get_logger

logger = get_logger(__name__)

logger.info("Starting process")
logger.warning("Potential issue")
logger.error("Error occurred", exc_info=True)
```

## Error Handling

- Use specific exception types, not generic `Exception`
- Always log errors with context
- Use `exc_info=True` for stack traces

```python
try:
    result = risky_operation()
except ValueError as e:
    logger.error(f"Invalid value: {e}", exc_info=True)
    raise
except ConnectionError as e:
    logger.warning(f"Connection failed: {e}")
    # Handle gracefully
```

## Comments

- Use comments to explain *why*, not *what*
- Keep comments up-to-date with code changes
- Use TODO comments sparingly, prefer creating issues

```python
# Good
# Prevent race condition in singleton initialization
with _icgl_lock:
    ...

# Bad
# Lock the lock
with _icgl_lock:
    ...
```

## Async/Await

- Use `async def` for I/O-bound operations
- Prefer `await` over `.result()`
- Use `asyncio.gather()` for parallel operations

```python
async def fetch_data():
    results = await asyncio.gather(
        fetch_from_api(),
        fetch_from_db(),
        fetch_from_cache()
    )
    return results
```

## Testing

- Test files: `test_*.py` in `/tests` directory
- Test classes: `Test<ModuleName>`
- Test functions: `test_<functionality>`

```python
class TestKnowledgeBase:
    def test_add_concept(self):
        ...
    
    def test_invalid_concept_fails(self):
        ...
```

---

*Last updated: 2026-01-16*
