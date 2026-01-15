# 🤖 AutoBeto: Consensus AI Foundation

**AutoBeto** is the implementation foundation for **Consensus AI** — a high-performance, command-line governance framework designed to manage complex decisions, prevent conceptual drift, and preserve human sovereignty.

## 🏛️ Core Identity

Consensus AI is not just a tool; it's a **Smart Decision Court**. It transforms complex thinking into a conscious governance process that preserves meaning and ensures the human remains the final authority.

> [!NOTE]
> Read the full [Consensus AI Manifesto](file:///c:/Users/Bakheet/Documents/Projects/AutoBeto/docs/manifesto.md) to understand the philosophy, goals, and core components of the system.

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
