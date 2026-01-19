import pandas as pd
import re
from unidecode import unidecode

INPUT = "segment_transcripts_gemini_nepali_clean.csv"
OUTPUT = "segment_transcripts_gemini_nepali_clean.csv"

# Mixed-script detector
MIXED = re.compile(r'(?=.*[A-Za-z])(?=.*[\u0900-\u097F])')

# Nepali suffixes
SUFFIXES = [
    "हरुसँग","हरुलाई","हरुको","हरु","लाई","को","मा","बाट","ले","सँग","कै","कि","मै","का"
]

# Punctuation
PUNCT = ".,?।"

# Minimal dictionary (high-value terms only)
DICT = {
    "AI": "एआई",
    "tech": "टेक",
    "technology": "टेक्नोलोजी",
    "bank": "बैंक",
    "business": "बिजनेस",
    "system": "सिस्टम",
    "level": "लेभल",
    "content": "कन्टेन्ट",
    "training": "ट्रेनिङ",
    "policy": "नीति",
    "company": "कम्पनी",
    "companies": "कम्पनीहरु",
    "exchange": "एक्सचेन्ज",
    "exchanges": "एक्सचेन्जहरु",
    "risk": "रिस्क",
    "risks": "रिस्कहरु",
    "thing": "थिङ",
    "things": "थिङ्स",
    "English": "इङ्लिस",
}

def strip_punct(token):
    pre = ""
    post = ""
    while token and token[0] in PUNCT:
        pre += token[0]
        token = token[1:]
    while token and token[-1] in PUNCT:
        post = token[-1] + post
        token = token[:-1]
    return pre, token, post

def transliterate_en(word):
    return "".join({
        "a":"अ","b":"ब","c":"क","d":"ड","e":"ए","f":"फ","g":"ग",
        "h":"ह","i":"इ","j":"ज","k":"क","l":"ल","m":"म","n":"न",
        "o":"ओ","p":"प","q":"क","r":"र","s":"स","t":"ट","u":"उ",
        "v":"भ","w":"व","x":"क्स","y":"य","z":"ज"
    }.get(ch.lower(), ch) for ch in word)

def normalize_token(token):
    if not MIXED.search(token):
        return token

    pre, core, post = strip_punct(token)

    for suf in SUFFIXES:
        if core.endswith(suf):
            base = core[:-len(suf)]
            ne = DICT.get(base.lower(), transliterate_en(base))
            return pre + ne + suf + post

    return token

def normalize_text(text):
    return " ".join(normalize_token(t) for t in text.split())

# Load and process CSV
df = pd.read_csv(INPUT, encoding="utf-8")

for col in df.columns:
    df[col] = df[col].astype(str).apply(normalize_text)

df.to_csv(OUTPUT, index=False, encoding="utf-8")

print("✅ All mixed words converted →", OUTPUT)
