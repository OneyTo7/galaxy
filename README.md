# 智学 · AI 认知诊断实验教学平台（校园方向）

> 不只是判对错，更看见学生怎么错、卡在哪个点，并给出针对性练习。

参赛作品。主链路：**AI 命题 → 沙箱提交 → 评测 → 误区诊断 → 变式练习 → 学情报告**，全程有状态、有积累、有闭环。

## 技术栈

| 端 | 选型 | 备注 |
| --- | --- | --- |
| 后端 | Python 3.12 + FastAPI + SQLAlchemy 2.0 + Alembic | 模块化单体，DDD 限界上下文 |
| 前端 | Vue 3 + TypeScript + Vite + Element Plus + ECharts | `<script setup>` + Pinia |
| AI | LangChain + httpx 调移动云 MoMA | MOCK=1 离线可演示 |
| 基础设施 | PostgreSQL + Redis + MinIO | Docker Compose 一键部署 |

## 目录结构

```
galaxy/
├── backend/            # FastAPI 单体：app/core + app/contexts/<限界上下文>/
├── frontend/           # Vue 3 前端
├── docs/               # 项目方案 / 开发方案 / 前端设计规范 / 权限矩阵 / 深化改造方案
├── .zhanlu/skills/     # 工程规范：fastapi / vue3 / architecture / code-review
└── docker-compose.yml  # backend + worker（评测进程）
```

## 快速开始

### 前置

- Python 3.12+、Node 18+、PostgreSQL、Redis
- 比赛环境用移动云 MoMA；本地开发用 `MOCK=1` 跑通全链路

### 后端

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env              # 编辑数据库/Redis/MoMA 配置
alembic upgrade head              # 迁移
MOCK=1 python scripts/seed_demo.py  # 种子数据（知识点+用户+作业+提交+掌握度）
MOCK=1 uvicorn app.main:app --reload --port 8000      # API
MOCK=1 python -m app.worker                          # 评测 worker（另开终端）
```

### 前端

```bash
cd frontend
npm install
npm run dev        # http://localhost:5173（proxy /api → 8000）
npm run build      # 类型检查 + 构建
```

### 演示账号

| 用户名 | 密码 | 角色 |
| --- | --- | --- |
| teacher1 | 123456 | 教师 |
| studentA | 123456 | 学生 |

## 核心能力

- **受控知识点体系**：20 个入门编程知识点 + Q 矩阵（作业 × 知识点），诊断 prompt 约束模型只能从中选择
- **BKT 学生掌握度模型**：每个学生每个知识点维护贝叶斯知识追踪概率，跨提交持续更新
- **误区诊断 + evidence 事实校验**：LLM 输出的 evidence 必须命中真实报错/失败用例，不命中则重试或降级
- **变式闭环**：按掌握度自适应选难度 → 生成可提交的 practice 作业 → 提交后掌握度更新 → 误区自动标记"已克服"
- **学情看板**：班级知识点掌握度热力图 + 个人雷达 + 成长曲线 + 风险预警
- **反作弊**：代码 token 指纹 + winnowing + Jaccard 相似度为主，LLM 判 AI 代写降级为辅助

## 文档

- [开发方案](docs/) — 里程碑、分工、接口契约
- [深化改造方案](docs/) — D1-D5 设计细节
- [权限矩阵](docs/权限矩阵.md) — RBAC 端点权限
- [前端设计规范](docs/) — 色板/排版/组件
- [后端 README](backend/README.md) — 架构分层、限界上下文、迁移
- [前端 README](frontend/README.md) — 页面、API 模块、设计系统

## 部署

```bash
docker compose up -d
```

详见 [docker-compose.yml](docker-compose.yml)。
