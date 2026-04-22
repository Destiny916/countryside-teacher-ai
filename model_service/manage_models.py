#!/usr/bin/env python3
import os
import sys
import argparse
import subprocess
from pathlib import Path


def get_python_env():
    venv_python = Path(__file__).parent.parent / ".conda" / "bin" / "python"
    if venv_python.exists():
        return str(venv_python)
    return sys.executable


def start_vllm_for_qwen(model_path: str, port: int = 8000, gpu_memory_utilization: float = 0.85):
    python = get_python_env()

    cmd = [
        python, "-m", "vllm.entrypoints.openai.api_server",
        "--model", model_path,
        "--served-model-name", "qwen-7b",
        "--gpu-memory-utilization", str(gpu_memory_utilization),
        "--max-model-len", "8192",
        "--port", str(port),
        "--host", "0.0.0.0",
        "--dtype", "half",
        "--enforce-eager",
        "--tensor-parallel-size", "1",
    ]

    print(f"Starting vLLM server for Qwen2.5-7B...")
    print(f"Command: {' '.join(cmd)}")
    print(f"Model path: {model_path}")
    print(f"Port: {port}")

    env = os.environ.copy()
    proc = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

    print("vLLM server starting, waiting for model to load...")
    print("This may take several minutes for the first load...")

    import time
    import httpx

    for i in range(60):
        try:
            resp = httpx.get(f"http://localhost:{port}/v1/models", timeout=5.0)
            if resp.status_code == 200:
                print(f"\n✓ vLLM server is ready!")
                print(f"  API available at: http://localhost:{port}")
                print(f"  Chat endpoint: http://localhost:{port}/v1/chat/completions")
                return proc
        except Exception:
            pass
        time.sleep(5)
        if i % 6 == 0:
            print(f"  Still loading... ({i*5}s elapsed)")

    print("Server may still be starting, check output below:")
    for line in iter(proc.stdout.readline, ''):
        if line:
            print(line.strip())

    return proc


def start_sensevoice(model_path: str = None):
    from app.core.asr_handler import ASRHandler

    if model_path:
        os.environ['ASR_MODEL_PATH'] = model_path

    handler = ASRHandler()
    print("Initializing SenseVoice ASR model...")
    handler.initialize()
    print("✓ SenseVoice ASR model loaded successfully")
    return handler


def start_cosyvoice(model_path: str = None):
    from app.core.tts_handler import TTSHandler

    if model_path:
        os.environ['TTS_MODEL_PATH'] = model_path

    handler = TTSHandler()
    print("Initializing CosyVoice TTS model...")
    handler.initialize()
    print("✓ CosyVoice TTS model loaded successfully")
    return handler


def start_embedding_model(model_path: str = None):
    from langchain_community.embeddings import HuggingFaceEmbeddings

    if model_path is None:
        model_path = str(Path(__file__).parent.parent / "models" / "embedding")

    print(f"Loading embedding model from {model_path}...")
    embeddings = HuggingFaceEmbeddings(
        model_name=model_path,
        model_kwargs={'device': 'cpu'}
    )
    print("✓ Embedding model loaded successfully")
    return embeddings


def check_model_status():
    print("Checking model status...")
    models_dir = Path(__file__).parent.parent / "models"

    model_status = []

    qwen_path = models_dir / "qwen-7b"
    if qwen_path.exists() and any(qwen_path.iterdir()):
        model_status.append(("Qwen2.5-7B", True, str(qwen_path)))
    else:
        model_status.append(("Qwen2.5-7B", False, str(qwen_path)))

    sensevoice_path = models_dir / "sensevoice"
    if sensevoice_path.exists() and any(sensevoice_path.iterdir()):
        model_status.append(("SenseVoice", True, str(sensevoice_path)))
    else:
        model_status.append(("SenseVoice", False, str(sensevoice_path)))

    cosyvoice_path = models_dir / "cosyvoice"
    if cosyvoice_path.exists() and any(cosyvoice_path.iterdir()):
        model_status.append(("CosyVoice", True, str(cosyvoice_path)))
    else:
        model_status.append(("CosyVoice", False, str(cosyvoice_path)))

    embedding_path = models_dir / "embedding"
    if embedding_path.exists() and any(embedding_path.iterdir()):
        model_status.append(("Embedding", True, str(embedding_path)))
    else:
        model_status.append(("Embedding", False, str(embedding_path)))

    print("\nModel Status:")
    print("-" * 60)
    for name, status, path in model_status:
        icon = "✓" if status else "✗"
        print(f"  [{icon}] {name}: {path}")

    return model_status


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Manage models for village teacher assistant')
    parser.add_argument('--check', action='store_true', help='Check model status')
    parser.add_argument('--download', type=str, choices=['qwen', 'sensevoice', 'cosyvoice', 'embedding', 'all'],
                        default='all', help='Download models')
    parser.add_argument('--start-vllm', action='store_true', help='Start vLLM server')
    parser.add_argument('--model-path', type=str, help='Path to Qwen model')
    parser.add_argument('--port', type=int, default=8000, help='vLLM server port')
    args = parser.parse_args()

    if args.check:
        check_model_status()
    else:
        check_model_status()
