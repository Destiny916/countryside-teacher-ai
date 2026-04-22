import importlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload
        self.raise_for_status_called = False

    def raise_for_status(self):
        self.raise_for_status_called = True

    def json(self):
        return self.payload


class FakeHttpClient:
    def __init__(self):
        self.calls = []

    def post(self, url, json=None):
        response = FakeResponse({"url": url, "payload": json})
        self.calls.append((url, json, response))
        return response

    def close(self):
        self.closed = True


def test_vllm_client_generate_posts_expected_payload(monkeypatch):
    monkeypatch.setenv("VLLM_HOST", "127.0.0.1")
    monkeypatch.setenv("VLLM_PORT", "9000")

    from model_service.inference import VLLMClient

    fake_client = FakeHttpClient()
    client = VLLMClient(client=fake_client)

    result = client.generate(
        "hello",
        max_tokens=16,
        temperature=0.5,
        top_p=0.8,
        stop=["END"],
        stream=True,
    )

    assert fake_client.calls[0][0] == "http://127.0.0.1:9000/generate"
    assert fake_client.calls[0][1] == {
        "prompt": "hello",
        "max_tokens": 16,
        "temperature": 0.5,
        "top_p": 0.8,
        "stop": ["END"],
        "stream": True,
    }
    assert result["url"] == "http://127.0.0.1:9000/generate"
    assert result["payload"]["prompt"] == "hello"


def test_vllm_client_generate_defaults_stop_to_empty_list():
    from model_service.inference import VLLMClient

    fake_client = FakeHttpClient()
    client = VLLMClient(host="localhost", port=8000, client=fake_client)

    client.generate("hello")

    assert fake_client.calls[0][1]["stop"] == []


def test_vllm_client_chat_posts_expected_payload(monkeypatch):
    monkeypatch.setenv("VLLM_HOST", "localhost")
    monkeypatch.setenv("VLLM_PORT", "8000")

    from model_service.inference import VLLMClient

    fake_client = FakeHttpClient()
    client = VLLMClient(client=fake_client)

    result = client.chat(
        [{"role": "user", "content": "hi"}],
        max_tokens=32,
        temperature=0.3,
        stream=True,
    )

    assert fake_client.calls[0][0] == "http://localhost:8000/v1/chat/completions"
    assert fake_client.calls[0][1] == {
        "messages": [{"role": "user", "content": "hi"}],
        "max_tokens": 32,
        "temperature": 0.3,
        "stream": True,
    }
    assert result["url"].endswith("/v1/chat/completions")


def test_build_vllm_command_contains_expected_flags():
    from model_service.vllm_server import build_vllm_command

    cmd = build_vllm_command("/models/qwen", gpu_memory_utilization=0.85, max_model_len=8192, port=8000)

    assert cmd[:3] == ["python", "-m", "vllm.entrypoints.openai.api_server"]
    assert "--model" in cmd
    assert "/models/qwen" in cmd
    assert "--served-model-name" in cmd
    assert "qwen-7b" in cmd
    assert "--gpu-memory-utilization" in cmd
    assert "0.85" in cmd
    assert "--max-model-len" in cmd
    assert "8192" in cmd
    assert "--port" in cmd
    assert "8000" in cmd
    assert "--host" in cmd
    assert "0.0.0.0" in cmd
    assert "--dtype" in cmd
    assert "half" in cmd
    assert "--enforce-eager" in cmd
    assert "--cpu-offload-gb" in cmd
    assert "8" in cmd


def test_default_quant_config():
    from model_service.quantize import default_quant_config

    config = default_quant_config()

    assert config["zero_point"] is True
    assert config["q_group_size"] == 128
    assert config["w_bit"] == 4
    assert config["version"] == "GEMM"


def test_model_service_modules_import_without_heavy_dependencies():
    for module_name in [
        "model_service",
        "model_service.inference",
        "model_service.vllm_server",
        "model_service.quantize",
    ]:
        importlib.import_module(module_name)
