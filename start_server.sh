#!/data/data/com.termux/files/usr/bin/bash

# NyetRadio Webhook Server - Quick Start Script
# Jalanin server dengan 1 command

clear

echo "╔═══════════════════════════════════════════════╗"
echo "║   🎵 NyetRadio Metadata Webhook Server       ║"
echo "╚═══════════════════════════════════════════════╝"
echo ""

# Cek Python installed
if ! command -v python &> /dev/null; then
    echo "❌ Python not found!"
    echo "📦 Installing Python..."
    pkg install python -y
fi

# Cek Flask installed
if ! python -c "import flask" &> /dev/null; then
    echo "❌ Flask not found!"
    echo "📦 Installing Flask & Requests..."
    pip install flask requests
fi

echo "✅ Dependencies OK"
echo ""

# Cek file webhook_server.py exists
if [ ! -f "webhook_server.py" ]; then
    echo "❌ File webhook_server.py not found!"
    echo "📁 Please download webhook_server.py to this directory"
    exit 1
fi

echo "🚀 Starting webhook server..."
echo "📡 Endpoint: http://localhost:5000/update-metadata"
echo ""
echo "💡 Tips:"
echo "   - Keep Termux running in background"
echo "   - Don't close this terminal"
echo "   - Press Ctrl+C to stop server"
echo ""
echo "─────────────────────────────────────────────────"
echo ""

# Start server
python webhook_server.py
