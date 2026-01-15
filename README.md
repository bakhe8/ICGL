# 🤖 AutoBeto

**AutoBeto** is a high-performance, command-line automation toolkit designed for developers who value simplicity and power. Built with Python, it provides a robust foundation for creating, managing, and executing automation tasks with a beautiful UI and professional logging.

## ✨ Features

- 🖥️ **Rich CLI**: Beautiful terminal output leveraging `rich` and `click`.
- ⚙️ **Config Driven**: Seamless configuration management via `YAML` and `.env`.
- 📝 **Pro Logging**: Structured logging powered by `loguru`.
- 🧪 **Test-Ready**: Built-in test suite using `pytest`.
- 🚀 **Extensible**: Easily add new automation tasks as CLI commands.

## 🚀 Getting Started

### Installation

```bash
# Clone the repository
git clone https://github.com/bakhe8/AutoBeto.git
cd AutoBeto

# Install dependencies
pip install -e .
# OR using Poetry
poetry install
```

### Usage

Run the welcome command:

```bash
autobeto hello
```

Execute an automation task:

```bash
autobeto auto my_task
```

## 🛠️ Project Structure

- `src/autobeto/cli.py`: CLI command definitions.
- `src/autobeto/config/`: Configuration management.
- `src/autobeto/utils/`: Utility functions (logging, etc.).
- `config.yaml`: Main configuration file.
- `tests/`: Automated test suite.

---
**Made with ❤️ for Automation Enthusiasts**
