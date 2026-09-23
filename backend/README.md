# backend

FastAPI 模块化单体 + DDD 限界上下文。

## 运行

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

- OpenAPI 文档（即前端契约）：http://localhost:8000/docs
- 健康检查：http://localhost:8000/health

## 分层（见 `.zhanlu/skills/fastapi/SKILL.md`）

`app/contexts/<限界上下文>/{router,service,repository,models,schemas,deps}.py` + `providers/`
导入只向下流：Router → Service → Repository → Provider，不跨上下文直查表。
