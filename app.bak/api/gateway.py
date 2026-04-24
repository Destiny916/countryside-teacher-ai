import os
from typing import Dict, List, Any, Optional
from app.api.backends import (
    ModelBackend,
    create_backend,
    LocalVLLMBackend,
    RemoteOpenAIBackend,
    BACKEND_REGISTRY
)


class ModelGateway:
    def __init__(self):
        self.backends: Dict[str, ModelBackend] = {}
        self.primary_backend: Optional[str] = None
        self.fallback_backends: List[str] = []
        self._initialize_backends()

    def _initialize_backends(self):
        env_backend_type = os.getenv('DEFAULT_BACKEND', 'remote_nvidia')
        self._register_backend(env_backend_type, is_primary=True)

        all_backends = ['local_vllm', 'remote_nvidia', 'remote_zhipu', 'remote_deepseek', 'remote_qianfan']
        for backend_type in all_backends:
            if backend_type != env_backend_type:
                self._register_backend(backend_type, is_primary=False)

    def _register_backend(
        self,
        backend_type: str,
        is_primary: bool = False,
        **kwargs
    ) -> bool:
        try:
            if backend_type == 'local_vllm':
                backend = LocalVLLMBackend(
                    host=os.getenv('VLLM_HOST', 'localhost'),
                    port=int(os.getenv('VLLM_PORT', 8000)),
                    model_name=os.getenv('VLLM_MODEL_NAME', 'qwen-7b')
                )
            elif backend_type == 'remote_nvidia':
                backend = RemoteOpenAIBackend(
                    base_url=os.getenv('OPENAI_BASE_URL', 'https://integrate.api.nvidia.com/v1'),
                    api_key=os.getenv('OPENAI_API_KEY', ''),
                    default_model=os.getenv('NVIDIA_MODEL', 'z-ai/glm-5.1')
                )
            elif backend_type == 'remote_zhipu':
                backend = create_backend('remote_zhipu', api_key=kwargs.get('api_key'))
            elif backend_type == 'remote_deepseek':
                backend = create_backend('remote_deepseek', api_key=kwargs.get('api_key'))
            elif backend_type == 'remote_qianfan':
                backend = create_backend('remote_qianfan',
                    api_key=kwargs.get('api_key'),
                    secret_key=kwargs.get('secret_key'))
            else:
                backend = create_backend(backend_type, **kwargs)

            self.backends[backend_type] = backend

            if is_primary:
                self.primary_backend = backend_type

            return True
        except Exception as e:
            print(f"Failed to register backend {backend_type}: {e}")
            return False

    def set_primary_backend(self, backend_type: str) -> bool:
        if backend_type not in self.backends:
            if not self._register_backend(backend_type):
                return False

        if not self.backends[backend_type].is_available():
            return False

        self.primary_backend = backend_type
        return True

    def add_fallback(self, backend_type: str) -> bool:
        if backend_type not in self.backends:
            if not self._register_backend(backend_type):
                return False

        if backend_type not in self.fallback_backends:
            self.fallback_backends.append(backend_type)
        return True

    def remove_fallback(self, backend_type: str):
        if backend_type in self.fallback_backends:
            self.fallback_backends.remove(backend_type)

    def chat(
        self,
        messages: List[Dict[str, str]],
        backend_type: Optional[str] = None,
        use_fallback: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        if backend_type is None:
            backend_type = self.primary_backend

        if backend_type not in self.backends:
            raise ValueError(f"Backend {backend_type} not registered")

        backend = self.backends[backend_type]

        if not backend.is_available() and not use_fallback:
            raise RuntimeError(f"Backend {backend_type} is not available")

        if not backend.is_available() and use_fallback:
            for fallback_type in self.fallback_backends:
                if fallback_type in self.backends and self.backends[fallback_type].is_available():
                    print(f"Primary backend {backend_type} unavailable, using fallback {fallback_type}")
                    return self.backends[fallback_type].chat(messages, **kwargs)
            raise RuntimeError("No available backends")

        return backend.chat(messages, **kwargs)

    def get_status(self) -> Dict[str, Any]:
        status = {
            'primary': self.primary_backend,
            'fallbacks': self.fallback_backends,
            'backends': {}
        }

        for backend_type, backend in self.backends.items():
            try:
                is_available = backend.is_available()
            except:
                is_available = False

            status['backends'][backend_type] = {
                'name': backend.get_name(),
                'available': is_available,
                'is_primary': backend_type == self.primary_backend,
                'is_fallback': backend_type in self.fallback_backends
            }

        return status

    def list_available_backends(self) -> List[Dict[str, Any]]:
        result = []
        for backend_type, backend in self.backends.items():
            try:
                is_available = backend.is_available()
            except:
                is_available = False

            result.append({
                'type': backend_type,
                'name': backend.get_name(),
                'available': is_available
            })
        return result


_gateway = None


def get_model_gateway() -> ModelGateway:
    global _gateway
    if _gateway is None:
        _gateway = ModelGateway()
    return _gateway
