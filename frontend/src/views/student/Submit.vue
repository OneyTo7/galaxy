<script setup lang="ts">
import { ref, reactive, onMounted, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { submit, getEvaluation } from '@/api/submission'
import { diagnose } from '@/api/diagnose'
import { getAssignment } from '@/api/assignment'
import { Loading } from '@element-plus/icons-vue'
import CodeEditor from '@/components/CodeEditor.vue'
import { ElMessage } from 'element-plus'
import type { EvaluationOut, AssignmentOut, DiagnoseOut } from '@/types/api'

const POLL_INTERVAL = 2000
const MAX_POLL_COUNT = 30

const route = useRoute()
const router = useRouter()
const assignmentId = Number(route.query.assignment) || 0
const assignment = ref<AssignmentOut | null>(null)
const form = reactive({ assignment_id: assignmentId, code: '# 在这里写代码\nprint("hello world")', lang: 'python' })
const submissionId = ref<number | null>(null)
const evaluation = ref<EvaluationOut | null>(null)
const diagnosis = ref<DiagnoseOut | null>(null)
const diagnosing = ref(false)
const loading = ref(false)
let pollTimer: number | null = null
let pollCount = 0

const langOptions = [
  { label: 'Python', value: 'python' },
  { label: 'C', value: 'c' },
  { label: 'C++', value: 'cpp' },
  { label: 'Java', value: 'java' },
]

onMounted(async () => {
  if (assignmentId) {
    try {
      assignment.value = await getAssignment(assignmentId)
      form.lang = assignment.value!.lang
    } catch (e) {
      console.error('加载作业详情失败', e)
    }
  }
})

async function handleSubmit() {
  loading.value = true
  evaluation.value = null
  try {
    const res = await submit(form.assignment_id, form.code, form.lang)
    submissionId.value = res.submission_id
    pollCount = 0
    ElMessage.success('已提交，等待评测...')
    startPolling()
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '提交失败')
  } finally {
    loading.value = false
  }
}

function startPolling() {
  if (pollTimer) clearInterval(pollTimer)
  pollTimer = window.setInterval(async () => {
    if (!submissionId.value) return
    pollCount++
    if (pollCount > MAX_POLL_COUNT) {
      if (pollTimer) clearInterval(pollTimer)
      pollTimer = null
      ElMessage.warning('评测超时，请稍后在「我的提交」查看结果')
      return
    }
    try {
      const res = await getEvaluation(submissionId.value)
      evaluation.value = res
      if (res.status === 'done') {
        if (pollTimer) clearInterval(pollTimer)
        pollTimer = null
        autoDiagnose()
      }
    } catch (e) {
      console.error('评测查询失败', e)
    }
  }, POLL_INTERVAL)
}

onBeforeUnmount(() => {
  if (pollTimer) clearInterval(pollTimer)
})

async function autoDiagnose() {
  if (!submissionId.value) return
  diagnosing.value = true
  diagnosis.value = null
  try {
    diagnosis.value = await diagnose(submissionId.value)
  } catch (e: any) {
    console.error('自动诊断失败', e)
  } finally {
    diagnosing.value = false
  }
}
</script>

