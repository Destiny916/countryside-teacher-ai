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


class NvidiaOpenAIClient:
    def __init__(self):
        self.api_key = os.getenv('NVIDIA_API_KEY', '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')
        self.base_url = os.getenv('NVIDIA_BASE_URL', 'https://integrate.api.nvidia.com/v1')
        self.model = os.getenv('NVIDIA_MODEL', 'z-ai/glm-5.1')
        self.client = httpx.Client(
            timeout=300.0,
            headers={
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
        )

    def chat(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 16384,
        temperature: float = 0.7,
        stream: bool = False
    ) -> Dict[str, Any]:
        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": 1.0,
            "stream": stream,
            "extra_body": {
                "chat_template_kwargs": {
                    "enable_thinking": True,
                    "clear_thinking": False
                }
            }
        }
        response = self.client.post(f"{self.base_url}/chat/completions", json=payload)
        response.raise_for_status()
        return response.json()

    def close(self):
        self.client.close()


class SiliconFlowOpenAIClient:
    def __init__(self):
        self.api_key = os.getenv('SILICON_FLOW_API_KEY', 'sk-czzpwrzncqygoqmwdtojcmmsfgwzdnoqgrruarzdcrfjzzgn')
        self.base_url = os.getenv('SILICON_FLOW_BASE_URL', 'https://api.siliconflow.cn/v1')
        self.model = os.getenv('SILICON_FLOW_MODEL', 'deepseekv3.2')
        self.client = httpx.Client(
            timeout=300.0,
            headers={
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
        )

    def chat(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 16384,
        temperature: float = 0.7,
        stream: bool = False
    ) -> Dict[str, Any]:
        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": 0.9,
            "stream": stream
        }
        response = self.client.post(f"{self.base_url}/chat/completions", json=payload)
        response.raise_for_status()
        return response.json()

    def close(self):
        self.client.close()


_client = None


def get_vllm_client() -> VLLMClient:
    global _client
    if _client is None:
        # 检查使用哪种API服务
        api_type = os.getenv('API_TYPE', 'local').lower()
        
        if api_type == 'nvidia':
            _client = NvidiaOpenAIClient()
        elif api_type == 'silicon_flow':
            _client = SiliconFlowOpenAIClient()
        else:
            _client = VLLMClient()
    return _client
