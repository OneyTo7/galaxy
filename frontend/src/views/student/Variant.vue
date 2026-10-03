<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { generateVariant } from '@/api/variant'
import { listMySubmissions, submit, getEvaluation } from '@/api/submission'
import CodeEditor from '@/components/CodeEditor.vue'
import { ElMessage } from 'element-plus'
import type { VariantOut, SubmissionOut, EvaluationOut } from '@/types/api'

const POLL_INTERVAL = 2000
const MAX_POLL_COUNT = 30

const route = useRoute()
const router = useRouter()
const submissions = ref<SubmissionOut[]>([])
const submissionId = ref(Number(route.query.submission) || undefined)
const selectedSubmission = ref<SubmissionOut | null>(null)
const variant = ref<VariantOut | null>(null)
const code = ref('')
const loading = ref(false)
const submitting = ref(false)
const evaluation = ref<EvaluationOut | null>(null)
let pollTimer: number | null = null
let pollCount = 0

async function loadSubmissions() {
  try {
    submissions.value = await listMySubmissions()
    if (submissionId.value) {
      selectedSubmission.value = submissions.value.find(s => s.id === submissionId.value) || null
    }
  } catch (e) { console.error('加载提交列表失败', e) }
}

async function handleGenerate() {
  if (!submissionId.value) { ElMessage.warning('请先选择一条提交记录'); return }
  loading.value = true
  variant.value = null
  evaluation.value = null
  try {
    variant.value = await generateVariant(submissionId.value)
    code.value = ''
    selectedSubmission.value = submissions.value.find(s => s.id === submissionId.value) || null
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '生成失败')
  } finally {
    loading.value = false
  }
}

async function handleSubmitVariant() {
  if (!selectedSubmission.value || !code.value.trim()) {
    ElMessage.warning('请先写代码')
    return
  }
  submitting.value = true
  evaluation.value = null
  try {
    const res = await submit(selectedSubmission.value.assignment_id, code.value, variant.value?.lang || 'python')
    ElMessage.success('已提交变式代码，等待评测...')
    startPolling(res.submission_id)
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '提交失败')
  } finally {
    submitting.value = false
  }
}

function startPolling(subId: number) {
  if (pollTimer) clearInterval(pollTimer)
  pollCount = 0
  pollTimer = window.setInterval(async () => {
    pollCount++
    if (pollCount > MAX_POLL_COUNT) {
      if (pollTimer) clearInterval(pollTimer)
      pollTimer = null
      ElMessage.warning('评测超时，请在「我的提交」查看结果')
      return
    }
    try {
      const res = await getEvaluation(subId)
      evaluation.value = res
      if (res.status === 'done') {
        if (pollTimer) clearInterval(pollTimer)
        pollTimer = null
      }
    } catch (e) {
      console.error('评测查询失败', e)
    }
  }, POLL_INTERVAL)
}

onMounted(loadSubmissions)
onBeforeUnmount(() => { if (pollTimer) clearInterval(pollTimer) })
</script>

