import os
import yt_dlp

OUTPUT_DIR = "audio_small"
os.makedirs(OUTPUT_DIR, exist_ok=True)

YOUTUBE_URLS = [
    # "https://www.youtube.com/watch?v=wQUkAHs_-1M",
    # "https://www.youtube.com/watch?v=7aL7tKGvoyE",
    # "https://www.youtube.com/watch?v=rqgFNBX8KMg",
    # "https://www.youtube.com/watch?v=6KTz9aR4HnE",
    # "https://www.youtube.com/watch?v=m5AdVEW31KY",
    # "https://www.youtube.com/watch?v=hRbRBes4YAY",
    # "https://www.youtube.com/watch?v=xD4n_RSWjwo",
    # "https://www.youtube.com/watch?v=2UUeAIjmU7w",
    # "https://www.youtube.com/watch?v=_E28SKoAyIc",
    # "https://www.youtube.com/watch?v=pvYRilq_M2w",
    # "http://youtube.com/watch?v=E6DwHnQubag",
    # "https://www.youtube.com/watch?v=kyZE2AABkHo",
    # "https://www.youtube.com/shorts/2s-B7ZW0XJM",
    # "https://www.youtube.com/watch?v=wQUkAHs_-1M",
    # "https://www.youtube.com/watch?v=HfnjIJTnxsg",
    # "https://www.youtube.com/watch?v=H8ly868IocE",
    # "https://www.youtube.com/watch?v=sM4jakkRz2Q",
    # "https://www.youtube.com/watch?v=XkU_KxSV9Os",
    # "https://www.youtube.com/watch?v=BMqTMmkJjmI",
    # "https://www.youtube.com/watch?v=t5pmKbzR1r4",
    # "https://www.youtube.com/watch?v=M0UWfpAknWM",
    # "https://www.youtube.com/watch?v=Q5hCVCPMiQs",
    # "https://www.youtube.com/watch?v=dGlXDdBaSDc"
    # "https://www.youtube.com/watch?v=IwWPUL8MHi8",
    # "https://www.youtube.com/watch?v=I87GGs55pgU",
    # "https://www.youtube.com/watch?v=kLCUkQ3kHDk",
    # "https://www.youtube.com/watch?v=fFIfQJb9s-0",
    # "https://www.youtube.com/watch?v=yzvOJAvQPUk",
    # "https://www.youtube.com/watch?v=gbC66B8BBuc",
    # "https://www.youtube.com/watch?v=GAj-fv-NF_Q&",
    # "https://www.youtube.com/watch?v=cQyigImufIo",
    # "https://www.youtube.com/watch?v=2aQJ8NZFc1Q", 
    # "https://www.youtube.com/watch?v=fYUMmsfK-Ok",
    # "https://www.youtube.com/watch?v=faFx_3qoaVM",
    # "https://www.youtube.com/watch?v=oXbalSJZyVs"
    # "https://www.youtube.com/watch?v=1C-oG5_3w2w",
    # "https://www.youtube.com/watch?v=odhSsbd1ee4",
    # "https://www.youtube.com/watch?v=uzd5j-8w8hw",
    # "https://www.youtube.com/watch?v=QJd1sYMTMHE"




]

ydl_opts = {
    "format": "bestaudio/best",
    "outtmpl": os.path.join(OUTPUT_DIR, "%(id)s.%(ext)s"),  # SAFE filenames
    "postprocessors": [
        {
            "key": "FFmpegExtractAudio",
            "preferredcodec": "wav",
        }
    ],
    "postprocessor_args": [
        "-ar", "16000",        # Phase 1: sample rate
        "-ac", "1",            # Phase 1: mono
        "-sample_fmt", "s16",  # Phase 1: 16-bit PCM
    ],
    "prefer_ffmpeg": True,
    "quiet": False,
}

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    ydl.download(YOUTUBE_URLS)

print("Download + Phase 1 standardization complete.")
