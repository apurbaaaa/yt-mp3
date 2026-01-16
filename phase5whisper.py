import os
from pathlib import Path
import pandas as pd
import soundfile as sf
from tqdm import tqdm
import torch

from transformers import AutoProcessor, AutoModelForSpeechSeq2Seq

# ---------------- CONFIG ----------------
SEG_DIR = Path("audio_segments_p3")
OUT_CSV = "segment_transcripts_whisper.csv"

MODEL_ID = "openai/whisper-large-v3"
SAMPLE_RATE = 16000
MAX_FILES = 10  # Number of audio files to transcribe
# --------------------------------------


def load_whisper():
    device = "cpu"

    print(device)

    dtype = torch.float16 if device != "cpu" else torch.float16

    processor = AutoProcessor.from_pretrained(MODEL_ID)
    model = AutoModelForSpeechSeq2Seq.from_pretrained(
        MODEL_ID,
        dtype=dtype,
        low_cpu_mem_usage=True,
    ).to(device)

    return processor, model, device


def transcribe_whisper(wav_path: Path, processor, model, device) -> str:
    audio, sr = sf.read(wav_path)

    if sr != SAMPLE_RATE:
        raise RuntimeError(f"{wav_path.name} has sr={sr}")

    if audio.ndim == 2:
        audio = audio.mean(axis=1)

    inputs = processor(
        audio,
        sampling_rate=SAMPLE_RATE,
        return_tensors="pt",
    )

    input_features = inputs.input_features.to(
        device,
        dtype=next(model.parameters()).dtype
    )


    with torch.no_grad():
        predicted_ids = model.generate(
            input_features,
            task="transcribe",
            language=None,   # allow Nepali–English code-switching
        )

    text = processor.batch_decode(
        predicted_ids,
        skip_special_tokens=True
    )[0]

    return text.strip()


def main():
    # Get all WAV files from the directory
    wav_files = sorted(SEG_DIR.glob("*.wav"))[:MAX_FILES]
    
    if not wav_files:
        print(f"No WAV files found in {SEG_DIR}")
        return
    
    print(f"Found {len(wav_files)} audio files to transcribe")
    
    processor, model, device = load_whisper()
    rows = []

    for wav_path in tqdm(wav_files, desc="Transcribing"):
        segment_id = wav_path.stem  # filename without extension

        try:
            text = transcribe_whisper(
                wav_path,
                processor,
                model,
                device,
            )
        except Exception as e:
            print(f"\nFailed on {segment_id}: {e}")
            continue

        rows.append({
            "segmentid": segment_id,
            "text": text,
        })

    out_df = pd.DataFrame(rows)
    out_df.to_csv(OUT_CSV, index=False)

    print(f"\nPhase 5 complete: wrote {len(out_df)} rows to {OUT_CSV}")


if __name__ == "__main__":
    main()
