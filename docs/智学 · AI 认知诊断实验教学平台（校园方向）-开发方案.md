# 智学 · AI 认知诊断实验教学平台（校园方向）-开发方案

> 时间窗：2026-09-24 ~ 2026-10-23（约 4 周，含国庆）
> 架构：**FastAPI 模块化单体 + DDD 限界上下文**，全栈 Python + Vue。
> 一期主链路必达，二期按进度裁剪。本文为开发依据，与 `项目方案.md`（参赛说明）互补。
> 阅读对象：队长（后端核心 / 前端骨架）、冰糖（AI 模块 / 前端看板）。标注【冰糖做】【队长做】【对接点】。

---

## 一、目标与范围

- **一期（必达，主链路）**：智能命题 → 沙箱提交 → 严格评测 → 误区诊断 → 变式练习 → 班级学情报告。
- **二期（按 W3 实际进度裁剪）**：申诉复核、反作弊 / AI 代写检测、成绩导出、跨课程看板、审计合规。
- **交付物**：可运行代码（后端单体 + 前端）+ 演示视频 + 参赛说明文档 + 部署验证记录（加分项）。

---

## 二、人员与分工

| 角色 | 成员 | 技术栈 | 职责 |
| --- | --- | --- | --- |
| 后端核心 / 前端骨架 | 队长（多年 Java，现用 Python） | Python(FastAPI)、Docker、Vue 3 | 架构、评测引擎 / 沙箱、提交 / 评测 / 学情 / 状态机 / 鉴权、部署、接口契约、**前端骨架与业务页**、联调主导 |
| AI 模块 / 前端看板 | 冰糖（大三，Vue / Python 熟，Java 在学） | Python、Vue 3、ECharts | **诊断 / 变式 / 命题模块**(调 MoMA)、**学情看板**(ECharts)、**诊断反馈页**、分担部分业务 CRUD、联调 |

**分工原则**：

- 全栈统一 **Python(FastAPI) + Vue**，两人共栈协同：队长主导核心模块（评测 / 沙箱 / 状态机 / 鉴权）+ 前端骨架与业务页；冰糖主导 AI 模块（诊断 / 变式 / 命题）+ 学情看板 / 反馈页，并可分担部分业务 CRUD（她 Python 熟）。
- **DDD 限界上下文**划分后端模块，**单体部署**，模块间走清晰 service 接口、不跨上下文直查表；未来可按上下文拆微服务。
- **评测沙箱**单独容器隔离执行学生代码（部署隔离，非微服务）。
- 接口契约由队长定（见 §3.4），冰糖按契约 + mock 并行开发，W2 集中联调。

---

## 三、技术方案（详细）

### 3.0 总览与对接方式

```
[ 前端 Vue ]  ──HTTP/JSON──▶  [ 后端 FastAPI 单体 ]
                              ├─ user / assignment / submission / evaluation / sandbox / report / appeal / cheating  【队长主导】
                              └─ diagnose / variant / assignment(命题)  【冰糖，单体内模块】
                                   └─ httpx 调 移动云 MoMA
```

- 前端只跟**后端单体**打交道，`/api/*`。
- 后端是单体：诊断 / 变式 / 命题是**单体内部模块**（不再是独立服务），其他上下文直接 import 调用其 service，不走 HTTP。
- 鉴权：JWT（`python-jose`），前端 axios 带 `Authorization: Bearer <token>`。
- 统一响应 `{code, message, data}`，时间 ISO-8601，错误 `code != 0`。

**对接节奏（关键，两人都要看）**：

| 时机 | 对接内容 | 谁等谁 |
| --- | --- | --- |
| W0 末 | 接口契约（OpenAPI + JSON 样例，§3.4）定稿 | 队长先出契约，冰糖据此 mock |
| W1 中 | 提交 / 评测结果接口（诊断走 mock） | 队长出评测，冰糖反馈页接结果 |
| W2 初 | 诊断 / 变式模块被提交/评测上下文调用 | 队长调冰糖的 service（单体内 import） |
| W2 中 | 主链路端到端联调（命题→评测→诊断→变式→学情） | 两人一起 |
| W3 初 | 部署联调（Docker Compose + MoMA 切真） | 队长主导，冰糖配合 |

> AI 模块在单体内，联调比跨服务简单：冰糖写好 service + 单测，队长 import 即用。

---

