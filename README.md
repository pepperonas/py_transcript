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
python batch_transcribe.py              # uses sounds/ next to the script
python batch_transcribe.py /path/to/mp3s # or any other directory
```

The script will:
1. Find all `.mp3` files in the `sounds/` directory (or the given directory, recursively)
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

## Tests

The unit tests cover file discovery (recursion, skipping already transcribed
files, deterministic order) and the transcription loop (stripped UTF-8 output,
per-file error isolation, no empty `.txt` on a malformed result). Whisper is
never loaded: a fake model stands in for it, and `whisper`/`tqdm` are only
imported once there is real work to do.

```bash
python3 -m venv .venv-test
.venv-test/bin/pip install -r requirements-dev.txt
.venv-test/bin/python -m pytest -q
```

GitHub Actions runs the same suite on every push (`.github/workflows/tests.yml`).

## Requirements

- Python 3.8+
- openai-whisper
- tqdm
- ffmpeg (required by Whisper)
