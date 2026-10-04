<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { checkCheating, getCheatingReports } from '@/api/cheating'
import { listMySubmissions } from '@/api/submission'
import { ElMessage } from 'element-plus'
import type { CheatingReportOut, SubmissionOut } from '@/types/api'

const route = useRoute()
const submissions = ref<SubmissionOut[]>([])
const submissionId = ref(Number(route.query.submission) || undefined)
const reports = ref<CheatingReportOut[]>([])
const loading = ref(false)

async function loadSubmissions() {
  try { submissions.value = await listMySubmissions() } catch (e) { console.error('加载提交列表失败', e) }
}

onMounted(loadSubmissions)

async function handleCheck() {
  if (!submissionId.value) {
    ElMessage.warning('请先选择一条提交记录')
    return
  }
  loading.value = true
  try {
    await checkCheating(submissionId.value)
    ElMessage.success('检测完成')
    reports.value = await getCheatingReports(submissionId.value)
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '检测失败')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="page cheating-page">
    <div class="page-header">
      <div class="page-title-with-chip">
        <span class="page-title-chip"><el-icon><Warning /></el-icon></span>
        <div>
          <h1>反作弊检测</h1>
          <p class="page-desc">AI 分析代码特征，判断是否疑似 AI 生成。可疑度越高越可能非手写。</p>
        </div>
      </div>
    </div>

    <div class="panel action-bar rise-in" style="--enter-idx:0">
      <div class="input-group">
        <span class="label">选择提交</span>
        <el-select v-model="submissionId" placeholder="选择一条提交" style="width: 240px">
          <el-option v-for="s in submissions" :key="s.id" :label="`#${s.id} 作业${s.assignment_id} ${s.status} ${s.score}分`" :value="s.id" />
        </el-select>
      </div>
      <el-button type="primary" :loading="loading" @click="handleCheck"><el-icon style="margin-right:4px"><Aim /></el-icon>开始检测</el-button>
    </div>

    <div v-if="!loading && reports.length === 0 && submissionId" class="empty-state-v2 rise-in" style="--enter-idx:1">
      <span class="empty-ico"><el-icon><Document /></el-icon></span>
      <p>暂无检测记录，点击「开始检测」</p>
    </div>

    <div class="reports">
      <div v-for="(r, idx) in reports" :key="r.id" class="panel report-card rise-in" :class="r.status" :style="`--enter-idx:${idx + 1}`">
        <div class="report-head">
          <div class="status-badge" :class="r.status">
            {{ r.status === 'flagged' ? '⚠ 疑似 AI 生成' : '✓ 未检出' }}
          </div>
          <div class="conf-display">
            <span class="conf-num">{{ (r.score * 100).toFixed(0) }}%</span>
            <span class="conf-label">可疑度</span>
          </div>
        </div>
        <p class="report-detail">{{ r.detail }}</p>
        <span class="report-time">{{ r.created_at }}</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.cheating-page { max-width: 700px; }
.action-bar { display: flex; align-items: center; gap: var(--space-md); margin-bottom: var(--space-lg); }
.input-group { display: flex; align-items: center; gap: var(--space-xs); }
.label { font-size: var(--fs-body); color: var(--text-secondary); }

.reports { display: flex; flex-direction: column; gap: var(--space-md); }
.report-card { border-left: 4px solid var(--success); }
.report-card.flagged { border-left-color: var(--danger); }
.report-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: var(--space-md); }
.status-badge { font-size: var(--fs-body); font-weight: 700; padding: 6px 16px; border-radius: var(--radius-sm); }
.status-badge.cleared { color: var(--success); background: rgba(18, 183, 106, 0.12); }
.status-badge.flagged { color: var(--danger); background: rgba(239, 68, 68, 0.10); }
.conf-display { text-align: right; }
.conf-num { font-size: var(--fs-data); font-weight: 700; display: block; }
.conf-label { font-size: var(--fs-caption); color: var(--text-secondary); }
.report-detail { font-size: var(--fs-body); line-height: 1.6; color: var(--ink-2); margin: 0 0 var(--space-sm); }
.report-time { font-size: var(--fs-caption); color: var(--text-secondary); }
</style>
