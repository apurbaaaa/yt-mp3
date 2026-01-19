import pandas as pd
import re

df = pd.read_csv("segment_transcripts_gemini_nepali_clean.csv", encoding="utf-8")

pattern = re.compile(r'(?=.*[A-Za-z])(?=.*[\u0900-\u097F])')

words = (
    df["text"]
    .astype(str)
    .str.findall(r'\S+')
    .explode()
    .dropna()
    .unique()
)

mixed_words = [w for w in words if pattern.search(w)]

print(mixed_words)
