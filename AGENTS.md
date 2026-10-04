# AGENTS.md — 智学 · AI 认知诊断实验教学平台（galaxy）

比赛项目（2026-09-24 ~ 2026-10-23）。主链路：AI 命题 → 沙箱提交 → 评测 → 误区诊断 → 变式练习 → 学情报告。
技术栈：FastAPI 模块化单体（DDD 限界上下文）+ Vue 3 + TS + Vite。所有文档/提交信息为中文。

## 目录结构

```
backend/            # FastAPI 单体：app/core + app/contexts/<限界上下文>/，alembic 迁移
frontend/           # Vue 3：<script setup> + Pinia + Element Plus + Monaco + ECharts
docs/               # 项目方案 / 开发方案 / 前端设计规范 / 权限矩阵（改对应区域前必读）
.zhanlu/skills/     # 项目工程规范：fastapi / vue3 / architecture / code-review / langchain
docker-compose.yml  # backend + worker（评测进程，挂 docker.sock）
```

13 个限界上下文：user / organization / assignment / submission / evaluation / diagnose / variant / ai / report / grade / appeal / cheating / audit。

## 常用命令

```bash
# 后端（http://localhost:8000/docs 即前端契约，/health 健康检查）
cd backend && source .venv/bin/activate
uvicorn app.main:app --reload --port 8000
python -m app.worker                                  # 独立评测进程，消费 Redis 提交队列
alembic upgrade head                                  # 迁移（backend/ 下执行）
python scripts/init_db.py                             # 初始化数据；另有 drop_all.py / terminate_locks.py

# 前端（5173，vite proxy /api → 8000）
cd frontend
npm run dev
npm run build        # vue-tsc -b && vite build —— 构建即类型检查，无独立 lint/test 命令

# 部署
docker compose up -d
```

无测试框架（无 pytest/vitest 配置）；验证以 OpenAPI /docs 手测 + `npm run build` 类型检查为准。

## 后端架构铁律（详见 .zhanlu/skills/fastapi/SKILL.md，改代码前先读）

- 每上下文 `router / service / repository / models / schemas / deps` + `providers/`，导入只向下流：**Router → Service → Repository → Provider**。
- **不跨上下文直查表**：模块间只 import 对方 service。
- Router：≤10 行可执行代码，声明 `response_model=`，禁止 import sqlalchemy/httpx/models/repository。
- Service：禁止 import sqlalchemy/httpx/FastAPI（含 HTTPException）；构造注入 Protocol 类型 repo；抛领域异常（`app/core/exceptions.py` 的 DomainError 子类，main.py 全局映射 HTTP 状态码）。
- Repository：唯一可 import sqlalchemy 的层，返回领域对象非 ORM 模型。
- Provider（`providers/`，如 MoMA）：唯一可 import httpx 的层；返回类型化结果或 `ProviderError`，**绝不返回原始 dict**；每个外部服务独立 httpx.AsyncClient（bulkhead），lifespan 关闭。
- 统一响应 `{code, message, data}`（`core/response.py` 的 `ok()`/`err()`）。
- 文件 LOC：400+ 规划拆分，600+ 必须先拆。
- 不装 DI 容器，用 FastAPI `Depends()` + `app/core/deps.py` 工厂。

## 前端约定（详见 .zhanlu/skills/vue3/SKILL.md + docs/前端设计规范.md）

- 组件 `<script setup>` + TS；`@` 别名指向 `src/`。
- 请求统一走 `src/utils/request.ts`（axios，baseURL `/api`，JWT 存 localStorage，401 自动清 token 跳 /login）；模块请求放 `src/api/*.ts`，不直接裸调 axios。
- Pinia 用 setup store，每域一文件（`stores/auth.ts`…）；state/getters 解构必须 `storeToRefs()`。
- Monaco 用 `components/CodeEditor.vue` 封装（v-model 取代码字符串）；图表用 vue-echarts `<v-chart>`。
- UI 严格遵守 docs/前端设计规范.md 的 CSS 变量 token：浅色底 `#F7F9FF`、主蓝 `#4F7CFF`、ECharts 固定 6 色板、圆角/阴影/间距变量、200ms ease-out；禁止网格/光晕/粒子/霓虹风。

## 鉴权与权限（RBAC，改端点前必读 docs/权限矩阵.md）

- JWT 含 `role`：`student / assistant / teacher / admin`；守卫在 `app/core/deps.py`（`get_current_user`、`require_teacher` 等、`require_staff` = teacher|assistant|admin）。
- 数据属主校验在后端：teacher 资源须 `course.teacher_id == user.id`，student 须 `submission.user_id == user.id`。前端按角色渲染菜单只是 UX，**不替代后端权限**；路由守卫目前只查 token 存在。
- 页面按角色分目录：`views/student/`、`views/teacher/`、`views/admin/`，路由集中注册在 `src/router/index.ts`。

## 配置与运行模式（backend/.env，不入 git，模板 .env.example）

- `MOCK=1`：diagnose / variant / 命题等 AI 模块返回固定 JSON，不调真 MoMA；切真只改 env。
- `SANDBOX_MODE=subprocess`（本地默认）| `docker`（真实隔离沙箱）。
- `DATABASE_URL` 默认 `sqlite:///./dev.db`；`REDIS_URL` 为空时提交队列不生效（评测走同步路径）。
- MoMA 端点/key/model 只走 `MOMA_*` env，不写死代码。

## 协作约定

- `main` 受保护，`feature/*` 分支合并；提交信息中文（feat/fix/style: 描述）。
- AI 模块（diagnose/variant/命题）是单体内模块，被其他上下文直接 import service 调用，不走 HTTP。
