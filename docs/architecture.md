# AutoBeto Architecture

This document describes the high-level architecture of AutoBeto.

## Components

- **CLI (`cli.py`)**: Entry point for all commands. Uses `click` for subcommands.
- **Config (`config/`)**: Manages settings from `config.yaml` and `.env`.
- **Utils (`utils/`)**: Shared utilities like logging and path helpers.

## Flow

1. User runs `autobeto [command]`.
2. `main.py` initializes logging and configuration.
3. `cli.py` executes the corresponding function.
