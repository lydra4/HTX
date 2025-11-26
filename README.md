# HTX - Media Intelligence Platform

HTX is a comprehensive media intelligence platform that enables video and audio processing, transcription, and semantic search capabilities. The platform consists of a FastAPI backend for media processing and a React/TypeScript frontend for user interaction.

## Features

- **Video Processing**: Upload and process video files with frame extraction and analysis
- **Audio Processing**: Extract and process audio from video files
- **Transcription**: Generate transcriptions from audio content
- **Semantic Search**: Search through video content using embeddings and semantic similarity
- **Embeddings Generation**: Create vector embeddings for searchable content
- **RESTful API**: FastAPI backend with comprehensive API endpoints
- **Modern Frontend**: React/TypeScript frontend with Vite

## Prerequisites

- Python 3.12.0
- Node.js (for frontend development)
- FFmpeg (for video/audio processing)
- Conda (recommended for environment management)

## Installation

### Linux

1. **Install system dependencies:**

```bash
sudo apt-get update && sudo apt-get install -y libgl1-mesa-glx libglib2.0-0 libsm6 libxrender1 libxext6 ffmpeg
```

2. **Create and activate conda environment:**

```bash
conda env create -f env.yaml
conda activate htx
```

   The Python dependencies are automatically installed via the conda environment.

3. **Install frontend dependencies:**

```bash
cd frontend
npm install
cd ..
```

### macOS

1. **Install system dependencies using Homebrew:**

```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install required libraries
brew install ffmpeg
brew install libgl libglib libsm libxrender libxext
```

2. **Create and activate conda environment:**

```bash
conda env create -f env.yaml
conda activate htx
```

   The Python dependencies are automatically installed via the conda environment.

3. **Install frontend dependencies:**

```bash
cd frontend
npm install
cd ..
```

### Windows

1. **Install FFmpeg:**

   - Download FFmpeg from [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)
   - Extract and add to your system PATH
   - Or use Chocolatey: `choco install ffmpeg`

2. **Note on OpenCV dependencies:**

   On Windows, OpenCV typically bundles its dependencies, so additional system libraries are not required. However, if you encounter issues, you may need to install Visual C++ Redistributables.

3. **Create and activate conda environment:**

```bash
conda env create -f env.yaml
conda activate htx
```

   The Python dependencies are automatically installed via the conda environment.

4. **Install frontend dependencies:**

```bash
cd frontend
npm install
cd ..
```

## Usage

### Backend

1. **Start the backend server:**

```bash
python src/backend_app.py
```

The API will be available at `http://localhost:8000` (default). API documentation is available at `http://localhost:8000/`.

### Frontend

1. **Start the development server:**

```bash
cd frontend
npm run dev
```

The frontend will be available at `http://localhost:5173` (default Vite port).

### Extraction Pipeline

To extract and process media files:

```bash
python src/extract.py
```

### Generate Embeddings

To generate embeddings for searchable content:

```bash
python src/generate_embeddings.py
```

## Project Structure

```
HTX/
├── backend/              # FastAPI backend application
│   ├── routes/          # API route handlers
│   ├── services/        # Business logic services
│   ├── models.py        # Database models
│   ├── schemas.py       # Pydantic schemas
│   └── app.py           # FastAPI app factory
├── frontend/            # React/TypeScript frontend
│   ├── src/
│   │   ├── components/  # React components
│   │   └── api/         # API client
│   └── package.json
├── src/                 # Core processing scripts
│   ├── extraction/      # Extraction pipeline
│   ├── embeddings/      # Embeddings generation
│   └── utils/           # Utility functions
├── config/              # Configuration files (Hydra)
├── docker/              # Docker configuration
├── requirements-prod.txt    # Production dependencies
├── requirements-dev.txt    # Development dependencies
└── env.yaml             # Conda environment file
```

## Development

### Running Tests

**Backend tests:**

```bash
pytest backend/tests/
```

**Frontend tests:**

```bash
cd frontend
npm test
```

### Code Quality

The project uses:
- `black` for code formatting
- `ruff` for linting
- `mypy` for type checking
- `pre-commit` hooks

Install pre-commit hooks:

```bash
pre-commit install
```

## Docker

Docker configurations are available in the `docker/` directory. Build and run using:

```bash
docker build -f docker/htx.Dockerfile -t htx:latest .
```

## Configuration

Configuration files are managed using Hydra and located in the `config/` directory:
- `backend_app.yaml` - Backend application configuration
- `extract_config.yaml` - Extraction pipeline configuration
- `generate_embeddings.yaml` - Embeddings generation configuration
- `logging.yaml` - Logging configuration

