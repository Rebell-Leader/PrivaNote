# Setup Guide for PrivaNote

## Dependencies Installation

### Method 1: Using uv (Recommended - Current Setup)
```bash
pip install uv
uv sync
```

### Method 2: Using pip (Alternative)
If you prefer to use pip, create a `requirements.txt` file with these dependencies:

```txt
# PrivaNote - Privacy-First AI Meeting Assistant
# Core dependencies

streamlit>=1.48.0
faster-whisper>=1.2.0
openai>=1.99.1
ollama>=0.5.2
pandas>=2.3.1
pydub>=0.25.1
torch>=2.8.0
torchaudio>=2.8.0
```

Then install with:
```bash
pip install -r requirements.txt
```

### Method 3: Direct pip installation
```bash
pip install streamlit>=1.48.0 faster-whisper>=1.2.0 openai>=1.99.1 ollama>=0.5.2 pandas>=2.3.1 pydub>=0.25.1 torch>=2.8.0 torchaudio>=2.8.0
```

## Additional Setup for GPU Support

If you have NVIDIA GPU and want CUDA acceleration:

```bash
# Uninstall CPU version first
pip uninstall torch torchaudio

# Install CUDA version
pip install torch>=2.8.0+cu121 torchaudio>=2.8.0+cu121 --index-url https://download.pytorch.org/whl/cu121
```

## Verifying Installation

Run this to check if everything is installed correctly:

```python
import streamlit as st
import faster_whisper
import openai
import ollama
import pandas as pd
import pydub
import torch
import torchaudio

print("✅ All dependencies installed successfully!")
print(f"PyTorch version: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")
```

## Environment Variables

Create a `.env` file (optional):
```bash
# For OpenAI cloud analysis
OPENAI_API_KEY=your_openai_api_key_here

# For custom Ollama host (optional)
OLLAMA_HOST=localhost:11434
```

## Running the Application

```bash
streamlit run app.py --server.port 5000
```

Then open: http://localhost:5000