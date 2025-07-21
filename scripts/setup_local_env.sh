#!/usr/bin/env bash
set -e

echo "== Xcode command-line tools =="
if ! xcode-select -p &> /dev/null; then
  echo "Installing Xcode command-line tools..."
  xcode-select --install
else
  echo "Xcode command-line tools already installed."
fi

echo "\n== Miniforge / Conda =="
if ! command -v conda &> /dev/null; then
  echo "Conda not found. Installing Miniforge3 (arm64)..."
  installer=Miniforge3-MacOSX-arm64.sh
  url=https://github.com/conda-forge/miniforge/releases/latest/download/$installer
  curl -LO "$url"
  bash "$installer" -b -p "$HOME/miniforge3"
  rm "$installer"
  export PATH="$HOME/miniforge3/bin:$PATH"
else
  echo "Conda found at $(which conda)."
fi

echo "\n== Create & Activate environment =="
if conda env list | grep -q "local-llm"; then
  echo "Environment 'local-llm' already exists."
else
  conda create -n local-llm python=3.10 -y
fi
# initialize conda for this shell session
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate local-llm

echo "\n== Docker Desktop (Apple Silicon) =="
if ! command -v docker &> /dev/null; then
  echo "Docker not found. Please install Docker Desktop for Mac (Apple Silicon)."
else
  echo "Docker found at $(which docker)."
fi

echo "\n== PyTorch MPS backend check =="
python - << 'EOF'
import torch
print("MPS available:", torch.backends.mps.is_available())
EOF

echo "\nLocal environment setup complete."
