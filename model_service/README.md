# 模型服务

本目录包含乡村老师助教系统的模型服务相关脚本。

## 模型列表

| 模型 | 用途 | 大小 | HuggingFace ID |
|------|------|------|----------------|
| Qwen2.5-7B-Instruct | 对话生成 | ~14GB | Qwen/Qwen2.5-7B-Instruct |
| SenseVoice | 语音识别(ASR) | ~2GB | iic/SenseVoiceSmall |
| CosyVoice | 语音合成(TTS) | ~1GB | FunAudioLLM/CosyVoice-300M |
| Embedding | 向量嵌入 | ~500MB | sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2 |

## 快速开始

### 1. 下载模型

使用交互式脚本下载模型：

```bash
cd /home/wengyikun/workcode/trae
bash model_service/download.sh
```

或使用Python脚本：

```bash
cd /home/wengyikun/workcode/trae
/home/wengyikun/workcode/trae/.conda/bin/python model_service/download_models.py --model all
```

单独下载某个模型：

```bash
/home/wengyikun/workcode/trae/.conda/bin/python model_service/download_models.py --model embedding
/home/wengyikun/workcode/trae/.conda/bin/python model_service/download_models.py --model qwen
```

### 2. 检查模型状态

```bash
/home/wengyikun/workcode/trae/.conda/bin/python model_service/manage_models.py --check
```

### 3. 启动模型服务

启动vLLM服务器（用于Qwen对话）：

```bash
/home/wengyikun/workcode/trae/.conda/bin/python model_service/start_all.py
```

或者直接启动vLLM：

```bash
/home/wengyikun/workcode/trae/.conda/bin/python model_service/vllm_server.py \
    --model_path /home/wengyikun/workcode/trae/models/qwen-7b \
    --port 8000
```

## 脚本说明

### download_models.py

模型下载脚本，支持以下参数：
- `--model`: 选择要下载的模型 (qwen/sensevoice/cosyvoice/embedding/all)
- `--no-resume`: 重新下载，不使用断点续传

### download.sh

Bash脚本，提供交互式下载界面。

### manage_models.py

模型管理脚本，支持：
- `--check`: 检查模型状态

### start_all.py

启动所有模型服务的脚本。

### vllm_server.py

vLLM服务器启动脚本，支持参数：
- `--model_path`: 模型路径
- `--port`: 服务端口 (默认8000)
- `--gpu_memory_utilization`: GPU内存利用率 (默认0.85)
- `--max_model_len`: 最大模型长度 (默认8192)
- `--tensor_parallel_size`: 张量并行大小 (默认1)

### inference.py

vLLM客户端封装，提供与OpenAI API兼容的接口。

## 模型路径配置

模型默认保存在 `../models/` 目录下：

```
/home/wengyikun/workcode/trae/
└── models/
    ├── qwen-7b/           # Qwen2.5-7B
    ├── sensevoice/        # SenseVoice
    ├── cosyvoice/         # CosyVoice
    └── embedding/         # Embedding模型
```

如需更改模型路径，可通过环境变量或config.py配置。

## vLLM API使用示例

启动服务后，可通过以下方式调用：

```python
from model_service.inference import get_vllm_client

client = get_vllm_client()

# 对话
result = client.chat(
    messages=[
        {"role": "system", "content": "你是一位小学老师。"},
        {"role": "user", "content": "春天的特点有哪些？"}
    ],
    temperature=0.7
)

print(result['choices'][0]['message']['content'])
```

## 注意事项

1. **首次下载**：大模型（如Qwen2.5-7B）首次下载可能需要较长时间
2. **磁盘空间**：确保有足够的磁盘空间（建议100GB以上）
3. **GPU**：vLLM需要GPU运行，确保CUDA环境配置正确
4. **内存**：Qwen2.5-7B至少需要8GB显存，建议12GB以上
