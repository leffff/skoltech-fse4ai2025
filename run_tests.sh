#!/bin/bash

echo "Running API Tests..."
echo "===================="

# Install specific compatible versions
python3 -m pip install "httpx>=0.21.0,<0.24.0"
python3 -m pip install -r backend/requirements.txt
python3 -m pip install pytest

# Run tests
python3 -m pytest tests/ -v

if [ $? -eq 0 ]; then
    echo "✅ All tests passed!"
else
    echo "❌ Tests failed!"
    exit 1
fi