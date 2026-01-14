import os
import wave

def get_audio_duration(file_path):
    """Get duration of WAV file in seconds"""
    try:
        with wave.open(file_path, 'r') as audio_file:
            frames = audio_file.getnframes()
            rate = audio_file.getframerate()
            duration = frames / float(rate)
            return duration
    except Exception as e:
        return None

def format_duration(seconds):
    """Format duration as MM:SS"""
    if seconds is None:
        return "ERROR"
    mins = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{mins:02d}:{secs:02d}"

dir1 = 'audio_small'
dir2 = 'audio_clean_p2'

files1 = {}
files2 = {}

print("Reading audio files from audio_small...")
for f in os.listdir(dir1):
    path = os.path.join(dir1, f)
    if os.path.isfile(path) and not f.startswith('.'):
        base = os.path.splitext(f)[0]
        duration = get_audio_duration(path)
        files1[base] = duration

print("Reading audio files from audio_clean_p2...")
for f in os.listdir(dir2):
    path = os.path.join(dir2, f)
    if os.path.isfile(path) and not f.startswith('.'):
        base = os.path.splitext(f)[0]
        duration = get_audio_duration(path)
        files2[base] = duration

common = set(files1.keys()) & set(files2.keys())

print(f'\nTotal files in audio_small: {len(files1)}')
print(f'Total files in audio_clean_p2: {len(files2)}')
print(f'Common files: {len(common)}')
print(f'\nFiles with different durations:\n')
print(f'{"File Name":<50} | {"audio_small":<12} | {"audio_clean_p2":<12} | {"Difference":<12}')
print('-' * 95)

count = 0
for base in sorted(common):
    dur1 = files1[base]
    dur2 = files2[base]
    
    if dur1 is not None and dur2 is not None:
        diff = abs(dur1 - dur2)
        if diff > 0.5:  # More than 0.5 seconds difference
            diff_str = f"{diff:.1f}s"
            print(f'{base[:50]:<50} | {format_duration(dur1):<12} | {format_duration(dur2):<12} | {diff_str:<12}')
            count += 1

print('-' * 95)
print(f'\nTotal files with different durations (>0.5s): {count}')
