#!/bin/bash
# TroyBW Creator Studio — Launch Script
# Troy's email: troychen1507@gmail.com

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Load Titan API keys
ENV_FILE="$HOME/titan/.env.live"
if [ -f "$ENV_FILE" ]; then
  set -a && source "$ENV_FILE" && set +a
  echo "✅ Titan API keys loaded"
else
  # Try alternate locations
  for f in "$HOME/.env.live" "$HOME/titan_signal/.env.live" "$HOME/.env"; do
    if [ -f "$f" ]; then
      set -a && source "$f" && set +a
      echo "✅ Keys loaded from $f"
      break
    fi
  done
fi

if [ -z "$OPENAI_API_KEY" ]; then
  echo "⚠️  Warning: OPENAI_API_KEY not found. Set it manually or source your .env.live file."
fi

# Install dependencies if missing
echo "🔧 Checking dependencies..."
pip3 install fastapi uvicorn httpx --quiet 2>/dev/null

echo ""
echo "============================================"
echo "   🎮 TROYBW CREATOR STUDIO — STARTING!"
echo "   Open: http://localhost:8010"
echo "   Troy's email: troychen1507@gmail.com"
echo "============================================"
echo ""

# Open browser automatically after 2 seconds
(sleep 2 && open "http://localhost:8010") &

python3 server.py
