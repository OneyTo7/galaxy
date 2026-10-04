<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { PieChart as EPieChart, BarChart as EBarChart, RadarChart as ERadarChart, HeatmapChart as EHeatmapChart } from 'echarts/charts'
import { TooltipComponent, LegendComponent, GridComponent as EGridComponent, VisualMapComponent } from 'echarts/components'
import VChart from 'vue-echarts'
import { ElMessage } from 'element-plus'
import { getAssignmentReport } from '@/api/report'
import { listAssignments } from '@/api/assignment'
import { getMasteryMatrix } from '@/api/mastery'
import { listCourses } from '@/api/organization'
import type { LearningReport, AssignmentOut, MasteryMatrixOut } from '@/types/api'

use([CanvasRenderer, EPieChart, EBarChart, ERadarChart, EHeatmapChart, TooltipComponent, LegendComponent, EGridComponent, VisualMapComponent])

const assignments = ref<AssignmentOut[]>([])
const selectedId = ref<number | null>(null)
const report = ref<LearningReport | null>(null)
const loading = ref(false)
const courses = ref<{ id: number; name: string }[]>([])
const selectedCourseId = ref<number | null>(null)
const matrix = ref<MasteryMatrixOut | null>(null)
const matrixLoading = ref(false)

async function loadAssignments() {
  try { assignments.value = await listAssignments() } catch (e) { console.error('加载作业失败', e) }
}

async function loadCourses() {
  try { courses.value = await listCourses() } catch { /* 学生角色无课程列表 */ }
}

async function loadReport() {
  if (!selectedId.value) return
  loading.value = true
  report.value = null
  try { report.value = await getAssignmentReport(selectedId.value) }
  catch (e: any) { ElMessage.error(e.response?.data?.detail || '加载学情报告失败') }
  finally { loading.value = false }
}

async function loadMatrix() {
  if (!selectedCourseId.value) return
  matrixLoading.value = true
  matrix.value = null
  try { matrix.value = await getMasteryMatrix(selectedCourseId.value) }
  catch (e: any) { console.error('掌握度矩阵加载失败', e) }
  finally { matrixLoading.value = false }
}

watch(selectedId, loadReport)
watch(selectedCourseId, loadMatrix)
onMounted(() => { loadAssignments(); loadCourses() })

const colors = ['#4F7CFF', '#60A5FA', '#34D399', '#FFB020', '#F87171', '#A78BFA']

const pieOption = computed((): any => ({
  tooltip: { trigger: 'item', backgroundColor: '#FFFFFF', borderColor: '#E5E9F2', textStyle: { color: '#1F2937' } },
  legend: { bottom: 0, textStyle: { color: '#6B7280', fontSize: 12 } },
  series: [{ type: 'pie', radius: ['40%', '70%'], data: report.value?.misconception_stats?.map((s) => ({ name: s.misconception_type, value: s.count })) || [], color: colors, itemStyle: { borderColor: '#FFFFFF', borderWidth: 2 }, label: { color: '#6B7280', fontSize: 12 } }],
}))

const barOption = computed((): any => ({
  tooltip: { trigger: 'axis', backgroundColor: '#FFFFFF', borderColor: '#E5E9F2', textStyle: { color: '#1F2937' }, axisPointer: { type: 'shadow', shadowStyle: { color: 'rgba(79,124,255,0.04)' } } },
  xAxis: { type: 'category', data: report.value?.knowledge_stats?.map((s) => s.knowledge_point) || [], axisLabel: { rotate: 30, color: '#6B7280', fontSize: 12 }, axisLine: { lineStyle: { color: '#E5E9F2' } } },
  yAxis: { type: 'value', axisLabel: { color: '#6B7280', fontSize: 12 }, splitLine: { lineStyle: { color: '#E5E9F2' } } },
  grid: { left: '3%', right: '5%', bottom: '12%', top: '5%', containLabel: true },
  series: [{ type: 'bar', data: report.value?.knowledge_stats?.map((s) => s.count) || [], itemStyle: { borderRadius: [4, 4, 0, 0], color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: '#4F7CFF' }, { offset: 1, color: '#60A5FA' }] } }, barWidth: '45%' }],
}))

