import os
import yt_dlp

OUTPUT_DIR = "audio_small"
YOUTUBE_URLS = [
    "https://www.youtube.com/shorts/GxuMrM5o20Q"
]

os.makedirs(OUTPUT_DIR, exist_ok=True)

ydl_opts = {
    "format": "bestaudio/best",
    "outtmpl": os.path.join(OUTPUT_DIR, "%(title)s.%(ext)s"),
    "postprocessors": [
        {
            "key": "FFmpegExtractAudio",
            "preferredcodec": "opus",
            "preferredquality": "48",  # kbps
        }
    ],
}

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    ydl.download(YOUTUBE_URLS)
print("Download and conversion complete.")