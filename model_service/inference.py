import os
from typing import Any

try:
    import httpx
except ImportError:  # pragma: no cover - exercised when only injected clients are used
    httpx = None

DEFAULT_TIMEOUT = 300.0

_vllm_client: "VLLMClient | None" = None


def _get_env_host_port(host: str | None, port: int | None) -> tuple[str, int]:
    resolved_host = host or os.getenv("VLLM_HOST", "localhost")
    resolved_port = port if port is not None else int(os.getenv("VLLM_PORT", "8000"))
    return resolved_host, resolved_port


class VLLMClient:
    def __init__(self, host: str | None = None, port: int | None = None, client: Any | None = None):
        self.host, self.port = _get_env_host_port(host, port)
        self.base_url = f"http://{self.host}:{self.port}"
        owns_client = client is None
        if client is None:
            if httpx is None:
                raise ImportError("httpx is required to create the default VLLMClient")
            client = httpx.Client(timeout=DEFAULT_TIMEOUT)
        self.client = client
        self._owns_client = owns_client

    def generate(
        self,
        prompt: str,
        max_tokens: int = 2048,
        temperature: float = 0.7,
        top_p: float = 0.9,
        stop: list[str] | None = None,
        stream: bool = False,
    ) -> Any:
        response = self.client.post(
            f"{self.base_url}/generate",
            json={
                "prompt": prompt,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "top_p": top_p,
                "stop": stop or [],
                "stream": stream,
            },
        )
        response.raise_for_status()
        return response.json()

    def chat(
        self,
        messages: list[dict[str, Any]],
        max_tokens: int = 2048,
        temperature: float = 0.7,
        stream: bool = False,
    ) -> Any:
        response = self.client.post(
            f"{self.base_url}/v1/chat/completions",
            json={
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "stream": stream,
            },
        )
        response.raise_for_status()
        return response.json()

    def close(self) -> None:
        global _vllm_client
        if self._owns_client and hasattr(self.client, "close"):
            self.client.close()
        if _vllm_client is self:
            _vllm_client = None


def get_vllm_client(host: str | None = None, port: int | None = None) -> VLLMClient:
    global _vllm_client
    if _vllm_client is None:
        _vllm_client = VLLMClient(host=host, port=port)
    return _vllm_client
