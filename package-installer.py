import subprocess
import sys

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", *package.split()])

# List of required packages
required_packages = [
    "PyQt5==5.15.7",
    "pytube==15.0.0",
    "numpy==1.23.4",
    "pyaudio==0.2.13",
    "pyqtgraph==0.13.3",
    "PyQtWebEngine==5.15.7",
    "QWebEngineView"
]

# Check and install PyTorch separately with appropriate CUDA support
try:
    import torch
except ImportError:
    install("torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121")

# Check and install Whisper (OpenAI) directly from GitHub
try:
    import whisper
except ImportError:
    install("git+https://github.com/openai/whisper.git")

# Check and install other packages if necessary
for package in required_packages:
    try:
        __import__(package.split("==")[0])
    except ImportError:
        install(package)
