<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { listMySubmissions } from '@/api/submission'
import { getEvaluation } from '@/api/submission'
import { diagnose } from '@/api/diagnose'
import { ElMessage } from 'element-plus'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart, PieChart } from 'echarts/charts'
import { TooltipComponent, GridComponent, LegendComponent } from 'echarts/components'
import VChart from 'vue-echarts'
import type { SubmissionOut, EvaluationOut, DiagnoseOut } from '@/types/api'

use([CanvasRenderer, LineChart, PieChart, TooltipComponent, GridComponent, LegendComponent])

const route = useRoute()
const router = useRouter()
const submissions = ref<SubmissionOut[]>([])
const loading = ref(false)
const selectedSub = ref<SubmissionOut | null>(null)
const evaluation = ref<EvaluationOut | null>(null)
const diagnosis = ref<DiagnoseOut | null>(null)
const detailLoading = ref(false)

// 学生 ID 从 query 取
const studentId = Number(route.query.student) || 0

async function load() {
  loading.value = true
  try {
    const all = await listMySubmissions()
    submissions.value = all.filter(s => s.user_id === studentId || !studentId)
    if (submissions.value.length > 0) viewSub(submissions.value[0])
  } catch (e) { console.error('加载失败', e) }
  finally { loading.value = false }
}

async function viewSub(sub: SubmissionOut) {
  selectedSub.value = sub
  evaluation.value = null
  diagnosis.value = null
  detailLoading.value = true
  try {
    evaluation.value = await getEvaluation(sub.id)
    try { diagnosis.value = await diagnose(sub.id) } catch {}
  } catch (e: any) { ElMessage.error(e.response?.data?.detail || '加载失败') }
  finally { detailLoading.value = false }
}

const scoreTrend = computed(() => {
  const done = submissions.value.filter(s => s.status === 'done').reverse()
  return {
    tooltip: { trigger: 'axis', backgroundColor: '#FFFFFF', borderColor: '#E5E9F2', textStyle: { color: '#1F2937' } },
    xAxis: { type: 'category', data: done.map(s => `#${s.id}`), axisLabel: { color: '#6B7280' }, axisLine: { lineStyle: { color: '#E5E9F2' } } },
    yAxis: { type: 'value', min: 0, max: 100, axisLabel: { color: '#6B7280' }, splitLine: { lineStyle: { color: '#E5E9F2' } } },
    grid: { left: '3%', right: '5%', bottom: '10%', containLabel: true },
    series: [{ type: 'line', data: done.map(s => s.score), smooth: true, itemStyle: { color: '#4F7CFF' }, lineStyle: { color: '#4F7CFF', width: 2 }, areaStyle: { color: 'rgba(79,124,255,0.08)' } }],
  }
})

const avgScore = computed(() => {
  const done = submissions.value.filter(s => s.status === 'done')
  if (!done.length) return 0
  return Math.round(done.reduce((sum, s) => sum + s.score, 0) / done.length)
})

onMounted(load)
</script>

<template>
  <div class="page" v-loading="loading">
    <div class="page-header">
      <div>
        <h1>学生个人报告</h1>
        <p class="page-desc">学生成绩走势、误区分布与诊断历史。</p>
      </div>
      <el-button @click="router.back()">返回</el-button>
    </div>

    <div v-if="submissions.length === 0 && !loading" class="empty-state">
      <p class="empty-text">暂无提交记录</p>
    </div>

    <template v-else>
      <div class="stat-row">
        <div class="stat-card">
          <span class="stat-num">{{ submissions.length }}</span>
          <span class="stat-label">提交总数</span>
        </div>
        <div class="stat-card">
          <span class="stat-num">{{ submissions.filter(s => s.status === 'done').length }}</span>
          <span class="stat-label">已完成</span>
        </div>
        <div class="stat-card">
          <span class="stat-num">{{ avgScore }}</span>
          <span class="stat-label">平均分</span>
        </div>
      </div>

      <div class="split-layout">
        <aside class="sidebar">
          <div class="card">
            <h3>提交历史</h3>
            <div class="sub-list">
              <div v-for="s in submissions" :key="s.id" class="sub-item" :class="{ active: selectedSub?.id === s.id }" @click="viewSub(s)">
                <span class="sub-id">#{{ s.id }}</span>
                <el-tag :type="s.status === 'done' ? 'success' : 'warning'" size="small">{{ s.status }}</el-tag>
                <span v-if="s.status === 'done'" class="sub-score">{{ s.score }}</span>
              </div>
            </div>
          </div>
        </aside>

        <main class="main-content">
          <div class="card">
            <h3>成绩走势</h3>
            <v-chart class="chart" :option="scoreTrend" autoresize />
          </div>

          <div v-if="selectedSub" v-loading="detailLoading">
            <div class="card">
              <div class="eval-header">
                <h3>提交 #{{ selectedSub.id }}</h3>
                <el-tag :type="selectedSub.status === 'done' ? 'success' : 'warning'" size="small">{{ selectedSub.status }}</el-tag>
                <span v-if="selectedSub.status === 'done'" class="score-big">{{ selectedSub.score }}分</span>
              </div>
              <div v-if="evaluation" class="section">
                <h4>评测结果</h4>
                <div v-for="r in evaluation.results" :key="r.case_id" class="case-row" :class="{ fail: !r.passed }">
                  <span class="case-icon">{{ r.passed ? '✓' : '✗' }}</span>
                  <span>用例 {{ r.case_id }}</span>
                  <span v-if="r.stderr" class="case-err">{{ r.stderr }}</span>
                </div>
              </div>
            </div>

            <div v-if="diagnosis" class="card diagnosis-card">
              <div class="diag-head">
                <span class="diag-badge">AI 误区诊断</span>
                <span class="diag-conf">{{ (diagnosis.confidence * 100).toFixed(0) }}%</span>
              </div>
              <div class="diag-row">
                <span class="diag-label">误区类型</span>
                <span class="diag-value primary">{{ diagnosis.misconception_type }}</span>
              </div>
              <div class="diag-row">
                <span class="diag-label">证据</span>
                <p class="diag-text">{{ diagnosis.evidence }}</p>
              </div>
              <div class="diag-row">
                <span class="diag-label">知识点</span>
                <el-tag size="small">{{ diagnosis.knowledge_point }}</el-tag>
              </div>
            </div>
          </div>
        </main>
      </div>
    </template>
  </div>
