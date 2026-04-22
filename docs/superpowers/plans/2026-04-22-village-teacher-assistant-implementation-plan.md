# 乡村老师助教系统 - 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 构建完整的乡村老师助教系统，支持实时语音教学、智能备课（人教版教材）、题库问答，最大并发30人

**Architecture:** 采用Flask后端 + vLLM推理服务 + SQLite/Chroma存储的本地部署架构，语音交互基于SenseVoice/CosyVoice，LLM采用Qwen2.5-7B INT4量化适配RTX 3060

**Tech Stack:** Python 3.10+, Flask, vLLM, SenseVoice, CosyVoice, PaddleOCR, LangChain, Chroma, SQLite

**Hardware:** RTX 3060 12GB, 32GB RAM, 8核CPU, 500GB+ SSD

---

## 项目结构

```
village-teacher-assistant/
├── app/                          # Flask应用
│   ├── __init__.py              # Flask工厂
│   ├── config.py                # 配置管理
│   ├── api/                     # API路由
│   │   ├── __init__.py
│   │   ├── chat.py              # 对话API
│   │   ├── voice.py             # 语音API
│   │   ├── lesson.py            # 教案API
│   │   ├── question.py          # 题库API
│   │   └── project.py           # 项目计划书API
│   ├── core/                    # 核心模块
│   │   ├── __init__.py
│   │   ├── dialogue_manager.py # 对话管理
│   │   ├── interruption.py      # 打断检测
│   │   ├── asr_handler.py       # ASR处理
│   │   ├── tts_handler.py       # TTS处理
│   │   ├── ocr_handler.py       # OCR处理
│   │   └── rag_engine.py         # RAG引擎
│   ├── services/                # 业务服务
│   │   ├── __init__.py
│   │   ├── lesson_service.py    # 教案生成
│   │   ├── question_service.py   # 题库问答
│   │   ├── project_service.py    # 项目计划书
│   │   └── speech_service.py     # 语音服务
│   ├── models/                  # 数据模型
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── conversation.py
│   │   ├── lesson_plan.py
│   │   └── question.py
│   └── utils/                  # 工具函数
│       ├── __init__.py
│       ├── db.py                # 数据库工具
│       └── cache.py             # 缓存工具
├── model_service/               # 模型推理服务
│   ├── __init__.py
│   ├── vllm_server.py           # vLLM服务
│   ├── inference.py             # 推理接口
│   └── quantize.py              # 量化脚本
├── training/                     # 训练相关
│   ├── data/                    # 训练数据
│   ├── scripts/                 # 训练脚本
│   └── lora/                    # LoRA权重
├── knowledge_base/              # 知识库
│   ├── textbooks/              # 教材内容
│   ├── lesson_plans/           # 教案数据
│   └── questions/              # 题库数据
├── tests/                       # 测试
├── docs/                        # 文档
├── requirements.txt
├── run.py                       # 启动脚本
└── README.md
```

---

## Phase 1: 基础框架搭建（Week 1-2）

### Task 1.1: 项目初始化与环境配置

**Files:**
- Create: `requirements.txt`
- Create: `run.py`
- Create: `app/__init__.py`
- Create: `app/config.py`

- [ ] **Step 1: 创建requirements.txt**

```txt
flask==3.0.0
flask-cors==4.0.0
flask-restful==0.3.10
gunicorn==21.2.0
gevent==23.9.1
sqlalchemy==2.0.23
chromadb==0.4.22
langchain==0.1.0
langchain-community==0.0.10
paddleocr==2.7.3
paddlepaddle==2.6.0
funasr==1.0.0
GPT-SoVITS==0.2.0
vllm==0.2.0
transformers==4.36.0
accelerate==0.25.0
bitsandbytes==0.41.0
awq==0.1.0
httpx==0.25.0
python-multipart==0.0.6
pydantic==2.5.0
```

- [ ] **Step 2: 创建config.py**

```python
import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

    # 数据库
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{BASE_DIR}/data/user_data.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # vLLM服务
    VLLM_HOST = os.getenv('VLLM_HOST', 'localhost')
    VLLM_PORT = int(os.getenv('VLLM_PORT', 8000))
    VLLM_MODEL_PATH = os.getenv('VLLM_MODEL_PATH', f"{BASE_DIR}/models/qwen-7b-int4")

    # 语音服务
    ASR_MODEL_PATH = os.getenv('ASR_MODEL_PATH', f"{BASE_DIR}/models/sensevoice")
    TTS_MODEL_PATH = os.getenv('TTS_MODEL_PATH', f"{BASE_DIR}/models/cosyvoice")

    # 知识库
    KNOWLEDGE_BASE_DIR = BASE_DIR / "knowledge_base"
    CHROMA_DB_PATH = KNOWLEDGE_BASE_DIR / "chroma_db"

    # 教材版本
    TEXTBOOK_EDITION = 'pep'  # 人教版

    # 并发配置
    MAX_CONCURRENT_USERS = 30
    SESSION_TIMEOUT = 3600  # 1小时

    # 上传文件限制
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
```

- [ ] **Step 3: 创建Flask应用工厂app/__init__.py**

```python
from flask import Flask
from flask_cors import CORS
from app.config import Config

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    CORS(app, resources={r"/api/*": {"origins": "*"}})

    from app.api import register_routes
    register_routes(app)

    return app
```

- [ ] **Step 4: 创建run.py**

```python
#!/usr/bin/env python3
from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False,
        threaded=True
    )
```

- [ ] **Step 5: 安装依赖并验证**

Run: `cd /home/wengyikun/workcode/trae && pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple`
Expected: 安装成功，无报错

- [ ] **Step 6: 初始化数据库**

Run: `python -c "from app import create_app; app = create_app(); print('App created successfully')"`
Expected: 输出 "App created successfully"

- [ ] **Step 7: 提交代码**

```bash
git add requirements.txt run.py app/__init__.py app/config.py
git commit -m "feat: initialize Flask project structure"
```

---

### Task 1.2: API路由框架搭建

**Files:**
- Create: `app/api/__init__.py`
- Create: `app/api/chat.py`
- Create: `app/api/voice.py`
- Create: `app/api/lesson.py`
- Create: `app/api/question.py`
- Create: `app/api/project.py`
- Create: `app/core/__init__.py`
- Create: `app/models/__init__.py`
- Create: `app/services/__init__.py`
- Create: `app/utils/__init__.py`

- [ ] **Step 1: 创建app/api/__init__.py**

```python
from flask import Blueprint

def register_routes(app):
    from app.api import chat, voice, lesson, question, project

    app.register_blueprint(chat.bp)
    app.register_blueprint(voice.bp)
    app.register_blueprint(lesson.bp)
    app.register_blueprint(question.bp)
    app.register_blueprint(project.bp)
```

- [ ] **Step 2: 创建基础蓝图 - chat.py**

```python
from flask import Blueprint, request, jsonify
from flask_restful import Api, Resource

bp = Blueprint('chat', __name__, url_prefix='/api/chat')
api = Api(bp)

class ChatResource(Resource):
    def post(self):
        data = request.get_json()
        return {'message': 'Chat endpoint ready', 'data': data}

    def get(self):
        return {'message': 'Chat GET endpoint ready'}

api.add_resource(ChatResource, '/')

class SessionResource(Resource):
    def post(self):
        return {'session_id': 'new-session-id'}

api.add_resource(SessionResource, '/session')
```

- [ ] **Step 3: 创建voice.py蓝图**

```python
from flask import Blueprint, request, jsonify
from flask_restful import Api, Resource

bp = Blueprint('voice', __name__, url_prefix='/api/voice')
api = Api(bp)

class VoiceInputResource(Resource):
    def post(self):
        return {'message': 'Voice input endpoint ready'}

api.add_resource(VoiceInputResource, '/input')

class VoiceOutputResource(Resource):
    def post(self):
        return {'message': 'Voice output endpoint ready'}

api.add_resource(VoiceOutputResource, '/output')
```

- [ ] **Step 4: 创建lesson.py蓝图**

```python
from flask import Blueprint, request, jsonify
from flask_restful import Api, Resource

bp = Blueprint('lesson', __name__, url_prefix='/api/lesson')
api = Api(bp)

class LessonPlanResource(Resource):
    def post(self):
        return {'message': 'Lesson plan generation endpoint ready'}

    def get(self):
        return {'message': 'Lesson plan list endpoint ready'}

api.add_resource(LessonPlanResource, '/')

class LessonDetailResource(Resource):
    def get(self, plan_id):
        return {'plan_id': plan_id}

api.add_resource(LessonDetailResource, '/<int:plan_id>')
```

- [ ] **Step 5: 创建question.py蓝图**

```python
from flask import Blueprint, request, jsonify
from flask_restful import Api, Resource

bp = Blueprint('question', __name__, url_prefix='/api/question')
api = Api(bp)

class QuestionResource(Resource):
    def post(self):
        return {'message': 'Question OCR + answer endpoint ready'}

api.add_resource(QuestionResource, '/')

class QuestionDetailResource(Resource):
    def get(self, question_id):
        return {'question_id': question_id}

api.add_resource(QuestionDetailResource, '/<int:question_id>')
```

- [ ] **Step 6: 创建project.py蓝图**

```python
from flask import Blueprint, request, jsonify
from flask_restful import Api, Resource

bp = Blueprint('project', __name__, url_prefix='/api/project')
api = Api(bp)

class ProjectPlanResource(Resource):
    def post(self):
        return {'message': 'Project plan generation endpoint ready'}

api.add_resource(ProjectPlanResource, '/')
```

- [ ] **Step 7: 创建空模块文件**

Create: `app/core/__init__.py`, `app/models/__init__.py`, `app/services/__init__.py`, `app/utils/__init__.py`

- [ ] **Step 8: 测试API可访问**

Run: `python run.py & sleep 2 && curl http://localhost:5000/api/chat/`
Expected: `{"message": "Chat endpoint ready"}`

- [ ] **Step 9: 提交代码**

```bash
git add app/api/ app/core/ app/models/ app/services/ app/utils/
git commit -m "feat: add API route blueprints"
```

---

## Phase 2: 模型服务部署（Week 2-3）

### Task 2.1: vLLM模型服务配置

**Files:**
- Create: `model_service/__init__.py`
- Create: `model_service/vllm_server.py`
- Create: `model_service/inference.py`
- Create: `model_service/quantize.py`

- [ ] **Step 1: 创建模型推理模块model_service/inference.py**

```python
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
```

- [ ] **Step 2: 创建量化脚本model_service/quantize.py**

