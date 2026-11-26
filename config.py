
from pathlib import Path

# Main project directory
BASE_DIR = Path(__file__).resolve().parent

# Project name
PROJECT_NAME = "Coursera Multimodal Intelligence Platform"

# Data directories
DATA_DIR = BASE_DIR / "data"
UPLOAD_DIR = DATA_DIR / "uploads"
PROCESSED_DIR = DATA_DIR / "processed"
FAISS_DIR = DATA_DIR / "vector_store"


# Create required folders automatically
DATA_DIR.mkdir(exist_ok=True)
UPLOAD_DIR.mkdir(exist_ok=True)
PROCESSED_DIR.mkdir(exist_ok=True)
FAISS_DIR.mkdir(exist_ok=True)
