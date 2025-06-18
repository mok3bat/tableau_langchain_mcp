#!/bin/bash

# Tableau LangChain MCP Server - Quick Start Script

echo "🚀 Tableau LangChain MCP Server - Quick Start"
echo "============================================="

# Check if Python 3.8+ is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✓ Found Python $PYTHON_VERSION"

# Check if we're in a virtual environment
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "⚠️  You're not in a virtual environment. It's recommended to create one:"
    echo "   python3 -m venv venv"
    echo "   source venv/bin/activate  # On Windows: venv\\Scripts\\activate"
    echo ""
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Exiting. Please set up a virtual environment first."
        exit 1
    fi
else
    echo "✓ Virtual environment active: $VIRTUAL_ENV"
fi

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo "✓ Dependencies installed successfully"

# Install the package in development mode
echo ""
echo "🔧 Installing package in development mode..."
pip install -e .

if [ $? -ne 0 ]; then
    echo "❌ Failed to install package"
    exit 1
fi

echo "✓ Package installed successfully"

# Set up environment file
echo ""
echo "⚙️  Setting up configuration..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✓ Created .env file from template"
    echo "📝 Please edit .env with your Tableau and OpenAI credentials"
else
    echo "ℹ .env file already exists"
fi

# Run tests
echo ""
echo "🧪 Running tests..."
python simple_test.py

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 Setup completed successfully!"
    echo ""
    echo "Next steps:"
    echo "1. Edit .env file with your credentials:"
    echo "   - Tableau Server details and Connected App credentials"
    echo "   - OpenAI API key"
    echo "   - Datasource LUID"
    echo ""
    echo "2. Test your configuration:"
    echo "   python simple_test.py"
    echo ""
    echo "3. Add to your MCP client configuration:"
    echo "   See README.md for configuration examples"
    echo ""
    echo "4. Start using your MCP server!"
else
    echo ""
    echo "⚠️  Setup completed with some issues. Please check the test output above."
fi
