#!/usr/bin/env bash
set -e

# Support update flag for Miniforge installer
UPDATE_MINIFORGE=0
while getopts "u" opt; do
  case $opt in
    u) UPDATE_MINIFORGE=1 ;;
    *) echo "Usage: $0 [-u]" >&2; exit 1 ;;
  esac
done
shift $((OPTIND-1))

echo "== Xcode command-line tools =="
if ! xcode-select -p &> /dev/null; then
  echo "Installing Xcode command-line tools..."
  xcode-select --install
else
  echo "Xcode command-line tools already installed."
fi

echo "\n== Miniforge / Conda =="
installer=Miniforge3-MacOSX-arm64.sh
url=https://github.com/conda-forge/miniforge/releases/latest/download/$installer
if [ -d "$HOME/miniforge3" ]; then
  if [ "$UPDATE_MINIFORGE" -eq 1 ]; then
    echo "Updating Miniforge3 installation at $HOME/miniforge3..."
    curl -LO "$url"
    bash "$installer" -b -u -p "$HOME/miniforge3"
    rm "$installer"
  else
    echo "Miniforge3 already installed at $HOME/miniforge3"
  fi
else
  echo "Installing Miniforge3 (arm64) to $HOME/miniforge3..."
  curl -LO "$url"
  bash "$installer" -b -p "$HOME/miniforge3"
  rm "$installer"
fi
export PATH="$HOME/miniforge3/bin:$PATH"

echo "\n== Create & Activate environment =="
if conda env list | grep -q "local-llm"; then
  echo "Environment 'local-llm' already exists."
else
  conda create -n local-llm python=3.10 -y
fi
# initialize conda for this shell session
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate local-llm

echo "\n== Python dependencies =="
pip install --upgrade pip
pip install transformers bitsandbytes accelerate peft onnxruntime fastapi streamlit uvicorn \
  beautifulsoup4 requests pydantic python-dotenv pytest

echo "\n== Docker Desktop (Apple Silicon) =="
if ! command -v docker &> /dev/null; then
  echo "Docker CLI not found. Ensure Docker Desktop for Mac (Apple Silicon) is installed and the 'docker' command is on your PATH."
else
  echo "Docker found: $(docker --version)"
fi

echo "\n== PyTorch MPS backend check =="
python - << 'EOF'
import torch
print("MPS available:", torch.backends.mps.is_available())
EOF

echo "\nLocal environment setup complete."
