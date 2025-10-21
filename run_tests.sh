#!/bin/bash

echo "Running API Tests..."
echo "===================="

# Install dependencies
pip install -r backend/requirements.txt

# Run tests
pytest tests/test_api.py -v

if [ $? -eq 0 ]; then
    echo "✅ All tests passed!"
else
    echo "❌ Tests failed!"
    exit 1
fi
