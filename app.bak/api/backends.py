import os
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import httpx


class ModelBackend(ABC):
    @abstractmethod
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        pass

    @abstractmethod
    def is_available(self) -> bool:
        pass

    @abstractmethod
    def get_name(self) -> str:
        pass


class LocalVLLMBackend(ModelBackend):
    def __init__(
        self,
        host: str = None,
        port: int = None,
        model_name: str = "qwen-7b"
    ):
        self.host = host or os.getenv('VLLM_HOST', 'localhost')
        self.port = port or int(os.getenv('VLLM_PORT', 8000))
        self.model_name = model_name
        self.base_url = f"http://{self.host}:{self.port}"

    def get_name(self) -> str:
        return f"local_vllm_{self.model_name}"

    def is_available(self) -> bool:
        try:
            resp = httpx.get(f"{self.base_url}/v1/models", timeout=5.0)
            return resp.status_code == 200
        except:
            return False

    def chat(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        payload = {
            "messages": messages,
            "max_tokens": kwargs.get('max_tokens', 2048),
            "temperature": kwargs.get('temperature', 0.7),
            "top_p": kwargs.get('top_p', 0.9),
            "stream": kwargs.get('stream', False)
        }

        with httpx.Client(timeout=300.0) as client:
            response = client.post(
                f"{self.base_url}/v1/chat/completions",
                json=payload
            )
            response.raise_for_status()
            return response.json()


class RemoteOpenAIBackend(ModelBackend):
    def __init__(
        self,
        base_url: str = None,
        api_key: str = None,
        default_model: str = "z-ai/glm-5.1"
    ):
        self.base_url = base_url or os.getenv('OPENAI_BASE_URL', 'https://integrate.api.nvidia.com/v1')
        self.api_key = api_key or os.getenv('OPENAI_API_KEY', '')
        self.default_model = default_model

    def get_name(self) -> str:
        return f"remote_{self.default_model}"

    def is_available(self) -> bool:
        try:
            with httpx.Client(timeout=10.0) as client:
                resp = client.get(
                    f"{self.base_url}/models",
                    headers={"Authorization": f"Bearer {self.api_key}"}
                )
                return resp.status_code == 200
        except:
            return False

    def chat(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        from openai import OpenAI

        client = OpenAI(
            base_url=self.base_url,
            api_key=self.api_key
        )

        model = kwargs.get('model', self.default_model)
        extra_body = kwargs.get('extra_body', {})

        if kwargs.get('stream', False):
            return client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=kwargs.get('temperature', 1),
                top_p=kwargs.get('top_p', 1),
                max_tokens=kwargs.get('max_tokens', 16384),
                stream=True,
                extra_body=extra_body
            )
        else:
            return client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=kwargs.get('temperature', 1),
                top_p=kwargs.get('top_p', 1),
                max_tokens=kwargs.get('max_tokens', 16384),
                extra_body=extra_body
            )


class RemoteZhipuBackend(RemoteOpenAIBackend):
    def __init__(self, api_key: str = None):
        super().__init__(
            base_url="https://bigmodel.cn/api/paas/v4",
            api_key=api_key or os.getenv('ZHIPU_API_KEY', ''),
            default_model="glm-4"
        )


class RemoteDeepSeekBackend(RemoteOpenAIBackend):
    def __init__(self, api_key: str = None):
        super().__init__(
            base_url="https://api.deepseek.com/v1",
            api_key=api_key or os.getenv('DEEPSEEK_API_KEY', ''),
            default_model="deepseek-chat"
        )


class RemoteQianfanBackend(RemoteOpenAIBackend):
    def __init__(self, api_key: str = None, secret_key: str = None):
        super().__init__(
            base_url="https://qianfan.baidubce.com/v2",
            api_key=api_key or os.getenv('QIANFAN_API_KEY', ''),
            default_model="ernie-4.0-8k-latest"
        )
        self.secret_key = secret_key or os.getenv('QIANFAN_SECRET_KEY', '')


BACKEND_REGISTRY = {
    'local_vllm': LocalVLLMBackend,
    'remote_openai': RemoteOpenAIBackend,
    'remote_zhipu': RemoteZhipuBackend,
    'remote_deepseek': RemoteDeepSeekBackend,
    'remote_qianfan': RemoteQianfanBackend,
}


def create_backend(backend_type: str, **kwargs) -> ModelBackend:
    if backend_type not in BACKEND_REGISTRY:
        raise ValueError(f"Unknown backend type: {backend_type}")
    return BACKEND_REGISTRY[backend_type](**kwargs)
