import argparse
import subprocess
from typing import Sequence

DEFAULT_SERVED_MODEL_NAME = "qwen-7b"


def build_vllm_command(
    model_path: str,
    gpu_memory_utilization: float = 0.85,
    max_model_len: int = 8192,
    port: int = 8000,
) -> list[str]:
    return [
        "python",
        "-m",
        "vllm.entrypoints.openai.api_server",
        "--model",
        model_path,
        "--served-model-name",
        DEFAULT_SERVED_MODEL_NAME,
        "--gpu-memory-utilization",
        str(gpu_memory_utilization),
        "--max-model-len",
        str(max_model_len),
        "--port",
        str(port),
        "--host",
        "0.0.0.0",
        "--dtype",
        "half",
        "--enforce-eager",
        "--cpu-offload-gb",
        "8",
    ]


def start_vllm_server(
    model_path: str,
    gpu_memory_utilization: float = 0.85,
    max_model_len: int = 8192,
    port: int = 8000,
    cwd: str | None = None,
) -> subprocess.Popen[bytes]:
    cmd = build_vllm_command(
        model_path=model_path,
        gpu_memory_utilization=gpu_memory_utilization,
        max_model_len=max_model_len,
        port=port,
    )
    return subprocess.Popen(cmd, cwd=cwd)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Start a local vLLM server")
    parser.add_argument("--model_path", required=True)
    parser.add_argument("--port", type=int, default=8000)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    start_vllm_server(model_path=args.model_path, port=args.port)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
