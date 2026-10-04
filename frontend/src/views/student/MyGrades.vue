<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { listMySubmissions } from '@/api/submission'
import { listMyCourses, listCourseAssignments } from '@/api/organization'
import { getMyMastery } from '@/api/mastery'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { RadarChart } from 'echarts/charts'
import { TooltipComponent } from 'echarts/components'
import VChart from 'vue-echarts'
import type { SubmissionOut, AssignmentOut, MasteryCellOut } from '@/types/api'

use([CanvasRenderer, RadarChart, TooltipComponent])

interface Course { id: number; name: string; code: string }

const router = useRouter()
const courses = ref<Course[]>([])
const selectedCourseId = ref<number | null>(null)
const submissions = ref<SubmissionOut[]>([])
const allAssignments = ref<AssignmentOut[]>([])
const masteryPoints = ref<MasteryCellOut[]>([])
const loading = ref(false)

async function loadCourses() {
  try {
    courses.value = await listMyCourses()
    if (courses.value.length > 0) {
      selectedCourseId.value = courses.value[0].id
      loadCourseData()
    }
  } catch (e) { console.error('加载课程失败', e) }
}

async function loadCourseData() {
  if (!selectedCourseId.value) return
  loading.value = true
  try {
    const [assigns, subs] = await Promise.all([
      listCourseAssignments(selectedCourseId.value),
      listMySubmissions(),
    ])
    allAssignments.value = assigns.filter((a: AssignmentOut) => a.status === 'published')
    submissions.value = subs as SubmissionOut[]
    // D2: 加载个人掌握度雷达
    try {
      const m = await getMyMastery(selectedCourseId.value)
      masteryPoints.value = m.points
    } catch (e) { console.error('掌握度加载失败', e) }
  } catch (e) { console.error('加载成绩失败', e) }
  finally { loading.value = false }
}

const gradeRows = computed(() => {
  return allAssignments.value.map(a => {
    const sub = submissions.value.find(s => s.assignment_id === a.id && s.status === 'done')
    return { id: a.id, title: a.title, lang: a.lang, score: sub?.score ?? null, status: sub ? '已提交' : '未提交' }
  })
})

const avgScore = computed(() => {
  const done = gradeRows.value.filter(r => r.score !== null)
  if (!done.length) return 0
  return Math.round(done.reduce((sum, r) => sum + (r.score || 0), 0) / done.length)
})

const completedCount = computed(() => gradeRows.value.filter(r => r.score !== null).length)

// D2: 个人掌握度雷达
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

// D2: 已克服误区徽章数
const overcomeCount = computed(() => masteryPoints.value.filter(p => p.status === 'mastered').length)

onMounted(loadCourses)
</script>

<template>
  <div class="page">
    <div class="page-header">
      <div>
        <h1>我的成绩</h1>
        <p class="page-desc">查看你选课程的作业成绩与完成情况。</p>
      </div>
      <el-select v-model="selectedCourseId" placeholder="选择课程" style="width: 240px" @change="loadCourseData">
        <el-option v-for="c in courses" :key="c.id" :label="c.name" :value="c.id" />
      </el-select>
    </div>

    <div v-if="!loading && courses.length === 0" class="empty-state">
      <p class="empty-text">暂未选课</p>
    </div>

    <template v-else-if="selectedCourseId">
      <div class="stat-row">
        <div class="stat-card">
          <span class="stat-num">{{ completedCount }}<span class="sub">/{{ gradeRows.length }}</span></span>
          <span class="stat-label">已完成</span>
        </div>
        <div class="stat-card">
          <span class="stat-num">{{ avgScore }}</span>
          <span class="stat-label">平均分</span>
        </div>
        <div class="stat-card">
          <span class="stat-num overcome">{{ overcomeCount }}</span>
          <span class="stat-label">已掌握知识点</span>
        </div>
      </div>

      <div v-if="masteryPoints.length" class="card chart-card">
        <h3>我的知识点掌握度</h3>
        <v-chart class="chart" :option="masteryRadar" autoresize />
      </div>

      <div class="card">
        <el-table :data="gradeRows" border>
          <el-table-column prop="title" label="作业" />
          <el-table-column prop="lang" label="语言" width="80" />
          <el-table-column label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="row.score !== null ? 'success' : 'warning'" size="small">{{ row.status }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="分数" width="80">
            <template #default="{ row }">
              <span v-if="row.score !== null" :class="{ high: row.score >= 80, low: row.score < 60 }" class="score-cell">{{ row.score }}</span>
              <span v-else class="text-placeholder">-</span>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="80">
            <template #default="{ row }">
              <el-button v-if="row.score === null" size="small" type="primary" @click="router.push(`/submit?assignment=${row.id}`)">去做</el-button>
            </template>
          </el-table-column>
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
.stat-num { font-size: var(--fs-data); font-weight: 700; display: block; }
.sub { font-size: var(--fs-h2); color: var(--text-placeholder); font-weight: 400; }
.stat-label { font-size: var(--fs-caption); color: var(--text-secondary); display: block; margin-top: 4px; }

.card { background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius-lg); padding: var(--space-sm); box-shadow: var(--shadow-card); }
.chart-card { padding: var(--space-md); margin-bottom: var(--space-md); }
.chart-card h3 { margin: 0 0 var(--space-sm); font-size: var(--fs-h3, 16px); }
.chart { height: 300px; }
.overcome { color: var(--success, #34D399); }
.score-cell { font-weight: 700; }
.score-cell.high { color: var(--success); }
.score-cell.low { color: var(--danger); }
.text-placeholder { color: var(--text-placeholder); }
</style>