<template>
  <div class="variant-page">
    <div class="header">
      <h1>变式练习</h1>
      <p class="desc">基于你的误区，AI 生成一道换情境的变式题，帮你对症练习同一个知识点。</p>
    </div>

    <div v-if="!variant" class="action-bar">
      <div class="input-group">
        <span class="label">选择提交</span>
        <el-select v-model="submissionId" placeholder="选择一条提交" style="width: 240px">
          <el-option v-for="s in submissions" :key="s.id" :label="`#${s.id} 作业${s.assignment_id} ${s.status} ${s.score}分`" :value="s.id" />
        </el-select>
      </div>
      <el-button type="primary" :loading="loading" @click="handleGenerate">生成变式题</el-button>
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
        <div class="back-link">
          <el-button text @click="variant = null">选择其他提交</el-button>
        </div>
      </aside>

      <main class="code-panel">
        <div class="code-header">
          <h3>你的代码</h3>
          <el-button type="primary" :loading="submitting" @click="handleSubmitVariant">提交评测</el-button>
        </div>
        <CodeEditor v-model="code" :lang="variant.lang" />

        <div v-if="evaluation" class="result">
          <div class="result-header">
            <el-tag :type="evaluation.status === 'done' ? 'success' : 'warning'">{{ evaluation.status }}</el-tag>
            <span v-if="evaluation.status === 'done'" class="score">得分 {{ evaluation.score }}</span>
          </div>
          <div v-for="r in evaluation.results" :key="r.case_id" class="case-row" :class="{ fail: !r.passed }">
            <span class="case-icon">{{ r.passed ? '✓' : '✗' }}</span>
            <span>用例 {{ r.case_id }}</span>
            <span v-if="r.stderr" class="case-err">{{ r.stderr }}</span>
          </div>
          <div v-if="evaluation.status === 'done'" class="result-actions">
            <el-button text size="small" @click="router.push('/my-submissions')">查看我的提交</el-button>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<style scoped>
.variant-page { max-width: 1200px; }
.header { margin-bottom: 32px; }
.header h1 { font-family: 'Space Grotesk'; font-size: 28px; margin: 0 0 8px; }
.desc { color: var(--galaxy-text-secondary); font-size: 15px; margin: 0; }
.action-bar { display: flex; align-items: center; gap: 16px; }
.input-group { display: flex; align-items: center; gap: 8px; }
.label { font-size: 14px; color: var(--galaxy-text-secondary); }

.split-layout { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.problem-panel {
  background: var(--galaxy-card-solid); border: 1px solid var(--galaxy-border);
  border-radius: 10px; padding: 24px; overflow-y: auto; max-height: calc(100vh - 220px);
}
.variant-badge {
  display: inline-block; font-size: 12px; color: var(--galaxy-accent);
  background: var(--galaxy-accent-soft); padding: 4px 10px; border-radius: 4px; margin-bottom: 12px;
}
.problem-panel h2 { font-size: 20px; margin: 0 0 12px; }
.desc-text { color: var(--galaxy-text-secondary); white-space: pre-wrap; line-height: 1.7; font-size: 14px; }
.cases, .points { margin-top: 20px; }
.cases h3, .points h3 { font-size: 15px; margin: 0 0 10px; }
.case-item { background: var(--galaxy-bg); border-radius: 6px; padding: 10px; margin-bottom: 8px; }
.case-item pre { margin: 4px 0 0; font-family: 'JetBrains Mono'; font-size: 12px; color: var(--galaxy-text-secondary); }
.points ul { padding-left: 20px; color: var(--galaxy-text-secondary); }
.back-link { margin-top: 20px; }

.code-panel { display: flex; flex-direction: column; gap: 12px; }
.code-header {
  display: flex; justify-content: space-between; align-items: center;
  background: var(--galaxy-card-solid); border: 1px solid var(--galaxy-border);
  border-radius: 8px; padding: 12px 20px;
}
.code-header h3 { margin: 0; font-size: 15px; }

.result {
  background: var(--galaxy-card-solid); border: 1px solid var(--galaxy-border);
  border-radius: 8px; padding: 16px; max-height: 200px; overflow-y: auto;
}
.result-header { display: flex; align-items: center; gap: 12px; margin-bottom: 10px; }
.score { font-family: 'Space Grotesk'; font-weight: 700; font-size: 18px; color: var(--galaxy-accent); }
.case-row { display: flex; align-items: center; gap: 8px; padding: 4px 0; border-bottom: 1px solid var(--galaxy-border); font-size: 14px; }
.case-row.fail { color: var(--galaxy-error); }
.case-icon { font-weight: 700; }
.case-err { color: var(--galaxy-error); font-family: 'JetBrains Mono'; font-size: 12px; }
.result-actions { margin-top: 12px; }

@media (max-width: 900px) { .split-layout { grid-template-columns: 1fr; } }
</style>
