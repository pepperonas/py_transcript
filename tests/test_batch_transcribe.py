"""Unit tests for batch_transcribe — Whisper is never imported or loaded."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import batch_transcribe as bt  # noqa: E402


class FakeModel:
    """Stands in for a Whisper model; records calls, returns canned results."""

    def __init__(self, results=None, fail_on=()):
        self.results = results or {}
        self.fail_on = set(fail_on)
        self.calls = []

    def transcribe(self, path, **kwargs):
        self.calls.append((path, kwargs))
        name = Path(path).name
        if name in self.fail_on:
            raise RuntimeError("boom")
        return self.results.get(name, {"text": f"  text of {name}  "})


def touch(path, content=""):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def test_module_import_does_not_load_whisper():
    assert "whisper" not in sys.modules


def test_default_sounds_dir_is_next_to_script():
    assert bt.DEFAULT_SOUNDS_DIR == Path(bt.__file__).resolve().parent / "sounds"


def test_find_pending_recurses_and_skips_transcribed(tmp_path):
    a = touch(tmp_path / "a.mp3")
    b = touch(tmp_path / "sub" / "deep" / "b.mp3")
    done = touch(tmp_path / "sub" / "done.mp3")
    touch(tmp_path / "sub" / "done.txt", "already")
    touch(tmp_path / "notes.txt")
    touch(tmp_path / "song.wav")

    all_mp3, pending = bt.find_pending(tmp_path)

    assert set(all_mp3) == {a, b, done}
    assert pending == sorted([a, b])


def test_find_pending_is_sorted_and_deterministic(tmp_path):
    for name in ["c.mp3", "a.mp3", "b.mp3"]:
        touch(tmp_path / name)
    _, pending = bt.find_pending(tmp_path)
    assert [p.name for p in pending] == ["a.mp3", "b.mp3", "c.mp3"]


def test_find_pending_txt_must_share_exact_stem(tmp_path):
    touch(tmp_path / "x.mp3")
    touch(tmp_path / "x.mp3.txt")  # not the expected sibling name
    _, pending = bt.find_pending(tmp_path)
    assert [p.name for p in pending] == ["x.mp3"]


def test_find_pending_empty_and_missing_dir(tmp_path):
    assert bt.find_pending(tmp_path) == ([], [])
    assert bt.find_pending(tmp_path / "does-not-exist") == ([], [])


def test_transcribe_writes_stripped_text_and_counts(tmp_path):
    f1 = touch(tmp_path / "one.mp3")
    f2 = touch(tmp_path / "two.mp3")
    model = FakeModel()

    ok, failed = bt.transcribe_files(model, [f1, f2])

    assert (ok, failed) == (2, 0)
    assert (tmp_path / "one.txt").read_text(encoding="utf-8") == "text of one.mp3"
    assert (tmp_path / "two.txt").read_text(encoding="utf-8") == "text of two.mp3"


def test_transcribe_uses_english_transcribe_task(tmp_path):
    f = touch(tmp_path / "one.mp3")
    model = FakeModel()
    bt.transcribe_files(model, [f])
    path, kwargs = model.calls[0]
    assert path == str(f)
    assert kwargs == {"language": "en", "task": "transcribe", "verbose": False}


def test_transcribe_failure_does_not_abort_batch(tmp_path, capsys):
    bad = touch(tmp_path / "bad.mp3")
    good = touch(tmp_path / "good.mp3")
    model = FakeModel(fail_on={"bad.mp3"})

    ok, failed = bt.transcribe_files(model, [bad, good])

    assert (ok, failed) == (1, 1)
    assert not (tmp_path / "bad.txt").exists()
    assert (tmp_path / "good.txt").exists()
    assert "bad.mp3" in capsys.readouterr().out


def test_malformed_result_leaves_no_empty_txt(tmp_path):
    """A result without 'text' must not create a .txt that marks the file done."""
    f = touch(tmp_path / "weird.mp3")
    model = FakeModel(results={"weird.mp3": {"segments": []}})

    ok, failed = bt.transcribe_files(model, [f])

    assert (ok, failed) == (0, 1)
    assert not (tmp_path / "weird.txt").exists()
    _, pending = bt.find_pending(tmp_path)
    assert pending == [f]


def test_unicode_text_is_written_as_utf8(tmp_path):
    f = touch(tmp_path / "u.mp3")
    model = FakeModel(results={"u.mp3": {"text": " Grüße – 你好 "}})
    bt.transcribe_files(model, [f])
    assert (tmp_path / "u.txt").read_bytes() == "Grüße – 你好".encode("utf-8")


def test_progress_wrapper_is_used(tmp_path):
    f = touch(tmp_path / "p.mp3")
    seen = []

    def progress(items):
        seen.append(list(items))
        return seen[-1]

    bt.transcribe_files(FakeModel(), [f], progress=progress)
    assert seen == [[f]]


def test_main_exits_early_without_importing_whisper(tmp_path, capsys):
    touch(tmp_path / "a.mp3")
    touch(tmp_path / "a.txt", "done")
    bt.main([str(tmp_path)])
    out = capsys.readouterr().out
    assert "Found 1 MP3 files total" in out
    assert "All files already have transcriptions!" in out
    assert "whisper" not in sys.modules


def test_main_loads_model_only_when_needed(tmp_path, monkeypatch, capsys):
    import types

    touch(tmp_path / "a.mp3")
    model = FakeModel()
    fake_whisper = types.SimpleNamespace(load_model=lambda name: model)
    fake_tqdm = types.SimpleNamespace(tqdm=lambda it, **kw: it)
    monkeypatch.setitem(sys.modules, "whisper", fake_whisper)
    monkeypatch.setitem(sys.modules, "tqdm", fake_tqdm)

    bt.main([str(tmp_path)])

    assert (tmp_path / "a.txt").read_text(encoding="utf-8") == "text of a.mp3"
    out = capsys.readouterr().out
    assert "Successful: 1" in out and "Failed: 0" in out
