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
  <div class="cheating-page">
    <div class="header">
      <h1>反作弊检测</h1>
      <p class="desc">AI 分析代码特征，判断是否疑似 AI 生成。可疑度越高越可能非手写。</p>
    </div>

    <div class="action-bar">
      <div class="input-group">
        <span class="label">选择提交</span>
        <el-select v-model="submissionId" placeholder="选择一条提交" style="width: 240px">
          <el-option v-for="s in submissions" :key="s.id" :label="`#${s.id} 作业${s.assignment_id} ${s.status} ${s.score}分`" :value="s.id" />
        </el-select>
      </div>
      <el-button type="primary" :loading="loading" @click="handleCheck">开始检测</el-button>
    </div>

    <div v-if="!loading && reports.length === 0 && submissionId" class="empty">
      <p>暂无检测记录，点击「开始检测」</p>
    </div>

    <div class="reports">
      <div v-for="r in reports" :key="r.id" class="report-card" :class="r.status">
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
.header { margin-bottom: 32px; }
.header h1 { font-family: 'Space Grotesk'; font-size: 28px; margin: 0 0 8px; }
.desc { color: var(--galaxy-text-secondary); font-size: 15px; margin: 0; }
.action-bar { display: flex; align-items: center; gap: 16px; margin-bottom: 32px; }
.input-group { display: flex; align-items: center; gap: 8px; }
.label { font-size: 14px; color: var(--galaxy-text-secondary); }
.empty { text-align: center; padding: 40px 0; color: var(--galaxy-text-secondary); }

.reports { display: flex; flex-direction: column; gap: 16px; }
.report-card {
  background: var(--galaxy-card); border: 1px solid var(--galaxy-border);
  border-radius: 12px; padding: 24px; border-left: 4px solid var(--galaxy-success);
}
.report-card.flagged { border-left-color: var(--galaxy-error); }
.report-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.status-badge {
  font-size: 16px; font-weight: 700; padding: 6px 16px; border-radius: 6px;
}
.status-badge.cleared { color: var(--galaxy-success); background: rgba(61, 170, 82, 0.1); }
.status-badge.flagged { color: var(--galaxy-error); background: rgba(232, 93, 93, 0.1); }
.conf-display { text-align: right; }
.conf-num { font-family: 'Space Grotesk'; font-size: 28px; font-weight: 700; display: block; }
.conf-label { font-size: 12px; color: var(--galaxy-text-secondary); }
.report-detail { font-size: 15px; line-height: 1.6; color: var(--galaxy-text); margin: 0 0 12px; }
.report-time { font-size: 12px; color: var(--galaxy-text-secondary); }
</style>
