<script setup lang="ts">
import { ref, reactive, onMounted, onBeforeUnmount, watch } from 'vue'
import { useRoute } from 'vue-router'
import { submit, getEvaluation } from '@/api/submission'
import { getAssignment } from '@/api/assignment'
import CodeEditor from '@/components/CodeEditor.vue'
import { ElMessage } from 'element-plus'
import type { EvaluationOut, AssignmentOut } from '@/types/api'

const POLL_INTERVAL = 2000
const MAX_POLL_COUNT = 30

const route = useRoute()
const assignmentId = Number(route.query.assignment) || 0
const assignment = ref<AssignmentOut | null>(null)
const form = reactive({ assignment_id: assignmentId, code: '# 在这里写代码\nprint("hello world")', lang: 'python' })
const submissionId = ref<number | null>(null)
const evaluation = ref<EvaluationOut | null>(null)
const loading = ref(false)
let pollTimer: number | null = null
let pollCount = 0

onMounted(async () => {
  if (assignmentId) {
    try {
      assignment.value = await getAssignment(assignmentId)
      form.lang = assignment.value.lang
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
    <!-- 作业详情 -->
    <div v-if="assignment" class="assignment-detail">
      <h1>{{ assignment.title }}</h1>
      <div class="meta">
        <el-tag>语言 {{ assignment.lang }}</el-tag>
        <el-tag type="info">{{ assignment.test_cases?.length || 0 }} 个测试用例</el-tag>
      </div>
      <div class="desc-section">
        <h3>题目描述</h3>
        <p class="desc-text">{{ assignment.description }}</p>
      </div>
      <div v-if="assignment.test_cases?.some(tc => !tc.is_hidden)" class="cases-section">
        <h3>公开用例</h3>
        <div v-for="tc in assignment.test_cases.filter(tc => !tc.is_hidden)" :key="tc.id" class="case-item">
          <span class="case-name">{{ tc.name || '用例 ' + tc.id }}</span>
          <pre>输入: {{ tc.input }}</pre>
          <pre>期望输出: {{ tc.expected_output }}</pre>
        </div>
      </div>
    </div>

    <div v-else class="no-assignment">
      <p>未指定作业，请从<a href="/assignments">作业列表</a>选择一道题。</p>
    </div>

    <!-- 代码编辑器 -->
    <div v-if="assignment" class="editor-section">
      <h3>你的代码</h3>
      <CodeEditor v-model="form.code" :lang="form.lang" />
      <div class="actions">
        <el-button type="primary" :loading="loading" @click="handleSubmit">提交评测</el-button>
      </div>
    </div>

    <!-- 评测结果 -->
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
.assignment-detail { background: var(--galaxy-card); border: 1px solid var(--galaxy-border); border-radius: 8px; padding: 24px; margin-bottom: 24px; }
.assignment-detail h1 { margin: 0 0 12px; font-size: 24px; }
.meta { display: flex; gap: 8px; margin-bottom: 20px; }
.desc-section h3, .cases-section h3, .editor-section h3 { font-size: 16px; margin: 0 0 12px; }
.desc-text { color: var(--galaxy-text-secondary); white-space: pre-wrap; line-height: 1.6; }
.cases-section { margin-top: 20px; }
.case-item { background: var(--galaxy-bg); border-radius: 6px; padding: 12px; margin-bottom: 8px; }
.case-name { font-weight: 500; }
.case-item pre { margin: 8px 0 0; font-family: 'JetBrains Mono'; font-size: 13px; color: var(--galaxy-text-secondary); }
.editor-section { margin-bottom: 24px; }
.actions { margin-top: 16px; }
.no-assignment { text-align: center; padding: 60px 0; color: var(--galaxy-text-secondary); }
.no-assignment a { color: var(--galaxy-accent); }
.result { background: var(--galaxy-card); border: 1px solid var(--galaxy-border); border-radius: 8px; padding: 20px; }
.result-header { display: flex; align-items: center; gap: 12px; margin-bottom: 16px; }
.score { font-family: 'Space Grotesk'; font-size: 20px; font-weight: 700; color: var(--galaxy-accent); }
.case { display: flex; align-items: center; gap: 8px; padding: 8px 0; border-bottom: 1px solid var(--galaxy-border); }
.case.fail { color: var(--galaxy-error); }
.case-icon { font-weight: 700; }
.case-err { color: var(--galaxy-error); font-family: 'JetBrains Mono'; font-size: 13px; }
</style>
