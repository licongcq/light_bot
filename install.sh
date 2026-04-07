#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
MODEL_URL="https://alphacephei.com/vosk/models/vosk-model-small-cn-0.22.zip"
MODEL_DIR="$PROJECT_DIR/models"

echo "=== Installing system dependencies ==="
sudo apt-get update
sudo apt-get install -y libportaudio2 portaudio19-dev python3-venv unzip wget

echo "=== Creating Python virtual environment ==="
python3 -m venv "$PROJECT_DIR/.venv"
source "$PROJECT_DIR/.venv/bin/activate"
pip install --upgrade pip
pip install -r "$PROJECT_DIR/requirements.txt"

echo "=== Downloading Vosk Chinese model ==="
if [ ! -d "$MODEL_DIR/vosk-model-small-cn-0.22" ]; then
    mkdir -p "$MODEL_DIR"
    wget -O /tmp/vosk-model-small-cn.zip "$MODEL_URL"
    unzip /tmp/vosk-model-small-cn.zip -d "$MODEL_DIR"
    rm /tmp/vosk-model-small-cn.zip
    echo "Model downloaded to $MODEL_DIR/vosk-model-small-cn-0.22"
else
    echo "Model already exists, skipping download"
fi

echo "=== Setting up config.yaml ==="
if [ ! -f "$PROJECT_DIR/config.yaml" ]; then
    cp "$PROJECT_DIR/config.yaml.example" "$PROJECT_DIR/config.yaml"
    echo "Created config.yaml from config.yaml.example — edit it before starting the service"
else
    echo "config.yaml already exists, leaving as-is"
fi

echo "=== Installing systemd service ==="
sed \
  -e "s|__PROJECT_DIR__|$PROJECT_DIR|g" \
  -e "s|__USER__|$USER|g" \
  "$PROJECT_DIR/light-bot.service.template" \
  | sudo tee /etc/systemd/system/light-bot.service > /dev/null
sudo systemctl daemon-reload
sudo systemctl enable light-bot

echo ""
echo "=== Setup complete ==="
echo "1. Edit config.yaml with your keywords and light URLs"
echo "2. Start the service: sudo systemctl start light-bot"
echo "3. View logs: journalctl -u light-bot -f"
