<script setup lang="ts">
import { ref, reactive, onBeforeUnmount } from 'vue'
import { submit, getEvaluation } from '@/api/submission'
import CodeEditor from '@/components/CodeEditor.vue'
import { ElMessage } from 'element-plus'
import type { EvaluationOut } from '@/types/api'

const POLL_INTERVAL = 2000
const MAX_POLL_COUNT = 30

const form = reactive({ assignment_id: 2, code: 'print("hello world")', lang: 'python' })
const submissionId = ref<number | null>(null)
const evaluation = ref<EvaluationOut | null>(null)
const loading = ref(false)
let pollTimer: number | null = null
let pollCount = 0

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
      ElMessage.warning('评测超时，请稍后查看结果')
      return
    }
    try {
      const res = await getEvaluation(submissionId.value)
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

onBeforeUnmount(() => {
  if (pollTimer) clearInterval(pollTimer)
})
</script>

<template>
  <div class="submit-page">
    <h1>提交作业</h1>
    <div class="form-bar">
      <span>作业 ID</span>
      <el-input-number v-model="form.assignment_id" :min="1" />
      <el-select v-model="form.lang" style="width: 120px">
        <el-option label="Python" value="python" />
      </el-select>
    </div>
    <CodeEditor v-model="form.code" :lang="form.lang" />
    <div class="actions">
      <el-button type="primary" :loading="loading" @click="handleSubmit">提交评测</el-button>
    </div>
    <div v-if="evaluation" class="result">
      <div class="result-header">
        <el-tag :type="evaluation.status === 'done' ? 'success' : 'warning'">{{ evaluation.status }}</el-tag>
        <span v-if="evaluation.status === 'done'" class="score">得分 {{ evaluation.score }}</span>
      </div>
      <div v-for="r in evaluation.results" :key="r.case_id" class="case" :class="{ fail: !r.passed }">
        <span class="case-icon">{{ r.passed ? '✓' : '✗' }}</span>
        <span>用例 {{ r.case_id }}</span>
        <span v-if="r.stderr" class="case-err">{{ r.stderr }}</span>
        <span v-if="r.timed_out" class="case-err">超时</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.submit-page { max-width: 900px; }
.form-bar { display: flex; align-items: center; gap: 12px; margin-bottom: 16px; }
.actions { margin-top: 16px; }
.result { margin-top: 24px; background: var(--galaxy-card); border: 1px solid var(--galaxy-border); border-radius: 8px; padding: 20px; }
.result-header { display: flex; align-items: center; gap: 12px; margin-bottom: 16px; }
.score { font-family: 'Space Grotesk'; font-size: 20px; font-weight: 700; color: var(--galaxy-accent); }
.case { display: flex; align-items: center; gap: 8px; padding: 8px 0; border-bottom: 1px solid var(--galaxy-border); }
.case.fail { color: var(--galaxy-error); }
.case-icon { font-weight: 700; }
.case-err { color: var(--galaxy-error); font-family: 'JetBrains Mono'; font-size: 13px; }
</style>
