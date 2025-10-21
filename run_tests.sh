#!/bin/bash

echo "Running API Tests..."
echo "===================="

# Install the project in editable mode (this includes pytest, pytest-cov, etc.)
python3 -m pip install --user -e .

# Run tests
python3 -m pytest tests/ -v

if [ $? -eq 0 ]; then
    echo "✅ All tests passed!"
else
    echo "❌ Tests failed!"
    exit 1
fi