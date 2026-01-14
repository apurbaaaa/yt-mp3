import subprocess
import os
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
from tqdm import tqdm

IN_DIR = Path("audio_small")
OUT_DIR = Path("audio_clean_p2")
OUT_DIR.mkdir(parents=True, exist_ok=True)

def clean_audio(wav_path: Path):
    out_path = OUT_DIR / wav_path.name

    cmd = [
        "ffmpeg",
        "-y",
        "-i", str(wav_path),
        "-af",
        (
            # Loudness normalization (speech-safe)
            "loudnorm=I=-16:LRA=11:TP=-1.5,"
            # Remove long silences only
            "silenceremove=start_periods=1:"
            "start_silence=0.8:"
            "start_threshold=-40dB,"
            # Background music + noise suppression
            "highpass=f=120,"          # remove rumble / music bass
            "lowpass=f=7500,"          # remove hiss
            "afftdn=nf=-25"            # very mild denoising
        ),
        "-ar", "16000",
        "-ac", "1",
        "-sample_fmt", "s16",
        str(out_path)
    ]

    subprocess.run(
        cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=True
    )

def main():
    wav_files = list(IN_DIR.glob("*.wav"))
    assert wav_files, "No WAV files found in audio_small/"

    workers = max(1, os.cpu_count() - 1)

    with ProcessPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(clean_audio, w) for w in wav_files]
        for _ in tqdm(as_completed(futures), total=len(futures)):
            pass

    print(f"Phase 2 complete: cleaned {len(wav_files)} files.")

if __name__ == "__main__":
    main()
