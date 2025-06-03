# Intro to Vibe Scripting

## Installation

First, install UV:

**Linux/macOS:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

## Setup

**Linux/macOS:**
```bash
#!/bin/bash

# Set project name (adjust as needed)
PROJECT_NAME="my-uv-project"
KERNEL_NAME="My UV Project"

# Exit if any command fails
set -e

echo "🔧 Initializing project..."
uv init --bare

echo "📦 Installing JupyterLab and ipykernel..."
uv add --dev jupyterlab ipykernel

echo "🧠 Registering Jupyter kernel..."
uv run python -m ipykernel install --user --name="$PROJECT_NAME" --display-name "$KERNEL_NAME"

echo "✅ Setup complete. Run with:"
echo "uv run jupyter lab"
```

**Windows (PowerShell):**
Run the included `setup.ps1` script:
```powershell
.\setup.ps1
```