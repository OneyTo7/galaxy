<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { PieChart, BarChart } from 'echarts/charts'
import { TooltipComponent, LegendComponent, GridComponent } from 'echarts/components'
import VChart from 'vue-echarts'
import { ElMessage } from 'element-plus'
import { getAssignmentReport } from '@/api/report'
import { listAssignments } from '@/api/assignment'
import type { LearningReport, AssignmentOut } from '@/types/api'

use([CanvasRenderer, PieChart, BarChart, TooltipComponent, LegendComponent, GridComponent])

const assignments = ref<AssignmentOut[]>([])
const selectedId = ref<number | null>(null)
const report = ref<LearningReport | null>(null)
const loading = ref(false)

async function loadAssignments() {
  try {
    assignments.value = await listAssignments()
    if (assignments.value.length > 0) {
      selectedId.value = assignments.value[0].id
    }
  } catch (e) {
    console.error('加载作业列表失败', e)
  }
}

async function loadReport() {
  if (!selectedId.value) return
  loading.value = true
  report.value = null
  try {
    report.value = await getAssignmentReport(selectedId.value)
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '加载学情报告失败')
  } finally {
    loading.value = false
  }
}

watch(selectedId, loadReport)
onMounted(loadAssignments)

const pieOption = computed(() => ({
  tooltip: { trigger: 'item', backgroundColor: '#1A2632', borderColor: '#2A3641', textStyle: { color: '#E2E8F0' } },
  legend: { bottom: 0, textStyle: { color: '#94A3B8', fontSize: 12 } },
  series: [{
    type: 'pie',
    radius: ['45%', '72%'],
    data: report.value?.misconception_stats?.map((s) => ({ name: s.misconception_type, value: s.count })) || [],
    color: ['#5B7FFF', '#39D0D8', '#A371F7', '#3FB950', '#E8A345', '#F85149'],
    itemStyle: { borderColor: '#0F1923', borderWidth: 2, borderRadius: 4 },
    label: { color: '#94A3B8', fontSize: 12 },
    emphasis: { itemStyle: { shadowBlur: 20, shadowColor: 'rgba(91, 127, 255, 0.3)' } },
  }],
}))

const barOption = computed(() => ({
  tooltip: { trigger: 'axis', backgroundColor: '#1A2632', borderColor: '#2A3641', textStyle: { color: '#E2E8F0' }, axisPointer: { type: 'shadow', shadowStyle: { color: 'rgba(91, 127, 255, 0.05)' } } },
  xAxis: { type: 'category', data: report.value?.knowledge_stats?.map((s) => s.knowledge_point) || [], axisLabel: { rotate: 30, color: '#94A3B8', fontSize: 12 }, axisLine: { lineStyle: { color: '#2A3641' } } },
  yAxis: { type: 'value', axisLabel: { color: '#94A3B8', fontSize: 12 }, splitLine: { lineStyle: { color: 'rgba(42, 54, 65, 0.4)' } } },
  grid: { left: '3%', right: '5%', bottom: '12%', top: '5%', containLabel: true },
  series: [{
    type: 'bar',
    data: report.value?.knowledge_stats?.map((s) => s.count) || [],
    itemStyle: {
      borderRadius: [4, 4, 0, 0],
      color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: '#5B7FFF' }, { offset: 1, color: '#39D0D8' }] },
    },
    barWidth: '45%',
    emphasis: { itemStyle: { shadowBlur: 15, shadowColor: 'rgba(91, 127, 255, 0.4)' } },
  }],
}))

