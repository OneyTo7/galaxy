# 智学 · AI 认知诊断实验教学平台（校园方向）-深化改造方案

> 版本：1.0 | 2026-10-03
> 定位：不改广度，加深度。把主链路从"每步一次调用"改造成"有状态、有积累、有闭环"的认知诊断系统。
> 前置阅读：`开发方案.md`、`权限矩阵.md`。工期目标：W2（10/08–10/14）完成核心，W3 前半收尾。

---

## 一、现状问题与改造目标

| # | 现状 | 问题 | 改造后 |
| --- | --- | --- | --- |
| 1 | 诊断 = 一次 LLM 调用，`knowledge_point` 是自由字符串 | 无学生知识状态，无积累，类型不可聚合 | 受控知识点体系 + BKT 学生掌握度模型，跨提交持续更新 |
| 2 | 变式题生成后即被遗忘 | 诊断→变式→再验证闭环断裂 | 变式题升级为可提交的练习作业，做对即标记"误区已克服" |
| 3 | evidence 无程序化校验 | 模型编造证据无法发现 | 事实校验：evidence 必须命中真实报错/失败用例，否则重试/降级 |
| 4 | 反作弊 = 单次 LLM 判 AI 代写 | 学术上不可信，答辩易被攻击 | 同班代码相似度（n-gram 指纹）为主 + LLM 为辅的综合研判 |
| 5 | 学情报告 = Counter 计数 | 无推断无预警 | 掌握度热力图、成长曲线、风险预警，数据来自掌握度模型 |

**设计原则**：
1. 所有新能力在 `MOCK=1` 下可完整演示（掌握度、闭环、相似度均为确定性计算，不依赖真模型）。
2. 遵守现有 DDD 边界：新增 `mastery` 限界上下文，其他上下文只 import 其 service，不跨上下文查表。
3. 复用既有管线：变式练习走既有 提交→队列→评测→worker 链路，不新建评测路径。

---

## 二、总体设计：闭环数据流

```
命题（带知识点标签，Q 矩阵）
  → 学生提交 → 评测（逐用例结果）
      → worker 评分后调 mastery.record_submission()     ① 正/负观测
  → 触发诊断（evidence 事实校验，输出受控知识点） 
      → mastery.record_diagnosis()                      ② 负观测 + 误区登记
  → 变式生成（按掌握度选难度）→ 创建练习作业（per-student）
      → 学生提交变式 → 评测 → worker
          → mastery.record_submission()                 ③ 靶向观测（学习率加成）
          → 误区克服判定（misconception.status → overcome）
  → 学情看板：掌握度热力图 / 个人雷达 / 成长曲线 / 预警名单
```

新增 `app/contexts/mastery/`（models / schemas / service / repository / router / deps），掌握度是唯一事实源（single source of truth），report 上下文改为读 mastery 而非自行计数。

---

## 三、D1 知识点体系与 Q 矩阵【1 人日】

### 3.1 受控知识点体系（taxonomy）

新表 `knowledge_points`：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| id | PK | |
| code | string(32) unique | 如 `loop-boundary`、`array-index` |
| name | string(64) | 如"循环边界条件" |
| category | string(32) | 循环 / 数组 / 函数 / 递归 / 逻辑 / IO / 字符串 |
| sort_order | int | 展示排序 |

内置种子数据 ~20 个入门编程知识点（`scripts/seed_knowledge_points.py`，Java/Python 通用的语言无关体系，如：循环终止条件、数组越界、off-by-one、函数返回值、递归出口、输入解析、类型转换、边界输入、多重循环控制、字符串切片……）。教师可在管理页补充。

### 3.2 Q 矩阵（题目 × 知识点）

新表 `assignment_knowledge_points`：`assignment_id` FK、`knowledge_point_id` FK、`weight`（float，默认 1.0），唯一约束 `(assignment_id, knowledge_point_id)`。

可选精化：`test_cases.knowledge_point_id` 可空 FK——用例级标签存在时，该知识点的观测只用该子集用例；不存在时用整题用例。一期先只做作业级。

### 3.3 标签来源

1. **AI 命题时自动标注**：命题契约（`assignment` 生成）的输出 schema 增加 `knowledge_points: [{code, weight}]`，prompt 中给出受控 code 列表要求从中选择（闭环约束，杜绝编造）。生成后写入 Q 矩阵。
2. **教师手动改标**：`PUT /api/assignments/{id}/knowledge-points`。
3. **存量作业回填**：`MOCK` 下用规则匹配标题/描述关键词，真模型下一次性 LLM 打标（后台脚本，非页面功能）。

### 3.4 诊断收敛到体系（关键改动）