### 3.1 前端（【队长骨架 + 冰糖协作看板 / 反馈页】）

#### 3.1.1 技术栈

| 用途 | 选型 | 备注 |
| --- | --- | --- |
| 框架 | Vue 3（`<script setup>` + Composition API） | 队长骨架；冰糖沿用 |
| 构建 | Vite | `npm create vue@latest` |
| 状态 | Pinia | 用户 / 课程 / 提交 |
| 路由 | Vue Router | 学生 / 教师 / 管理三布局 |
| UI | Element Plus | 表单 / 表格 / 弹窗 |
| 编辑器 | Monaco Editor（`@guolao/monaco-editor` + `monaco-editor`） | Java / Python 高亮 |
| 图表 | ECharts（`vue-echarts`） | 学情看板（冰糖） |
| 请求 | axios | baseURL 指后端，拦截器带 JWT |

#### 3.1.2 目录结构（建议）

```
frontend/src/
├─ api/            # axios 封装 + 模块请求（队长建骨架，冰糖按需加 report.ts）
├─ components/
│  ├─ CodeEditor.vue         # 【队长】 Monaco 封装
│  ├─ SubmissionResult.vue   # 【队长】 评测结果
│  ├─ MisconceptionCard.vue  # 【冰糖】 误区反馈卡
│  └─ VariantPractice.vue    # 【冰糖】 变式练习
├─ views/
│  ├─ student/  # 提交页【队长】、诊断反馈页【冰糖】、变式练习页【冰糖】、我的成绩【队长】
│  ├─ teacher/  # 命题页【队长】、学情看板【冰糖】、申诉处理【队长】、反作弊报告【冰糖】
│  └─ admin/     # 用户/课程/班级/配额【队长】
├─ stores/        # Pinia（队长建 auth/course/submission）
├─ router/        # 路由 + 权限守卫【队长】
├─ mock/          # 开发期 mock（§3.1.5）
└─ utils/         # request.ts（axios 封装，【队长】）
```

> 约定：队长建 `request.ts` + `api/` 骨架 + 路由 + 布局；冰糖在自己页面调既有封装，不重复造。

#### 3.1.3 关键页面与组件（归属）

- **【队长】** `CodeEditor.vue`、`SubmissionResult.vue`、命题页、申诉处理页、管理页、我的成绩页。
- **【冰糖】** `MisconceptionCard.vue`（误区类型 / 证据 / 知识点，证据高亮代码行）、`VariantPractice.vue`、`LearningDashboard.vue`（ECharts 误区饼图 + 知识点柱图 + 预警表）、反作弊报告页（图表）。

#### 3.1.4 怎么调后端 API

`src/utils/request.ts`（队长建）：

```ts
import axios from 'axios'
export const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE || '/api',
  timeout: 30000,
})
request.interceptors.request.use(cfg => {
  const token = useAuthStore().token
  if (token) cfg.headers.Authorization = `Bearer ${token}`
  return cfg
})
```

- 开发期 `vite.config.ts` 设 `server.proxy['/api'] = 'http://localhost:8000'`，避免跨域。

#### 3.1.5 mock 先行

- W0 契约一出，冰糖在 `src/mock/` 按契约写死 JSON（`vite-plugin-mock` 或 axios 适配层）；W2 切真只关 mock。

#### 3.1.6 本地起

```bash
cd frontend
npm create vue@latest .
npm i element-plus @guolao/monaco-editor monaco-editor echarts vue-echarts pinia axios vue-router
npm run dev        # http://localhost:5173
```

> 队长本地同时起后端 8000 + 前端 5173，接口即时联调；冰糖拉前端，起 5173 + mock 自测自己页面。

#### 3.1.7 学情看板图表（【冰糖】 ECharts 要点）

- 误区分布饼图 `type:'pie'`，数据来自 `GET /api/classes/{id}/learning-report` 的 `misconceptionStats`。
- 知识点薄弱柱图 `type:'bar'`；`vue-echarts` 的 `<v-chart :option="opt" />` 响应式刷新。

---

### 3.2 后端（【全 Python FastAPI 单体 + DDD】，队长主导核心、冰糖做 AI 模块）

#### 3.2.1 技术栈

