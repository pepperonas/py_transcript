# MP3 Batch Transcription

Batch transcription tool using OpenAI Whisper to convert MP3 audio files to text.

## Setup

```bash
# Create virtual environment
python3 -m venv venv

# Activate
source venv/bin/activate

# Install dependencies
pip install openai-whisper tqdm
```

## Usage

```bash
source venv/bin/activate
python batch_transcribe.py
```

The script will:
1. Find all `.mp3` files in the `sounds/` directory (recursively)
2. Skip files that already have a `.txt` transcription
3. Transcribe using Whisper "small" model (English)
4. Save transcriptions as `.txt` files next to each MP3

## Project Structure

```
py_transcript/
├── batch_transcribe.py   # Main transcription script
├── venv/                 # Python virtual environment
└── sounds/               # MP3 files organized in subdirectories
    ├── OMNI/
    ├── caller/
    ├── effects/
    ├── games/
    └── ...
```

## Requirements

- Python 3.8+
- openai-whisper
- tqdm
- ffmpeg (required by Whisper)
