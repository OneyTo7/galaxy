<script setup lang="ts">
import { ref } from 'vue'
import { useRoute } from 'vue-router'
import { diagnose } from '@/api/diagnose'
import { ElMessage } from 'element-plus'
import type { DiagnoseOut } from '@/types/api'

const route = useRoute()
const submissionId = ref(Number(route.query.submission) || 8)
const result = ref<DiagnoseOut | null>(null)
const loading = ref(false)

async function handleDiagnose() {
  loading.value = true
  result.value = null
  try {
    result.value = await diagnose(submissionId.value)
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '诊断失败')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="diagnose-page">
    <h1>误区诊断</h1>
    <p class="desc">AI 读取学生代码与评测结果，输出误区类型、证据、知识点与置信度。</p>
    <div class="form-bar">
      <span>提交 ID</span>
      <el-input-number v-model="submissionId" :min="1" />
      <el-button type="primary" :loading="loading" @click="handleDiagnose">触发诊断</el-button>
    </div>
    <div v-if="result" class="result">
      <div class="diag-card">
        <div class="diag-row">
          <span class="label">误区类型</span>
          <span class="value accent">{{ result.misconception_type }}</span>
        </div>
        <div class="diag-row">
          <span class="label">证据</span>
          <p class="value">{{ result.evidence }}</p>
        </div>
        <div class="diag-row">
          <span class="label">知识点</span>
          <span class="value">{{ result.knowledge_point }}</span>
        </div>
        <div class="diag-row">
          <span class="label">置信度</span>
          <span class="value">{{ (result.confidence * 100).toFixed(0) }}%</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.diagnose-page { max-width: 800px; }
.desc { color: var(--galaxy-text-secondary); margin-bottom: 24px; }
.form-bar { display: flex; align-items: center; gap: 12px; margin-bottom: 32px; }
.result { background: var(--galaxy-card); border: 1px solid var(--galaxy-border); border-radius: 8px; padding: 24px; }
.diag-card { display: flex; flex-direction: column; gap: 20px; }
.diag-row { display: flex; flex-direction: column; gap: 4px; }
.label { font-size: 13px; color: var(--galaxy-text-secondary); text-transform: uppercase; letter-spacing: 0.5px; }
.value { font-size: 16px; line-height: 1.6; }
.value.accent { color: var(--galaxy-accent); font-family: 'Space Grotesk'; font-weight: 700; font-size: 20px; }
</style>
