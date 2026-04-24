#!/usr/bin/env python3
import subprocess
import os
import argparse
import time
import signal
import sys


def check_model_path(model_path: str) -> bool:
    if os.path.exists(model_path):
        return True
    return False


def download_model(model_name: str, output_path: str):
    print(f"Downloading model {model_name} to {output_path}...")
    cmd = [
        "huggingface-cli", "download",
        model_name,
        "--local-dir", output_path,
        "--local-dir-use-symlinks", "False"
    ]
    subprocess.run(cmd)


def start_vllm_server(
    model_path: str,
    gpu_memory_utilization: float = 0.85,
    max_model_len: int = 8192,
    port: int = 8000,
    tensor_parallel_size: int = 1
):
    if not check_model_path(model_path):
        print(f"Model path {model_path} does not exist!")
        print("Please download the model first.")
        return False

    cmd = [
        sys.executable, "-m", "vllm.entrypoints.openai.api_server",
        "--model", model_path,
        "--served-model-name", "qwen-7b",
        "--gpu-memory-utilization", str(gpu_memory_utilization),
        "--max-model-len", str(max_model_len),
        "--port", str(port),
        "--host", "0.0.0.0",
        "--dtype", "half",
        "--enforce-eager",
        "--tensor-parallel-size", str(tensor_parallel_size),
    ]

    print(f"Starting vLLM server with command: {' '.join(cmd)}")
    print(f"Model: {model_path}")
    print(f"Port: {port}")

    env = os.environ.copy()
    proc = subprocess.Popen(cmd, env=env)

    def signal_handler(sig, frame):
        print("\nShutting down vLLM server...")
        proc.terminate()
        proc.wait()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    print("Waiting for server to start...")
    time.sleep(5)

    max_retries = 30
    for i in range(max_retries):
        try:
            import httpx
            resp = httpx.get(f"http://localhost:{port}/v1/models", timeout=5.0)
            if resp.status_code == 200:
                print(f"vLLM server is ready! Available at http://localhost:{port}")
                print(f"Model: {model_path}")
                proc.wait()
                return
        except Exception:
            pass
        time.sleep(2)
        print(f"Waiting... ({i+1}/{max_retries})")

    print("Server failed to start within timeout.")
    proc.terminate()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Start vLLM server')
    parser.add_argument('--model_path', type=str, required=True, help='Path to model')
    parser.add_argument('--port', type=int, default=8000, help='Server port')
    parser.add_argument('--gpu_memory_utilization', type=float, default=0.85, help='GPU memory utilization')
    parser.add_argument('--max_model_len', type=int, default=8192, help='Max model length')
    parser.add_argument('--tensor_parallel_size', type=int, default=1, help='Tensor parallel size')
    args = parser.parse_args()

    start_vllm_server(
        args.model_path,
        gpu_memory_utilization=args.gpu_memory_utilization,
        max_model_len=args.max_model_len,
        port=args.port,
        tensor_parallel_size=args.tensor_parallel_size
    )
