# 乡村老师助教系统

这是乡村老师助教系统的完整实现，支持实时语音教学、智能备课（人教版教材）、题库问答，以及技能管理功能。

## 已完成的功能

### 核心功能
- **对话管理**：支持多轮对话、教学模式、打断检测
- **语音处理**：语音识别（ASR）和语音合成（TTS）
- **RAG知识库**：基于Chroma向量数据库的教材内容检索
- **教案生成**：根据年级、学科、课题生成标准教案
- **题库问答**：支持图片题目OCR识别和详细解答
- **项目计划**：生成乡村教育数字化项目计划书
- **技能管理**：从GitHub仓库读取和使用技能

### 技术实现
- `app/config.py`：集中配置管理
- `app/__init__.py`：Flask应用工厂
- `app/api/`：API路由（chat、voice、lesson、question、project、skill）
- `app/core/`：核心模块（dialogue_manager、interruption、asr_handler、tts_handler、ocr_handler、rag_engine）
- `app/services/`：业务服务（lesson_service、question_service、project_service、skill_service）
- `app/static/`：前端资源（CSS、JavaScript）
- `app/templates/`：前端模板
- `run.py`：统一启动入口

## 运行与验证

### 安装依赖

```bash
pip install -r requirements.txt
```

### 配置说明

系统支持三种模型服务模式，可在 `.env` 文件中配置：

```bash
# API类型：local（本地vLLM）、nvidia（NVIDIA API）、silicon_flow（硅基流动API）
API_TYPE=silicon_flow

# 硅基流动API配置
SILICON_FLOW_API_KEY=sk-czzpwrzncqygoqmwdtojcmmsfgwzdnoqgrruarzdcrfjzzgn
SILICON_FLOW_BASE_URL=https://api.siliconflow.cn/v1
SILICON_FLOW_MODEL=deepseekv3.2
```

### 启动服务

```bash
python run.py
```

### 验证API

```bash
# 测试会话创建
curl -X POST http://localhost:5000/api/chat/session -H "Content-Type: application/json" -d '{"user_id": "test_user"}'

# 测试对话功能
curl -X POST http://localhost:5000/api/chat/ -H "Content-Type: application/json" -d '{"session_id": "SESSION_ID", "text": "你好，小慧老师！"}'

# 测试技能管理
curl http://localhost:5000/api/skills/

# 测试教案生成
curl -X POST http://localhost:5000/api/lesson/ -H "Content-Type: application/json" -d '{"grade": 1, "subject": "math", "topic": "分数的认识"}'
```

## 功能说明

### 1. 问答模式
- 支持文本和语音输入
- 智能对话，支持打断和恢复
- 适合学生提问和日常交流

### 2. 教学模式
- 输入教学主题和大纲
- 系统会按照大纲逐步讲解
- 支持中途提问和打断

### 3. 备课模式
- 选择年级、学科和课题
- 自动生成符合人教版标准的教案
- 包含教学目标、重点难点、教学过程等

### 4. 项目计划
- 输入学校基本信息
- 生成乡村教育数字化项目计划书
- 包含预算估算和实施计划

### 5. 技能管理
- 从 GitHub 仓库自动拉取技能
- 支持查看和使用技能
- 技能会自动保存到本地

## 技能管理功能

技能管理功能允许系统从 GitHub 仓库读取和使用技能，具体实现：

1. **技能来源**：从 `https://github.com/Destiny916/frequent-skill.git` 仓库拉取
2. **本地缓存**：技能会保存到本地，下次启动时优先使用本地缓存
3. **使用方式**：在前端界面的"技能管理"模式中查看和使用技能

## 技术架构

- **后端**：Flask + vLLM/API服务
- **存储**：SQLite/Chroma向量数据库
- **语音交互**：SenseVoice/CosyVoice
- **OCR**：PaddleOCR
- **前端**：HTML/CSS/JavaScript

## 系统状态

系统已经完整实现，包含所有核心功能，可以正常运行。用户可以通过前端界面使用所有功能，包括技能管理。