`diagnose` 的 prompt 增加受控列表：**"knowledge_point 必须从以下列表中选择：loop-boundary(循环边界条件), …"**；`GenerateResult` 增加字段 `knowledge_point_code`。`Misconception` 表增加 `knowledge_point_id` FK（可空）+ 解析逻辑（code 精确匹配 → name 模糊匹配 → 最近的 category 兜底 → 置空并保留原字符串）。解析失败不阻塞诊断入库。

---

## 四、D2 学生掌握度模型（BKT）【1.5 人日，核心】

### 4.1 数据模型

新表 `student_mastery`（当前状态）：

| 字段 | 说明 |
| --- | --- |
| user_id + knowledge_point_id | 唯一约束 |
| mastery | float 0–1，掌握概率 P(L) |
| attempts / correct | 累计观测次数 / 正确次数 |
| status | `unmastered`(<0.3 且 attempts≥2) / `learning` / `mastered`(≥0.85) |
| first_seen_at / last_updated_at | |

新表 `mastery_events`（追加式事件流，成长曲线与审计的数据源）：

| 字段 | 说明 |
| --- | --- |
| user_id, knowledge_point_id | |
| submission_id | 可空（诊断事件也挂提交） |
| source | `assignment` / `diagnosis` / `variant` |
| observed | bool（正确/错误） |
| mastery_before / mastery_after | 更新前后值，画曲线用 |
| created_at | |

**幂等**：唯一约束 `(user_id, knowledge_point_id, source, submission_id)`——worker 队列重投、重复触发诊断都不会重复记账，靠插入冲突即跳过。

### 4.2 观测（opportunity）推导规则

对一次提交 s（作业 a，知识点 k）：

1. 取该知识点覆盖的用例集 C（用例级标签的子集，否则全量），加权通过率 `r = Σ(passed·weight) / Σ(weight)`；
2. `r ≥ 0.6` → observed=True，否则 False；C 为空（编译失败等）→ False；
3. 同一提交对同一知识点只产生 **1 条** assignment 事件（多次提交算多次观测，这正是练习的意义）。

诊断事件：该提交最新的、`knowledge_point_id` 非空且 `confidence ≥ 0.5` 的诊断，对命中知识点产生 1 条 source=diagnosis 的 **False** 观测（诊断是负证据）。

变式事件：练习作业的提交产生 source=variant 观测，规则同 1–2。

### 4.3 BKT 更新算法

每个知识点一组参数（初始全局默认，存 `knowledge_points` 表可调）：`p_init=0.30, p_transit=0.20, p_slip=0.10, p_guess=0.20`。

每条观测 o（True=正确）：

```
似然更新：  P(L|o) = P(L)·[o ? (1-slip) : slip]  /  ( P(L)·[o ? (1-slip) : slip] + (1-P(L))·[o ? guess : (1-guess)] )
学习更新：  P(L)' = P(L|o) + (1-P(L|o)) · transit_effective
```

`transit_effective` 分来源：普通作业 `transit`；**变式靶向练习 `transit × 1.5`**（上限 0.5，"针对性练习学习增益更高"，答辩可讲）；诊断负证据用更高 `slip=0.25`（二手信号，降权）。

首见知识点：以 `p_init` 起步；`mastery`、`status` 随每次事件刷新；达到 `mastered` 后只降不升可豁免（不实现，保持简单）。

### 4.4 服务接口与挂载点

`MasteryService`（新上下文，对外仅三个方法）：

```python
record_submission(submission_id: int) -> None     # worker 评分后调用（D3 闭环同入口）
record_diagnosis(misconception_id: int) -> None   # diagnose service 入库后调用
matrix(course_id) / student_mastery(user_id, course_id) / events(user_id, course_id)  # 查询
```

挂载点：
- `app/worker.py`：`update_score` 之后加 `mastery_svc.record_submission(sub.id)`（try/except 包裹，掌握度失败不回滚评分）；
- `diagnose/service.py`：`_repo.create` 之后加 `record_diagnosis`；
- 两处均通过构造注入，保持 Protocol 依赖风格。

### 4.5 误区克服状态机

`misconceptions` 表加 `status`（`open` / `overcome`，默认 open）与 `overcome_at`。规则：知识点 k 上产生一条 observed=True 的新事件（来源不限）时，将该生该知识点所有 `open` 误区置 `overcome`。这是"诊断→变式→克服"闭环的落点，也是学生报告页时间线的素材。

---

## 五、D3 变式闭环【1 人日】

### 5.1 练习作业机制（复用整条提交管线）

`assignments` 表加两列：
- `kind`：`formal`（默认）/ `practice`；
- `assigned_user_id`：可空，practice 时为目标学生。

利用点：`course_id` 本就可空（练习作业不挂课程 → 天然绕开选课校验）；`SubmissionService.submit` 不需改；评测 worker 不需改——**practice 作业自动走完整 提交→评测→掌握度 链路**。

