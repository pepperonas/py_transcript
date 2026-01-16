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

## Dependencies

- openai-whisper
- tqdm
