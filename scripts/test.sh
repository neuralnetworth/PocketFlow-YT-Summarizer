#!/bin/bash
# Test runner script for uv

set -e

echo "Running tests with uv..."
uv run pytest "$@"