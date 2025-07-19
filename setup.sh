#!/bin/bash

set -e

if [[ ! -f "PenAI.py" || ! -f "chatgpt_wrapper.js" ]]; then
  echo "[!] This script must be run from the directory containing PenAI.py and chatgpt_wrapper.js"
  exit 1
fi

echo "[+] Running setup..."

sudo apt update

if ! command -v zaproxy >/dev/null 2>&1; then
  echo "[+] Installing ZAPROXY..."
  sudo apt install -y zaproxy
else
  echo "[+] ZAPROXY already installed."
fi

if ! command -v npm >/dev/null 2>&1; then
  echo "[+] Installing npm..."
  sudo apt install -y npm
else
  echo "[+] npm already installed."
fi

if ! sqlmap --version >/dev/null 2>&1; then
  echo "[!] sqlmap not found or not working. Attempting to fix by unsetting SSLKEYLOGFILE..."
  unset SSLKEYLOGFILE
else
  echo "[+] sqlmap found."
fi

echo "You still need to export the OPENAI_API_KEY"

echo "[+] Initializing npm and installing dependencies..."
npm init -y
npm install openai dotenv

if ! locate rockyou.txt | grep -q '/usr/share/wordlists/rockyou.txt'; then
  echo "[+] rockyou.txt not found, attempting to decompress..."
  sudo gzip -d /usr/share/wordlists/rockyou.txt.gz || echo "[!] Could not decompress rockyou.txt.gz (might already be extracted)"
else
  echo "[+] rockyou.txt found."
fi

echo "[+] Launching ZAP in a separate terminal..."
gnome-terminal -- bash -c "zaproxy -daemon -port 8080 -config api.key= -config api.disablekey=true -config api.addrs.addr.name='.*' -config api.addrs.addr.regex=true; exec bash"

echo "[✓] Setup complete."
