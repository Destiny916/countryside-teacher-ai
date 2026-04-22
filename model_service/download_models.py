#!/usr/bin/env python3
import os
import argparse
from pathlib import Path
from huggingface_hub import snapshot_download


MODELS = {
    "qwen": {
        "name": "Qwen/Qwen2.5-7B-Instruct",
        "description": "Qwen2.5-7B 大语言模型",
        "path": "models/qwen-7b"
    },
    "sensevoice": {
        "name": "iic/SenseVoiceSmall",
        "description": "SenseVoice 语音识别模型",
        "path": "models/sensevoice"
    },
    "cosyvoice": {
        "name": "FunAudioLLM/CosyVoice-300M",
        "description": "CosyVoice 语音合成模型",
        "path": "models/cosyvoice"
    },
    "embedding": {
        "name": "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        "description": "多语言embedding模型",
        "path": "models/embedding"
    }
}


def download_model(model_key: str, resume_download: bool = True):
    if model_key not in MODELS:
        print(f"Unknown model: {model_key}")
        print(f"Available models: {list(MODELS.keys())}")
        return False

    model_info = MODELS[model_key]
    model_name = model_info["name"]
    output_path = Path(__file__).parent.parent / model_info["path"]

    if output_path.exists() and any(output_path.iterdir()):
        print(f"Model already exists at {output_path}")
        response = input("Do you want to re-download? (y/N): ")
        if response.lower() != 'y':
            print("Skipping download.")
            return True

    print(f"Downloading {model_info['description']}...")
    print(f"Model: {model_name}")
    print(f"Output: {output_path}")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        snapshot_download(
            repo_id=model_name,
            local_dir=str(output_path),
            local_dir_use_symlinks=False,
            resume_download=resume_download
        )
        print(f"Download complete! Model saved to {output_path}")
        return True
    except Exception as e:
        print(f"Download failed: {e}")
        return False


def download_all(resume_download: bool = True):
    for model_key in MODELS:
        print(f"\n{'='*50}")
        print(f"Downloading {model_key}...")
        print('='*50)
        success = download_model(model_key, resume_download)
        if not success:
            print(f"Failed to download {model_key}, continuing with next...")


def list_models():
    print("Available models:")
    for key, info in MODELS.items():
        path = Path(__file__).parent.parent / info["path"]
        exists = "✓" if path.exists() and any(path.iterdir()) else "✗"
        print(f"  [{exists}] {key}: {info['description']}")
        print(f"       HuggingFace: {info['name']}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Download models for village teacher assistant')
    parser.add_argument('--model', type=str, choices=list(MODELS.keys()) + ['all'],
                        help='Model to download', default='all')
    parser.add_argument('--no-resume', action='store_true',
                        help='Start fresh download without resuming')
    args = parser.parse_args()

    resume = not args.no_resume

    if args.model == 'all':
        download_all(resume)
    else:
        download_model(args.model, resume)

    print("\n" + "="*50)
    print("Current model status:")
    list_models()
