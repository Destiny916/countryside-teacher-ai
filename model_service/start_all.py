#!/usr/bin/env python3
import os
import sys
import time
import signal
import subprocess
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.parent
VENV_PYTHON = SCRIPT_DIR / ".conda" / "bin" "python"

def get_python():
    if VENV_PYTHON.exists():
        return str(VENV_PYTHON)
    return sys.executable

class ModelServerManager:
    def __init__(self):
        self.processes = {}

    def check_vllm(self, port=8000):
        try:
            import httpx
            resp = httpx.get(f"http://localhost:{port}/v1/models", timeout=3.0)
            return resp.status_code == 200
        except:
            return False

    def start_vllm_server(self, model_path=None, port=8000):
        if model_path is None:
            model_path = str(SCRIPT_DIR / "models" / "qwen-7b")

        if not Path(model_path).exists():
            print(f"Error: Model path {model_path} does not exist!")
            print(f"Please download the model first using download_models.py")
            return False

        if self.check_vllm(port):
            print(f"vLLM server is already running on port {port}")
            return True

        print(f"Starting vLLM server...")
        print(f"  Model: {model_path}")
        print(f"  Port: {port}")
        print("  This may take a few minutes to load the model...")

        cmd = [
            get_python(), "-m", "vllm.entrypoints.openai.api_server",
            "--model", model_path,
            "--served-model-name", "qwen-7b",
            "--gpu-memory-utilization", "0.85",
            "--max-model-len", "8192",
            "--port", str(port),
            "--host", "0.0.0.0",
            "--dtype", "half",
        ]

        env = os.environ.copy()
        proc = subprocess.Popen(
            cmd,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )

        self.processes['vllm'] = proc

        print("Waiting for vLLM server to be ready...")
        for i in range(60):
            if self.check_vllm(port):
                print(f"\n✓ vLLM server is ready!")
                print(f"  API: http://localhost:{port}")
                print(f"  Chat: http://localhost:{port}/v1/chat/completions")
                return True

            time.sleep(3)
            sys.stdout.write(".")
            sys.stdout.flush()

        print("\nWarning: Server may still be loading. Check output below:")
        return False

    def stop_all(self):
        for name, proc in self.processes.items():
            print(f"Stopping {name}...")
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Start all model services')
    parser.add_argument('--skip-vllm', action='store_true', help='Skip vLLM server')
    parser.add_argument('--port', type=int, default=8000, help='vLLM port')
    parser.add_argument('--model-path', type=str, help='Qwen model path')
    args = parser.parse_args()

    manager = ModelServerManager()

    def signal_handler(sig, frame):
        print("\nShutting down...")
        manager.stop_all()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    if not args.skip_vllm:
        success = manager.start_vllm_server(args.model_path, args.port)
        if not success:
            print("\nNote: vLLM server may still be starting.")
            print("You can check its status with: curl http://localhost:{}/v1/models".format(args.port))

    print("\nModel services started!")
    print("Press Ctrl+C to stop all services.")

    while True:
        time.sleep(1)


if __name__ == "__main__":
    main()
