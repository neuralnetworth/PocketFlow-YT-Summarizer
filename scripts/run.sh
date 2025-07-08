#!/bin/bash
# Run script for uv

set -e

echo "Running YouTube Summarizer with uv..."
uv run python main.py "$@"