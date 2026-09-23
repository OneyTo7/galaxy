---
name: vue3
description: Vue 3 + Pinia 开发最佳实践：setup store、Composition API、TypeScript、副作用、持久化、测试、反模式；含本项目栈约定（Element Plus / Monaco / ECharts / axios）。
---

# Vue 3 + Pinia Skill

> 本项目栈：Vue 3（`<script setup>` + Composition API）+ Vite + Pinia + Vue Router + Element Plus + Monaco Editor + ECharts（vue-echarts）+ axios。目录：`src/{api,components,views,stores,router,mock,utils}`。

## 本项目约定
- 组件用 `<script setup>`（+ TS 视项目统一）
- 状态：组件局部用 `ref`/`reactive`/`computed`；跨路由/跨组件树共享用 Pinia
- 请求：统一 `src/utils/request.ts`（axios + JWT 拦截器，baseURL `/api`），模块请求放 `src/api/`
- 编辑器：Monaco（`@guolao/monaco-editor`），封装 `CodeEditor.vue`，`v-model` 取代码字符串
- 图表：`vue-echarts` 的 `<v-chart :option="opt" />`，响应式刷新
- mock：`src/mock/` 按后端契约写死 JSON，接口未好时用，W2 切真只关 mock

## 状态归属
- 组件内状态用 `ref`/`reactive`/`computed`
- 跨路由/跨组件树共享用 Pinia
- 可分享导航状态用路由 params/query
- 服务端状态用 API 层，别把服务端缓存复制进 Pinia（除非是可编辑草稿/离线缓存）

## Store 结构
- 用 setup store：`defineStore('name', () => { ... })`
- 每域一文件：`stores/auth.ts`、`stores/course.ts`、`stores/submission.ts`
- state/getters/actions 同属一域；setup store 必须 return 所有 state 以便 devtools/SSR/插件追踪
- getters 纯函数无副作用；写/IO/编排放 actions

```ts
import { computed, ref } from 'vue'
import { defineStore } from 'pinia'

export const useSubmissionStore = defineStore('submission', () => {
  const current = ref<Submission | null>(null)
  const status = ref<'idle' | 'loading' | 'done' | 'error'>('idle')
  const canSubmit = computed(() => status.value !== 'loading')
  async function submit(code: string, lang: string) {
    status.value = 'loading'
    try { current.value = await api.create({ code, lang }); status.value = 'done' }
    catch { status.value = 'error' }
  }
  return { current, status, canSubmit, submit }
})
```

## 组件用法
- store 在 `<script setup>` 顶部调用
- 解构 state/getters 用 `storeToRefs()`；actions 可直接解构（仍绑 store）
- 大业务流程别写组件里，移到 actions 或 composables
- 派生状态优先 `computed` 而非 `watch`

```vue
<script setup>
import { storeToRefs } from 'pinia'
import { useSubmissionStore } from '@/stores/submission'
const store = useSubmissionStore()
const { canSubmit, status } = storeToRefs(store)
const { submit } = store
</script>

<template>
  <button :disabled="!canSubmit" @click="submit(code, lang)">提交</button>
</template>
```

## TypeScript
- 显式类型 store state / action payload / API 响应
- 避免 `any`；用 `unknown` 收窄外部输入
- 工作流状态用判别联合（`status`/`error`）
- store ID 稳定描述性（devtools + 持久化 key）

## Actions 与副作用
- action 可同步/异步，聚焦一个用户/域工作流
- 边界处校验输入再改 state
- 异步工作流显式 `status`/`error`/`lastUpdatedAt`
- 重试前重置旧 error
- 订阅/定时器/socket/浏览器监听别放 store，除非 store 拥有其生命周期与清理

## 持久化
- 只持久化需跨刷新存活的字段（偏好、未完成草稿）
- 禁止持久化 secret / token / PII / 授权决策
- 用字段白名单 + 版本迁移
- 持久化状态视为不可信输入，关键流程前校验
- 注意 hydration 时机，依赖持久值的 UI 先等就绪再渲染

## 测试
- `@pinia/testing` 做需 store 的组件测试
- 直接测 action 的域行为与边界
- 测试间 reset Pinia 避免状态泄漏
- Vite HMR 用 `acceptHMRUpdate(useSubmissionStore)`

## 反模式
- Pinia 不是所有响应值的垃圾桶
- 不用 `storeToRefs()` 直接解构 state（丢响应性）
- 通过 action 改 props/路由对象
- 把服务端对象/请求实例/DOM 节点/定时器放 store state
- setup 里 store 间循环读取；用 actions/computed 组合
