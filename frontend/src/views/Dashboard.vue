<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { listMyCourses, listCourseAssignments, listCourseStudents } from '@/api/organization'
import { listMySubmissions } from '@/api/submission'
import { ElMessage } from 'element-plus'

interface Course { id: number; name: string; code: string; teacher_id: number; created_at: string }
interface CourseAssign { id: number; title: string; status: string; lang: string }
interface MySubmission { id: number; assignment_id: number; status: string; score: number }

const auth = useAuthStore()
const router = useRouter()
const courses = ref<Course[]>([])
const loading = ref(false)
const selectedCourse = ref<Course | null>(null)
const assignments = ref<CourseAssign[]>([])
const students = ref<[number, string][]>([])
const mySubmissions = ref<MySubmission[]>([])
const detailLoading = ref(false)

async function loadCourses() {
  loading.value = true
  try {
    courses.value = await listMyCourses()
    if (courses.value.length > 0) selectCourse(courses.value[0])
  } catch (e) { console.error('加载课程失败', e) }
  finally { loading.value = false }
}

async function selectCourse(c: Course) {
  selectedCourse.value = c
  detailLoading.value = true
  assignments.value = []
  students.value = []
  mySubmissions.value = []
  try {
    const [a, s] = await Promise.all([
      listCourseAssignments(c.id),
      auth.role === 'teacher' ? listCourseStudents(c.id) : Promise.resolve([]),
    ])
    assignments.value = a
    students.value = s
    if (auth.role === 'student') {
      const allSubs = await listMySubmissions()
      mySubmissions.value = allSubs as MySubmission[]
    }
  } catch (e) { console.error('加载课程详情失败', e) }
  finally { detailLoading.value = false }
}

const publishedAssignments = computed(() => assignments.value.filter(a => a.status === 'published'))
const completedCount = computed(() => publishedAssignments.value.filter(a => mySubmissions.value.some(s => s.assignment_id === a.id && s.status === 'done')).length)
const myAvgScore = computed(() => {
  const done = mySubmissions.value.filter(s => s.status === 'done')
  if (!done.length) return 0
  return Math.round(done.reduce((sum, s) => sum + s.score, 0) / done.length)
})
const assignmentProgress = computed(() => {
  return publishedAssignments.value.map(a => {
    const sub = mySubmissions.value.find(s => s.assignment_id === a.id && s.status === 'done')
    return { ...a, submitted: !!sub, score: sub?.score ?? null }
  })
})
const progressPercent = computed(() => {
  if (!publishedAssignments.value.length) return 0
  return Math.round((completedCount.value / publishedAssignments.value.length) * 100)
})

onMounted(loadCourses)
</script>

<template>
  <div class="page">
    <div class="page-header">
      <div>
        <h1>我的课程</h1>
        <p class="page-desc">{{ auth.role === 'teacher' ? '管理你的课程、作业与班级学情。' : '查看你选的课程，做作业、看诊断、查成绩。' }}</p>
      </div>
      <el-button v-if="auth.role === 'teacher'" type="primary" @click="router.push('/admin')">创建课程</el-button>
    </div>

    <div v-if="!loading && courses.length === 0" class="empty-state">
      <p class="empty-text">{{ auth.role === 'teacher' ? '暂无课程，去创建一门吧' : '暂未选课' }}</p>
      <el-button v-if="auth.role === 'teacher'" type="primary" @click="router.push('/admin')">创建课程</el-button>
    </div>

    <div v-else class="split-layout">
      <aside class="sidebar">
        <div v-for="c in courses" :key="c.id" class="sidebar-item" :class="{ active: selectedCourse?.id === c.id }" @click="selectCourse(c)">
          <h4>{{ c.name }}</h4>
          <span class="code">{{ c.code }}</span>
        </div>
      </aside>

      <main class="main-content" v-loading="detailLoading">
        <template v-if="selectedCourse">
          <div class="detail-header">
            <h2>{{ selectedCourse.name }}</h2>
            <span class="code-tag">{{ selectedCourse.code }}</span>
          </div>

          <div class="stat-row">
            <div class="stat-card">
              <span class="stat-num">{{ assignments.length }}</span>
              <span class="stat-label">作业总数</span>
            </div>
            <div v-if="auth.role === 'teacher'" class="stat-card">
              <span class="stat-num">{{ students.length }}</span>
              <span class="stat-label">选课学生</span>
            </div>
            <div v-if="auth.role === 'student'" class="stat-card">
              <span class="stat-num">{{ completedCount }}<span class="sub">/{{ publishedAssignments.length }}</span></span>
              <span class="stat-label">已完成</span>
            </div>
            <div v-if="auth.role === 'student' && mySubmissions.length" class="stat-card">
              <span class="stat-num">{{ myAvgScore }}</span>
              <span class="stat-label">平均分</span>
            </div>
            <div class="stat-card">
              <span class="stat-num">{{ publishedAssignments.length }}</span>
              <span class="stat-label">已发布</span>
            </div>
          </div>

          <div v-if="auth.role === 'student' && publishedAssignments.length" class="section">
            <div class="progress-bar-wrap">
              <span class="progress-label">完成进度</span>
              <span class="progress-num">{{ progressPercent }}%</span>
            </div>
            <div class="progress-track">
              <div class="progress-fill" :style="{ width: progressPercent + '%' }"></div>
            </div>
          </div>

          <div class="section">
            <div class="section-header">
              <h3>{{ auth.role === 'student' ? '作业进度' : '课程作业' }}</h3>
              <el-button v-if="auth.role === 'teacher'" size="small" type="primary" @click="router.push('/assignment-generate')">AI命题</el-button>
            </div>
            <div v-if="assignmentProgress.length === 0 && auth.role === 'student'" class="empty-inline">暂无已发布作业</div>
            <div v-if="assignments.length === 0 && auth.role === 'teacher'" class="empty-inline">暂无作业</div>
            <div v-for="a in (auth.role === 'student' ? assignmentProgress : assignments)" :key="a.id" class="assign-row">
              <div class="assign-info">
                <span class="assign-title">{{ a.title }}</span>
                <el-tag v-if="auth.role === 'student' && a.submitted" type="success" size="small">{{ a.score }}分</el-tag>
                <el-tag v-else-if="auth.role === 'student'" type="warning" size="small">未提交</el-tag>
                <el-tag v-else :type="a.status === 'published' ? 'success' : 'info'" size="small">{{ a.status === 'published' ? '已发布' : '草稿' }}</el-tag>
              </div>
              <el-button v-if="auth.role === 'student' && !a.submitted" size="small" type="primary" @click="router.push(`/submit?assignment=${a.id}`)">去做</el-button>
              <el-button v-if="auth.role === 'student' && a.submitted" size="small" @click="router.push('/my-submissions')">查看</el-button>
            </div>
          </div>

          <div v-if="auth.role === 'teacher' && students.length" class="section">
            <h3>选课学生</h3>
            <el-table :data="students.map(([id, cls]) => ({ student_id: id, class_name: cls }))" border size="small">
              <el-table-column prop="student_id" label="学生 ID" width="100" />
              <el-table-column prop="class_name" label="班级" />
            </el-table>
          </div>
        </template>
      </main>
    </div>
  </div>
