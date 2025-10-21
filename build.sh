#!/bin/bash

echo "Building BLIP Image Captioning Project..."
echo "=========================================="

# Install build dependencies
python3 -m pip install --upgrade pip build setuptools wheel

# Build the package
echo "Building package..."
python3 -m build

# Check if build was successful
if [ $? -eq 0 ]; then
    echo "✅ Build successful!"
    echo "📦 Package created in dist/ directory:"
    ls -la dist/
else
    echo "❌ Build failed!"
    exit 1
fi