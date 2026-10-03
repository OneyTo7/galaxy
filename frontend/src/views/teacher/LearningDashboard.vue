<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { PieChart, BarChart, RadarChart } from 'echarts/charts'
import { TooltipComponent, LegendComponent, GridComponent } from 'echarts/components'
import VChart from 'vue-echarts'
import { ElMessage } from 'element-plus'
import { getAssignmentReport } from '@/api/report'
import { listAssignments } from '@/api/assignment'
import type { LearningReport, AssignmentOut } from '@/types/api'

use([CanvasRenderer, PieChart, BarChart, RadarChart, TooltipComponent, LegendComponent, GridComponent])

const assignments = ref<AssignmentOut[]>([])
const selectedId = ref<number | null>(null)
const report = ref<LearningReport | null>(null)
const loading = ref(false)

async function loadAssignments() {
  try { assignments.value = await listAssignments() } catch (e) { console.error('加载作业失败', e) }
}

async function loadReport() {
  if (!selectedId.value) return
  loading.value = true
  report.value = null
  try { report.value = await getAssignmentReport(selectedId.value) }
  catch (e: any) { ElMessage.error(e.response?.data?.detail || '加载学情报告失败') }
  finally { loading.value = false }
}

watch(selectedId, loadReport)
onMounted(loadAssignments)

const colors = ['#4F7CFF', '#60A5FA', '#34D399', '#FFB020', '#F87171', '#A78BFA']

const pieOption = computed(() => ({
  tooltip: { trigger: 'item', backgroundColor: '#FFFFFF', borderColor: '#E5E9F2', textStyle: { color: '#1F2937' } },
  legend: { bottom: 0, textStyle: { color: '#6B7280', fontSize: 12 } },
  series: [{ type: 'pie', radius: ['40%', '70%'], data: report.value?.misconception_stats?.map((s) => ({ name: s.misconception_type, value: s.count })) || [], color: colors, itemStyle: { borderColor: '#FFFFFF', borderWidth: 2 }, label: { color: '#6B7280', fontSize: 12 } }],
}))

const barOption = computed(() => ({
  tooltip: { trigger: 'axis', backgroundColor: '#FFFFFF', borderColor: '#E5E9F2', textStyle: { color: '#1F2937' }, axisPointer: { type: 'shadow', shadowStyle: { color: 'rgba(79,124,255,0.04)' } } },
  xAxis: { type: 'category', data: report.value?.knowledge_stats?.map((s) => s.knowledge_point) || [], axisLabel: { rotate: 30, color: '#6B7280', fontSize: 12 }, axisLine: { lineStyle: { color: '#E5E9F2' } } },
  yAxis: { type: 'value', axisLabel: { color: '#6B7280', fontSize: 12 }, splitLine: { lineStyle: { color: '#E5E9F2' } } },
  grid: { left: '3%', right: '5%', bottom: '12%', top: '5%', containLabel: true },
  series: [{ type: 'bar', data: report.value?.knowledge_stats?.map((s) => s.count) || [], itemStyle: { borderRadius: [4, 4, 0, 0], color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: '#4F7CFF' }, { offset: 1, color: '#60A5FA' }] } }, barWidth: '45%' }],
}))

const radarOption = computed(() => ({
  tooltip: { backgroundColor: '#FFFFFF', borderColor: '#E5E9F2', textStyle: { color: '#1F2937' } },
  radar: { indicator: (report.value?.misconception_stats?.map(s => ({ name: s.misconception_type, max: s.count + 2 })) || []).slice(0, 6), axisName: { color: '#6B7280', fontSize: 12 }, splitLine: { lineStyle: { color: '#E5E9F2' } }, splitArea: { areaStyle: { color: ['rgba(247,249,255,0.5)', 'rgba(255,255,255,0.5)'] } }, axisLine: { lineStyle: { color: '#E5E9F2' } } },
  series: [{ type: 'radar', data: [{ value: report.value?.misconception_stats?.map(s => s.count) || [], itemStyle: { color: '#4F7CFF' }, areaStyle: { color: 'rgba(79,124,255,0.12)' }, lineStyle: { color: '#4F7CFF', width: 2 } }] }],
}))
</script>

