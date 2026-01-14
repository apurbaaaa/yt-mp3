import os
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed

import torch
import soundfile as sf
import numpy as np
from tqdm import tqdm

# ---------------- CONFIG ----------------
IN_DIR = Path("audio_clean_p2")
OUT_DIR = Path("audio_segments_p3")
OUT_DIR.mkdir(parents=True, exist_ok=True)

SAMPLE_RATE = 16000
MIN_SEG_SEC = 8.0
MAX_SEG_SEC = 25.0

VAD_THRESHOLD = 0.5
MERGE_GAP_SEC = 0.3
# ---------------------------------------


def load_vad():
    model, utils = torch.hub.load(
        repo_or_dir="snakers4/silero-vad",
        model="silero_vad",
        trust_repo=True
    )
    get_speech_timestamps = utils[0]
    return model, get_speech_timestamps


def merge_segments(timestamps):
    merged = []
    for t in timestamps:
        start, end = t["start"], t["end"]
        if not merged:
            merged.append([start, end])
        else:
            if start - merged[-1][1] <= int(MERGE_GAP_SEC * SAMPLE_RATE):
                merged[-1][1] = end
            else:
                merged.append([start, end])
    return [(s / SAMPLE_RATE, e / SAMPLE_RATE) for s, e in merged]


def chunk_segments(segments):
    chunks = []
    for s, e in segments:
        cur = s
        while cur < e:
            nxt = min(cur + MAX_SEG_SEC, e)
            if nxt - cur >= MIN_SEG_SEC:
                chunks.append((cur, nxt))
            cur = nxt
    return chunks


def process_file(wav_path: Path):
    audio, sr = sf.read(wav_path)

    if sr != SAMPLE_RATE:
        raise RuntimeError(f"{wav_path.name} has sr={sr}, expected {SAMPLE_RATE}")

    # mono
    if audio.ndim == 2:
        audio = audio.mean(axis=1)

    audio = torch.from_numpy(audio).float()

    model, get_speech_timestamps = load_vad()
    timestamps = get_speech_timestamps(
        audio,
        model,
        sampling_rate=SAMPLE_RATE,
        threshold=VAD_THRESHOLD,
    )

    merged = merge_segments(timestamps)
    chunks = chunk_segments(merged)

    base = wav_path.stem
    count = 0

    for i, (s, e) in enumerate(chunks):
        out_path = OUT_DIR / f"{base}_seg{i:03d}.wav"
        segment = audio[int(s * SAMPLE_RATE): int(e * SAMPLE_RATE)].numpy()
        sf.write(out_path, segment, SAMPLE_RATE)
        count += 1

    return count


def main():
    wav_files = list(IN_DIR.glob("*.wav"))
    assert wav_files, "No WAV files found in audio_clean_p2/"

    workers = max(1, os.cpu_count() - 1)
    total = 0

    with ProcessPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(process_file, w) for w in wav_files]
        for f in tqdm(as_completed(futures), total=len(futures)):
            total += f.result()

    print(f"Phase 3 complete: generated {total} segments.")


if __name__ == "__main__":
    main()
