"""
语音合成处理器
基于CosyVoice/GPT-SoVITS
"""
import os
from typing import Optional
import numpy as np
import base64
import io

class TTSHandler:
    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path or os.getenv('TTS_MODEL_PATH')
        self.model = None
        self._initialized = False

    def initialize(self):
        if self._initialized:
            return
        print(f"Loading TTS model from {self.model_path}...")
        try:
            from cosyvoice import CosyVoice
            self.model = CosyVoice(self.model_path)
        except ImportError:
            print("CosyVoice not available, using placeholder")
            self.model = None
        self._initialized = True

    def synthesize(
        self,
        text: str,
        speed: float = 0.9,
        voice: str = "female_tianmei"
    ) -> bytes:
        self.initialize()

        if self.model is None:
            return self._placeholder_audio()

        output = self.model.inference(text, speed=speed, stream=False)

        if hasattr(output, 'numpy'):
            audio_data = output.numpy()
        else:
            audio_data = np.array(output)

        wav_bytes = io.BytesIO()
        import scipy.io.wavfile as wavfile
        wavfile.write(wav_bytes, rate=24000, data=audio_data)

        return wav_bytes.getvalue()

    def synthesize_to_file(
        self,
        text: str,
        output_path: str,
        speed: float = 0.9
    ):
        audio_bytes = self.synthesize(text, speed=speed)
        with open(output_path, 'wb') as f:
            f.write(audio_bytes)

    def _placeholder_audio(self) -> bytes:
        import struct
        sample_rate = 24000
        duration = 0.1
        samples = int(sample_rate * duration)
        header = struct.pack('<4sI4s', b'RIFF', 36 + samples * 2, b'WAVE')
        fmt_chunk = struct.pack('<4sIHHIIHH', b'fmt ', 16, 1, 1, sample_rate, sample_rate * 2, 2, 16)
        data_header = struct.pack('<4sI', b'data', samples * 2)
        return header + fmt_chunk + data_header + b'\x00' * (samples * 2)

_tts_handler = None

def get_tts_handler() -> TTSHandler:
    global _tts_handler
    if _tts_handler is None:
        _tts_handler = TTSHandler()
    return _tts_handler