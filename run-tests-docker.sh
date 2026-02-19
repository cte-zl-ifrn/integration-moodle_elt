#!/bin/bash
# Script to run tests in Docker Compose

set -e

echo "🐳 Running tests in Docker Compose"
echo "===================================="

# Build and run test container
echo "📦 Building test container..."
docker compose --profile test build test

echo ""
echo "🧪 Running tests..."
docker compose --profile test up --exit-code-from test test

# Clean up
echo ""
echo "🧹 Cleaning up..."
docker compose --profile test down -v

echo ""
echo "✅ Docker tests completed!"
