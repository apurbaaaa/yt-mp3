from datasets import load_dataset

ds = load_dataset("spktsagar/openslr-nepali-asr-cleaned", name="original", split="train[:10]", trust_remote_code=True)
print(f"Columns: {ds.column_names}")
print(f"Features: {ds.features}")
print(f"\nFirst example keys: {list(ds[0].keys())}")
for key in ds[0].keys():
    print(f"  {key}: {type(ds[0][key])} = {str(ds[0][key])[:100]}")
