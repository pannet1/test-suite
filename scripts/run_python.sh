#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

echo "--- Setting up test-suite ---"

# Install uv if not present
if ! command -v uv >/dev/null 2>&1; then
    echo "Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
fi

export PATH="$HOME/.local/bin:$PATH"

# Setup venv
if [ ! -d ".venv" ]; then
    uv venv .venv
fi

uv pip install -e . --python .venv/bin/python

echo "--- Setup complete ---"
echo "Run: .venv/bin/python src/main.py"

# Run main.py if no args passed
if [ $# -eq 0 ]; then
    .venv/bin/python src/main.py "$@"
fi