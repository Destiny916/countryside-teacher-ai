# Village Teacher Assistant

这是乡村老师助教系统的 Phase 1 基础框架初始化结果，当前已完成 Flask 应用骨架、基础配置和 Task 1.2 的 API 路由框架。

## 已完成

- `requirements.txt`：按计划列出后续 Phase 1 所需依赖
- `app/config.py`：集中配置 `BASE_DIR` 与运行参数
- `app/__init__.py`：Flask 应用工厂 `create_app`
- `app/api/`：Task 1.2 的路由框架与蓝图注册入口
- `app/core/`、`app/models/`、`app/services/`、`app/utils/`：空模块骨架，供后续阶段扩展
- `run.py`：统一启动入口

## 运行与验证

安装 Phase 1 轻量运行依赖：

```bash
python -m pip install flask==3.0.0 flask-cors==4.0.0 flask-restful==0.3.10
```

验证应用工厂是否可创建：

```bash
python -c "from app import create_app; app = create_app(); print('App created successfully')"
```

用 Flask test client 验证路由骨架：

```bash
python - <<'PY'
from app import create_app

app = create_app()
client = app.test_client()
checks = [
    ("GET", "/api/chat/"),
    ("POST", "/api/chat/session"),
    ("POST", "/api/voice/input"),
    ("POST", "/api/voice/output"),
    ("GET", "/api/lesson/"),
    ("POST", "/api/lesson/"),
    ("GET", "/api/lesson/7"),
    ("POST", "/api/question/"),
    ("GET", "/api/question/8"),
    ("POST", "/api/project/"),
]
for method, path in checks:
    response = getattr(client, method.lower())(path)
    assert response.status_code == 200, (method, path, response.status_code, response.get_json())
print("API smoke OK")
PY
```

启动服务：

```bash
python run.py
```

## 当前说明

- Task 1.2 已完成以下路由骨架：
  - `GET /api/chat/` 和 `POST /api/chat/`
  - `POST /api/chat/session`
  - `POST /api/voice/input` 和 `POST /api/voice/output`
  - `GET /api/lesson/`、`POST /api/lesson/`、`GET /api/lesson/<plan_id>`
  - `POST /api/question/`、`GET /api/question/<question_id>`
  - `POST /api/project/`
- 验证命令：
  - `python -B -c "import ast, pathlib; files=['app/api/__init__.py','app/api/chat.py','app/api/voice.py','app/api/lesson.py','app/api/question.py','app/api/project.py','app/core/__init__.py','app/models/__init__.py','app/services/__init__.py','app/utils/__init__.py']; [ast.parse(pathlib.Path(f).read_text()) for f in files]; print('Syntax OK')"`
  - 结果：`Syntax OK`
  - `python -c "from app import create_app; app = create_app(); print('App created successfully')"`
  - 结果：`App created successfully`
  - Flask test client 路由 smoke test
  - 结果：`API smoke OK`
- 当前只安装了 Phase 1 路由验证所需的轻量 Flask 依赖，以及模型服务单元测试所需的 `pytest`；`vLLM`、`PaddleOCR`、`Chroma` 等模型与数据依赖留到后续阶段按任务安装。

## Phase 2 模型服务

本阶段补齐了本地 vLLM 推理服务相关的最小工具层，仍然保持“按需调用，不自动启动”的原则：

- `model_service/inference.py`：提供 `VLLMClient`，默认从 `VLLM_HOST` 和 `VLLM_PORT` 读取服务地址，或回退到 `localhost:8000`
- `model_service/vllm_server.py`：提供 `build_vllm_command(...)` 和 `start_vllm_server(...)`，用于显式生成并启动 vLLM 命令
- `model_service/quantize.py`：提供 `default_quant_config()` 和 `quantize_model(...)`，AWQ 相关重依赖只在函数内部导入

验证命令：

```bash
pytest -q tests/test_model_service.py
```

说明：

- 这些模块不会在导入时自动启动 vLLM
- 这些模块不会自动下载模型
- 量化和服务启动都需要在调用对应函数或 CLI 时才会发生