const radarOption = computed((): any => ({
  tooltip: { backgroundColor: '#FFFFFF', borderColor: '#E5E9F2', textStyle: { color: '#1F2937' } },
  radar: { indicator: (report.value?.misconception_stats?.map(s => ({ name: s.misconception_type, max: s.count + 2 })) || []).slice(0, 6), axisName: { color: '#6B7280', fontSize: 12 }, splitLine: { lineStyle: { color: '#E5E9F2' } }, splitArea: { areaStyle: { color: ['rgba(247,249,255,0.5)', 'rgba(255,255,255,0.5)'] } }, axisLine: { lineStyle: { color: '#E5E9F2' } } },
  series: [{ type: 'radar', data: [{ value: report.value?.misconception_stats?.map(s => s.count) || [], itemStyle: { color: '#4F7CFF' }, areaStyle: { color: 'rgba(79,124,255,0.12)' }, lineStyle: { color: '#4F7CFF', width: 2 } }] }],
}))

// D2: 掌握度热力图（学生 × 知识点）
const heatOption = computed((): any => {
  const m = matrix.value
  if (!m || !m.cells.length) return {}
  const kps: string[] = []
  for (const c of m.cells) { if (!kps.includes(c.code)) kps.push(c.code) }
  const students = m.students.map(s => s.display_name || `用户${s.user_id}`)
  const data: [number, number, number][] = []
  m.cells.forEach(c => {
    const x = kps.indexOf(c.code)
    const y = m.students.findIndex(s => s.user_id === c.user_id)
    if (y >= 0 && c.mastery !== null) data.push([x, y, Math.round(c.mastery * 100)])
  })
  return {
    tooltip: { position: 'top', backgroundColor: '#FFFFFF', borderColor: '#E5E9F2', textStyle: { color: '#1F2937' }, formatter: (p: any) => `${students[p.value[1]]} / ${kps[p.value[0]]}<br/>掌握度: ${p.value[2]}%` },
    grid: { left: '3%', right: '4%', bottom: '15%', top: '5%', containLabel: true },
    xAxis: { type: 'category', data: kps, splitArea: { show: true }, axisLabel: { rotate: 30, color: '#6B7280', fontSize: 11 } },
    yAxis: { type: 'category', data: students, splitArea: { show: true }, axisLabel: { color: '#6B7280', fontSize: 11 } },
    visualMap: { min: 0, max: 100, calculable: true, orient: 'horizontal', left: 'center', bottom: '2%', inRange: { color: ['#F87171', '#FFB020', '#60A5FA', '#34D399'] }, textStyle: { color: '#6B7280' } },
    series: [{ type: 'heatmap', data, label: { show: true, color: '#1F2937', fontSize: 10 }, emphasis: { itemStyle: { shadowBlur: 10, shadowColor: 'rgba(0,0,0,0.3)' } } }],
  }
})
</script>

