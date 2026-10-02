<script setup lang="ts">
import { ref } from 'vue'
import { checkCheating, getCheatingReports } from '@/api/cheating'
import { ElMessage } from 'element-plus'
import type { CheatingReportOut } from '@/types/api'

const submissionId = ref(8)
const reports = ref<CheatingReportOut[]>([])
const loading = ref(false)

async function handleCheck() {
  loading.value = true
  try {
    await checkCheating(submissionId.value)
    ElMessage.success('检测完成')
    loadReports()
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '检测失败')
  } finally {
    loading.value = false
  }
}

async function loadReports() {
  try {
    reports.value = await getCheatingReports(submissionId.value)
  } catch (e) {
    console.error('加载报告失败', e)
  }
}
</script>

<template>
  <div class="cheating-page">
    <h1>反作弊报告</h1>
    <p class="desc">AI 代写检测，判断代码是否疑似 AI 生成。</p>
    <div class="form-bar">
      <span>提交 ID</span>
      <el-input-number v-model="submissionId" :min="1" />
      <el-button type="primary" :loading="loading" @click="handleCheck">触发检测</el-button>
    </div>
    <div v-if="reports.length" class="reports">
      <div v-for="r in reports" :key="r.id" class="report-card" :class="r.status">
        <div class="report-header">
          <el-tag :type="r.status === 'flagged' ? 'danger' : 'success'">
            {{ r.status === 'flagged' ? '疑似 AI 生成' : '未检出' }}
          </el-tag>
          <span class="score">可疑度 {{ (r.score * 100).toFixed(0) }}%</span>
        </div>
        <p class="detail">{{ r.detail }}</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.cheating-page { max-width: 800px; }
.desc { color: var(--galaxy-text-secondary); margin-bottom: 24px; }
.form-bar { display: flex; align-items: center; gap: 12px; margin-bottom: 24px; }
.reports { display: flex; flex-direction: column; gap: 16px; }
.report-card { background: var(--galaxy-card); border: 1px solid var(--galaxy-border); border-radius: 8px; padding: 20px; }
.report-card.flagged { border-left: 4px solid var(--galaxy-error); }
.report-header { display: flex; align-items: center; gap: 12px; margin-bottom: 12px; }
.score { font-family: 'Space Grotesk'; font-weight: 700; }
.detail { color: var(--galaxy-text-secondary); line-height: 1.6; margin: 0; }
</style>
