# frontend

Vue 3 + TypeScript + Vite + Element Plus + ECharts。`<script setup>` + Pinia + Vue Router。

## 运行

```bash
cd frontend
npm install
npm run dev        # http://localhost:5173（vite proxy /api → 8000）
npm run build      # vue-tsc 类型检查 + vite build
```

开发期 `vite.config.ts` 设 `server.proxy['/api'] = 'http://localhost:8000'`，避免跨域。

## 设计系统 v2「靛蓝学术 Indigo Scholar」

全局样式在 `src/assets/main.css`，提供：

- **Token 系统**：色彩（品牌蓝 `#4F7CFF` + 靛蓝墨色 `#16204B` + 暗靛蓝侧栏 `#171F3D`）、圆角（14/8/6）、阴影（3 级）、间距、字号
- **共享组件类**：`.page-title-chip`（图标标题徽章）、`.stat-card-v2`（带图标统计卡）、`.panel`（面板容器）、`.section-title`（带图标区块标题）、`.empty-state-v2`（空状态）、`.rise-in`（stagger 进场动效）、`.skeleton-block`（shimmer 骨架屏）
- **Element Plus 全面覆盖**：按钮/输入/表格/标签/对话框等均走 token
- **无障碍**：`prefers-reduced-motion` 支持，`focus-visible` 可见焦点环

布局壳 `src/layout/DefaultLayout.vue`：暗靛蓝侧栏（品牌徽章 + 图标分组导航 + 用户区）+ 浅靛内容区。

## 目录结构

```
src/
├── api/              # axios 请求模块（每个后端上下文一个 .ts）
├── assets/main.css   # 设计系统 v2 全局样式
├── components/       # CodeEditor.vue（Monaco 封装）
├── layout/           # DefaultLayout.vue（侧栏布局）
├── router/           # 路由 + 角色权限守卫
├── stores/           # Pinia（auth.ts）
├── types/api.ts      # 后端响应类型定义
├── utils/request.ts  # axios 实例（baseURL /api，JWT 拦截器，401 自动跳登录）
└── views/
    ├── student/      # 提交 / 诊断 / 变式 / 我的成绩 / 我的提交 / 选课
    ├── teacher/     # 学情看板 / AI 命题 / 作业详情 / 代码批改 / 学生报告
    └── admin/       # 课程管理
```

## 页面

| 页面 | 路径 | 角色 | 说明 |
| --- | --- | --- | --- |
| Login | `/login` | 公开 | 暗靛蓝品牌侧 + 登录卡 + 演示账号快捷填充 |
| Dashboard | `/dashboard` | 全部 | 课程侧栏 + 统计卡 + 作业进度 |
| 学情看板 | `/learning-report` | 教师 | 误区饼图/柱图/雷达 + **掌握度热力图** + 摘要表 |
| 学生个人报告 | `/student-report` | 教师 | 成绩走势 + **掌握度雷达** + **成长曲线** + 误区列表 |
| 误区诊断 | `/diagnose` | 学生 | 诊断结果 + evidence 校验徽章 + 受控知识点标签 |
| 变式练习 | `/variant` | 学生 | 难度三档 + practice 作业 + 通过后克服提示 |
| 代码提交 | `/submit` | 学生 | Monaco 编辑器 + 评测结果 + 自动诊断 |
| 我的成绩 | `/my-grades` | 学生 | 成绩册 + **个人掌握度雷达** + 已掌握知识点计数 |
| AI 命题 | `/assignment-generate` | 教师 | 一句话生成题面/用例/评分细则/参考实现 |
| 代码批改 | `/code-review` | 教师 | 学生提交列表 + 评测结果 + AI 诊断 |
| 反作弊 | `/cheating` | 教师 | 相似度检测报告 |
| 成绩册 | `/gradebook` | 教师 | 课程成绩一览 |
| 申诉 | `/appeal` | 学生/教师 | 申诉提交 + 教师终审 |
| 课程管理 | `/admin` | 教师/管理员 | 课程/班级/选课管理 |

## 路由权限

`src/router/index.ts` 每个路由带 `meta: { roles: [...] }`，`beforeEach` 校验：
- 未登录 → 重定向 `/login`
- 角色不匹配 → 重定向 `/dashboard`

## 请求层

`src/utils/request.ts`：
- `baseURL: '/api'`，vite proxy 到后端 8000
- 请求拦截器：从 localStorage 读 token，加 `Authorization: Bearer`
- 响应拦截器：401 清 token + 跳 `/login`

## 图表

ECharts 通过 `vue-echarts` 的 `<v-chart :option="opt" />` 渲染，按需引入 chart 类型 + components。配色用设计规范的固定 6 色板。

**注意**：echarts 的 chart 类名（`PieChart`/`BarChart` 等）与 Element Plus 图标组件名冲突，导入时用别名（如 `PieChart as EPieChart`）。
