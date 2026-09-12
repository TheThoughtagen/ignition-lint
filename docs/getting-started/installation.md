---
sidebar_position: 1
title: Installation
---

# Installation

## Prerequisites

- **Python 3.10+**
- **pip** or **uv** package manager
- Access to Ignition Perspective project files

## Install from PyPI

```bash
pip install ignition-lint-toolkit
```

## Install with uv (recommended)

[uv](https://docs.astral.sh/uv/) is a fast Python package manager ideal for workspace management.

```bash
# Install uv if you don't have it
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and set up the project
git clone https://github.com/TheThoughtagen/ignition-lint.git
cd ignition-lint

# Install dependencies
uv sync
```

## Install from source

```bash
git clone https://github.com/TheThoughtagen/ignition-lint.git
cd ignition-lint

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .
```

## Verify installation

```bash
ignition-lint --help
```

You should see the CLI help output with available options and commands.

## Editor integration

For VS Code JSON schema validation, locate the installed schema:

```sh
python -c "from ignition_lint.schemas import schema_path_for; print(schema_path_for('robust'))"
```

Use the printed path in your editor's JSON schema settings. See [editor integration](../integration/editor-integration.md).

Continue with [your first check](quickstart.md).