</template>

<style scoped>
.page { max-width: 100%; }
.page-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: var(--space-lg); }
.page-desc { margin: 0; font-size: var(--fs-body); color: var(--text-secondary); }

.empty-state { text-align: center; padding: var(--space-xl) 0; }
.empty-text { color: var(--text-secondary); margin-bottom: var(--space-md); }

.split-layout { display: grid; grid-template-columns: 260px 1fr; gap: var(--space-lg); }

.sidebar { display: flex; flex-direction: column; gap: var(--space-xs); }
.sidebar-item { background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius-lg); padding: var(--space-md); cursor: pointer; transition: all var(--duration) var(--ease); }
.sidebar-item:hover { border-color: var(--primary); box-shadow: var(--shadow-card); }
.sidebar-item.active { border-color: var(--primary); background: var(--bg-hover); }
.sidebar-item h4 { margin: 0 0 4px; font-size: var(--fs-body); }
.code { font-size: var(--fs-caption); color: var(--text-placeholder); font-family: 'JetBrains Mono'; }

.main-content { background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius-lg); padding: var(--space-lg); min-height: 400px; }
.detail-header { display: flex; align-items: center; gap: var(--space-xs); margin-bottom: var(--space-lg); }
.code-tag { font-size: var(--fs-caption); color: var(--text-secondary); background: var(--bg-hover); padding: 3px 10px; border-radius: var(--radius-sm); font-family: 'JetBrains Mono'; }

.stat-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: var(--space-sm); margin-bottom: var(--space-lg); }
.stat-card { background: var(--bg-page); border: 1px solid var(--border); border-radius: var(--radius-md); padding: var(--space-sm) var(--space-md); }
.stat-num { font-size: var(--fs-data); font-weight: 700; color: var(--text-primary); display: block; line-height: 1.1; }
.sub { font-size: var(--fs-h2); color: var(--text-placeholder); font-weight: 400; }
.stat-label { font-size: var(--fs-caption); color: var(--text-secondary); display: block; margin-top: 4px; }

.section { margin-bottom: var(--space-lg); }
.section-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: var(--space-sm); }
.empty-inline { color: var(--text-placeholder); font-size: var(--fs-body); padding: var(--space-md) 0; }

.progress-bar-wrap { display: flex; justify-content: space-between; margin-bottom: var(--space-xs); font-size: var(--fs-caption); color: var(--text-secondary); }
.progress-num { font-weight: 700; color: var(--primary); }
.progress-track { height: 8px; background: var(--bg-page); border-radius: 4px; overflow: hidden; }
.progress-fill { height: 100%; background: linear-gradient(90deg, var(--primary), var(--info)); border-radius: 4px; transition: width 0.5s var(--ease); }

.assign-row { display: flex; justify-content: space-between; align-items: center; padding: var(--space-xs) 0; border-bottom: 1px solid var(--border); }
.assign-info { display: flex; align-items: center; gap: var(--space-xs); }
.assign-title { font-size: var(--fs-body); color: var(--text-primary); }

@media (max-width: 768px) {
  .split-layout { grid-template-columns: 1fr; }
  .stat-row { grid-template-columns: repeat(2, 1fr); }
}
</style>
