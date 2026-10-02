<script setup lang="ts">
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { generateVariant } from '@/api/variant'
import CodeEditor from '@/components/CodeEditor.vue'
import { ElMessage } from 'element-plus'
import type { VariantOut } from '@/types/api'

const route = useRoute()
const router = useRouter()
const submissionId = ref(Number(route.query.submission) || 0)
const variant = ref<VariantOut | null>(null)
const code = ref('')
const loading = ref(false)
</script>

<template>
  <div class="variant-page">
    <div class="header">
      <h1>变式练习</h1>
      <p class="desc">基于你的误区，AI 生成一道换情境的变式题，帮你对症练习同一个知识点。</p>
    </div>

    <div v-if="!variant" class="action-bar">
      <div class="input-group">
        <span class="label">提交 ID</span>
        <el-input-number v-model="submissionId" :min="1" controls-position="right" style="width: 120px" />
      </div>
      <el-button type="primary" :loading="loading" @click="async () => {
        loading = true; variant = null
        try { variant = await generateVariant(submissionId); code = '' }
        catch (e: any) { ElMessage.error(e.response?.data?.detail || '生成失败') }
        finally { loading = false }
      }">生成变式题</el-button>
      <el-button text @click="router.push('/my-submissions')">从我的提交选择</el-button>
    </div>

    <div v-if="variant" class="split-layout">
      <aside class="problem-panel">
        <div class="variant-badge">AI 变式题</div>
        <h2>{{ variant.title }}</h2>
        <p class="desc-text">{{ variant.description }}</p>
        <div v-if="variant.cases?.length" class="cases">
          <h3>测试用例</h3>
          <div v-for="(c, i) in variant.cases" :key="i" class="case-item">
            <pre>输入: {{ c.input }}</pre>
            <pre>期望: {{ c.expected_output }}</pre>
          </div>
        </div>
        <div v-if="variant.scoring_points?.length" class="points">
          <h3>评分点</h3>
          <ul>
            <li v-for="p in variant.scoring_points" :key="p">{{ p }}</li>
          </ul>
        </div>
      </aside>

      <main class="code-panel">
        <div class="code-header">
          <h3>你的代码</h3>
          <el-button @click="router.push('/submit')">提交评测 →</el-button>
        </div>
        <CodeEditor v-model="code" :lang="variant.lang" />
        <p class="hint">写完后复制到「提交作业」页，选择对应作业 ID 提交评测。</p>
      </main>
    </div>
  </div>
</template>

<style scoped>
.variant-page { max-width: 1200px; }
.header { margin-bottom: 32px; }
.header h1 { font-family: 'Space Grotesk'; font-size: 28px; margin: 0 0 8px; }
.desc { color: var(--galaxy-text-secondary); font-size: 15px; margin: 0; }
.action-bar { display: flex; align-items: center; gap: 16px; margin-bottom: 32px; }
.input-group { display: flex; align-items: center; gap: 8px; }
.label { font-size: 14px; color: var(--galaxy-text-secondary); }

.split-layout { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.problem-panel {
  background: var(--galaxy-card);
  border: 1px solid var(--galaxy-border);
  border-radius: 12px;
  padding: 24px;
  overflow-y: auto;
  max-height: calc(100vh - 200px);
}
.variant-badge {
  display: inline-block;
  font-size: 12px;
  color: var(--galaxy-accent);
  background: rgba(91, 127, 255, 0.1);
  padding: 4px 10px;
  border-radius: 4px;
  margin-bottom: 12px;
}
.problem-panel h2 { font-size: 20px; margin: 0 0 12px; }
.desc-text { color: var(--galaxy-text-secondary); white-space: pre-wrap; line-height: 1.7; font-size: 14px; }
.cases, .points { margin-top: 20px; }
.cases h3, .points h3 { font-size: 15px; margin: 0 0 10px; }
.case-item { background: var(--galaxy-bg); border-radius: 6px; padding: 10px; margin-bottom: 8px; }
.case-item pre { margin: 4px 0 0; font-family: 'JetBrains Mono'; font-size: 12px; color: var(--galaxy-text-secondary); }
.points ul { padding-left: 20px; color: var(--galaxy-text-secondary); }

.code-panel { display: flex; flex-direction: column; gap: 12px; }
.code-header {
  display: flex; justify-content: space-between; align-items: center;
  background: var(--galaxy-card); border: 1px solid var(--galaxy-border);
  border-radius: 8px; padding: 12px 20px;
}
.code-header h3 { margin: 0; font-size: 15px; }
.hint { font-size: 13px; color: var(--galaxy-text-secondary); margin: 0; text-align: center; }

@media (max-width: 900px) { .split-layout { grid-template-columns: 1fr; } }
</style>
