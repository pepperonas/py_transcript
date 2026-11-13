# MP3 Batch Transcription Project

Batch transcription tool using OpenAI Whisper to convert MP3 audio files to text.

## Quick Start

```bash
# Activate virtual environment
source venv/bin/activate

# Run transcription
python batch_transcribe.py
```

## Project Structure

- `batch_transcribe.py` - Main script that transcribes all MP3 files in `sounds/`
- `venv/` - Python virtual environment with dependencies
- `sounds/` - Directory containing MP3 files organized in subdirectories

## How It Works

- Recursively finds all `.mp3` files in `sounds/`
- Skips files that already have a corresponding `.txt` file
- Uses Whisper "small" model (English language)
- Creates `.txt` files alongside each MP3 with the transcription

## Tests

`python -m pytest -q` (venv `.venv-test`, deps in `requirements-dev.txt`, CI in
`.github/workflows/tests.yml`). Tests never load Whisper — `whisper`/`tqdm` are
imported lazily inside `main()`; keep it that way or the suite needs torch.
The default sounds dir is `sounds/` next to the script (it used to be a
hard-coded `/Users/martin/Desktop/yt/...` path that no longer existed).

## Dependencies

- openai-whisper
- tqdm
