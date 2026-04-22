import httpx
from typing import Optional, List, Dict, Any
import os


class VLLMClient:
    def __init__(self, host: str = None, port: int = None):
        self.host = host or os.getenv('VLLM_HOST', 'localhost')
        self.port = port or int(os.getenv('VLLM_PORT', 8000))
        self.base_url = f"http://{self.host}:{self.port}"
        self.client = httpx.Client(timeout=300.0)

    def generate(
        self,
        prompt: str,
        max_tokens: int = 2048,
        temperature: float = 0.7,
        top_p: float = 0.9,
        stop: Optional[List[str]] = None,
        stream: bool = False
    ) -> Dict[str, Any]:
        payload = {
            "prompt": prompt,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "stop": stop or [],
            "stream": stream
        }
        response = self.client.post(f"{self.base_url}/generate", json=payload)
        response.raise_for_status()
        return response.json()

    def chat(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 2048,
        temperature: float = 0.7,
        stream: bool = False
    ) -> Dict[str, Any]:
        payload = {
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": stream
        }
        response = self.client.post(f"{self.base_url}/v1/chat/completions", json=payload)
        response.raise_for_status()
        return response.json()

    def close(self):
        self.client.close()


_client = None


def get_vllm_client() -> VLLMClient:
    global _client
    if _client is None:
        _client = VLLMClient()
    return _client
