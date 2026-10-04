# backend

FastAPI 模块化单体 + DDD 限界上下文。14 个限界上下文，导入只向下流：Router → Service → Repository → Provider，不跨上下文直查表。

## 运行

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
MOCK=1 python scripts/seed_demo.py      # 种子数据
MOCK=1 uvicorn app.main:app --reload --port 8000
MOCK=1 python -m app.worker             # 评测 worker（另开终端）
```

- OpenAPI 文档（即前端契约）：http://localhost:8000/docs
- 健康检查：http://localhost:8000/health

## 配置

`.env` 关键变量（不入 git，模板 `.env.example`）：

| 变量 | 默认 | 说明 |
| --- | --- | --- |
| `DATABASE_URL` | `sqlite:///./dev.db` | PostgreSQL 生产 / SQLite 本地 |
| `REDIS_URL` | 空 | 评测提交队列；空时走同步路径 |
| `MOCK` | `1` | diagnose/variant/命题等 AI 模块返回固定 JSON，不调真 MoMA |
| `SANDBOX_MODE` | `subprocess` | `subprocess`（本地）或 `docker`（隔离沙箱） |
| `MOMA_*` | — | MoMA 端点/key/model，只走 env 不写死 |

## 限界上下文

```
app/contexts/
├── user/           # 用户 / 角色 / 鉴权（JWT）
├── organization/   # 课程 / 班级 / 选课
├── assignment/     # 作业 / 用例 / AI 命题
├── submission/     # 提交（含 practice 属主校验）
├── evaluation/     # 评测引擎：沙箱执行 / 逐用例评分
├── mastery/        # BKT 掌握度模型 + 事件流（核心）
├── diagnose/       # 误区诊断 + evidence 事实校验 + 受控知识点收敛
├── variant/        # 变式生成 + practice 作业闭环
├── report/         # 学情聚合 API（含 mastery_summary）
├── grade/          # 成绩册
├── appeal/         # 申诉状态机
├── cheating/       # 反作弊：代码相似度 + AI 辅助
├── audit/          # 审计日志
└── ai/             # MoMA LLM 共享封装
```

每个上下文结构：`router.py` / `service.py` / `repository.py` / `models.py` / `schemas.py` / `deps.py` + `providers/`。

## 分层铁律（详见 .zhanlu/skills/fastapi/SKILL.md）

- **Router**：≤10 行可执行代码，声明 `response_model=`，禁止 import sqlalchemy/httpx/models/repository
- **Service**：禁止 import sqlalchemy/httpx/FastAPI（含 HTTPException）；构造注入 Protocol 类型依赖；抛领域异常（`core/exceptions.py` 的 DomainError 子类）
- **Repository**：唯一可 import sqlalchemy 的层
- **Provider**（`providers/`）：唯一可 import httpx 的层；返回类型化结果或 `ProviderError`，每个外部服务独立 httpx.AsyncClient（bulkhead）

## 核心模块说明

### mastery（BKT 掌握度）

- `bkt.py`：纯函数，似然更新 + 学习转移 + 状态判定 + 难度选择，无 IO 便于单测
- `record_submission(submission_id)`：worker 评分后调用，按 Q 矩阵标签为每个知识点记一次观测（加权通过率 ≥ 0.6 为正证据）
- `record_diagnosis(...)`：诊断入库后调用，记一次负证据（二手信号，降权）
- `apply_event`：原子操作（单次 commit），并发下唯一约束 `uq_mastery_event_once` 保证幂等
- 误区克服：知识点出现正确观测 → `mark_open_overcome` 翻转 `misconceptions.status` open→overcome

### diagnose（诊断 + 校验）

- `validator.py`：evidence 事实校验纯函数，三条命中规则（stderr 公共子串 / case_id / 代码片段）
- `resolver.py`：受控知识点解析，code 精确 → name 精确 → name 模糊包含
- 校验不通过重试 1 次 → 仍不通过降级为规则标签，置信度减半，`evidence_validated=False`

### variant（变式闭环）

- 按掌握度选难度：<0.4 easy / 0.4-0.7 medium / >0.7 hard
- 生成后建 practice 作业（`kind=practice`，`course_id=None` 绕开选课校验，`assigned_user_id` 限定目标学生）
- 幂等：同一诊断已有变式直接返回

### cheating（反作弊）

- `similarity.py`：去注释 → token 归一化（标识符→ID，数字→LIT）→ k-gram winnowing 指纹 → Jaccard
- ≥80 flagged / 60-79 suspected / <60 不报告
- LLM 判 AI 代写降级为辅助：单独命中只 suspected

## 数据库迁移

```bash
alembic upgrade head          # 应用所有迁移
alembic revision --autogenerate -m "描述"  # 生成新迁移
```

迁移文件在 `migrations/versions/`。`env.py` 导入了所有上下文的 models 以支持 autogenerate。

## 种子脚本

```bash
MOCK=1 python scripts/seed_demo.py            # 幂等：已有则跳过
MOCK=1 python scripts/seed_demo.py --reset      # 清空 mastery+知识点后重建
```

生成：20 个知识点 + 3 用户（teacher1/studentA/studentB）+ 2 作业 + Q 矩阵 + 学生提交 + BKT 掌握度。

## worker

独立评测进程，消费 Redis 提交队列：

```bash
python -m app.worker
```

流程：`consume_submission` → 评测 → 评分 → `record_submission`（掌握度）。mastery 失败不回滚评分（独立 try/except + `logging.exception`）。