<template>
  <div class="page">
    <div class="page-header">
      <div class="page-title-with-chip">
        <span class="page-title-chip"><el-icon><DataAnalysis /></el-icon></span>
        <div>
          <h1>学情看板</h1>
          <p class="page-desc">选择作业，查看提交情况、误区分布与知识点掌握度。</p>
        </div>
      </div>
      <el-select v-model="selectedId" placeholder="选择作业" style="width: 280px" :loading="loading">
        <el-option v-for="a in assignments" :key="a.id" :label="a.title" :value="a.id" />
      </el-select>
    </div>

    <div v-if="!selectedId && assignments.length === 0" class="empty-state-v2">
      <div class="empty-ico"><el-icon><Document /></el-icon></div>
      <p>暂无作业，先去 AI 命题生成一道吧。</p>
    </div>
    <div v-else-if="selectedId && !loading && !report" class="empty-state-v2">
      <div class="empty-ico"><el-icon><DataLine /></el-icon></div>
      <p>暂无提交数据。</p>
    </div>

    <template v-if="report">
      <div class="stat-row">
        <div class="stat-card-v2 rise-in" style="--enter-idx:0">
          <div class="stat-ico blue"><el-icon><Document /></el-icon></div>
          <div>
            <span class="stat-num-v2">{{ report.submission_count }}</span>
            <span class="stat-label-v2">提交数</span>
          </div>
        </div>
        <div class="stat-card-v2 rise-in" style="--enter-idx:1">
          <div class="stat-ico amber"><el-icon><Trophy /></el-icon></div>
          <div>
            <span class="stat-num-v2">{{ report.avg_score }}</span>
            <span class="stat-label-v2">平均分</span>
          </div>
        </div>
        <div class="stat-card-v2 rise-in" style="--enter-idx:2">
          <div class="stat-ico red"><el-icon><Aim /></el-icon></div>
          <div>
            <span class="stat-num-v2">{{ report.misconception_stats?.length || 0 }}</span>
            <span class="stat-label-v2">误区类型</span>
          </div>
        </div>
      </div>

      <div class="chart-row">
        <div class="panel chart-card rise-in" style="--enter-idx:3">
          <div class="section-title"><span class="title-ico"><el-icon><PieChart /></el-icon></span>误区分布</div>
          <v-chart class="chart" :option="pieOption" autoresize />
        </div>
        <div class="panel chart-card rise-in" style="--enter-idx:4">
          <div class="section-title"><span class="title-ico"><el-icon><Histogram /></el-icon></span>知识点薄弱</div>
          <v-chart class="chart" :option="barOption" autoresize />
        </div>
      </div>

      <div class="chart-row">
        <div class="panel chart-card chart-wide rise-in" style="--enter-idx:5">
          <div class="section-title"><span class="title-ico"><el-icon><Aim /></el-icon></span>误区雷达</div>
          <v-chart class="chart" :option="radarOption" autoresize />
        </div>
      </div>

      <!-- D2: 掌握度热力图（学生 × 知识点）-->
      <div class="chart-row">
        <div class="panel chart-card chart-wide rise-in" style="--enter-idx:6">
          <div class="heatmap-header">
            <div class="section-title" style="margin: 0">
              <span class="title-ico"><el-icon><Grid /></el-icon></span>知识点掌握度热力图
            </div>
            <el-select v-model="selectedCourseId" placeholder="选择课程" size="small" style="width: 200px" :loading="matrixLoading">
              <el-option v-for="c in courses" :key="c.id" :label="c.name" :value="c.id" />
            </el-select>
          </div>
          <div v-if="matrix && matrix.cells.length">
            <v-chart class="chart chart-tall" :option="heatOption" autoresize />
          </div>
          <div v-else-if="selectedCourseId" class="empty-inline">该课程暂无掌握度数据</div>
          <div v-else class="empty-inline">选择课程查看班级知识点掌握度</div>
        </div>
      </div>

      <div v-if="report.mastery_summary?.length" class="panel section rise-in" style="--enter-idx:7">
        <div class="section-title"><span class="title-ico"><el-icon><TrendCharts /></el-icon></span>知识点掌握度摘要</div>
        <el-table :data="report.mastery_summary" border size="small">
          <el-table-column prop="code" label="编码" width="140" />
          <el-table-column prop="name" label="知识点" />
          <el-table-column prop="category" label="分类" width="100" />
          <el-table-column label="班均掌握度" width="120">
            <template #default="{ row }">
              <span :class="{ mastered: row.avg_mastery >= 0.85, atrisk: row.avg_mastery < 0.3 }">{{ (row.avg_mastery * 100).toFixed(0) }}%</span>
            </template>
          </el-table-column>
          <el-table-column prop="student_count" label="覆盖学生" width="90" />
          <el-table-column label="风险人数" width="90">
            <template #default="{ row }">
              <span :class="{ atrisk: row.at_risk_count > 0 }">{{ row.at_risk_count }}</span>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <div v-if="report.students?.length" class="panel section rise-in" style="--enter-idx:8">
        <div class="section-title"><span class="title-ico"><el-icon><User /></el-icon></span>学生列表</div>
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

.stat-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 14px; margin-bottom: 18px; }

.chart-row { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 16px; }
.chart-card { padding: 18px 20px; }
.chart-wide { grid-column: span 2; }
.chart { height: 280px; }
.chart-tall { height: 360px; }
.heatmap-header { display: flex; justify-content: space-between; align-items: center; gap: 12px; margin-bottom: 14px; flex-wrap: wrap; }
.empty-inline { text-align: center; padding: var(--space-lg) 0; color: var(--text-secondary); font-size: 13px; }

.section { margin-top: 16px; }
.score-cell { font-weight: 700; }
.score-cell.high { color: var(--success); }
.score-cell.low { color: var(--danger); }
.mastered { color: var(--success); font-weight: 600; }
.atrisk { color: var(--danger); font-weight: 600; }

@media (max-width: 900px) {
  .chart-row { grid-template-columns: 1fr; }
  .chart-wide { grid-column: span 1; }
  .stat-row { grid-template-columns: 1fr; }
}
</style>
