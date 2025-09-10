import os
import json
import torch
import whisper
from multiprocessing import Pool, cpu_count
from tqdm import tqdm

# ─── CONFIG ────────────────────────────────────────────────────────────────
INPUT_DIR     = "mp3_files"
OUTPUT_DIR    = "whisper_local"
MODEL_SIZE    = "medium"            # medium model for noisy audio
NUM_CPUS      = cpu_count() - 1 or 1   # leave one core free
# ────────────────────────────────────────────────────────────────────────────

model = None  # will be loaded in each worker/process

def init_model():
    """Load Whisper model once per process."""
    global model
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = whisper.load_model(MODEL_SIZE, device=device)
    if device == "cuda":
        model = model.to(device).half()

def transcribe_file(audio_path: str):
    """Transcribe a single file and write JSON out."""
    global model
    result = model.transcribe(
        audio_path,
        language="en",
        fp16=torch.cuda.is_available()
    )
    name = os.path.splitext(os.path.basename(audio_path))[0]
    out_path = os.path.join(OUTPUT_DIR, f"{name}.json")
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)
    return audio_path

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # collect audio files
    audio_files = [
        os.path.join(INPUT_DIR, fn)
        for fn in os.listdir(INPUT_DIR)
        if fn.lower().endswith((".mp3", ".wav", ".m4a", ".flac"))
    ]
    total = len(audio_files)

    # GPU path: sequential with progress bar
    if torch.cuda.is_available():
        init_model()
        for audio in tqdm(audio_files, desc="Transcribing (GPU)", unit="file"):
            transcribe_file(audio)

    # CPU path: parallel with progress bar
    else:
        with Pool(processes=NUM_CPUS, initializer=init_model) as pool:
            for _ in tqdm(
                pool.imap_unordered(transcribe_file, audio_files),
                total=total,
                desc="Transcribing (CPU)",
                unit="file"
            ):
                pass

if __name__ == "__main__":
    main()