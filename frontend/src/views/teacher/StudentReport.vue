<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { listMySubmissions } from '@/api/submission'
import { getEvaluation } from '@/api/submission'
import { diagnose, getDiagnosis } from '@/api/diagnose'
import { getStudentMastery, getStudentMasteryEvents } from '@/api/mastery'
import { ElMessage } from 'element-plus'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart, PieChart, RadarChart } from 'echarts/charts'
import { TooltipComponent, GridComponent, LegendComponent } from 'echarts/components'
import VChart from 'vue-echarts'
import type { SubmissionOut, EvaluationOut, MisconceptionOut, MasteryCellOut, MasteryEventOut } from '@/types/api'

use([CanvasRenderer, LineChart, PieChart, RadarChart, TooltipComponent, GridComponent, LegendComponent])

const route = useRoute()
const router = useRouter()
const submissions = ref<SubmissionOut[]>([])
const loading = ref(false)
const selectedSub = ref<SubmissionOut | null>(null)
const evaluation = ref<EvaluationOut | null>(null)
const diagnosisList = ref<MisconceptionOut[]>([])
const masteryPoints = ref<MasteryCellOut[]>([])
const masteryEvents = ref<MasteryEventOut[]>([])
const detailLoading = ref(false)

// 学生 ID 从 query 取
const studentId = Number(route.query.student) || 0
const courseId = Number(route.query.course) || 1

async function load() {
  loading.value = true
  try {
    const all = await listMySubmissions()
    submissions.value = all.filter((s: SubmissionOut) => s.user_id === studentId || !studentId)
    if (submissions.value.length > 0) viewSub(submissions.value[0])
    // D2: 加载掌握度雷达 + 成长曲线
    try {
      const m = await getStudentMastery(courseId, studentId)
      masteryPoints.value = m.points
      masteryEvents.value = await getStudentMasteryEvents(courseId, studentId)
    } catch (e) { console.error('掌握度加载失败', e) }
  } catch (e) { console.error('加载失败', e) }
  finally { loading.value = false }
}