const radarOption = computed(() => ({
  tooltip: { backgroundColor: '#1A2632', borderColor: '#2A3641', textStyle: { color: '#E2E8F0' } },
  radar: {
    indicator: (report.value?.misconception_stats?.map(s => ({ name: s.misconception_type, max: s.count + 2 })) || []).slice(0, 6),
    axisName: { color: '#94A3B8', fontSize: 12 },
    splitLine: { lineStyle: { color: 'rgba(42, 54, 65, 0.5)' } },
    splitArea: { areaStyle: { color: ['rgba(15, 25, 35, 0.3)', 'rgba(22, 32, 40, 0.3)'] } },
    axisLine: { lineStyle: { color: 'rgba(42, 54, 65, 0.6)' } },
  },
  series: [{
    type: 'radar',
    data: [{
      value: report.value?.misconception_stats?.map(s => s.count) || [],
      itemStyle: { color: '#5B7FFF' },
      areaStyle: { color: 'rgba(91, 127, 255, 0.15)' },
      lineStyle: { color: '#5B7FFF', width: 2 },
    }],
  }],
}))
</script>

<template>
  <div class="dashboard-page">
    <h1>学情看板</h1>
    <p class="desc">选择作业，查看学生提交情况、误区分布与知识点薄弱。</p>
    <div class="filter-bar">
      <el-select v-model="selectedId" placeholder="选择作业" style="width: 400px" :loading="loading" @change="loadReport">
        <el-option v-for="a in assignments" :key="a.id" :label="a.title" :value="a.id" />
      </el-select>
      <el-button :loading="loading" @click="loadReport">刷新</el-button>
    </div>

    <div v-if="!selectedId && assignments.length === 0" class="empty">
      <p>暂无作业，先去 AI 命题生成一道吧。</p>
    </div>

    <div v-if="selectedId && !loading && !report" class="empty">
      <p>暂无提交数据。</p>
    </div>

    <div v-if="report" class="report-content">
      <div class="stats-row">
        <div class="stat-card"><div class="stat-label">提交数</div><div class="stat-value">{{ report.submission_count }}</div></div>
        <div class="stat-card"><div class="stat-label">平均分</div><div class="stat-value">{{ report.avg_score }}</div></div>
      </div>
      <div class="charts-row">
        <div class="chart-card">
          <h3>误区分布</h3>
          <v-chart class="chart" :option="pieOption" autoresize />
        </div>
        <div class="chart-card">
          <h3>知识点薄弱</h3>
          <v-chart class="chart" :option="barOption" autoresize />
        </div>
      </div>
      <div class="charts-row">
        <div class="chart-card chart-wide">
          <h3>误区雷达</h3>
          <v-chart class="chart" :option="radarOption" autoresize />
        </div>
      </div>
      <div v-if="report.students?.length" class="students">
        <h3>学生列表</h3>
        <el-table :data="report.students" border>
          <el-table-column prop="user_id" label="学生 ID" width="100" />
          <el-table-column prop="score" label="得分" width="80" />
          <el-table-column prop="misconception_type" label="误区" />
        </el-table>
      </div>
    </div>
  </div>
</template>

<style scoped>
.dashboard-page { max-width: 1200px; }
.desc { color: var(--galaxy-text-secondary); margin-bottom: 24px; }
.filter-bar { display: flex; align-items: center; gap: 12px; margin-bottom: 24px; }
.empty { text-align: center; padding: 60px 0; color: var(--galaxy-text-secondary); }
.stats-row { display: flex; gap: 16px; margin-bottom: 24px; }
.stat-card { background: var(--galaxy-card); border: 1px solid var(--galaxy-border); border-radius: 8px; padding: 20px; flex: 1; }
.stat-label { font-size: 13px; color: var(--galaxy-text-secondary); margin-bottom: 8px; }
.stat-value { font-family: 'Space Grotesk'; font-size: 28px; font-weight: 700; }
.charts-row { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 24px; }
.chart-card { background: var(--galaxy-card); border: 1px solid var(--galaxy-border); border-radius: var(--radius-md); padding: 20px; }
.chart-card h3 { margin: 0 0 16px; font-size: 16px; }
.chart-wide { grid-column: span 2; }
.chart { height: 300px; }
.students h3 { margin: 0 0 12px; font-size: 16px; }
</style>
