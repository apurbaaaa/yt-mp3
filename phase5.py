import os
from pathlib import Path
import pandas as pd
import soundfile as sf
import base64
import time
from tqdm import tqdm
from dotenv import load_dotenv

from google import genai
from google.genai import types

def transcribe(audio_bytes: bytes) -> str:
    response = client.models.generate_content(
        model="models/gemini-2.5-flash",
        contents=[
            "Transcribe the following audio accurately. "
            "The speech may contain Nepali and English code-switching, use nepali letters format for nepali words and english for english words. "
            "Return only the transcription text.",
            types.Part.from_bytes(
                data=audio_bytes,
                mime_type="audio/wav",
            ),
        ],
    )
    if response and response.text:
        return response.text.strip()
    return ""


# ---------------- CONFIG ----------------
SEG_DIR = Path("audio_segments_p3")
OUT_CSV = "segment_transcripts_gemini.csv"

MODEL_ID = "models/gemini-2.5-flash"
SAMPLE_RATE = 16000
RATE_LIMIT_DELAY = 7  # seconds between requests to avoid rate limit
SKIP_FILES = 628 # Skip first N files
MAX_FILES = 1000  # Number of audio files to transcribe after skip
APPEND_MODE = True  # Append to existing CSV instead of overwriting
# --------------------------------------

load_dotenv()
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
assert GEMINI_API_KEY, "GEMINI_API_KEY not set"

client = genai.Client(api_key=GEMINI_API_KEY)

def load_audio_bytes(wav_path: Path) -> bytes:
    """Load WAV file and return as bytes"""
    with open(wav_path, 'rb') as f:
        return f.read()






def main():
    # Get all WAV files from the directory
    all_wav_files = sorted(SEG_DIR.glob("*.wav"))
    wav_files = all_wav_files[SKIP_FILES:SKIP_FILES + MAX_FILES]
    
    if not wav_files:
        print(f"No WAV files found in {SEG_DIR} (skipping first {SKIP_FILES})")
        return
    
    print(f"Processing files {SKIP_FILES+1} to {SKIP_FILES+len(wav_files)} (total: {len(wav_files)} files)")
    
    rows = []

    for idx, wav_path in enumerate(tqdm(wav_files, desc="Transcribing")):
        segment_id = wav_path.stem  # filename without extension

        try:
            audio_bytes = load_audio_bytes(wav_path)
            text = transcribe(audio_bytes)
            
            # Rate limiting: wait between requests
            if idx < len(wav_files) - 1:  # Don't wait after the last request
                time.sleep(RATE_LIMIT_DELAY)
                
        except Exception as e:
            print(f"\nFailed on {segment_id}: {e}")
            continue

        rows.append({
            "segmentid": segment_id,
            "text": text,
        })

    out_df = pd.DataFrame(rows)
    
    # Append to existing CSV or create new one
    if APPEND_MODE and Path(OUT_CSV).exists():
        existing_df = pd.read_csv(OUT_CSV)
        out_df = pd.concat([existing_df, out_df], ignore_index=True)
        print(f"Appended {len(rows)} new rows to existing {OUT_CSV}")
    
    out_df.to_csv(OUT_CSV, index=False)

    print(f"\nPhase 5 complete: wrote {len(out_df)} total rows to {OUT_CSV}")


if __name__ == "__main__":
    main()