排除规则（避免污染正式数据）：
- `AssignmentService.list`（教师作业列表）过滤 `kind == 'formal'`；
- `ReportService` / `Gradebook` 统计过滤 practice；
- 学生侧新增"我的练习"入口：`GET /api/assignments?kind=practice&mine=1`（按 assigned_user_id 过滤）。

### 5.2 变式生成流程改造

`variant_exercises` 表加：`origin_misconception_id` FK、`practice_assignment_id` FK、`difficulty`（`easy/medium/hard`）。

`VariantService.generate` 新流程：
1. 取最新诊断（现有逻辑）→ 解析其 `knowledge_point_id`；
2. 查该生该知识点 `student_mastery` → **难度选择**：mastery <0.4 → easy（同型换数）、0.4–0.7 → medium（换情境）、>0.7 → hard（组合考点）；provider 契约加 `difficulty` 参数；
3. 生成成功后创建 practice Assignment（title=变式题 title、cases 复用 `VariantResult.cases`、`assigned_user_id` = 该生、`status='published'`），回写 `practice_assignment_id`；
4. 响应体增加 `practice_assignment_id`，前端"去练习"按钮直接跳 `/submit?assignmentId=…`。

`POST /api/submissions/{id}/variant` 幂等：同一诊断重复请求不重复建练习作业（先查 `variant_exercises` 最新一条未过期的直接返回）。

### 5.3 学生端动线

诊断反馈页 →「生成变式」→「去练习」→ 提交页（预载练习作业）→ 评测结果 → 掌握度更新 + 若通过则页面显示"✅ 误区已克服"。演示动线完整。

---

## 六、D4 Evidence 事实校验【0.5 人日】

`diagnose` provider 返回后、入库前插入校验函数 `validate_evidence(evidence, signals) -> bool`，signals 为该提交的：编译 stderr、各用例 stderr、失败用例 id 列表、代码行内容。

命中规则（任一满足即通过）：
1. evidence 与任一 stderr 有 ≥8 字符的公共子串（或按 token 的重叠率 ≥0.3）；
2. evidence 包含失败用例的 case_id / 序号；
3. evidence 引用的代码片段（≥10 字符）确实出现在提交代码中。

处理策略：不通过 → 带"证据与实际信号不符，请引用真实报错或失败用例"重试 1 次；仍不通过 → 降级为规则标签（按主导错误类型给 `编译错误/运行时错误/用例未通过/边界偏差` 之一），`confidence` 减半，`misconceptions.evidence_validated=False`（新列，默认 True）。`MOCK` 模式下 evidence 取自真实 signals，天然通过。

看板/报告对 `evidence_validated=False` 的诊断打"低置信"标记，体现系统不盲信模型。

---

## 七、D5 反作弊升级：代码相似度为主【1 人日】

### 7.1 算法（同班同作业两两比对，教师手动触发）

1. **归一化**：去注释/空行 → 词法切分为 token 流 → 标识符映射为 `ID`、字面量映射为 `LIT`（挫败改名/换常量攻击）；
2. **指纹**：k-gram（k=8 tokens）滚动哈希 → winnowing（窗口 w=5 取最小哈希）得指纹集合；
3. **相似度**：指纹集合 Jaccard × 100；
4. **取证**：取公共 k-gram 还原的 top-3 代码片段区间，写入 detail 供教师对照。

班级规模 n ≤ 100，两两比对 O(n²) 在请求内可完成，无需异步。

### 7.2 判定分级（替代单一 flagged）

| 相似度 | status | 含义 |
| --- | --- | --- |
| ≥ 80 | `flagged` | 高度相似，重点核查 |
| 60–79 | `suspected` | 疑似，建议人工比对 |
| < 60 | — | 不产生相似度报告 |

`check_type` 扩展：`similarity`（一条报告覆盖一个学生对，`detail` 存 `{partner_id, partner_name, similarity, snippets}`）与既有 `ai_generated` 并存。**LLM 判 AI 代写降级为辅助信号**：单独命中只产生 `suspected`，不再直接 `flagged`。

`CheatingReport` 表加 `meta` JSON 列容纳上述结构化 detail（原 detail 文本保留兼容）。

---

## 八、API 契约变更

