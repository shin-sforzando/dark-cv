# Dark CV

A Python project to enhance images taken in dark environments.

## Getting Started

### Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) - Python Environment Manager
  - [Ruff](https://github.com/astral-sh/ruff) - Linter & Formatter
  - [ty](https://github.com/davidvujic/ty) - Type Checker
  - [pre-commit](https://pre-commit.com/) - Git Hooks Manager

### Installation

Create a virtual environment and install dependencies:

```bash
uv venv
uv sync
```

To activate the virtual environment, run:

```bash
source .venv/bin/activate
```

Set up pre-commit hooks:

```bash
uv run pre-commit install
```
