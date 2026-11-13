#!/usr/bin/env python3
"""
Batch MP3 Transcription using OpenAI Whisper
Optimized for processing large numbers of files
"""

import sys
from pathlib import Path

# Default: the sounds/ directory next to this script (works for any clone location).
DEFAULT_SOUNDS_DIR = Path(__file__).resolve().parent / "sounds"


def find_pending(sounds_dir):
    """Return (all_mp3s, pending) where pending are MP3s without a sibling .txt.

    Both lists are sorted so runs are reproducible.
    """
    mp3_files = sorted(Path(sounds_dir).rglob("*.mp3"))
    pending = [mp3 for mp3 in mp3_files if not mp3.with_suffix(".txt").exists()]
    return mp3_files, pending


def transcribe_files(model, files, progress=lambda it: it):
    """Transcribe each file with ``model`` and write the text next to it.

    Returns (successful, failed). A failing file never aborts the batch and
    never leaves a half-written .txt behind (which would mark it as done).
    """
    successful = 0
    failed = 0

    for mp3_file in progress(files):
        txt_file = mp3_file.with_suffix(".txt")

        try:
            # Transcribe with English language setting
            result = model.transcribe(
                str(mp3_file),
                language="en",
                task="transcribe",
                verbose=False
            )

            # Extract first: a malformed result must not create an empty .txt,
            # which would mark the file as done on the next run.
            text = result["text"].strip()

            # Save transcription
            with open(txt_file, "w", encoding="utf-8") as f:
                f.write(text)

            successful += 1

        except Exception as e:
            print(f"\nError processing {mp3_file.name}: {e}")
            failed += 1

    return successful, failed


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    sounds_dir = Path(argv[0]) if argv else DEFAULT_SOUNDS_DIR

    mp3_files, files_to_process = find_pending(sounds_dir)

    print(f"Found {len(mp3_files)} MP3 files total")
    print(f"Files to process (no existing .txt): {len(files_to_process)}")

    if not files_to_process:
        print("All files already have transcriptions!")
        return

    # Heavy imports only when there is real work to do.
    import whisper
    from tqdm import tqdm

    # Load model once (small model = good balance of speed and accuracy)
    print("\nLoading Whisper model: small")
    model = whisper.load_model("small")
    print("Model loaded!\n")

    successful, failed = transcribe_files(
        model, files_to_process,
        progress=lambda it: tqdm(it, desc="Transcribing", unit="file"),
    )

    print(f"\n\nCompleted!")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")


if __name__ == "__main__":
    main()