<template>
  <div v-if="!assignment" class="empty-state-v2 rise-in" style="--enter-idx:0">
    <div class="empty-ico"><el-icon><Document /></el-icon></div>
    <p>未指定作业，请从<router-link to="/assignments" style="color: var(--primary)">作业列表</router-link>选择一道题。</p>
  </div>

  <div v-else class="split-layout">
    <!-- 左侧：题目 -->
    <aside class="problem-panel panel rise-in" style="--enter-idx:0">
      <div class="problem-head">
        <div class="page-title-with-chip">
          <span class="page-title-chip"><el-icon><Reading /></el-icon></span>
          <div>
            <h1>{{ assignment.title }}</h1>
            <p class="page-desc">按要求完成并提交代码，系统将自动评测并给出诊断。</p>
          </div>
        </div>
      </div>
      <div class="meta">
        <el-tag v-if="assignment.kind === 'practice'" size="small" type="warning">变式练习</el-tag>
        <el-tag size="small">要求语言 {{ assignment.lang }}</el-tag>
        <el-tag size="small" type="info">{{ assignment.test_cases?.length || 0 }} 个用例</el-tag>
      </div>
      <div class="section">
        <div class="section-title"><span class="title-ico"><el-icon><Document /></el-icon></span>题目描述</div>
        <p class="desc-text">{{ assignment.description }}</p>
      </div>
      <div v-if="assignment.test_cases?.some(tc => !tc.is_hidden)" class="section">
        <div class="section-title"><span class="title-ico"><el-icon><List /></el-icon></span>公开用例</div>
        <div v-for="tc in assignment.test_cases.filter(tc => !tc.is_hidden)" :key="tc.id" class="case-item">
          <span class="case-name">{{ tc.name || '用例 ' + tc.id }}</span>
          <pre>输入: {{ tc.input }}</pre>
          <pre>期望: {{ tc.expected_output }}</pre>
        </div>
      </div>
    </aside>

    <!-- 右侧：代码 + 评测 -->
    <main class="code-panel">
      <div class="code-header panel rise-in" style="--enter-idx:1">
        <div class="code-header-left">
          <div class="section-title" style="margin: 0"><span class="title-ico"><el-icon><Edit /></el-icon></span>代码编辑</div>
          <el-select v-model="form.lang" size="small" style="width: 120px">
            <el-option v-for="opt in langOptions" :key="opt.value" :label="opt.label" :value="opt.value" />
          </el-select>
        </div>
        <el-button type="primary" :loading="loading" @click="handleSubmit">
          <el-icon style="margin-right: 4px"><Promotion /></el-icon>提交评测
        </el-button>
      </div>
      <div class="rise-in" style="--enter-idx:2">
        <CodeEditor v-model="form.code" :lang="form.lang" />
      </div>

      <div v-if="evaluation" class="result panel rise-in" style="--enter-idx:3">
        <div class="section-title"><span class="title-ico"><el-icon><DataLine /></el-icon></span>评测结果</div>
        <div class="result-header">
          <el-tag :type="evaluation.status === 'done' ? 'success' : 'warning'">{{ evaluation.status }}</el-tag>
          <span v-if="evaluation.status === 'done'" class="score">得分 {{ evaluation.score }}</span>
        </div>
        <div v-for="r in evaluation.results" :key="r.case_id" class="case-result" :class="{ fail: !r.passed }">
          <span class="case-icon">{{ r.passed ? '✓' : '✗' }}</span>
          <span>用例 {{ r.case_id }}</span>
          <span v-if="r.stderr" class="case-err">{{ r.stderr }}</span>
          <span v-if="r.timed_out" class="case-err">超时</span>
        </div>
      </div>

      <!-- 自动诊断加载 -->
      <div v-if="diagnosing" class="diagnose-loading rise-in" style="--enter-idx:4">
        <el-icon class="is-loading"><Loading /></el-icon>
        <span>AI 正在诊断你的代码误区...</span>
      </div>

      <div v-if="diagnosis" class="diagnosis-card rise-in" style="--enter-idx:4">
        <div class="diag-head">
          <span class="diag-badge"><el-icon style="margin-right: 4px"><MagicStick /></el-icon>AI 误区诊断</span>
          <span class="diag-confidence">{{ (diagnosis.confidence * 100).toFixed(0) }}%</span>
        </div>
        <div class="diag-body">
          <div class="diag-row">
            <span class="diag-label">误区类型</span>
            <span class="diag-value accent">{{ diagnosis.misconception_type }}</span>
          </div>
          <div class="diag-row">
            <span class="diag-label">证据</span>
            <p class="diag-text">{{ diagnosis.evidence }}</p>
          </div>
          <div class="diag-row">
            <span class="diag-label">知识点</span>
            <span class="diag-value">{{ diagnosis.knowledge_point }}</span>
          </div>
        </div>
        <div class="diag-actions">
          <el-button type="primary" size="small" @click="router.push(`/variant?submission=${submissionId}`)">
            <el-icon style="margin-right: 4px"><MagicStick /></el-icon>去做变式练习
          </el-button>
          <el-button text size="small" @click="router.push('/my-submissions')">
            <el-icon style="margin-right: 4px"><Document /></el-icon>查看我的提交
          </el-button>
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
.split-layout {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-md);
  height: calc(100vh - 64px - 64px);
}