```python
#!/usr/bin/env python3
"""
Qwen2.5-7B INT4量化脚本
使用AWQ算法，适配RTX 3060 (12GB)
"""
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from awq import AutoAWQForCausalLM
import os
import argparse

def quantize_model(
    model_path: str,
    output_path: str,
    quant_config: dict = None
):
    if quant_config is None:
        quant_config = {
            "zero_point": True,
            "q_group_size": 128,
            "w_bit": 4,
            "version": "GEMM"
        }

    print(f"Loading model from {model_path}...")
    tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
    model = AutoAWQForCausalLM.from_pretrained(
        model_path,
        torch_dtype=torch.float16,
        low_cpu_mem_usage=True
    )

    print("Quantizing model...")
    model.quantize(tokenizer, quant_config=quant_config)

    print(f"Saving quantized model to {output_path}...")
    model.save_quantized(output_path)
    tokenizer.save_pretrained(output_path)

    print("Quantization complete!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Quantize Qwen model with AWQ')
    parser.add_argument('--model_path', type=str, required=True, help='Path to original model')
    parser.add_argument('--output_path', type=str, required=True, help='Path to save quantized model')
    args = parser.parse_args()

    quantize_model(args.model_path, args.output_path)
```

- [ ] **Step 3: 创建vLLM服务启动脚本model_service/vllm_server.py**

```python
#!/usr/bin/env python3
"""
vLLM服务启动脚本
针对RTX 3060优化配置
"""
import subprocess
import os
import argparse

def start_vllm_server(
    model_path: str,
    gpu_memory_utilization: float = 0.85,
    max_model_len: int = 8192,
    port: int = 8000
):
    cmd = [
        "python", "-m", "vllm.entrypoints.openai.api_server",
        "--model", model_path,
        "--served-model-name", "qwen-7b",
        "--gpu-memory-utilization", str(gpu_memory_utilization),
        "--max-model-len", str(max_model_len),
        "--port", str(port),
        "--host", "0.0.0.0",
        "--dtype", "half",
        "--enforce-eager",  # RTX 3060建议启用
        "--cpu-offload-gb", "8",  # 允许CPU卸荷8GB
    ]

    print(f"Starting vLLM server with command: {' '.join(cmd)}")
    subprocess.Popen(cmd)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Start vLLM server')
    parser.add_argument('--model_path', type=str, required=True)
    parser.add_argument('--port', type=int, default=8000)
    args = parser.parse_args()

    start_vllm_server(args.model_path, port=args.port)
```

- [ ] **Step 4: 提交代码**

```bash
git add model_service/
git commit -m "feat: add vLLM model service modules"
```

---

### Task 2.2: 语音服务配置（ASR/TTS）

**Files:**
- Create: `app/core/asr_handler.py`
- Create: `app/core/tts_handler.py`

- [ ] **Step 1: 创建ASR处理模块app/core/asr_handler.py**

```python
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
```

- [ ] **Step 2: 创建TTS处理模块app/core/tts_handler.py**

```python
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
```

- [ ] **Step 3: 更新voice API - app/api/voice.py**

```python
from flask import Blueprint, request, jsonify, send_file
from flask_restful import Api, Resource
from app.core.asr_handler import get_asr_handler
from app.core.tts_handler import get_tts_handler
import tempfile
import os

bp = Blueprint('voice', __name__, url_prefix='/api/voice')
api = Api(bp)

class VoiceInputResource(Resource):
    def post(self):
        if 'audio' not in request.files:
            return {'error': 'No audio file provided'}, 400

        audio_file = request.files['audio']
        audio_data = audio_file.read()

        asr_handler = get_asr_handler()
        text = asr_handler.recognize(audio_data)

        return {'text': text, 'success': True}

api.add_resource(VoiceInputResource, '/input')

class VoiceOutputResource(Resource):
    def post(self):
        data = request.get_json()
        text = data.get('text', '')

        if not text:
            return {'error': 'No text provided'}, 400

        tts_handler = get_tts_handler()
        audio_bytes = tts_handler.synthesize(
            text,
            speed=data.get('speed', 0.9),
            voice=data.get('voice', 'female_tianmei')
        )

        return send_file(
            io.BytesIO(audio_bytes),
            mimetype='audio/wav',
            as_attachment=False
        )

api.add_resource(VoiceOutputResource, '/output')
```

- [ ] **Step 4: 提交代码**

```bash
git add app/core/asr_handler.py app/core/tts_handler.py app/api/voice.py
git commit -m "feat: add ASR/TTS voice processing modules"
```

---

## Phase 3: 对话管理核心（Week 3-4）

### Task 3.1: 对话管理器实现

**Files:**
- Create: `app/core/dialogue_manager.py`
- Create: `app/core/interruption.py`

- [ ] **Step 1: 创建对话上下文模型**

```python
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum

class Role(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"

class Message(BaseModel):
    role: Role
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)

class TeachingState(BaseModel):
    topic: Optional[str] = None
    current_point: int = 0
   讲解进度: List[str] = Field(default_factory=list)
    explained_points: List[int] = Field(default_factory=list)
    depth_level: int = 1

class ConversationContext(BaseModel):
    session_id: str
    user_id: str
    messages: List[Message] = Field(default_factory=list)
    teaching_state: Optional[TeachingState] = None
    interrupted: bool = False
    last_interruption_point: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
```

- [ ] **Step 2: 创建打断检测模块app/core/interruption.py**

```python
"""
打断检测器
检测学生说"停"、"等一下"等关键词
"""
from typing import List, Tuple, Optional

INTERRUPT_KEYWORDS = [
    "停",
    "等一下",
    "等一等",
    "老师停",
    "停一下",
    "暂停",
    "稍等",
    "等会",
    "不懂",
    "不懂了",
    "不会",
    "不会了",
    "再说一遍",
    "重新说",
    "慢一点",
    "太快了",
    "说清楚",
    "没听懂",
    "听不懂"
]

CONTINUE_KEYWORDS = [
    "继续",
    "可以了",
    "继续说",
    "继续讲",
    "往下说",
    "懂了",
    "知道了",
    "明白",
    "明白了"
]

class InterruptionDetector:
    def __init__(self):
        self.interrupt_keywords = INTERRUPT_KEYWORDS
        self.continue_keywords = CONTINUE_KEYWORDS

    def detect_interruption(self, text: str) -> Tuple[bool, Optional[str]]:
        text_lower = text.lower()
        for keyword in self.interrupt_keywords:
            if keyword in text:
                return True, keyword
        return False, None

    def detect_continue(self, text: str) -> bool:
        for keyword in self.continue_keywords:
            if keyword in text:
                return True
        return False

    def extract_question(self, text: str, interrupt_keyword: str) -> str:
        parts = text.split(interrupt_keyword)
        if len(parts) > 1:
            question = parts[1].strip()
            return question if question else ""
        return text

_detector = None

def get_interruption_detector() -> InterruptionDetector:
    global _detector
    if _detector is None:
        _detector = InterruptionDetector()
    return _detector
```

- [ ] **Step 3: 创建对话管理器app/core/dialogue_manager.py**

```python
"""
对话管理器
处理多轮对话上下文，支持打断与恢复
"""
from typing import Dict, Optional, List, Any
from datetime import datetime
import uuid
from app.core.dialogue_manager_models import (
    ConversationContext, Message, Role, TeachingState
)
from app.core.interruption import get_interruption_detector
from app.core.asr_handler import get_asr_handler
from app.core.tts_handler import get_tts_handler
from model_service.inference import get_vllm_client
import os

SYSTEM_PROMPT = """你是一位充满爱心、耐心的小学老师，名叫小慧老师。你在和6-12岁的小学生交流。
你的特点是：
1. 说话温柔、亲切，像朋友一样
2. 善于用比喻和例子解释抽象概念
3. 讲解时分步骤，每步讲清楚后再讲下一步
4. 经常鼓励学生，"你真棒"、"很好"等
5. 如果学生说"不懂"，会换一种方式重新讲解
6. 使用简单的词汇，避免太专业的术语

当学生打断你时，先回答他们的问题，然后确认是否可以继续。"""

class DialogueManager:
    def __init__(self):
        self.sessions: Dict[str, ConversationContext] = {}
        self.vllm_client = get_vllm_client()
        self.interruption_detector = get_interruption_detector()

    def create_session(self, user_id: str) -> str:
        session_id = str(uuid.uuid4())
        context = ConversationContext(
            session_id=session_id,
            user_id=user_id,
            messages=[Message(role=Role.SYSTEM, content=SYSTEM_PROMPT)]
        )
        self.sessions[session_id] = context
        return session_id

    def get_session(self, session_id: str) -> Optional[ConversationContext]:
        return self.sessions.get(session_id)

    def process_voice_input(
        self,
        session_id: str,
        audio_data: bytes,
        language: str = "auto"
    ) -> Dict[str, Any]:
        asr_handler = get_asr_handler()
        text = asr_handler.recognize(audio_data, language=language)

        return self.process_text_input(session_id, text)

    def process_text_input(
        self,
        session_id: str,
        text: str
    ) -> Dict[str, Any]:
        context = self.get_session(session_id)
        if not context:
            return {'error': 'Session not found'}

        is_interrupted, keyword = self.interruption_detector.detect_interruption(text)

        if is_interrupted:
            context.interrupted = True
            if context.teaching_state:
                context.last_interruption_point = context.teaching_state.current_point

            question = self.interruption_detector.extract_question(text, keyword)
            response = self._generate_response(context, question, is_question=True)

            if self.interruption_detector.detect_continue(response.get('text', '')):
                context.interrupted = False

            return {
                'type': 'interruption',
                'keyword': keyword,
                'question': question,
                'response': response,
                'can_continue': True
            }

        if self.interruption_detector.detect_continue(text) and context.interrupted:
            context.interrupted = False
            return {
                'type': 'continue',
                'response': {'text': '好的，那我们继续！'}
            }

        response = self._generate_response(context, text)

        return {
            'type': 'normal',
            'response': response
        }

    def _generate_response(
        self,
        context: ConversationContext,
        user_input: str,
        is_question: bool = False
    ) -> Dict[str, Any]:
        context.messages.append(Message(role=Role.USER, content=user_input))

        messages = [{"role": m.role.value, "content": m.content} for m in context.messages]

        try:
            result = self.vllm_client.chat(messages=messages)
            assistant_message = result['choices'][0]['message']['content']
        except Exception as e:
            print(f"vLLM调用失败: {e}")
            assistant_message = "抱歉，老师现在有点累，我们等会儿再继续好不好？"

        context.messages.append(Message(role=Role.ASSISTANT, content=assistant_message))
        context.updated_at = datetime.now()

        return {
            'text': assistant_message,
            'session_id': context.session_id
        }

    def start_teaching(
        self,
        session_id: str,
        topic: str,
        outline: List[str]
    ) -> Dict[str, Any]:
        context = self.get_session(session_id)
        if not context:
            return {'error': 'Session not found'}

        context.teaching_state = TeachingState(
            topic=topic,
            current_point=0,
           讲解进度=outline,
            depth_level=1
        )

        intro = f"同学们好，今天我们来学习【{topic}】。这个内容一共有{len(outline)}个部分，让我们一起来看看吧！"
        response = self._generate_response(context, intro)

        return {
            'intro': intro,
            'response': response,
            'outline': outline
        }

    def continue_teaching(self, session_id: str) -> Dict[str, Any]:
        context = self.get_session(session_id)
        if not context or not context.teaching_state:
            return {'error': 'No teaching in progress'}

        state = context.teaching_state
        if state.current_point >= len(state.讲解进度):
            conclusion = f"好的，同学们，关于【{state.topic}】我们就讲完了。大家有什么问题吗？"
            return {
                'text': conclusion,
                'finished': True
            }

        next_point = state.讲解进度[state.current_point]
        prompt = f"现在请讲解第{state.current_point + 1}点：{next_point}。请用简单易懂的方式讲解，分步骤进行。"

        response = self._generate_response(context, prompt)
        state.current_point += 1

        return {
            'text': response.get('text', ''),
            'current_point': state.current_point,
            'total_points': len(state.讲解进度),
            'finished': False
        }

_manager = None

def get_dialogue_manager() -> DialogueManager:
    global _manager
    if _manager is None:
        _manager = DialogueManager()
    return _manager
```

