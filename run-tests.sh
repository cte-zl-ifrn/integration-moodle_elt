#!/bin/bash
# Script to run tests locally

set -e

echo "🧪 Running Moodle ELT Integration Tests"
echo "========================================"

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt
pip install --quiet -r requirements-dev.txt

# Run linting
echo ""
echo "🔍 Running linting checks..."
echo "----------------------------"
black --check dags/ tests/ || echo "⚠️  Black formatting issues found. Run 'black dags/ tests/' to fix."
isort --check-only dags/ tests/ || echo "⚠️  Import sorting issues found. Run 'isort dags/ tests/' to fix."
flake8 dags/ tests/ --max-line-length=100 --extend-ignore=E203,W503 || echo "⚠️  Flake8 issues found."

# Run tests
echo ""
echo "🧪 Running unit tests..."
echo "------------------------"
PYTHONPATH=./dags pytest tests/ -v --cov=dags --cov-report=term-missing --cov-report=html:htmlcov

# Display coverage report location
echo ""
echo "✅ Tests completed!"
echo "📊 Coverage report available at: htmlcov/index.html"
echo ""
echo "To view the report, run: open htmlcov/index.html (Mac) or xdg-open htmlcov/index.html (Linux)"