/* 左侧题目 */
.problem-panel { overflow-y: auto; }
.problem-head { margin-bottom: var(--space-md); }
.meta {
  display: flex;
  gap: 8px;
  margin-bottom: var(--space-md);
  flex-wrap: wrap;
}
.section { margin-bottom: var(--space-md); }
.desc-text {
  color: var(--text-secondary);
  white-space: pre-wrap;
  line-height: 1.7;
  font-size: var(--fs-body);
}
.case-item {
  background: var(--bg-sunken);
  border-radius: var(--radius-sm);
  padding: 10px 12px;
  margin-bottom: 8px;
}
.case-name {
  font-weight: 500;
  font-size: var(--fs-body);
}
.case-item pre {
  margin: 6px 0 0;
  font-family: 'SF Mono', Menlo, Consolas, monospace;
  font-size: var(--fs-code);
  color: var(--text-secondary);
}

/* 右侧代码 */
.code-panel {
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
}
.code-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: var(--space-sm);
}
.code-header-left { display: flex; align-items: center; gap: var(--space-sm); flex-wrap: wrap; }
.code-header :deep(.code-editor) {
  height: 500px;
}

/* 评测结果 */
.result {
  max-height: 240px;
  overflow-y: auto;
}
.result-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}
.score {
  font-family: -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Segoe UI', sans-serif;
  font-size: 20px;
  font-weight: 700;
  color: var(--primary);
}
.case-result {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 0;
  border-bottom: 1px solid var(--border);
  font-size: var(--fs-body);
}
.case-result.fail { color: var(--danger); }
.case-icon { font-weight: 700; }
.case-err {
  color: var(--danger);
  font-family: 'SF Mono', Menlo, Consolas, monospace;
  font-size: var(--fs-code);
}

/* 诊断加载 */
.diagnose-loading {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: var(--space-md);
  color: var(--text-secondary);
  font-size: var(--fs-body);
}

/* AI 诊断卡片 */
.diagnosis-card {
  background: linear-gradient(135deg, rgba(79, 124, 255, 0.06), rgba(79, 124, 255, 0.01));
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  overflow: hidden;
}
.diag-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 20px;
  border-bottom: 1px solid var(--border);
}
.diag-badge {
  font-size: 13px;
  font-weight: 600;
  color: var(--primary);
  background: rgba(79, 124, 255, 0.10);
  padding: 3px 10px;
  border-radius: var(--radius-sm);
}
.diag-confidence {
  font-family: -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Segoe UI', sans-serif;
  font-weight: 700;
  font-size: 16px;
  color: var(--text-secondary);
}
.diag-body { padding: 16px 20px; }
.diag-row { margin-bottom: 12px; }
.diag-row:last-child { margin-bottom: 0; }
.diag-label {
  display: block;
  font-size: var(--fs-caption);
  color: var(--text-placeholder);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 4px;
}
.diag-value { font-size: 15px; font-weight: 600; color: var(--ink); }
.diag-value.accent { color: var(--primary); font-size: 17px; }
.diag-text { font-size: var(--fs-body); line-height: 1.6; margin: 0; color: var(--ink-2); }
.diag-actions { padding: 12px 20px; display: flex; gap: 8px; }

/* 响应式：窄屏改上下布局 */
@media (max-width: 900px) {
  .split-layout {
    grid-template-columns: 1fr;
    height: auto;
  }
}
</style>