<template>
  <div class="page">
    <div class="page-header">
      <div>
        <h1>学情看板</h1>
        <p class="page-desc">选择作业，查看学生提交情况、误区分布与知识点薄弱。</p>
      </div>
      <el-select v-model="selectedId" placeholder="选择作业" style="width: 300px" :loading="loading">
        <el-option v-for="a in assignments" :key="a.id" :label="a.title" :value="a.id" />
      </el-select>
    </div>

    <div v-if="!selectedId && assignments.length === 0" class="empty-state">
      <p class="empty-text">暂无作业，先去 AI 命题生成一道吧。</p>
    </div>
    <div v-else-if="selectedId && !loading && !report" class="empty-state">
      <p class="empty-text">暂无提交数据。</p>
    </div>

    <template v-if="report">
      <div class="stat-row">
        <div class="stat-card">
          <span class="stat-num">{{ report.submission_count }}</span>
          <span class="stat-label">提交数</span>
        </div>
        <div class="stat-card">
          <span class="stat-num">{{ report.avg_score }}</span>
          <span class="stat-label">平均分</span>
        </div>
        <div class="stat-card">
          <span class="stat-num">{{ report.misconception_stats?.length || 0 }}</span>
          <span class="stat-label">误区类型</span>
        </div>
      </div>

      <div class="chart-row">
        <div class="chart-card">
          <h3>误区分布</h3>
          <v-chart class="chart" :option="pieOption" autoresize />
        </div>
        <div class="chart-card">
          <h3>知识点薄弱</h3>
          <v-chart class="chart" :option="barOption" autoresize />
        </div>
      </div>

      <div class="chart-row">
        <div class="chart-card chart-wide">
          <h3>误区雷达</h3>
          <v-chart class="chart" :option="radarOption" autoresize />
        </div>
      </div>

      <div v-if="report.students?.length" class="section">
        <h3>学生列表</h3>
        <el-table :data="report.students" border size="small">
          <el-table-column prop="user_id" label="学生 ID" width="100" />
          <el-table-column label="得分" width="80">
            <template #default="{ row }">
              <span :class="{ high: row.score >= 80, low: row.score < 60 }" class="score-cell">{{ row.score }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="misconception_type" label="误区" />
        </el-table>
      </div>
    </template>
  </div>
</template>

<style scoped>
.page { max-width: 100%; }
.page-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: var(--space-lg); }
.page-desc { margin: 0; font-size: var(--fs-body); color: var(--text-secondary); }
.empty-state { text-align: center; padding: var(--space-xl) 0; color: var(--text-secondary); }

.stat-row { display: flex; gap: var(--space-md); margin-bottom: var(--space-lg); }
.stat-card { flex: 1; background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius-lg); padding: var(--space-md); box-shadow: var(--shadow-card); }
.stat-num { font-size: var(--fs-data); font-weight: 700; color: var(--text-primary); display: block; }
.stat-label { font-size: var(--fs-caption); color: var(--text-secondary); margin-top: 4px; display: block; }

.chart-row { display: grid; grid-template-columns: 1fr 1fr; gap: var(--space-md); margin-bottom: var(--space-md); }
.chart-card { background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius-lg); padding: var(--space-md); box-shadow: var(--shadow-card); }
.chart-wide { grid-column: span 2; }
.chart-card h3 { margin: 0 0 var(--space-sm); font-size: var(--fs-h3); }
.chart { height: 280px; }

.section { margin-top: var(--space-md); }
.section h3 { font-size: var(--fs-h3); margin: 0 0 var(--space-sm); }
.score-cell { font-weight: 700; }
.score-cell.high { color: var(--success); }
.score-cell.low { color: var(--danger); }

@media (max-width: 768px) {
  .chart-row { grid-template-columns: 1fr; }
  .chart-wide { grid-column: span 1; }
  .stat-row { flex-direction: column; }
}
</style>
