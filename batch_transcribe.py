#!/usr/bin/env python3
"""
Batch MP3 Transcription using OpenAI Whisper
Optimized for processing large numbers of files
"""

import os
import sys
from pathlib import Path
import whisper
from tqdm import tqdm


def main():
    sounds_dir = Path("/Users/martin/Desktop/yt/py_transcript/sounds")

    # Find all MP3 files recursively
    mp3_files = list(sounds_dir.rglob("*.mp3"))

    # Filter out files that already have transcriptions
    files_to_process = []
    for mp3 in mp3_files:
        txt_file = mp3.with_suffix(".txt")
        if not txt_file.exists():
            files_to_process.append(mp3)

    print(f"Found {len(mp3_files)} MP3 files total")
    print(f"Files to process (no existing .txt): {len(files_to_process)}")

    if not files_to_process:
        print("All files already have transcriptions!")
        return

    # Load model once (small model = good balance of speed and accuracy)
    print("\nLoading Whisper model: small")
    model = whisper.load_model("small")
    print("Model loaded!\n")

    # Process files with progress bar
    successful = 0
    failed = 0

    for mp3_file in tqdm(files_to_process, desc="Transcribing", unit="file"):
        txt_file = mp3_file.with_suffix(".txt")

        try:
            # Transcribe with English language setting
            result = model.transcribe(
                str(mp3_file),
                language="en",
                task="transcribe",
                verbose=False
            )

            # Save transcription
            with open(txt_file, "w", encoding="utf-8") as f:
                f.write(result["text"].strip())

            successful += 1

        except Exception as e:
            print(f"\nError processing {mp3_file.name}: {e}")
            failed += 1

    print(f"\n\nCompleted!")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")


if __name__ == "__main__":
    main()