</template>

<style scoped>
.page { max-width: 100%; }
.page-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: var(--space-lg); }
.page-desc { margin: 0; font-size: var(--fs-body); color: var(--text-secondary); }
.empty-state { text-align: center; padding: var(--space-xl) 0; }
.empty-text { color: var(--text-secondary); }

.stat-row { display: flex; gap: var(--space-md); margin-bottom: var(--space-lg); }
.stat-card { flex: 1; background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius-lg); padding: var(--space-md); box-shadow: var(--shadow-card); }
.stat-num { font-size: var(--fs-data); font-weight: 700; display: block; }
.stat-label { font-size: var(--fs-caption); color: var(--text-secondary); display: block; margin-top: 4px; }

.split-layout { display: grid; grid-template-columns: 260px 1fr; gap: var(--space-lg); }

.card { background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius-lg); padding: var(--space-md); margin-bottom: var(--space-md); box-shadow: var(--shadow-card); }
.card h3 { margin: 0 0 var(--space-sm); font-size: var(--fs-h3); }
.card h4 { font-size: var(--fs-body); font-weight: 500; margin: 0 0 var(--space-xs); }
.chart { height: 240px; }

.sub-list { display: flex; flex-direction: column; gap: var(--space-xs); }
.sub-item { display: flex; align-items: center; gap: var(--space-xs); padding: var(--space-xs) var(--space-sm); border-radius: var(--radius-md); cursor: pointer; transition: all var(--duration) var(--ease); }
.sub-item:hover { background: var(--bg-hover); }
.sub-item.active { background: var(--bg-hover); border-left: 3px solid var(--primary); }
.sub-id { font-weight: 700; }
.sub-score { font-weight: 700; color: var(--primary); }

.eval-header { display: flex; align-items: center; gap: var(--space-sm); margin-bottom: var(--space-md); }
.score-big { font-size: var(--fs-h2); font-weight: 700; color: var(--primary); }
.section { margin-bottom: var(--space-md); }
.case-row { display: flex; align-items: center; gap: var(--space-xs); padding: var(--space-xs) 0; border-bottom: 1px solid var(--border); font-size: var(--fs-body); }
.case-row.fail { color: var(--danger); }
.case-icon { font-weight: 700; }
.case-err { color: var(--danger); font-size: var(--fs-code); }

.diagnosis-card { border-left: 3px solid var(--primary); }
.diag-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: var(--space-sm); }
.diag-badge { font-size: var(--fs-caption); font-weight: 600; color: var(--primary); background: rgba(79,124,255,0.1); padding: 3px 10px; border-radius: var(--radius-sm); }
.diag-conf { font-weight: 700; color: var(--text-secondary); }
.diag-row { margin-bottom: var(--space-sm); }
.diag-label { display: block; font-size: var(--fs-caption); color: var(--text-secondary); margin-bottom: 4px; }
.diag-value { font-size: var(--fs-body); font-weight: 600; }
.diag-value.primary { color: var(--primary); font-size: var(--fs-h3); }
.diag-text { margin: 0; font-size: var(--fs-body); line-height: 1.6; }
</style>
