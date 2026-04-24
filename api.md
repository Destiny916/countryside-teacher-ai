# 模型网关 API 文档

## 概述

模型网关 API 提供了一个统一的接口来管理多个模型后端，支持本地 vLLM 和远程 API（如 NVIDIA、智谱 DeepSeek、百度千帆等）之间的切换。

## 后端类型

| 后端类型 | 描述 | 配置 |
|----------|------|------|
| `local_vllm` | 本地 vLLM 服务 | `VLLM_HOST`, `VLLM_PORT` |
| `remote_nvidia` | NVIDIA NGC API | `OPENAI_API_KEY`, `NVIDIA_MODEL` |
| `remote_zhipu` | 智谱 AI | `ZHIPU_API_KEY` |
| `remote_deepseek` | DeepSeek | `DEEPSEEK_API_KEY` |
| `remote_qianfan` | 百度千帆 | `QIANFAN_API_KEY`, `QIANFAN_SECRET_KEY` |

## API 端点

### 1. 模型状态

获取所有后端的状态。

```
GET /api/model/status
```

**响应示例：**
```json
{
  "success": true,
  "data": {
    "primary": "remote_nvidia",
    "fallbacks": ["local_vllm"],
    "backends": {
      "remote_nvidia": {
        "name": "remote_z-ai/glm-5.1",
        "available": true,
        "is_primary": true,
        "is_fallback": false
      },
      "local_vllm": {
        "name": "local_vllm_qwen-7b",
        "available": false,
        "is_primary": false,
        "is_fallback": true
      }
    }
  }
}
```

### 2. 可用模型列表

列出所有已注册的后端。

```
GET /api/model/list
```

**响应示例：**
```json
{
  "success": true,
  "data": [
    {"type": "remote_nvidia", "name": "remote_z-ai/glm-5.1", "available": true},
    {"type": "local_vllm", "name": "local_vllm_qwen-7b", "available": false}
  ]
}
```

### 3. 切换主后端

切换主要使用的模型后端。

```
POST /api/model/switch
```

**请求体：**
```json
{
  "backend_type": "local_vllm"
}
```

**响应示例：**
```json
{
  "success": true,
  "message": "Switched to local_vllm"
}
```

### 4. 管理 fallback

添加或移除 fallback 后端。

```
POST /api/model/fallback
```

**请求体：**
```json
{
  "backend_type": "local_vllm",
  "action": "add"  // 或 "remove"
}
```

### 5. 对话接口

使用当前配置的后端进行对话。

```
POST /api/model/chat
```

**请求体：**
```json
{
  "messages": [
    {"role": "system", "content": "你是一个有帮助的助手。"},
    {"role": "user", "content": "你好！"}
  ],
  "temperature": 0.7,
  "max_tokens": 2048,
  "top_p": 0.9,
  "stream": false,
  "backend_type": null,  // 可选，指定后端
  "use_fallback": true   // 当主后端不可用时是否使用 fallback
}
```

### 6. 注册新后端

动态注册一个新的后端。

```
POST /api/model/register
```

**请求体：**
```json
{
  "backend_type": "remote_zhipu"
}
```

## 使用示例

### Python 示例

```python
import requests

# 1. 查看所有后端状态
response = requests.get("http://localhost:5000/api/model/status")
print(response.json())

# 2. 切换到本地 vLLM
response = requests.post(
    "http://localhost:5000/api/model/switch",
    json={"backend_type": "local_vllm"}
)
print(response.json())

# 3. 进行对话
response = requests.post(
    "http://localhost:5000/api/model/chat",
    json={
        "messages": [
            {"role": "user", "content": "你好，介绍一下你自己。"}
        ],
        "temperature": 0.7
    }
)
print(response.json())

# 4. 添加 fallback
response = requests.post(
    "http://localhost:5000/api/model/fallback",
    json={"backend_type": "remote_nvidia", "action": "add"}
)
print(response.json())
```

### cURL 示例

```bash
# 查看状态
curl http://localhost:5000/api/model/status

# 切换后端
curl -X POST http://localhost:5000/api/model/switch \
  -H "Content-Type: application/json" \
  -d '{"backend_type": "local_vllm"}'

# 对话
curl -X POST http://localhost:5000/api/model/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "你好！"}],
    "temperature": 0.7
  }'
```

## 环境变量配置

在 `.env` 文件中配置：

```bash
# 默认后端 (remote_nvidia / local_vllm / remote_zhipu / remote_deepseek / remote_qianfan)
DEFAULT_BACKEND=remote_nvidia

# NVIDIA API
OPENAI_API_KEY=your-nvidia-api-key
OPENAI_BASE_URL=https://integrate.api.nvidia.com/v1
NVIDIA_MODEL=z-ai/glm-5.1

# 本地 vLLM
VLLM_HOST=localhost
VLLM_PORT=8000
VLLM_MODEL_NAME=qwen-7b

# 智谱 AI
ZHIPU_API_KEY=your-zhipu-api-key

# DeepSeek
DEEPSEEK_API_KEY=your-deepseek-api-key

# 百度千帆
QIANFAN_API_KEY=your-qianfan-api-key
QIANFAN_SECRET_KEY=your-qianfan-secret-key
```

## 故障排除

1. **后端不可用**：检查网络连接和 API key 是否正确配置
2. **切换失败**：确保目标后端已注册且可用
3. **对话超时**：增加 `max_tokens` 或检查网络延迟