| 用途 | 选型 | 备注 |
| --- | --- | --- |
| Web | FastAPI + Uvicorn（开发）/ Gunicorn（部署） | 单体一个 app |
| ORM | SQLAlchemy 2.0 + Alembic | 迁移 |
| 校验 | Pydantic v2 | 请求 / 响应模型 |
| DB | PostgreSQL + Redis | Redis 做评测队列 / 缓存 |
| 沙箱 | Docker SDK for Python（`docker` 包） | 队长调容器 |
| 模型 | httpx | 调移动云 MoMA（OpenAI 兼容） |
| 鉴权 | PyJWT / python-jose + passlib(bcrypt) | JWT + RBAC |
| 配置 | pydantic-settings | `.env` 注入，不进 git |

#### 3.2.2 DDD 限界上下文与目录

```
backend/app/
├─ core/            # 配置 / 安全(JWT) / 依赖 / 异常 / DB session / 统一响应
├─ contexts/         # 限界上下文，每内含 models/schemas/service/router/repository
│  ├─ user/          # 用户 / 角色 / 课程 / 班级 / 权限 / 鉴权        【队长】
│  ├─ assignment/    # 作业 / 用例 / 评分细则 + 命题模块              【队长骨架 + 冰糖命题】
│  ├─ submission/    # 提交                                    【队长】
│  ├─ evaluation/    # 评测引擎：判分 / 调度 / Redis 队列          【队长】
│  ├─ sandbox/       # Docker 隔离执行                          【队长】
│  ├─ diagnose/      # 误区诊断（调 MoMA）                       【冰糖】
│  ├─ variant/       # 变式生成（调 MoMA）                       【冰糖】
│  ├─ report/        # 学情聚合 / 看板 API                       【队长】
│  ├─ appeal/        # 申诉状态机                                【队长】
│  └─ cheating/      # 反作弊                                   【队长】
└─ main.py          # FastAPI app，聚合各上下文 router
```

**DDD 约束**：模块间通过 `service` 接口调用，**不跨上下文直接查表**；每个上下文有自己的领域模型与聚合。单体部署、清晰边界、未来可按上下文拆微服务。

#### 3.2.3 评测引擎 + 沙箱（【队长】）

- `docker` SDK 拉容器：CPU / 内存上限、`network_mode='none'`、只读根 + 临时写卷、超时 kill。
- 流程：编译 → 逐用例运行（stdin 喂输入）→ 采集 stdout / exit / 耗时 / 内存 → 按用例权重评分（支持部分分）。
- 并发：Redis 队列 + asyncio 信号量限流（沙箱并发上限，如 4）。
- 语言：一期 Java + Python；C/C++ 二期。

#### 3.2.4 AI 模块（【冰糖】 单体内）

- `diagnose` / `variant` / `assignment(命题)` 三个 service，用 httpx 调 MoMA。
- prompt 模板（`prompts/*.txt`）+ **事实校验**：evidence 必须命中真实报错 / 失败用例；要求模型只输出 JSON 便于 `json.loads`。
- **mock 模式**：`.env` `MOCK=1` 返回固定 JSON（§3.2.5 样例），MoMA 未到位先跑通。
- 单体内 service，被 `submission` / `evaluation` / `report` 上下文直接 import 调用，不走 HTTP。

#### 3.2.5 AI 模块请求 / 响应契约（冰糖实现，队长调用）

**诊断** 入：`{code, lang, compileError, runErrors, testResults}` 出：`{misconceptionType, evidence, knowledgePoint, confidence}`
**变式** 入：`{misconceptionType, knowledgePoint, originalContext}` 出：`{title, description, cases:[{input,expectedOutput}], scoringPoints}`
**命题** 入：`{prompt:"出一道考察数组边界的入门题"}` 出：`{title, description, testCases:[{input,expectedOutput,isHidden}], scoringRubric, referenceCode}`

#### 3.2.6 怎么调移动云 MoMA

`contexts/diagnose/clients/moma.py`（冰糖）：

```python
async def chat(system: str, user: str) -> str:
    async with httpx.AsyncClient(timeout=60) as c:
        r = await c.post(
            f"{settings.MOMA_ENDPOINT}/chat/completions",
            headers={"Authorization": f"Bearer {settings.MOMA_API_KEY}"},
            json={"model": settings.MOMA_MODEL,
                  "messages":[{"role":"system","content":system},{"role":"user","content":user}]},
        )
        return r.json()["choices"][0]["message"]["content"]
```