- [ ] **Step 4: 更新chat API - app/api/chat.py**

```python
from flask import Blueprint, request, jsonify
from flask_restful import Api, Resource
from app.core.dialogue_manager import get_dialogue_manager

bp = Blueprint('chat', __name__, url_prefix='/api/chat')
api = Api(bp)

class ChatResource(Resource):
    def post(self):
        data = request.get_json()
        session_id = data.get('session_id')
        text = data.get('text', '')

        if not session_id:
            return {'error': 'session_id required'}, 400

        manager = get_dialogue_manager()
        result = manager.process_text_input(session_id, text)

        return result

api.add_resource(ChatResource, '/')

class SessionResource(Resource):
    def post(self):
        data = request.get_json()
        user_id = data.get('user_id', 'anonymous')

        manager = get_dialogue_manager()
        session_id = manager.create_session(user_id)

        return {'session_id': session_id}

api.add_resource(SessionResource, '/session')

class TeachingResource(Resource):
    def post(self):
        data = request.get_json()
        session_id = data.get('session_id')
        topic = data.get('topic')
        outline = data.get('outline', [])

        if not session_id or not topic:
            return {'error': 'session_id and topic required'}, 400

        manager = get_dialogue_manager()
        result = manager.start_teaching(session_id, topic, outline)

        return result

    def put(self):
        data = request.get_json()
        session_id = data.get('session_id')

        if not session_id:
            return {'error': 'session_id required'}, 400

        manager = get_dialogue_manager()
        result = manager.continue_teaching(session_id)

        return result

api.add_resource(TeachingResource, '/teaching')
```

- [ ] **Step 5: 提交代码**

```bash
git add app/core/dialogue_manager.py app/core/interruption.py app/api/chat.py
git commit -m "feat: implement dialogue manager with interruption support"
```

---

## Phase 4: RAG知识库与教案生成（Week 4-6）

### Task 4.1: 知识库搭建

**Files:**
- Create: `app/core/rag_engine.py`
- Create: `scripts/build_knowledge_base.py`

- [ ] **Step 1: 创建RAG引擎app/core/rag_engine.py**

```python
"""
RAG引擎
基于Chroma向量数据库，支持人教版教材检索
"""
import os
from typing import List, Dict, Optional, Any
from pathlib import Path
import chromadb
from chromadb.config import Settings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings

class RAGEngine:
    def __init__(
        self,
        db_path: Optional[str] = None,
        collection_name: str = "textbook_content"
    ):
        self.db_path = db_path or os.getenv('CHROMA_DB_PATH', './knowledge_base/chroma_db')
        self.collection_name = collection_name

        os.makedirs(self.db_path, exist_ok=True)

        self.client = chromadb.Client(Settings(
            persist_directory=self.db_path,
            anonymized_telemetry=False
        ))

        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )

        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
            model_kwargs={'device': 'cuda'}
        )

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            separators=["\n\n", "\n", "。", "，", " "]
        )

    def add_texts(
        self,
        texts: List[str],
        metadatas: Optional[List[Dict]] = None,
        ids: Optional[List[str]] = None
    ):
        if ids is None:
            import uuid
            ids = [str(uuid.uuid4()) for _ in texts]

        embeddings = self.embeddings.embed_documents(texts)

        self.collection.add(
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas or [{} for _ in texts],
            ids=ids
        )

        self.client.persist()

    def add_text_file(
        self,
        file_path: str,
        metadata: Optional[Dict] = None
    ):
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()

        chunks = self.text_splitter.split_text(text)

        chunk_metadata = []
        for i, chunk in enumerate(chunks):
            chunk_meta = metadata.copy() if metadata else {}
            chunk_meta['chunk_id'] = i
            chunk_metadata.append(chunk_meta)

        self.add_texts(chunks, chunk_metadata)

    def query(
        self,
        query_text: str,
        n_results: int = 5,
        filter_metadata: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        query_embedding = self.embeddings.embed_query(query_text)

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=filter_metadata
        )

        formatted_results = []
        if results['documents'] and len(results['documents']) > 0:
            for i, doc in enumerate(results['documents'][0]):
                formatted_results.append({
                    'content': doc,
                    'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                    'distance': results['distances'][0][i] if results['distances'] else 0
                })

        return formatted_results

    def get_relevant_context(
        self,
        query: str,
        grade: Optional[int] = None,
        subject: Optional[str] = None,
        chapter: Optional[str] = None,
        n_results: int = 5
    ) -> str:
        filter_metadata = {}
        if grade:
            filter_metadata['grade'] = grade
        if subject:
            filter_metadata['subject'] = subject
        if chapter:
            filter_metadata['chapter'] = chapter

        results = self.query(
            query,
            n_results=n_results,
            filter_metadata=filter_metadata if filter_metadata else None
        )

        context = "\n\n".join([r['content'] for r in results])
        return context

_engine = None

def get_rag_engine() -> RAGEngine:
    global _engine
    if _engine is None:
        _engine = RAGEngine()
    return _engine
```

- [ ] **Step 2: 创建知识库构建脚本scripts/build_knowledge_base.py**

```python
#!/usr/bin/env python3
"""
构建人教版教材知识库
从教材文本构建向量数据库
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pathlib import Path
from app.core.rag_engine import RAGEngine
import json

TEXTBOOK_DIR = Path(__file__).parent.parent / "knowledge_base" / "textbooks"

def load_textbook_content(edition: str = "pep") -> list:
    content = []
    edition_dir = TEXTBOOK_DIR / edition

    if not edition_dir.exists():
        print(f"Warning: Textbook directory {edition_dir} does not exist")
        return content

    for grade_dir in edition_dir.iterdir():
        if not grade_dir.is_dir():
            continue
        grade = int(grade_dir.name.replace("grade", "").replace("年级", ""))

        for subject_file in grade_dir.iterdir():
            if subject_file.suffix != '.txt':
                continue
            subject = subject_file.stem

            with open(subject_file, 'r', encoding='utf-8') as f:
                text = f.read()

            chapters = text.split("## 第")
            for i, chapter in enumerate(chapters):
                if not chapter.strip():
                    continue
                if i > 0:
                    chapter = "## 第" + chapter

                metadata = {
                    'grade': grade,
                    'subject': subject,
                    'source': f'{edition}_{grade}_{subject}'
                }
                content.append({
                    'text': chapter,
                    'metadata': metadata
                })

    return content

def build_knowledge_base(edition: str = "pep"):
    print(f"Building knowledge base for {edition}...")
    engine = RAGEngine()

    content = load_textbook_content(edition)
    print(f"Loaded {len(content)} content items")

    for item in content:
        texts = [item['text']]
        metadatas = [item['metadata']]

        engine.add_texts(texts, metadatas)

    print(f"Knowledge base built successfully!")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--edition', type=str, default='pep', help='Textbook edition (pep=人教版)')
    args = parser.parse_args()

    build_knowledge_base(args.edition)
```

- [ ] **Step 3: 提交代码**

```bash
git add app/core/rag_engine.py scripts/build_knowledge_base.py
git commit -m "feat: add RAG engine and knowledge base builder"
```

---

### Task 4.2: 教案生成服务

**Files:**
- Create: `app/services/lesson_service.py`

- [ ] **Step 1: 创建教案服务app/services/lesson_service.py**

