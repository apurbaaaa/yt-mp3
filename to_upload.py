import os
import sys
from typing import Optional

from datasets import Audio, DatasetDict, concatenate_datasets, load_dataset
from huggingface_hub import login


def get_token_from_env() -> Optional[str]:
	return (
		os.getenv("HUGGINGFACE_HUB_TOKEN")
		or os.getenv("HF_TOKEN")
		or os.getenv("HUGGINGFACE_TOKEN")
	)


def main():
	repo_id = os.getenv("HF_REPO_ID", "Crynl/Nep-Audio")

	token = get_token_from_env()
	try:
		if token:
			login(token=token)
		else:
			# Falls back to interactive login
			print("No token found in env; falling back to interactive login…")
			login()
	except Exception as e:
		print(f"Login failed: {e}")
		sys.exit(1)

	# Step 1: Load custom dataset from train.csv
	print("Loading custom dataset from train.csv…")
	custom_ds = load_dataset(
		"csv",
		data_files={"train": "train.csv"}
	)
	custom_ds = custom_ds.cast_column("audio", Audio(sampling_rate=16000))
	print(f"Custom dataset loaded: {len(custom_ds['train'])} samples")

	# Step 2: Load OpenSLR Nepali ASR dataset
	print("Loading OpenSLR Nepali ASR cleaned dataset…")
	openslr_dataset = load_dataset(
		"spktsagar/openslr-nepali-asr-cleaned",
		name="original",
		split="train",
		trust_remote_code=True
	)
	print(f"OpenSLR dataset loaded: {len(openslr_dataset)} samples")
	print(f"OpenSLR columns: {openslr_dataset.column_names}")

	# Step 3: Align OpenSLR schema to match custom dataset
	# OpenSLR has: utterance_id, speaker_id, utterance (Audio), transcription, num_frames
	# Custom has: audio, text
	# We need: audio, text
	print("Aligning column names…")
	openslr_dataset = openslr_dataset.rename_column('utterance', 'audio')
	openslr_dataset = openslr_dataset.rename_column('transcription', 'text')
	# Remove extra columns
	openslr_dataset = openslr_dataset.remove_columns(['utterance_id', 'speaker_id', 'num_frames'])
	print(f"OpenSLR columns after alignment: {openslr_dataset.column_names}")

	# Step 4: Combine both datasets (NO .map() call needed)
	print("Combining datasets…")
	combined_dataset = concatenate_datasets([custom_ds["train"], openslr_dataset])
	
	# Create final DatasetDict
	ds = DatasetDict({"train": combined_dataset})
	
	# Validation step (lightweight, no audio decode)
	print("\n" + "=" * 60)
	print("VALIDATION: Checking merged dataset")
	print("=" * 60)
	
	print(f"\nTotal samples: {len(ds['train']):,}")
	print(f"  - Custom dataset: {len(custom_ds['train']):,}")
	print(f"  - OpenSLR dataset: {len(openslr_dataset):,}")
	print(f"  - Sum: {len(custom_ds['train']) + len(openslr_dataset):,}")
	
	if len(ds['train']) != len(custom_ds['train']) + len(openslr_dataset):
		print("\n❌ ERROR: Sample count mismatch!")
		sys.exit(1)
	
	print(f"\nColumns: {ds['train'].column_names}")
	print("\nColumn types:")
	for col in ds['train'].column_names:
		print(f"  - {col}: {ds['train'].features[col]}")
	
	# Check schema only (no data iteration)
	if 'utterance' in ds['train'].column_names or 'transcription' in ds['train'].column_names:
		print("\n❌ ERROR: Old columns still present! Merge failed.")
		sys.exit(1)
	
	if 'audio' not in ds['train'].column_names or 'text' not in ds['train'].column_names:
		print("\n❌ ERROR: Required columns missing!")
		sys.exit(1)
	
	# Sample validation (only access metadata, not decoded audio)
	print("\nSample from custom data (index 0):")
	print(f"  Columns: {list(ds['train'][0].keys())}")
	print(f"  Text preview: {ds['train'][0]['text'][:80]}...")
	
	print(f"\nSample from OpenSLR data (index {len(custom_ds['train'])}):")
	print(f"  Columns: {list(ds['train'][len(custom_ds['train'])].keys())}")
	print(f"  Text preview: {ds['train'][len(custom_ds['train'])]['text'][:80]}...")
	
	print("\n✅ Validation passed! Dataset schema is correct.")
	print("=" * 60)
	
	# Confirm before uploading
	response = input(f"\nProceed with upload to {repo_id}? (y/n): ")
	if response.lower() != 'y':
		print("Upload cancelled.")
		sys.exit(0)
	
	print(f"\nUploading to {repo_id}… (this may take a while)")
	
	# Push directly to Hugging Face Hub
	ds.push_to_hub(
		repo_id=repo_id,
		commit_message="Upload combined dataset: custom data + OpenSLR Nepali ASR",
		private=False,
	)
	
	print(f"\n✅ Upload complete. Dataset available at: https://huggingface.co/datasets/{repo_id}")


if __name__ == "__main__":
	main()