- endpoint / key / model 走 `.env`，**不写死、不进 git**；`MOCK=1` 时返回固定 JSON。

#### 3.2.7 本地起

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install fastapi uvicorn sqlalchemy alembic pydantic pydantic-settings httpx docker redis python-jose passlib psycopg2-binary
# .env 写：MOCK=1 / DATABASE_URL=... / REDIS_URL=...
uvicorn app.main:app --reload --port 8000      # http://localhost:8000/docs
```

> 两人改不同上下文，各自分支 PR 合并避免冲突；冰糖本地起后端 + 前端自测 AI 模块 / 看板。

---

### 3.3 接口契约（【对接点】两人都看，W0 定稿）

统一响应 `{code:0, message:"ok", data:{...}}`。

| 端点 | 方法 | 说明 | 谁实现 | 谁调用 |
| --- | --- | --- | --- | --- |
| `/api/auth/login` | POST | 登录返 JWT | 队长 | 前端（队长页 + 冰糖页） |
| `/api/assignments` | POST | 命题（调命题模块） | 队长骨架+冰糖 | 命题页（队长） |
| `/api/assignments/{id}` | GET | 作业详情 | 队长 | 提交页（队长） |
| `/api/submissions` | POST | 提交，触发评测 | 队长 | 提交页（队长）/ 变式页（冰糖） |
| `/api/submissions/{id}/evaluation` | GET | 评测结果 | 队长 | 结果页（队长）/ 变式页（冰糖） |
| `/api/submissions/{id}/diagnose` | POST | 触发诊断 | 队长编排 | 诊断反馈页（冰糖） |
| `/api/variant` | POST | 取变式题 | 队长编排 | 变式练习页（冰糖） |
| `/api/classes/{id}/learning-report` | GET | 班级学情 | 队长 | 学情看板（冰糖） |

> 诊断 / 变式 / 命题是单体内模块，队长在编排接口里 import 冰糖的 service；对外只暴露 `/api/*`。W0 队长补全 OpenAPI，冰糖据此 mock。

---

### 3.4 数据模型（【队长】W0 出 Alembic 迁移 + ER 图）

核心表（与 `项目方案.md` 4.3 一致）：`User / Role / Course / Class / Enrollment / Assignment / TestCase / Submission / Evaluation / Misconception / VariantExercise / Grade / Appeal / AuditLog / CheatingReport`。前端只看 API 返回，不直接读库。

---

### 3.5 部署架构（【队长】W3）

Docker Compose 一键起：`backend`(FastAPI，挂 docker socket 做沙箱) + `frontend`(nginx 静态) + `postgres` + `redis` + `minio`(对象存储)，上云主机；MoMA 走移动云；`.env` 注入 key，不进 git。

---

### 3.6 本地开发环境

| 端 | 起 | 端口 | 谁起 |
| --- | --- | --- | --- |
| 前端 | `npm run dev` | 5173，proxy /api → 8000 | 队长（全栈）/ 冰糖（自测页面） |
| 后端 | `uvicorn app.main:app --reload` | 8000 | 队长（核心）+ 冰糖（AI 模块，各自上下文） |
| DB / Redis | docker postgres / redis | 5432 / 6379 | 队长 |

> 冰糖开发看板 / 反馈页只需前端 + mock；AI 模块自测起后端 + `/docs`。

---

## 四、开发步骤（里程碑）

里程碑：**M1 主链路可演示（W2 末）** / **M2 部署 + 验证 + 文档（W3 末）**

### W0（09-24 ~ 09-30）骨架与契约
- 队长：FastAPI 单体脚手架（`core` + Alembic + `user`/`assignment` CRUD）；DB schema；**接口契约 OpenAPI**；评测引擎骨架（编译 + 单用例）；**前端骨架**（Vue 脚手架 / 路由 / 布局 / Monaco / `request.ts` / 提交页）。
- 冰糖：`diagnose` 模块原型（prompt 跑通，`MOCK=1`）；学情看板脚手架（ECharts 装好）；诊断反馈页骨架（接 mock）。
- **【对接点】W0 末**：队长交契约 + 前端骨架，冰糖接 mock，确认无误。

### W1（10-01 ~ 10-07，含国庆 buffer）评测 + 沙箱 + 诊断模块
- 队长：评测引擎完整（多用例 / 权重 / 超时 / 内存）；Docker 沙箱（docker-py）；Redis 队列 + 限流；前端评测结果展示页。
- 冰糖：`diagnose` 模块跑通（单体内 service + 单测）；`variant` 脚本；诊断反馈页联调结果展示。
- **【对接点】W1 中**：`/api/submissions` + `/api/submissions/{id}/evaluation`，队长出，冰糖反馈页接。
- 国庆可能减速：本周以队长后端 + 业务页为主，冰糖远程推进 AI 模块 / 反馈页。

### W2（10-08 ~ 10-14）主链路联调
- 队长：诊断 / 变式编排（import 冰糖 service）；学情聚合 API；权限与三个状态机；前端业务页（命题 / 申诉）。
- 冰糖：`variant` 模块跑通；学情看板（ECharts）；`assignment` 命题模块；主链路端到端联调。
- **【对接点】W2 全周**：两人跑通 命题 → 提交 → 评测 → 诊断 → 变式 → 学情。
- 目标：W2 末 **M1 主链路可演示**。

### W3（10-15 ~ 10-21）二期裁剪 + 部署 + 验证 + 文档
- 队长：申诉状态机 + 申诉页、反作弊基础、成绩导出；云主机部署 + MoMA 切真；真实课程小范围试点验证。
- 冰糖：反作弊报告看板(ECharts)、成绩看板；演示视频录制；参赛文档校对。
- **【对接点】W3 初**：部署联调，MoMA 切真模型，两人一起验证主链路真跑。
- 目标：W3 末 **M2 部署 + 验证 + 文档**。

### Buffer（10-22 ~ 10-23）答辩准备
- 演示打磨、AI 节省工时数字对照、答辩预演。

---

## 五、排期表

| 周 | 队长（后端核心 + 前端骨架 / 业务页） | 冰糖（AI 模块 + 前端看板 / 反馈页） | 对接 |
| --- | --- | --- | --- |
| W0 9/24-30 | 单体脚手架 / CRUD / 契约 / 评测骨架 / 前端骨架 | diagnose 原型 / 看板脚手架 / 反馈页骨架 | 周末交契约+骨架 |
| W1 10/1-7 | 评测引擎 / 沙箱 / 队列 / 结果展示页 | diagnose 模块跑通 / variant 脚本 / 反馈页联调 | 周中提交评测接口 |
| W2 10/8-14 | 诊断编排 / 学情 API / 状态机 / 命题+申诉页 | variant 模块 / 学情看板 / 命题模块 / 联调 | 全周端到端联调 |
| W3 10/15-21 | 申诉 / 反作弊 / 导出 / 部署 / MoMA / 验证 | 反作弊看板 / 成绩看板 / 视频 / 文档 | 周初部署联调 |
| Buffer 10/22-23 | 答辩准备 | 答辩准备 | — |

---

## 六、风险与对策

| 风险 | 对策 |
| --- | --- |
| 队长 Python 半熟（多年 Java） | 核心模块用湛卢代码生成 + 参考开源 Python OJ；写足单测；冰糖 Python 熟可分担业务 CRUD |
| 冰糖 Java 不熟 | 不碰需 Java 的部分；全栈 Python 后她能参与后端 AI 模块 + 部分 CRUD |
| 模块化单体边界乱 | 严守 DDD：模块间走 service 接口、不跨上下文查表，PR review 把关 |
| 移动云 MoMA 资源未到位 | 开发期 `MOCK=1` 跑通链路，到位后切真（诊断 / 变式 / 命题三处） |
| 沙箱安全 | Docker 隔离 + 资源上限 + 无网络 + 超时 kill（与语言无关，必须做对） |
| 1 月紧 + 国庆减速 | 一期主链路必达，二期按 W3 实际进度裁剪 |
| prompt 输出不稳 | 要求 JSON only + few-shot；service 内二次校验 evidence 命中真实报错 |

---

## 七、湛卢 IDE 协作约定

- 全流程用湛卢 IDE：代码生成 / 智能调试 / 代码评审 / 单元测试 / Bug 修复。
- 高阶：命题 / 诊断沉淀为 Skill；MCP 接 MoMA / 对象存储 / 沙箱；自定义流程编排主链路。
- 分支：`main` 受保护，`feature/*` 分支 PR 合并，队长 review。
- 提交信息中文，规范同 `项目方案.md`。
- 落地「评测 + 诊断 + 变式」可复用教学后端范式（加分项）。
