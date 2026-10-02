<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { PieChart, BarChart } from 'echarts/charts'
import { TooltipComponent, LegendComponent, GridComponent } from 'echarts/components'
import VChart from 'vue-echarts'
import { ElMessage } from 'element-plus'
import { getAssignmentReport } from '@/api/report'
import type { LearningReport } from '@/types/api'

use([CanvasRenderer, PieChart, BarChart, TooltipComponent, LegendComponent, GridComponent])

const assignmentId = ref(2)
const report = ref<LearningReport | null>(null)
const loading = ref(false)

async function load() {
  loading.value = true
  try {
    report.value = await getAssignmentReport(assignmentId.value)
  } catch (e) {
    console.error('加载学情报告失败', e)
    ElMessage.error('加载学情报告失败')
  } finally {
    loading.value = false
  }
}

watch(assignmentId, load, { immediate: true })

const pieOption = computed(() => ({
  tooltip: { trigger: 'item' },
  legend: { bottom: 0 },
  series: [{
    type: 'pie',
    radius: ['40%', '70%'],
    data: report.value?.misconception_stats?.map((s) => ({ name: s.misconception_type, value: s.count })) || [],
    color: ['#5B7FFF', '#E8A345', '#3DAA52', '#E85D5D'],
  }],
}))

const barOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  xAxis: { type: 'category', data: report.value?.knowledge_stats?.map((s) => s.knowledge_point) || [], axisLabel: { rotate: 30 } },
  yAxis: { type: 'value' },
  series: [{
    type: 'bar',
    data: report.value?.knowledge_stats?.map((s) => s.count) || [],
    itemStyle: { color: '#5B7FFF', borderRadius: [4, 4, 0, 0] },
  }],
}))
</script>

<template>
  <div class="dashboard-page">
    <h1>学情看板</h1>
    <div class="filter-bar">
      <span>作业 ID</span>
      <el-input-number v-model="assignmentId" :min="1" />
      <el-button :loading="loading" @click="load">刷新</el-button>
    </div>
    <div v-if="report" class="stats-row">
      <div class="stat-card"><div class="stat-label">提交数</div><div class="stat-value">{{ report.submission_count }}</div></div>
      <div class="stat-card"><div class="stat-label">平均分</div><div class="stat-value">{{ report.avg_score }}</div></div>
    </div>
    <div v-if="report" class="charts-row">
      <div class="chart-card">
        <h3>误区分布</h3>
        <v-chart class="chart" :option="pieOption" autoresize />
      </div>
      <div class="chart-card">
        <h3>知识点薄弱</h3>
        <v-chart class="chart" :option="barOption" autoresize />
      </div>
    </div>
    <div v-if="report?.students?.length" class="students">
      <h3>学生列表</h3>
      <el-table :data="report.students" border>
        <el-table-column prop="user_id" label="学生 ID" width="100" />
        <el-table-column prop="score" label="得分" width="80" />
        <el-table-column prop="misconception_type" label="误区" />
      </el-table>
    </div>
  </div>
</template>

<style scoped>
.dashboard-page { max-width: 1200px; }
.filter-bar { display: flex; align-items: center; gap: 12px; margin-bottom: 24px; }
.stats-row { display: flex; gap: 16px; margin-bottom: 24px; }
.stat-card { background: var(--galaxy-card); border: 1px solid var(--galaxy-border); border-radius: 8px; padding: 20px; flex: 1; }
.stat-label { font-size: 13px; color: var(--galaxy-text-secondary); margin-bottom: 8px; }
.stat-value { font-family: 'Space Grotesk'; font-size: 28px; font-weight: 700; }
.charts-row { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 24px; }
.chart-card { background: var(--galaxy-card); border: 1px solid var(--galaxy-border); border-radius: 8px; padding: 20px; }
.chart-card h3 { margin: 0 0 16px; font-size: 16px; }
.chart { height: 300px; }
.students h3 { margin: 0 0 12px; font-size: 16px; }
</style>