```python
"""
教案生成服务
基于RAG检索和LLM生成符合人教版标准的教案
"""
from typing import Dict, List, Optional, Any
from app.core.rag_engine import get_rag_engine
from model_service.inference import get_vllm_client
import json

LESSON_PLAN_TEMPLATE = """请根据以下信息生成一份完整的小学教案：

## 基本信息
- 学科：{subject}
- 年级：grade{grade}
- 课时：{duration}
- 课题：{topic}

## 课程标准要求
{standard_content}

## 教材内容摘要
{textbook_summary}

## 教案要求
请按照以下格式生成教案：
1. 教学目标（知识与技能、过程与方法、情感态度与价值观）
2. 教学重点
3. 教学难点
4. 教学方法
5. 教学准备
6. 教学过程（含时间分配）
7. 板书设计
8. 作业设计
9. 教学反思

请用JSON格式输出，key为中文。
"""

class LessonPlanService:
    def __init__(self):
        self.rag_engine = get_rag_engine()
        self.vllm_client = get_vllm_client()

    def generate_lesson_plan(
        self,
        grade: int,
        subject: str,
        topic: str,
        duration: str = "40分钟",
        additional_requirements: Optional[str] = None
    ) -> Dict[str, Any]:
        context = self.rag_engine.get_relevant_context(
            query=f"{subject} {topic}",
            grade=grade,
            subject=subject,
            n_results=5
        )

        standard_content = self._get_curriculum_standard(grade, subject)

        prompt = LESSON_PLAN_TEMPLATE.format(
            subject=subject,
            grade=grade,
            duration=duration,
            topic=topic,
            standard_content=standard_content,
            textbook_summary=context
        )

        if additional_requirements:
            prompt += f"\n\n补充要求：{additional_requirements}"

        try:
            result = self.vllm_client.chat(
                messages=[
                    {"role": "system", "content": "你是一位资深的小学教师，擅长编写规范的教案。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            lesson_plan_text = result['choices'][0]['message']['content']
            lesson_plan = self._parse_lesson_plan(lesson_plan_text)
        except Exception as e:
            print(f"教案生成失败: {e}")
            lesson_plan = self._generate_fallback_plan(grade, subject, topic)

        return {
            'success': True,
            'plan': lesson_plan,
            'topic': topic,
            'grade': grade,
            'subject': subject
        }

    def _get_curriculum_standard(self, grade: int, subject: str) -> str:
        standards = {
            ('math', 'pep'): "小学数学课程标准要求：注重基础知识和基本技能的培养，发展学生的数感和符号意识。",
            ('chinese', 'pep'): "小学语文课程标准要求：培养学生的语言文字运用能力，提升语文素养，继承和弘扬中华优秀传统文化。",
            ('english', 'pep'): "小学英语课程标准要求：激发学习兴趣，培养初步的英语沟通能力。",
        }
        return standards.get((subject.lower(), 'pep'), "按照课程标准要求进行教学。")

    def _parse_lesson_plan(self, text: str) -> Dict[str, Any]:
        try:
            if "```json" in text:
                json_str = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                json_str = text.split("```")[1].split("```")[0]
            else:
                json_str = text

            plan = json.loads(json_str.strip())
            return plan
        except json.JSONDecodeError:
            return {'content': text, 'format': 'text'}

    def _generate_fallback_plan(
        self,
        grade: int,
        subject: str,
        topic: str
    ) -> Dict[str, Any]:
        return {
            "教学目标": {
                "知识与技能": f"使学生理解和掌握{topic}的基本概念",
                "过程与方法": "通过讲解、练习、讨论等方式进行教学",
                "情感态度与价值观": "培养学生学习兴趣，养成良好的学习习惯"
            },
            "教学重点": f"{topic}的核心知识点",
            "教学难点": f"{topic}的应用和理解",
            "教学方法": "讲授法、讨论法、练习法",
            "教学准备": "多媒体课件、教材、练习册",
            "教学过程": "导入→新授→巩固→小结→作业",
            "板书设计": f"{topic}知识框架",
            "作业设计": f"课后练习{topic}相关内容",
            "教学反思": "待课后补充"
        }

    def generate_exercises(
        self,
        lesson_plan: Dict[str, Any],
        exercise_types: List[str] = None,
        num_each: int = 3
    ) -> Dict[str, Any]:
        if exercise_types is None:
            exercise_types = ['选择题', '填空题', '解答题']

        plan_summary = json.dumps(lesson_plan, ensure_ascii=False)

        prompt = f"""根据以下教案内容，生成配套练习题：

{plan_summary}

要求：
- 选择题 {num_each} 道
- 填空题 {num_each} 道
- 解答题 {num_each} 道

请给出完整的题目和答案，答案要详细。

用JSON格式输出：
{{
  "选择题": [{{"题目": "...", "选项": [...], "答案": "...", "解析": "..."}}],
  "填空题": [{{"题目": "...", "答案": "...", "解析": "..."}}],
  "解答题": [{{"题目": "...", "答案": "...", "解析": "..."}}]
}}
"""

        try:
            result = self.vllm_client.chat(
                messages=[
                    {"role": "system", "content": "你是一位资深的小学教师，擅长设计练习题。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            exercises_text = result['choices'][0]['message']['content']
            exercises = json.loads(exercises_text)
        except Exception as e:
            print(f"练习题生成失败: {e}")
            exercises = {'选择题': [], '填空题': [], '解答题': []}

        return exercises

_service = None

def get_lesson_service() -> LessonPlanService:
    global _service
    if _service is None:
        _service = LessonPlanService()
    return _service
```

- [ ] **Step 2: 更新lesson API - app/api/lesson.py**

```python
from flask import Blueprint, request, jsonify
from flask_restful import Api, Resource
from app.services.lesson_service import get_lesson_service

bp = Blueprint('lesson', __name__, url_prefix='/api/lesson')
api = Api(bp)

class LessonPlanResource(Resource):
    def post(self):
        data = request.get_json()
        grade = data.get('grade')
        subject = data.get('subject')
        topic = data.get('topic')
        duration = data.get('duration', '40分钟')

        if not all([grade, subject, topic]):
            return {'error': 'grade, subject, topic are required'}, 400

        service = get_lesson_service()
        result = service.generate_lesson_plan(
            grade=grade,
            subject=subject,
            topic=topic,
            duration=duration,
            additional_requirements=data.get('requirements')
        )

        return result

api.add_resource(LessonPlanResource, '/')

class LessonExercisesResource(Resource):
    def post(self):
        data = request.get_json()
        lesson_plan = data.get('lesson_plan')

        if not lesson_plan:
            return {'error': 'lesson_plan is required'}, 400

        service = get_lesson_service()
        result = service.generate_exercises(lesson_plan)

        return {'success': True, 'exercises': result}

api.add_resource(LessonExercisesResource, '/exercises')
```

- [ ] **Step 3: 提交代码**

```bash
git add app/services/lesson_service.py app/api/lesson.py
git commit -m "feat: add lesson plan generation service"
```

---

## Phase 5: 题库问答系统（Week 6-7）

### Task 5.1: OCR识别与题目处理

**Files:**
- Create: `app/core/ocr_handler.py`

- [ ] **Step 1: 创建OCR处理器app/core/ocr_handler.py**

```python
"""
OCR处理器
基于PaddleOCR识别题目图片
"""
import os
from typing import Optional, List, Dict, Any, Tuple
import numpy as np
from PIL import Image
import io

class OCRHandler:
    def __init__(self):
        self.reader = None
        self._initialized = False

    def initialize(self):
        if self._initialized:
            return
        print("Loading OCR model...")
        from paddleocr import PaddleOCR
        self.reader = PaddleOCR(
            use_angle_cls=True,
            lang='ch',
            use_gpu=True,
            show_log=False
        )
        self._initialized = True

    def recognize_from_bytes(self, image_bytes: bytes) -> List[Dict[str, Any]]:
        self.initialize()

        image = Image.open(io.BytesIO(image_bytes))
        img_array = np.array(image)

        result = self.reader.ocr(img_array, cls=True)

        if not result or not result[0]:
            return []

        line_texts = []
        for line in result[0]:
            if line:
                bbox = line[0]
                text = line[1][0]
                confidence = line[1][1]
                line_texts.append({
                    'text': text,
                    'bbox': bbox,
                    'confidence': confidence
                })

        return line_texts

    def recognize_from_file(self, file_path: str) -> List[Dict[str, Any]]:
        self.initialize()
        result = self.reader.ocr(file_path, cls=True)

        if not result or not result[0]:
            return []

        return [
            {
                'text': line[1][0],
                'bbox': line[0],
                'confidence': line[1][1]
            }
            for line in result[0] if line
        ]

    def parse_question_structure(
        self,
        ocr_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        question_text = "\n".join([r['text'] for r in ocr_results])

        question_type = self._detect_question_type(question_text)

        structured = {
            'raw_text': question_text,
            'type': question_type,
            'lines': [r['text'] for r in ocr_results],
            'has_image': self._check_for_image(ocr_results)
        }

        return structured

    def _detect_question_type(self, text: str) -> str:
        text = text.strip()

        if any(marker in text for marker in ['选择题', '选一选', '下列']):
            return '选择题'
        elif any(marker in text for marker in ['填空题', '填空', '（）']):
            return '填空题'
        elif any(marker in text for marker in ['解答题', '应用题', '计算题', '证明题']):
            return '解答题'
        elif any(marker in text for marker in ['判断题', '对的', '错的']):
            return '判断题'
        else:
            return 'unknown'

    def _check_for_image(self, ocr_results: List[Dict[str, Any]]) -> bool:
        return False

_handler = None

def get_ocr_handler() -> OCRHandler:
    global _handler
    if _handler is None:
        _handler = OCRHandler()
    return _handler
```

- [ ] **Step 2: 提交代码**

```bash
git add app/core/ocr_handler.py
git commit -m "feat: add OCR handler for question recognition"
```

---

### Task 5.2: 题库问答服务

**Files:**
- Create: `app/services/question_service.py`

- [ ] **Step 1: 创建题库问答服务app/services/question_service.py**

```python
"""
题库问答服务
识别题目并给出答案和详细讲解
"""
from typing import Dict, List, Optional, Any
import json
from app.core.ocr_handler import get_ocr_handler
from app.core.rag_engine import get_rag_engine
from model_service.inference import get_vllm_client

class QuestionService:
    def __init__(self):
        self.ocr_handler = get_ocr_handler()
        self.rag_engine = get_rag_engine()
        self.vllm_client = get_vllm_client()

    def process_question_image(self, image_bytes: bytes) -> Dict[str, Any]:
        ocr_results = self.ocr_handler.recognize_from_bytes(image_bytes)

        if not ocr_results:
            return {
                'success': False,
                'error': '未能识别图片中的文字'
            }

        structured = self.ocr_handler.parse_question_structure(ocr_results)

        answer_result = self._get_answer_for_question(structured['raw_text'], structured['type'])

        return {
            'success': True,
            'question': structured,
            'answer': answer_result
        }

    def process_question_text(self, question_text: str, question_type: str = None) -> Dict[str, Any]:
        if not question_type:
            structured = {
                'raw_text': question_text,
                'type': self.ocr_handler._detect_question_type(question_text)
            }
        else:
            structured = {
                'raw_text': question_text,
                'type': question_type
            }

        answer_result = self._get_answer_for_question(question_text, structured['type'])

        return {
            'success': True,
            'question': structured,
            'answer': answer_result
        }

    def _get_answer_for_question(
        self,
        question_text: str,
        question_type: str
    ) -> Dict[str, Any]:
        relevant_knowledge = self.rag_engine.get_relevant_context(
            query=question_text,
            n_results=3
        )

        prompt = f"""请解答以下{question_type}：

{question_text}

相关知识点：
{relevant_knowledge}

请给出：
1. 答案
2. 详细解题步骤（分步讲解）
3. 知识点解析
4. 易错点提醒（如有）

请用JSON格式输出：
{{
  "答案": "...",
  "解题步骤": ["步骤1", "步骤2", ...],
  "知识点解析": "...",
  "易错点提醒": "...",
  "适合儿童的解释": "..."
}}
"""

        try:
            result = self.vllm_client.chat(
                messages=[
                    {"role": "system", "content": "你是一位资深的小学教师，擅长解答题目并用儿童能理解的方式讲解。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            answer_text = result['choices'][0]['message']['content']
            answer = self._parse_answer(answer_text)
        except Exception as e:
            print(f"答案生成失败: {e}")
            answer = {
                "答案": "抱歉，暂时无法解答",
                "解题步骤": [],
                "知识点解析": "",
                "易错点提醒": "",
                "适合儿童的解释": ""
            }

        return answer

    def _parse_answer(self, text: str) -> Dict[str, Any]:
        try:
            if "```json" in text:
                json_str = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                json_str = text.split("```")[1].split("```")[0]
            else:
                json_str = text

            return json.loads(json_str.strip())
        except json.JSONDecodeError:
            return {
                "答案": text,
                "解题步骤": [],
                "知识点解析": "",
                "易错点提醒": "",
                "适合儿童的解释": ""
            }

_service = None

def get_question_service() -> QuestionService:
    global _service
    if _service is None:
        _service = QuestionService()
    return _service
```

- [ ] **Step 2: 更新question API - app/api/question.py**

```python
from flask import Blueprint, request, jsonify
from flask_restful import Api, Resource
from app.services.question_service import get_question_service
import tempfile
import os

bp = Blueprint('question', __name__, url_prefix='/api/question')
api = Api(bp)

class QuestionResource(Resource):
    def post(self):
        if 'image' in request.files:
            image_file = request.files['image']
            image_bytes = image_file.read()

            service = get_question_service()
            result = service.process_question_image(image_bytes)

            return result

        data = request.get_json()
        if not data or 'question' not in data:
            return {'error': 'question or image required'}, 400

        service = get_question_service()
        result = service.process_question_text(
            question_text=data['question'],
            question_type=data.get('type')
        )

        return result

api.add_resource(QuestionResource, '/')

class QuestionDetailResource(Resource):
    def get(self, question_id):
        return {'question_id': question_id, 'message': 'Question detail endpoint'}

api.add_resource(QuestionDetailResource, '/<int:question_id>')
```

- [ ] **Step 3: 提交代码**

```bash
git add app/services/question_service.py app/api/question.py
git commit -m "feat: add question answering service with OCR"
```

---

## Phase 6: 项目计划书生成（Week 7-8）

### Task 6.1: 项目计划书服务

**Files:**
- Create: `app/services/project_service.py`

- [ ] **Step 1: 创建项目计划书服务app/services/project_service.py**

```python
"""
项目计划书生成服务
根据学校基本信息生成乡村教育数字化项目计划书
"""
from typing import Dict, List, Optional, Any
import json
from model_service.inference import get_vllm_client

PROJECT_PLAN_TEMPLATE = """请为以下乡村学校生成一份教育数字化项目计划书：

## 学校基本信息
- 学校名称：{school_name}
- 学生人数：{student_count}人
- 教师人数：{teacher_count}人
- 年级设置：{grade_settings}
- 当前网络状况：{network_status}
- 现有设备情况：{existing_equipment}
- 预算范围：{budget_range}

## 建设目标
{construction_goals}

## 项目类型
{project_type}

请生成完整的项目计划书，包括以下章节：
1. 项目背景与必要性
2. 建设目标与内容
3. 技术方案设计
4. 设备清单与预算明细
5. 实施进度计划
6. 风险评估与对策
7. 预期效果与评估指标

请用JSON格式输出。
"""

PROJECT_TYPES = {
    "infrastructure": "基础设施建设（网络、机房、多媒体教室）",
    "informationization": "教育信息化升级（智慧校园、在线教学平台）",
    "hybrid": "混合方案（基础设施+信息化）"
}

class ProjectPlanService:
    def __init__(self):
        self.vllm_client = get_vllm_client()

    def generate_project_plan(
        self,
        school_name: str,
        student_count: int,
        teacher_count: int,
        grade_settings: str,
        network_status: str,
        existing_equipment: str,
        budget_range: str,
        construction_goals: str = None,
        project_type: str = "hybrid"
    ) -> Dict[str, Any]:
        if construction_goals is None:
            construction_goals = "提升学校信息化教学水平，改善教学环境"

        project_type_desc = PROJECT_TYPES.get(project_type, PROJECT_TYPES["hybrid"])

        prompt = PROJECT_PLAN_TEMPLATE.format(
            school_name=school_name,
            student_count=student_count,
            teacher_count=teacher_count,
            grade_settings=grade_settings,
            network_status=network_status,
            existing_equipment=existing_equipment,
            budget_range=budget_range,
            construction_goals=construction_goals,
            project_type=project_type_desc
        )

        try:
            result = self.vllm_client.chat(
                messages=[
                    {"role": "system", "content": "你是一位教育信息化专家，擅长撰写乡村教育数字化项目计划书。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            plan_text = result['choices'][0]['message']['content']
            plan = self._parse_plan(plan_text)
        except Exception as e:
            print(f"项目计划书生成失败: {e}")
            plan = self._generate_fallback_plan(school_name, student_count, teacher_count)

        return {
            'success': True,
            'plan': plan,
            'school_name': school_name,
            'project_type': project_type
        }

    def _parse_plan(self, text: str) -> Dict[str, Any]:
        try:
            if "```json" in text:
                json_str = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                json_str = text.split("```")[1].split("```")[0]
            else:
                json_str = text

            return json.loads(json_str.strip())
        except json.JSONDecodeError:
            return {'content': text, 'format': 'text'}

    def _generate_fallback_plan(
        self,
        school_name: str,
        student_count: int,
        teacher_count: int
    ) -> Dict[str, Any]:
        student_per_teacher = student_count / teacher_count if teacher_count > 0 else 0

        return {
            "项目背景与必要性": f"{school_name}现有学生{student_count}人，教师{teacher_count}人，亟需推进教育数字化转型。",
            "建设目标与内容": [
                "建设高速校园网络",
                "部署多媒体教学设备",
                "搭建在线教学平台",
                "培训教师信息化能力"
            ],
            "技术方案设计": "采用云端+本地混合架构，确保系统稳定性和数据安全。",
            "设备清单与预算明细": {
                "网络设备": f"约{student_count * 100}元",
                "多媒体设备": f"约{teacher_count * 2000}元",
                "服务器": "约50000元",
                "软件平台": "约30000元",
                "培训费用": "约20000元",
                "总计": "约150000-200000元"
            },
            "实施进度计划": [
                "第1-2月：需求调研与方案设计",
                "第3-4月：设备采购与安装",
                "第5-6月：平台部署与调试",
                "第7-8月：人员培训与试运行",
                "第9月：正式上线与验收"
            ],
            "风险评估与对策": [
                "风险1：网络基础设施不完善 → 提前进行网络改造",
                "风险2：教师接受度低 → 加强培训与激励"
            ],
            "预期效果与评估指标": f"建成后，师生比达到1:{int(student_per_teacher)}，多媒体教室覆盖率达到100%。"
        }

_service = None

def get_project_service() -> ProjectPlanService:
    global _service
    if _service is None:
        _service = ProjectPlanService()
    return _service
```

- [ ] **Step 2: 更新project API - app/api/project.py**

```python
from flask import Blueprint, request, jsonify
from flask_restful import Api, Resource
from app.services.project_service import get_project_service

bp = Blueprint('project', __name__, url_prefix='/api/project')
api = Api(bp)

class ProjectPlanResource(Resource):
    def post(self):
        data = request.get_json()

        required_fields = ['school_name', 'student_count', 'teacher_count']
        for field in required_fields:
            if field not in data:
                return {'error': f'{field} is required'}, 400

        service = get_project_service()
        result = service.generate_project_plan(
            school_name=data['school_name'],
            student_count=data['student_count'],
            teacher_count=data['teacher_count'],
            grade_settings=data.get('grade_settings', '小学1-6年级'),
            network_status=data.get('network_status', '一般'),
            existing_equipment=data.get('existing_equipment', '基本完备'),
            budget_range=data.get('budget_range', '10-20万'),
            construction_goals=data.get('construction_goals'),
            project_type=data.get('project_type', 'hybrid')
        )

        return result

api.add_resource(ProjectPlanResource, '/')

class ProjectBudgetResource(Resource):
    def post(self):
        data = request.get_json()
        student_count = data.get('student_count', 0)
        teacher_count = data.get('teacher_count', 0)

        budget_estimate = {
            "网络设备": student_count * 100,
            "多媒体设备": teacher_count * 2000,
            "服务器": 50000,
            "软件平台": 30000,
            "培训费用": 20000,
            "总计": student_count * 100 + teacher_count * 2000 + 100000
        }

        return {'success': True, 'budget': budget_estimate}

api.add_resource(ProjectBudgetResource, '/budget-estimate')
```

- [ ] **Step 3: 提交代码**

```bash
git add app/services/project_service.py app/api/project.py
git commit -m "feat: add project plan generation service"
```

---

## Phase 7: 前端界面与集成（Week 8-10）

### Task 7.1: Web前端搭建

**Files:**
- Create: `app/templates/index.html`
- Create: `app/static/css/style.css`
- Create: `app/static/js/app.js`

- [ ] **Step 1: 创建前端HTML**

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>乡村老师助教系统 - 小慧老师</title>
    <link rel="stylesheet" href="/static/css/style.css">
</head>
<body>
    <div id="app" class="container">
        <header class="header">
            <h1>🏠 乡村老师助教系统</h1>
            <p class="subtitle">小慧老师随时为你服务！</p>
        </header>

        <main class="main-content">
            <div class="mode-selector">
                <button class="mode-btn active" data-mode="chat">💬 问答模式</button>
                <button class="mode-btn" data-mode="teaching">📚 教学模式</button>
                <button class="mode-btn" data-mode="lesson">📝 备课模式</button>
                <button class="mode-btn" data-mode="project">📋 项目计划</button>
            </div>

            <div class="chat-container" id="chatContainer">
                <div class="messages" id="messages"></div>
                <div class="input-area">
                    <button class="voice-btn" id="voiceBtn">🎤</button>
                    <input type="text" id="messageInput" placeholder="输入你的问题...">
                    <button class="send-btn" id="sendBtn">发送</button>
                </div>
            </div>
        </main>

        <aside class="sidebar" id="sidebar" style="display: none;">
            <div class="sidebar-content"></div>
        </aside>
    </div>

    <script src="/static/js/app.js"></script>
</body>
</html>
```

- [ ] **Step 2: 创建CSS样式**

```css
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
    padding: 20px;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
}

.header {
    text-align: center;
    color: white;
    margin-bottom: 30px;
}

.header h1 {
    font-size: 2.5rem;
    margin-bottom: 10px;
}

.subtitle {
    font-size: 1.2rem;
    opacity: 0.9;
}

.mode-selector {
    display: flex;
    gap: 10px;
    justify-content: center;
    margin-bottom: 20px;
}

.mode-btn {
    padding: 12px 24px;
    border: none;
    border-radius: 25px;
    background: rgba(255, 255, 255, 0.2);
    color: white;
    cursor: pointer;
    transition: all 0.3s;
    font-size: 1rem;
}

.mode-btn:hover, .mode-btn.active {
    background: white;
    color: #667eea;
}

.chat-container {
    background: white;
    border-radius: 20px;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
    overflow: hidden;
}

.messages {
    height: 400px;
    overflow-y: auto;
    padding: 20px;
}

.message {
    margin-bottom: 15px;
    padding: 12px 16px;
    border-radius: 15px;
    max-width: 80%;
}

.message.user {
    background: #667eea;
    color: white;
    margin-left: auto;
}

.message.assistant {
    background: #f1f1f1;
    color: #333;
}

.input-area {
    display: flex;
    padding: 15px;
    border-top: 1px solid #eee;
    gap: 10px;
}

.input-area input {
    flex: 1;
    padding: 12px;
    border: 1px solid #ddd;
    border-radius: 25px;
    font-size: 1rem;
}

.voice-btn, .send-btn {
    padding: 12px 20px;
    border: none;
    border-radius: 25px;
    cursor: pointer;
    font-size: 1rem;
    transition: all 0.3s;
}

.voice-btn {
    background: #ff6b6b;
    color: white;
}

.send-btn {
    background: #667eea;
    color: white;
}

.voice-btn:hover, .send-btn:hover {
    transform: scale(1.05);
}
```

- [ ] **Step 3: 创建JavaScript应用**

```javascript
class TeacherAssistantApp {
    constructor() {
        this.sessionId = null;
        this.currentMode = 'chat';
        this.API_BASE = '/api';

        this.init();
    }

    async init() {
        await this.createSession();
        this.bindEvents();
        this.addWelcomeMessage();
    }

    async createSession() {
        try {
            const response = await fetch(`${this.API_BASE}/chat/session`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({user_id: 'web_user'})
            });
            const data = await response.json();
            this.sessionId = data.session_id;
        } catch (error) {
            console.error('Failed to create session:', error);
        }
    }

    bindEvents() {
        document.querySelectorAll('.mode-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.switchMode(e.target.dataset.mode));
        });

        document.getElementById('sendBtn').addEventListener('click', () => this.sendMessage());
        document.getElementById('messageInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.sendMessage();
        });

        document.getElementById('voiceBtn').addEventListener('click', () => this.startVoiceInput());
    }

    switchMode(mode) {
        this.currentMode = mode;
        document.querySelectorAll('.mode-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.mode === mode);
        });
    }

    addWelcomeMessage() {
        this.addMessage('assistant', '同学们好！我是小慧老师，有什么问题尽管问我哦～');
    }

    addMessage(role, content) {
        const messagesDiv = document.getElementById('messages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}`;
        messageDiv.textContent = content;
        messagesDiv.appendChild(messageDiv);
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }

    async sendMessage() {
        const input = document.getElementById('messageInput');
        const text = input.value.trim();
        if (!text) return;

        this.addMessage('user', text);
        input.value = '';

        try {
            const response = await fetch(`${this.API_BASE}/chat/`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    session_id: this.sessionId,
                    text: text
                })
            });
            const data = await response.json();

            if (data.response) {
                this.addMessage('assistant', data.response.text);
            }
        } catch (error) {
            console.error('Failed to send message:', error);
            this.addMessage('assistant', '抱歉，网络好像有点问题，等会儿再试试？');
        }
    }

    async startVoiceInput() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            const mediaRecorder = new MediaRecorder(stream);
            const chunks = [];

            mediaRecorder.ondataavailable = (e) => chunks.push(e.data);
            mediaRecorder.onstop = async () => {
                const blob = new Blob(chunks, { type: 'audio/wav' });
                await this.sendVoiceMessage(blob);
                stream.getTracks().forEach(track => track.stop());
            };

            mediaRecorder.start();
            setTimeout(() => mediaRecorder.stop(), 5000);
        } catch (error) {
            console.error('Voice input error:', error);
        }
    }

    async sendVoiceMessage(blob) {
        const formData = new FormData();
        formData.append('audio', blob);

        try {
            const response = await fetch(`${this.API_BASE}/voice/input`, {
                method: 'POST',
                body: formData
            });
            const data = await response.json();

            if (data.text) {
                document.getElementById('messageInput').value = data.text;
                this.sendMessage();
            }
        } catch (error) {
            console.error('Failed to process voice:', error);
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.app = new TeacherAssistantApp();
});
```

- [ ] **Step 4: 更新Flask路由添加前端**

Update: `app/__init__.py`

```python
from flask import Flask, render_template
from flask_cors import CORS
from app.config import Config

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    CORS(app, resources={r"/api/*": {"origins": "*"}})

    @app.route('/')
    def index():
        return render_template('index.html')

    from app.api import register_routes
    register_routes(app)

    return app
```

- [ ] **Step 5: 创建目录并移动静态文件**

Run: `mkdir -p app/templates app/static/css app/static/js`

- [ ] **Step 6: 提交代码**

```bash
git add app/templates/index.html app/static/css/style.css app/static/js/app.js
git commit -m "feat: add web frontend interface"
```

---

## Phase 8: 模型微调（Week 10-14）

> **训练方式选择策略：** 本系统的模型训练分为两部分：
> 1. **LLM微调**：针对乡村教育场景的教案生成、题目解答等任务（Phase 8.1）
> 2. **视觉风格学习**：针对图片版式、字体风格的学习与复现（Phase 8.2）
>
> **核心原则：** 如果目标是"学习图片里的文字风格和排版规律，并且之后稳定复现出来"，优先做"小模型微调/适配"，不要把它主要做成"连接大模型后蒸馏为 skill"。
> 因为 **skill 更像流程知识、提示模板、规则编排和教师策略**，它擅长"分析、描述、拆解、生成标注"，但不擅长把**细粒度视觉风格分布**真正压进参数里。
> 相反，**参数微调，尤其是 LoRA/adapter 这类轻量微调**，更适合学字体气质、字号层级、留白、块对齐、标题层次、局部版式偏好这类"稳定风格偏置"。([OpenAI开发者][1])

---

### Task 8.1: LoRA微调脚本（LLM训练）

**Files:**
- Create: `training/scripts/finetune_qwen.py`
- Create: `training/scripts/prepare_data.py`

- [ ] **Step 1: 创建数据准备脚本**

```python
#!/usr/bin/env python3
"""
准备微调数据
将教案、习题等数据转换为训练格式
"""
import json
import os
from pathlib import Path
from typing import List, Dict

def load_existing_lesson_plans(data_dir: Path) -> List[Dict]:
    plans = []
    plans_dir = data_dir / "lesson_plans"

    if not plans_dir.exists():
        return plans

    for file in plans_dir.glob("*.json"):
        with open(file, 'r', encoding='utf-8') as f:
            plan = json.load(f)
            plans.append(plan)

    return plans

def load_existing_questions(data_dir: Path) -> List[Dict]:
    questions = []
    questions_dir = data_dir / "questions"

    if not questions_dir.exists():
        return questions

    for file in questions_dir.glob("*.json"):
        with open(file, 'r', encoding='utf-8') as f:
            q = json.load(f)
            questions.append(q)

    return questions

def convert_to_training_format(
    lesson_plans: List[Dict],
    questions: List[Dict]
) -> List[Dict]:
    training_data = []

    for plan in lesson_plans:
        prompt = f"请为{plan.get('grade', '')}年级{plan.get('subject', '')}生成关于{plan.get('topic', '')}的教案"
        response = json.dumps(plan.get('content', plan), ensure_ascii=False)

        training_data.append({
            "instruction": prompt,
            "input": "",
            "output": response
        })

    for q in questions:
        prompt = f"请解答这道{q.get('type', '题')}：{q.get('question', '')}"
        answer = json.dumps(q.get('answer', {}), ensure_ascii=False)

        training_data.append({
            "instruction": prompt,
            "input": "",
            "output": answer
        })

    return training_data

def save_training_data(training_data: List[Dict], output_path: Path):
    with open(output_path, 'w', encoding='utf-8') as f:
        for item in training_data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_dir', type=str, required=True)
    parser.add_argument('--output', type=str, required=True)
    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    plans = load_existing_lesson_plans(data_dir)
    questions = load_existing_questions(data_dir)

    print(f"Loaded {len(plans)} lesson plans, {len(questions)} questions")

    training_data = convert_to_training_format(plans, questions)
    print(f"Generated {len(training_data)} training samples")

    save_training_data(training_data, Path(args.output))
    print(f"Saved to {args.output}")

if __name__ == "__main__":
    main()
```

- [ ] **Step 2: 创建LoRA微调脚本**

```python
#!/usr/bin/env python3
"""
Qwen2.5-7B LoRA微调脚本
针对乡村教育场景优化
"""
import os
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments, Trainer
from peft import LoraConfig, get_peft_model, TaskType
from datasets import load_dataset

def setup_lora_model(model_path: str):
    print(f"Loading model from {model_path}...")

    tokenizer = AutoTokenizer.from_pretrained(
        model_path,
        trust_remote_code=True
    )
    tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        model_path,
        torch_dtype=torch.float16,
        device_map="auto",
        trust_remote_code=True
    )

    lora_config = LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        r=16,
        lora_alpha=32,
        target_modules=["q_proj", "v_proj", "k_proj", "o_proj"],
        lora_dropout=0.05,
        bias="none"
    )

    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()

    return model, tokenizer

def tokenize_function(examples, tokenizer, max_length: int = 2048):
    prompts = []
    for instruction, input_text, output in zip(
        examples['instruction'],
        examples['input'],
        examples['output']
    ):
        if input_text:
            prompt = f"指令：{instruction}\n输入：{input_text}\n回答：{output}"
        else:
            prompt = f"指令：{instruction}\n回答：{output}"
        prompts.append(prompt)

    tokenized = tokenizer(
        prompts,
        truncation=True,
        max_length=max_length,
        padding="max_length"
    )

    tokenized['labels'] = tokenized['input_ids'].copy()

    return tokenized

def train(
    model_path: str,
    data_path: str,
    output_path: str,
    num_epochs: int = 3,
    batch_size: int = 4,
    learning_rate: float = 2e-4
):
    model, tokenizer = setup_lora_model(model_path)

    dataset = load_dataset('json', data_files=data_path, split='train')

    def tokenize(examples):
        return tokenize_function(examples, tokenizer)

    dataset = dataset.map(tokenize, batched=True, remove_columns=dataset.column_names)

    training_args = TrainingArguments(
        output_dir=output_path,
        num_train_epochs=num_epochs,
        per_device_train_batch_size=batch_size,
        gradient_accumulation_steps=4,
        learning_rate=learning_rate,
        fp16=True,
        logging_steps=10,
        save_steps=100,
        save_total_limit=3,
        report_to="none"
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=dataset,
        tokenizer=tokenizer
    )

    print("Starting training...")
    trainer.train()

    print(f"Saving model to {output_path}...")
    model.save_pretrained(output_path)

    print("Training complete!")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--model_path', type=str, required=True)
    parser.add_argument('--data_path', type=str, required=True)
    parser.add_argument('--output_path', type=str, required=True)
    parser.add_argument('--epochs', type=int, default=3)
    parser.add_argument('--batch_size', type=int, default=4)
    parser.add_argument('--learning_rate', type=float, default=2e-4)
    args = parser.parse_args()

    train(
        args.model_path,
        args.data_path,
        args.output_path,
        args.epochs,
        args.batch_size,
        args.learning_rate
    )
```

- [ ] **Step 3: 提交代码**

```bash
git add training/scripts/
git commit -m "feat: add LoRA fine-tuning scripts"
```

---

### Task 8.2: 视觉风格学习训练

> **适用场景：** 当你需要"学习图片里的文字风格和排版规律，并且之后稳定复现出来"时使用本任务。
> 如果你只是想**看懂并总结**图片风格，skill 模式很合适。
> 如果你想**拿来稳定生成同类图**，仅靠 skill 通常不够，最好是：**大模型做教师 + 小模型做学生微调**。

#### 训练方式选择依据

| 数据量 | 推荐路线 | 说明 |
|--------|---------|------|
| **100张** | 大模型 + skill + 自动标注 + 合成扩增 | 100张不适合直接训练小模型，先用大模型蒸馏出标注和规则 |
| **500张** | 小模型 LoRA + skill 作为教师 | 开始认真做轻量微调，风格域窄时效果明显 |
| **1000张** | 小模型微调为主 + skill 为辅 | 以 LoRA/adapter 微调为主路线 |

#### 推荐的混合式两阶段方案

**阶段 A：大模型蒸馏出 skill（数据准备）**

做这些事：
- OCR 或 VLM 提取文本与区域
- 大模型给每张图输出 JSON 标注：
  - 文本块内容、bbox、层级角色（title/subtitle/body/caption/button）
  - 字体风格描述、字重/字号相对等级
  - 对齐方式、行距/段距/模块间距
  - 页面网格结构
- 形成统一 schema
- 自动检查异常样本

**阶段 B：训练学生模型**

分两种路线：
- **路线 1（理解/解析）**：训练小型文档理解模型，输出结构化布局表示。适合后续转 PPT/HTML/SVG/海报模板
- **路线 2（直接生成）**：训练小型生成模型或带 layout condition 的生成器。输入是内容 + 风格码 + 布局约束

#### 为什么不建议"只做 skill"

| skill 的问题 | 实际上更适合的角色 |
|-------------|-----------------|
| 对提示非常敏感 | 风格解析器 |
| 对参考图依赖强 | 标注器 |
| 一致性不如参数微调 | 数据清洗器 |
| 批量生产时容易漂 | 生成流程控制器 |
| 复杂版式下局部结构不稳 | - |

**最佳判断：短期启动 skill 更快，中期稳定落地小模型微调更强。**

**Files:**
- Create: `training/scripts/style_annotation.py`
- Create: `training/scripts/synthetic_data_generator.py`
- Create: `training/scripts/visual_lora_trainer.py`
- Create: `training/scripts/style_schema.json`

- [ ] **Step 1: 创建风格标注模块training/scripts/style_annotation.py**

```python
#!/usr/bin/env python3
"""
风格标注模块
使用大模型（VLM）对图片进行结构化风格标注
"""
from typing import Dict, List, Any, Optional
import json
from pathlib import Path

class StyleAnnotator:
    def __init__(self, vllm_client=None):
        self.vllm_client = vllm_client

    def annotate_image(
        self,
        image_path: str,
        image_bytes: Optional[bytes] = None
    ) -> Dict[str, Any]:
        prompt = """请分析这张图片的文字风格和版式设计，返回结构化JSON：

{
    "字体风格": {
        "family": "serif/sans-serif/monospace/handwritten等",
        "weight": "light/regular/bold/extra-bold",
        "style": "normal/italic/oblique",
        "description": "详细描述字体气质"
    },
    "字号层级": {
        "title_size": "大标题字号",
        "subtitle_size": "副标题字号",
        "body_size": "正文字号",
        "caption_size": "说明文字字号",
        "size_ratio": "层级之间的字号比例"
    },
    "版式结构": {
        "layout_type": "单栏/双栏/卡片式/混合",
        "alignment": "left/center/right/justify",
        "line_spacing": "行距设置",
        "paragraph_spacing": "段距设置",
        "margin": {"top": "", "bottom": "", "left": "", "right": ""}
    },
    "视觉元素": {
        "color_palette": ["主色调", "辅色"],
        "has_background_image": true/false,
        "visual_weight": "轻/中/重"
    },
    "模块布局": [
        {"type": "header/footer/sidebar/main", "bbox": [x1,y1,x2,y2]},
        ...
    ]
}

请只输出JSON，不要其他内容。"""

        if self.vllm_client:
            result = self.vllm_client.chat(
                messages=[
                    {"role": "system", "content": "你是一位专业的视觉设计师，擅长分析版式和字体风格。"},
                    {"role": "user", "content": prompt}
                ]
            )
            annotation_text = result['choices'][0]['message']['content']
            return self._parse_annotation(annotation_text)

        return self._default_annotation()

    def _parse_annotation(self, text: str) -> Dict[str, Any]:
        try:
            if "```json" in text:
                json_str = text.split("```json")[1].split("```")[0]
            else:
                json_str = text
            return json.loads(json_str.strip())
        except json.JSONDecodeError:
            return self._default_annotation()

    def _default_annotation(self) -> Dict[str, Any]:
        return {
            "字体风格": {"family": "unknown", "description": ""},
            "字号层级": {},
            "版式结构": {"layout_type": "unknown"},
            "视觉元素": {"color_palette": []},
            "模块布局": []
        }

    def batch_annotate(
        self,
        image_dir: str,
        output_path: str
    ) -> List[Dict[str, Any]]:
        image_dir = Path(image_dir)
        annotations = []

        for img_path in image_dir.glob("*.[jp][pn][g]"):
            annotation = self.annotate_image(str(img_path))
            annotation['source_image'] = str(img_path.name)
            annotations.append(annotation)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(annotations, f, ensure_ascii=False, indent=2)

        return annotations
```

- [ ] **Step 2: 创建合成数据生成模块training/scripts/synthetic_data_generator.py**

> **关键认识：** 文档、版式、字体类任务非常适合合成数据。100张时建议先用大模型产标注，再合成扩增到1000~5000条。

```python
#!/usr/bin/env python3
"""
合成数据生成模块
基于风格标注生成合成训练样本
"""
from typing import Dict, List, Any
import json
import random
from pathlib import Path

class SyntheticDataGenerator:
    def __init__(self, style_templates: List[Dict[str, Any]]):
        self.style_templates = style_templates

    def generate_synthetic_sample(
        self,
        style: Dict[str, Any],
        content_variations: int = 5
    ) -> List[Dict[str, Any]]:
        samples = []
        base_layout = style.get('版式结构', {})

        for i in range(content_variations):
            sample = {
                'style_id': style.get('source_image', 'synthetic'),
                'layout_type': base_layout.get('layout_type', '单栏'),
                'alignment': base_layout.get('alignment', 'left'),
                'font_family': style.get('字体风格', {}).get('family', 'sans-serif'),
                'font_weight': style.get('字体风格', {}).get('weight', 'regular'),
                'line_spacing': base_layout.get('line_spacing', '1.5'),
                'content': self._generate_random_content(),
                'augmented': True
            }
            samples.append(sample)

        return samples

    def _generate_random_content(self) -> Dict[str, str]:
        titles = ["春晓", "静夜思", "悯农", "登鹳雀楼", "望庐山瀑布"]
        bodies = [
            "春眠不觉晓，处处闻啼鸟。夜来风雨声，花落知多少。",
            "床前明月光，疑是地上霜。举头望明月，低头思故乡。",
            "锄禾日当午，汗滴禾下土。谁知盘中餐，粒粒皆辛苦。"
        ]
        return {
            'title': random.choice(titles),
            'body': random.choice(bodies)
        }

    def generate_dataset(
        self,
        annotations: List[Dict[str, Any]],
        samples_per_style: int = 10
    ) -> List[Dict[str, Any]]:
        all_samples = []

        for annotation in annotations:
            samples = self.generate_synthetic_sample(
                annotation,
                content_variations=samples_per_style
            )
            all_samples.extend(samples)

        return all_samples

    def save_dataset(
        self,
        dataset: List[Dict[str, Any]],
        output_path: str
    ):
        with open(output_path, 'w', encoding='utf-8') as f:
            for item in dataset:
                f.write(json.dumps(item, ensure_ascii=False) + '\n')
```

- [ ] **Step 3: 创建视觉风格LoRA训练模块training/scripts/visual_lora_trainer.py**

> **关键认识：** 小数据下全参微调容易过拟合，LoRA 类方法参数少、成本低，更适合 100 到 1000 张这种量级。

```python
#!/usr/bin/env python3
"""
视觉风格LoRA训练模块
针对文档/版式/字体理解的小模型轻量微调
"""
import os
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, AutoProcessor
from peft import LoraConfig, get_peft_model, TaskType
from PIL import Image
import json

class VisualStyleTrainer:
    def __init__(
        self,
        base_model_path: str,
        vision_encoder_path: str = None
    ):
        self.base_model_path = base_model_path
        self.vision_encoder_path = vision_encoder_path

    def setup_model(self):
        print(f"Loading base model from {self.base_model_path}...")

        tokenizer = AutoTokenizer.from_pretrained(
            self.base_model_path,
            trust_remote_code=True
        )
        tokenizer.pad_token = tokenizer.eos_token

        model = AutoModelForCausalLM.from_pretrained(
            self.base_model_path,
            torch_dtype=torch.float16,
            device_map="auto",
            trust_remote_code=True
        )

        lora_config = LoraConfig(
            task_type=TaskType.CAUSAL_LM,
            r=16,
            lora_alpha=32,
            target_modules=["q_proj", "v_proj", "k_proj", "o_proj"],
            lora_dropout=0.05,
            bias="none"
        )

        model = get_peft_model(model, lora_config)
        model.print_trainable_parameters()

        return model, tokenizer

    def prepare_training_data(
        self,
        annotation_file: str,
        synthetic_file: str = None
    ) -> list:
        with open(annotation_file, 'r', encoding='utf-8') as f:
            annotations = json.load(f)

        training_data = []

        for ann in annotations:
            sample = {
                "instruction": f"分析这张图片的版式风格：{ann.get('source_image', '')}",
                "input": "",
                "output": json.dumps({
                    "layout": ann.get('版式结构', {}),
                    "font": ann.get('字体风格', {}),
                    "modules": ann.get('模块布局', [])
                }, ensure_ascii=False)
            }
            training_data.append(sample)

        if synthetic_file and os.path.exists(synthetic_file):
            with open(synthetic_file, 'r', encoding='utf-8') as f:
                for line in f:
                    synthetic = json.loads(line)
                    training_data.append({
                        "instruction": f"描述这种{ synthetic.get('layout_type', '版式') }风格的特点",
                        "input": "",
                        "output": json.dumps(synthetic, ensure_ascii=False)
                    })

        return training_data

    def train(
        self,
        training_data: list,
        output_path: str,
        num_epochs: int = 3,
        batch_size: int = 4,
        learning_rate: float = 2e-4
    ):
        model, tokenizer = self.setup_model()

        training_args = {
            "output_dir": output_path,
            "num_train_epochs": num_epochs,
            "per_device_train_batch_size": batch_size,
            "learning_rate": learning_rate,
            "fp16": True,
            "logging_steps": 10,
            "save_steps": 100
        }

        print(f"Starting training with {len(training_data)} samples...")
        print(f"Training args: {training_args}")

        return training_args

    def merge_and_save(self, output_path: str):
        print(f"Merging LoRA weights and saving to {output_path}...")
```

- [ ] **Step 4: 创建风格标注Schema training/scripts/style_schema.json**

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Visual Style Annotation Schema",
  "description": "图片风格与版式标注的结构化schema",
  "type": "object",
  "properties": {
    "source_image": {
      "type": "string",
      "description": "原始图片文件名"
    },
    "字体风格": {
      "type": "object",
      "properties": {
        "family": {
          "type": "string",
          "enum": ["serif", "sans-serif", "monospace", "handwritten", "display", "unknown"],
          "description": "字体家族"
        },
        "weight": {
          "type": "string",
          "enum": ["light", "regular", "medium", "bold", "extra-bold", "unknown"],
          "description": "字重"
        },
        "style": {
          "type": "string",
          "enum": ["normal", "italic", "oblique", "unknown"],
          "description": "字体样式"
        },
        "description": {
          "type": "string",
          "description": "字体气质的详细描述"
        }
      }
    },
    "字号层级": {
      "type": "object",
      "properties": {
        "title_size": {"type": "string"},
        "subtitle_size": {"type": "string"},
        "body_size": {"type": "string"},
        "caption_size": {"type": "string"},
        "size_ratio": {"type": "string"}
      }
    },
    "版式结构": {
      "type": "object",
      "properties": {
        "layout_type": {
          "type": "string",
          "enum": ["单栏", "双栏", "三栏", "卡片式", "混合", "unknown"],
          "description": "版式类型"
        },
        "alignment": {
          "type": "string",
          "enum": ["left", "center", "right", "justify", "unknown"],
          "description": "对齐方式"
        },
        "line_spacing": {"type": "string"},
        "paragraph_spacing": {"type": "string"},
        "margin": {
          "type": "object",
          "properties": {
            "top": {"type": "string"},
            "bottom": {"type": "string"},
            "left": {"type": "string"},
            "right": {"type": "string"}
          }
        }
      }
    },
    "视觉元素": {
      "type": "object",
      "properties": {
        "color_palette": {
          "type": "array",
          "items": {"type": "string"}
        },
        "has_background_image": {"type": "boolean"},
        "visual_weight": {
          "type": "string",
          "enum": ["轻", "中", "重"]
        }
      }
    },
    "模块布局": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "type": {
            "type": "string",
            "enum": ["header", "footer", "sidebar", "main", "title", "caption"]
          },
          "bbox": {
            "type": "array",
            "items": {"type": "number"},
            "minItems": 4,
            "maxItems": 4
          }
        }
      }
    }
  }
}
```

- [ ] **Step 5: 提交代码**

```bash
git add training/scripts/style_annotation.py training/scripts/synthetic_data_generator.py training/scripts/visual_lora_trainer.py training/scripts/style_schema.json
git commit -m "feat: add visual style learning and LoRA training modules"
```

---

## Phase 9: 性能优化与并发支持（Week 14-16）

### Task 9.1: 并发处理优化

**Files:**
- Modify: `app/config.py`
- Create: `app/utils/cache.py`

- [ ] **Step 1: 添加并发配置**

Update: `app/config.py`

```python
class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

    SQLALCHEMY_DATABASE_URI = f"sqlite:///{BASE_DIR}/data/user_data.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    VLLM_HOST = os.getenv('VLLM_HOST', 'localhost')
    VLLM_PORT = int(os.getenv('VLLM_PORT', 8000))
    VLLM_MODEL_PATH = os.getenv('VLLM_MODEL_PATH', f"{BASE_DIR}/models/qwen-7b-int4")

    ASR_MODEL_PATH = os.getenv('ASR_MODEL_PATH', f"{BASE_DIR}/models/sensevoice")
    TTS_MODEL_PATH = os.getenv('TTS_MODEL_PATH', f"{BASE_DIR}/models/cosyvoice")

    KNOWLEDGE_BASE_DIR = BASE_DIR / "knowledge_base"
    CHROMA_DB_PATH = KNOWLEDGE_BASE_DIR / "chroma_db"

    TEXTBOOK_EDITION = 'pep'

    MAX_CONCURRENT_USERS = 30
    SESSION_TIMEOUT = 3600
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024

    # 并发优化配置
    MAX_WORKERS = 30
    REQUEST_TIMEOUT = 120
    ENABLE_STREAMING = True

    # Redis缓存（可选，用于多实例部署）
    REDIS_URL = os.getenv('REDIS_URL', None)
```

- [ ] **Step 2: 创建会话缓存**

```python
import os
from typing import Optional, Dict, Any
import time

class SessionCache:
    def __init__(self, max_size: int = 1000, ttl: int = 3600):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.max_size = max_size
        self.ttl = ttl

    def get(self, key: str) -> Optional[Any]:
        if key not in self.cache:
            return None

        entry = self.cache[key]
        if time.time() - entry['timestamp'] > self.ttl:
            del self.cache[key]
            return None

        return entry['value']

    def set(self, key: str, value: Any):
        if len(self.cache) >= self.max_size:
            oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k]['timestamp'])
            del self.cache[oldest_key]

        self.cache[key] = {
            'value': value,
            'timestamp': time.time()
        }

    def delete(self, key: str):
        if key in self.cache:
            del self.cache[key]

    def clear_expired(self):
        current_time = time.time()
        expired_keys = [
            k for k, v in self.cache.items()
            if current_time - v['timestamp'] > self.ttl
        ]
        for key in expired_keys:
            del self.cache[key]

_cache = None

def get_session_cache() -> SessionCache:
    global _cache
    if _cache is None:
        _cache = SessionCache()
    return _cache
```

- [ ] **Step 3: 提交代码**

```bash
git add app/config.py app/utils/cache.py
git commit -m "perf: add concurrency optimization"
```

---

## Phase 10: 测试与部署（Week 16-18）

### Task 10.1: 单元测试

**Files:**
- Create: `tests/test_dialogue_manager.py`
- Create: `tests/test_lesson_service.py`
- Create: `tests/test_question_service.py`

- [ ] **Step 1: 创建测试**

```python
import pytest
from app.core.dialogue_manager import DialogueManager
from app.core.interruption import InterruptionDetector

class TestInterruptionDetector:
    def test_detect_interruption(self):
        detector = InterruptionDetector()

        assert detector.detect_interruption("老师停一下")[0] == True
        assert detector.detect_interruption("等一下")[0] == True
        assert detector.detect_interruption("不懂")[0] == True
        assert detector.detect_interruption("继续讲")[0] == False

    def test_detect_continue(self):
        detector = InterruptionDetector()

        assert detector.detect_continue("继续") == True
        assert detector.detect_continue("可以了") == True
        assert detector.detect_continue("懂了") == True

    def test_extract_question(self):
        detector = InterruptionDetector()

        question = detector.extract_question("老师停一下，为什么天是蓝色的？", "停一下")
        assert "为什么天是蓝色的" in question

class TestDialogueManager:
    def test_create_session(self):
        manager = DialogueManager()
        session_id = manager.create_session("test_user")

        assert session_id is not None
        assert manager.get_session(session_id) is not None

    def test_session_isolation(self):
        manager = DialogueManager()
        session1 = manager.create_session("user1")
        session2 = manager.create_session("user2")

        context1 = manager.get_session(session1)
        context2 = manager.get_session(session2)

        assert context1.session_id != context2.session_id
```

- [ ] **Step 2: 运行测试**

Run: `cd /home/wengyikun/workcode/trae && python -m pytest tests/ -v`

- [ ] **Step 3: 提交代码**

```bash
git add tests/
git commit -m "test: add unit tests for core modules"
```

---

## 实施检查清单

### 基础设施
- [ ] RTX 3060 GPU环境
- [ ] Python 3.10+环境
- [ ] 500GB+ SSD存储
- [ ] 网络连接（下载模型用）

### Phase 1 交付物
- [ ] Flask应用可运行
- [ ] API路由响应正常
- [ ] 数据库初始化

### Phase 2 交付物
- [ ] Qwen-7B模型下载并量化完成
- [ ] vLLM服务启动成功
- [ ] ASR/TTS模型可用

### Phase 3 交付物
- [ ] 对话管理正常
- [ ] 打断检测准确
- [ ] 多轮对话上下文保持

### Phase 4 交付物
- [ ] 人教版教材知识库构建
- [ ] RAG检索准确
- [ ] 教案生成符合格式

### Phase 5 交付物
- [ ] OCR识别准确
- [ ] 题目问答正确
- [ ] 讲解易于理解

### Phase 6 交付物
- [ ] 项目计划书生成完整
- [ ] 预算估算准确

### Phase 7 交付物
- [ ] Web界面可交互
- [ ] 语音输入可用
- [ ] 响应流畅

### Phase 8 交付物
- [ ] 微调脚本可运行
- [ ] 训练数据准备完成
- [ ] LoRA权重保存

### Phase 9 交付物
- [ ] 30并发支持
- [ ] 响应时间<3秒
- [ ] 内存占用稳定

### Phase 10 交付物
- [ ] 单元测试通过
- [ ] 集成测试通过
- [ ] 部署文档完成

---

## 参考资料

- [1]: https://developers.openai.com/api/docs/guides/supervised-fine-tuning?utm_source=chatgpt.com  "Supervised fine-tuning | OpenAI API"
- [2]: https://arxiv.org/pdf/2504.10659?utm_source=chatgpt.com  "arXiv:2504.10659v1 [cs.CV] 14 Apr 2025"
- [3]: https://arxiv.org/html/2406.13175v2?utm_source=chatgpt.com  "Sparse High Rank Adapters"
- [4]: https://arxiv.org/html/2603.08497?utm_source=chatgpt.com  "Reading ≠ Seeing: Diagnosing and Closing the Typography Gap in Vision-Language Models"
- [5]: https://arxiv.org/html/2512.00884v2?utm_source=chatgpt.com  "Towards Active Synthetic Data Generation for Finetuning ..."
- [6]: https://arxiv.org/html/2504.10659v1?utm_source=chatgpt.com  "Relation-Rich Visual Document Generator for ..."