| 端点 | 方法 | 角色 | 说明 |
| --- | --- | --- | --- |
| `/api/knowledge-points` | GET | teacher/admin | 受控知识点列表 |
| `/api/assignments/{id}/knowledge-points` | PUT | teacher | 作业打标（Q 矩阵维护） |
| `/api/assignments?kind=practice&mine=1` | GET 扩展 | student | 我的练习作业 |
| `/api/courses/{id}/mastery-matrix` | GET | teacher | 班级掌握度矩阵（热力图数据） |
| `/api/students/{id}/mastery?course_id=` | GET | teacher | 单生掌握度雷达 + 风险状态 |
| `/api/students/{id}/mastery/events` | GET | teacher | 成长曲线事件流 |
| `/api/mastery/me?course_id=` | GET | student | 学生自查掌握度 |
| `/api/submissions/{id}/variant` | POST 响应扩展 | — | 增加 `practice_assignment_id`、`difficulty` |
| `/api/assignments/{id}/cheating-check` | POST 响应扩展 | teacher | 增加 similarity 报告对 |
| `/api/assignments/{id}/learning-report` | GET 响应扩展 | teacher | 增加 `mastery_summary`（各知识点班均掌握度、风险人数） |

OpenAPI（`/docs`）同步更新，前端按契约先行 mock。

---

## 九、数据库迁移清单（一次 Alembic revision）

新增：`knowledge_points`、`assignment_knowledge_points`、`student_mastery`、`mastery_events`。
修改：
- `assignments` + `kind`(default formal)、`assigned_user_id`；
- `misconceptions` + `knowledge_point_id`、`status`(default open)、`overcome_at`、`evidence_validated`(default true)；
- `variant_exercises` + `origin_misconception_id`、`practice_assignment_id`、`difficulty`；
- `cheating_reports` + `meta`(JSON)。

回填脚本：种子知识点；存量 misconception 的 knowledge_point 字符串 → taxonomy 解析回填 `knowledge_point_id`。

---

## 十、前端改造（Element Plus + ECharts，遵循设计规范 token）

| 页面 | 改造 |
| --- | --- |
| `teacher/LearningDashboard.vue` | + 班级 × 知识点掌握度**热力图**（ECharts heatmap，6 色板映射 mastery）；预警表由"低分"改为"高风险知识点 + at-risk 学生"；既有饼图/柱图保留 |
| `teacher/StudentReport.vue` | 雷达图数据源改为真实掌握度；+ **成长曲线**（mastery_events 时间序列，按知识点筛选）；+ 误区克服时间线（open→overcome） |
| `teacher/AssignmentGenerate.vue` | 命题结果展示知识点标签，教师可增删 |
| `student/Diagnose.vue` | 诊断卡显示受控知识点标签 + 低置信标记；「生成变式」→「去练习」按钮 |
| `student/Submit.vue` | 支持 practice 作业（入口预载，页面标注"变式练习"） |
| `student/MyGrades.vue` | + 个人掌握度雷达 + "已克服误区"徽章 |

---

## 十一、工期与分工（W2 为主，合计约 8 人日）

| 任务 | 工作量 | 负责 |
| --- | --- | --- |
| D4 evidence 校验 | 0.5d | 队长 |
| D1 知识点体系 + Q 矩阵 + 命题带标 | 1d | 队长 0.5 + 冰糖 0.5（命题 prompt） |
| D2 mastery 上下文 + BKT + worker/诊断挂钩 | 1.5d | 队长 |
| D3 变式闭环（practice 作业） | 1d | 队长 0.5 + 冰糖 0.5（前端动线） |
| D5 相似度反作弊 | 1d | 冰糖 |
| 报告 API + 前端三图（热力图/雷达/曲线） | 2d | 冰糖 1.5（看板）+ 队长 0.5（API） |
| 演示数据脚本 + 端到端联调 | 1d | 两人 |

顺序建议：D4 → D1 → D2 → D3 →（D5 与前端并行）→ 联调。D2/D3 未完成前，前端可用 mock 契约先行。

---

## 十二、边界与取舍（明确不做）

- 不做 IRT/DKT 等重型模型：BKT 参数固定、不逐生校准——够讲清"诊断有算法依据"，实现与解释成本最低；
- 不做知识点先修关系图（prerequisite graph）：taxonomy 保持扁平 + category 分组；
- 用例级知识点标签只留接口不做 UI（一期作业级够用）；
- 相似度不做跨作业/跨班比对，不做 AST 级（token 指纹对入门课程抄袭已足够）；
- 掌握度不回填历史（上线后新事件开始积累；演示用脚本造数据）。

---

## 十三、答辩演示叙事

> 同一道题，A、B 两名学生都得了 60 分——传统平台到此为止。
> 智学：A 未通过的是边界用例 → 诊断"循环边界条件"误区（evidence 命中真实 stderr）→ 掌握度热力图上 `loop-boundary` 变红 → 推送 easy 变式 → A 通过 → 误区标记"已克服"，热力图转绿，成长曲线抬升。
> B 未通过的是解析用例 → 诊断"输入解析"，推的是**不同的**变式。
> 教师看板：班级知识点掌握热力图 + 风险预警；反作弊：同班两份改名的相似代码被指纹命中。
> 一句话：分数相同，诊断不同，路径不同——这就是"认知诊断"四个字的兑现。