async function viewSub(sub: SubmissionOut) {
  selectedSub.value = sub
  evaluation.value = null
  diagnosisList.value = []
  detailLoading.value = true
  try {
    evaluation.value = await getEvaluation(sub.id)
    try { diagnosisList.value = await getDiagnosis(sub.id) } catch {}
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

// D2: 掌握度雷达图
const masteryRadar = computed(() => {
  const pts = masteryPoints.value.filter(p => p.mastery !== null)
  return {
    tooltip: { backgroundColor: '#FFFFFF', borderColor: '#E5E9F2', textStyle: { color: '#1F2937' } },
    radar: {
      indicator: pts.map(p => ({ name: p.name, max: 1.0 })),
      axisName: { color: '#6B7280', fontSize: 11 },
      splitLine: { lineStyle: { color: '#E5E9F2' } },
      splitArea: { areaStyle: { color: ['rgba(247,249,255,0.5)', 'rgba(255,255,255,0.5)'] } },
      axisLine: { lineStyle: { color: '#E5E9F2' } },
    },
    series: [{ type: 'radar', data: [{ value: pts.map(p => p.mastery), itemStyle: { color: '#4F7CFF' }, areaStyle: { color: 'rgba(79,124,255,0.12)' }, lineStyle: { color: '#4F7CFF', width: 2 } }] }],
  }
})

// D2: 掌握度成长曲线（按知识点筛选的事件流）
const growthChart = computed(() => {
  const events = masteryEvents.value
  const kps = [...new Set(events.map(e => e.code))]
  const series = kps.map((kp, idx) => ({
    name: kp,
    type: 'line',
    data: events.filter(e => e.code === kp).map(e => e.mastery_after),
    smooth: true,
    itemStyle: { color: ['#4F7CFF', '#34D399', '#FFB020', '#F87171', '#A78BFA'][idx % 5] },
  }))
  return {
    tooltip: { trigger: 'axis', backgroundColor: '#FFFFFF', borderColor: '#E5E9F2', textStyle: { color: '#1F2937' } },
    legend: { bottom: 0, textStyle: { color: '#6B7280', fontSize: 11 } },
    xAxis: { type: 'category', data: events.map((_, i) => `事件${i + 1}`), axisLabel: { color: '#6B7280' }, axisLine: { lineStyle: { color: '#E5E9F2' } } },
    yAxis: { type: 'value', min: 0, max: 1, axisLabel: { color: '#6B7280', formatter: (v: number) => `${(v * 100).toFixed(0)}%` }, splitLine: { lineStyle: { color: '#E5E9F2' } } },
    grid: { left: '3%', right: '5%', bottom: '15%', containLabel: true },
    series,
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
      <div class="page-title-with-chip">
        <span class="page-title-chip"><el-icon><Document /></el-icon></span>
        <div>
          <h1>学生个人报告</h1>
          <p class="page-desc">成绩走势、误区诊断历史与知识点掌握度成长。</p>
        </div>
      </div>
      <el-button @click="router.back()"><el-icon style="margin-right:4px"><Back /></el-icon>返回</el-button>
    </div>

    <div v-if="submissions.length === 0 && !loading" class="empty-state-v2">
      <div class="empty-ico"><el-icon><Document /></el-icon></div>
      <p>暂无提交记录</p>
    </div>

    <template v-else>
      <div class="stat-row">
        <div class="stat-card-v2 rise-in" style="--enter-idx:0">
          <div class="stat-ico blue"><el-icon><Document /></el-icon></div>
          <div>
            <span class="stat-num-v2">{{ submissions.length }}</span>
            <span class="stat-label-v2">提交总数</span>
          </div>
        </div>
        <div class="stat-card-v2 rise-in" style="--enter-idx:1">
          <div class="stat-ico green"><el-icon><CircleCheck /></el-icon></div>
          <div>
            <span class="stat-num-v2">{{ submissions.filter(s => s.status === 'done').length }}</span>
            <span class="stat-label-v2">已完成</span>
          </div>
        </div>
        <div class="stat-card-v2 rise-in" style="--enter-idx:2">
          <div class="stat-ico amber"><el-icon><Trophy /></el-icon></div>
          <div>
            <span class="stat-num-v2">{{ avgScore }}</span>
            <span class="stat-label-v2">平均分</span>
          </div>
        </div>
      </div>

      <div class="split-layout">
        <aside class="sidebar">
          <div class="panel">
            <div class="section-title"><span class="title-ico"><el-icon><Clock /></el-icon></span>提交历史</div>
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
          <div class="panel rise-in">
            <div class="section-title"><span class="title-ico"><el-icon><TrendCharts /></el-icon></span>成绩走势</div>
            <v-chart class="chart" :option="scoreTrend" autoresize />
          </div>

          <div v-if="masteryPoints.length" class="panel rise-in">
            <div class="section-title"><span class="title-ico"><el-icon><Aim /></el-icon></span>知识点掌握度雷达</div>
            <v-chart class="chart" :option="masteryRadar" autoresize />
          </div>

          <div v-if="masteryEvents.length" class="panel rise-in">
            <div class="section-title"><span class="title-ico"><el-icon><DataLine /></el-icon></span>掌握度成长曲线</div>
            <v-chart class="chart" :option="growthChart" autoresize />
          </div>

          <div v-if="selectedSub" v-loading="detailLoading">
            <div class="panel">
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

            <div v-if="diagnosisList.length" class="panel diagnosis-card rise-in">
              <div class="section-title"><span class="title-ico"><el-icon><Aim /></el-icon></span>AI 误区诊断</div>
              <div v-for="(diag, idx) in diagnosisList" :key="diag.id" class="diag-block" :class="{ overcome: diag.status === 'overcome' }">
                <div class="diag-head">
                  <span class="diag-badge">#{{ idx + 1 }}</span>
                  <span class="diag-conf">{{ (diag.confidence * 100).toFixed(0) }}%</span>
                  <el-tag v-if="diag.status === 'overcome'" type="success" size="small">已克服</el-tag>
                  <el-tag v-else type="warning" size="small">未克服</el-tag>
                  <el-tag v-if="!diag.evidence_validated" type="danger" size="small">低置信</el-tag>
                </div>
                <div class="diag-row">
                  <span class="diag-label">误区类型</span>
                  <span class="diag-value primary">{{ diag.misconception_type }}</span>
                </div>
                <div class="diag-row">
                  <span class="diag-label">证据</span>
                  <p class="diag-text">{{ diag.evidence }}</p>
                </div>
                <div class="diag-row">
                  <span class="diag-label">知识点</span>
                  <el-tag size="small">{{ diag.knowledge_point }}</el-tag>
                </div>
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

.stat-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 14px; margin-bottom: 18px; }

.split-layout { display: grid; grid-template-columns: 260px 1fr; gap: 22px; align-items: start; }

.sidebar { position: sticky; top: 28px; }
.chart { height: 240px; }

.sub-list { display: flex; flex-direction: column; gap: 6px; }
.sub-item { display: flex; align-items: center; gap: 8px; padding: 9px 12px; border-radius: var(--radius-md); cursor: pointer; transition: all var(--duration) var(--ease); }
.sub-item:hover { background: var(--bg-hover); }
.sub-item.active { background: var(--bg-hover); border-left: 3px solid var(--primary); }
.sub-id { font-weight: 700; color: var(--ink); font-size: 13px; }
.sub-score { font-weight: 700; color: var(--primary); margin-left: auto; }

.eval-header { display: flex; align-items: center; gap: 10px; margin-bottom: 14px; }
.eval-header h3 { margin: 0; }
.score-big { font-size: 20px; font-weight: 700; color: var(--primary); margin-left: auto; }
.section { margin-bottom: 14px; }
.section h4 { font-size: 13px; font-weight: 600; color: var(--ink-2); margin: 0 0 8px; }
.case-row { display: flex; align-items: center; gap: 8px; padding: 8px 0; border-bottom: 1px solid var(--border); font-size: 13px; }
.case-row.fail { color: var(--danger); }
.case-icon { font-weight: 700; }
.case-err { color: var(--danger); font-size: 12px; font-family: 'SF Mono', monospace; }

.diagnosis-card { border-left: 3px solid var(--primary); }
.diag-block { padding-bottom: 14px; margin-bottom: 14px; border-bottom: 1px solid var(--border); }
.diag-block:last-child { border-bottom: none; margin-bottom: 0; padding-bottom: 0; }
.diag-block.overcome { opacity: 0.68; }
.diag-head { display: flex; align-items: center; gap: 8px; margin-bottom: 10px; }
.diag-badge { font-size: 11px; font-weight: 600; color: var(--primary); background: rgba(79,124,255,0.10); padding: 2px 8px; border-radius: 4px; }
.diag-conf { font-weight: 700; color: var(--text-secondary); font-size: 13px; margin-left: auto; }
.diag-row { margin-bottom: 10px; }
.diag-label { display: block; font-size: 11px; color: var(--text-secondary); margin-bottom: 4px; letter-spacing: 0.04em; }
.diag-value { font-size: 13px; font-weight: 600; color: var(--ink); }
.diag-value.primary { color: var(--primary); font-size: 15px; }
.diag-text { margin: 0; font-size: 13px; line-height: 1.65; color: var(--ink-2); font-family: 'SF Mono', monospace; background: var(--bg-sunken); padding: 8px 10px; border-radius: 6px; }

@media (max-width: 900px) {
  .split-layout { grid-template-columns: 1fr; }
  .sidebar { position: static; }
  .stat-row { grid-template-columns: 1fr; }
}
</style>
