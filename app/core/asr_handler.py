"""
语音识别处理器
基于SenseVoice模型
"""
import os
from typing import Optional, BinaryIO
import numpy as np

class ASRHandler:
    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path or os.getenv('ASR_MODEL_PATH')
        self.model = None
        self._initialized = False

    def initialize(self):
        if self._initialized:
            return
        print(f"Loading ASR model from {self.model_path}...")
        from funasr import AutoModel
        self.model = AutoModel(
            model="iic/SenseVoiceSmall",
            model_revision="v2.0.4",
            device="cuda:0"
        )
        self._initialized = True

    def recognize(
        self,
        audio_data: bytes,
        language: str = "auto"
    ) -> str:
        self.initialize()

        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            f.write(audio_data)
            temp_path = f.name

        try:
            result = self.model.generate(
                input=temp_path,
                language=language,
                batch_size_s=300,
            )
            if result and len(result) > 0:
                return result[0].get("text", "")
            return ""
        finally:
            os.unlink(temp_path)

    def recognize_from_file(self, file_path: str, language: str = "auto") -> str:
        self.initialize()
        result = self.model.generate(
            input=file_path,
            language=language,
            batch_size_s=300,
        )
        if result and len(result) > 0:
            return result[0].get("text", "")
        return ""

_asr_handler = None

def get_asr_handler() -> ASRHandler:
    global _asr_handler
    if _asr_handler is None:
        _asr_handler = ASRHandler()
    return _asr_handler