import os
from pathlib import Path
import csv

import torch
import soundfile as sf
from tqdm import tqdm
from dotenv import load_dotenv

load_dotenv()

# ---- PyTorch / pyannote compatibility fixes ----
torch.serialization.add_safe_globals([type(lambda: None)])

_original_load = torch.load
def _patched_load(*args, **kwargs):
    kwargs["weights_only"] = False
    return _original_load(*args, **kwargs)
torch.load = _patched_load
# -----------------------------------------------

from pyannote.audio import Pipeline

# ---------------- CONFIG ----------------
SEG_DIR = Path("audio_segments_p3")
OUT_CSV = "speaker_segments.csv"

HF_TOKEN = os.environ.get("HF_TOKEN")
assert HF_TOKEN, "Set HF_TOKEN environment variable"

SAMPLE_RATE = 16000
# --------------------------------------


def main():
    pipeline = Pipeline.from_pretrained(
        "pyannote/speaker-diarization-community-1",
        token=HF_TOKEN,
    ).to(torch.device("mps"))

    rows = []

    wav_files = sorted(SEG_DIR.glob("*.wav"))
    assert wav_files, "No segment WAVs found"

    for wav_path in tqdm(wav_files):
        audio, sr = sf.read(wav_path)

        if sr != SAMPLE_RATE:
            raise RuntimeError(f"{wav_path.name} has sr={sr}")

        if audio.ndim == 2:
            audio = audio.mean(axis=1)

        waveform = torch.from_numpy(audio).float().unsqueeze(0)

        diarization = pipeline(
            {
                "waveform": waveform,
                "sample_rate": SAMPLE_RATE,
            }
        )

        # Get annotation object
        annotation = (
            diarization.speaker_diarization
            if hasattr(diarization, "speaker_diarization")
            else diarization
        )

        segment_id = wav_path.stem

        # map pyannote speaker labels → segment-local speaker IDs
        speaker_map = {}
        speaker_counter = 1

        for turn, _, speaker in annotation.itertracks(yield_label=True):
            if speaker not in speaker_map:
                speaker_map[speaker] = (
                    f"{segment_id}speaker{speaker_counter:02d}"
                )
                speaker_counter += 1

            rows.append({
                "segmentid": segment_id,
                "segmentspeakerid": speaker_map[speaker],
                "start": turn.start,
                "end": turn.end,
            })

    with open(OUT_CSV, "w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["segmentid", "segmentspeakerid", "start", "end"]
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"Phase 4 complete: wrote {len(rows)} diarization rows to {OUT_CSV}")


if __name__ == "__main__":
    main()
